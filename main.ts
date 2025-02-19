import { Editor, finishRenderMath, MarkdownPostProcessorContext, MarkdownView, Notice, Plugin, renderMath, EditorPosition } from 'obsidian';
import { EquationExtractor } from "src/EquationExtractor";
import { SympyEvaluator } from 'src/SympyEvaluator';
import { SolveModeModal } from 'src/SolveModeModal';
import { ObsimatEnvironment } from 'src/ObsimatEnvironment';

export default class ObsiMatPlugin extends Plugin {

    async onload() {
        this.sympy_evaluator = new SympyEvaluator();

        this.sympy_evaluator.onError((error) => {
            // limit error message to 4 lines,
            // need to check the developer console to see the full message.
            const maxLines = 4;
            const errorLines = error.split('\n');
            const truncatedError = errorLines.slice(0, maxLines).join('\n') + (errorLines.length > maxLines ? '\n...' : '');
            new Notice("Error\n" + truncatedError);
        });

        if(!this.manifest.dir) {
            new Notice("Obsimat could not determine its plugin directory, aborting load.");
            return;
        }

        this.sympy_evaluator.initialize(this.app.vault, this.manifest.dir);

        this.registerMarkdownCodeBlockProcessor("obsimat", this.renderObsimatCodeBlock.bind(this));


        // Add commands

        this.addCommand({
            id: 'evaluate-latex-expression-command',
            name: 'Evaluate LaTeX Expression (Sympy)',
            hotkeys: [ { modifiers: ["Alt"], key: "b" } ],
            editorCallback: this.evaluateCommand.bind(this)
        });
        
        this.addCommand({
            id: 'solve-latex-expression-command',
            name: 'Solve LaTeX Expression (Sympy)',
            hotkeys: [ { modifiers: ["Alt"], key: "l" } ],
            editorCallback: this.solveCommand.bind(this)
        });

        this.addCommand({
            id: 'convert-to-sympy-command',
            name: 'Convert LaTeX Expression To Sympy',
            editorCallback: this.convertToSympyCommand.bind(this)
        });
    }

    onunload() {
        // TODO: unload a BUNCH of stuff here.
    }

    private async evaluateCommand(editor: Editor, view: MarkdownView) {
        // Extract equation to evaluate
        const equation = EquationExtractor.extractEquation(editor.posToOffset(editor.getCursor()), editor);

        if (equation === null) {
            new Notice("You are not inside a math block");
            return;
        }

        // send it to python and wait for response.
        await this.sympy_evaluator.send("evaluate", {
            expression: equation.contents,
            environment: ObsimatEnvironment.fromMarkdownView(this.app, view)
        });
        const response = await this.sympy_evaluator.receive();

        const insert_pos: EditorPosition = editor.offsetToPos(equation.to)
        const insert_content = " = " + response.result


        // check if we have gotten a preferred insert position from SympyEvaluator,
        // if not just place it at the end of the equation.
        if (response.metadata.end_line !== undefined) {
            insert_pos.line = editor.offsetToPos(equation.from).line + response.metadata.end_line - 1;
            insert_pos.ch = editor.getLine(insert_pos.line).length;
        }

        // insert result at the end of the equation.
        editor.replaceRange(insert_content, insert_pos);
        editor.setCursor(editor.offsetToPos(editor.posToOffset(insert_pos) + insert_content.length));
    }

    private async solveCommand(editor: Editor, view: MarkdownView) {
        // Extract the equation to solve
        const equation = EquationExtractor.extractEquation(editor.posToOffset(editor.getCursor()), editor);

        if (equation === null) {
            new Notice("You are not inside a math block");
            return;
        }

        const obsimat_env = ObsimatEnvironment.fromMarkdownView(this.app, view);

        // Send it to python.
        await this.sympy_evaluator.send("solve", {
            expression: equation.contents,
            environment: obsimat_env
        });

        let response = await this.sympy_evaluator.receive();

        // response may have different statuses depending on the equation.
        // if the equation is multivariate, then we need to prompt the user for which symbols should be solved for.

        if (response.status === "multivariate_equation") {
            const symbol_selector = new SolveModeModal(
                response.result['symbols'],
                response.result['equation_count'],
                obsimat_env.domain ?? "",
                this.app);
            symbol_selector.open();
            
            // wait for the solve configuration.
            const config = await symbol_selector.getSolveConfig();
            obsimat_env.domain = config.domain;

            await this.sympy_evaluator.send("solve", { expression: equation.contents, environment: obsimat_env, symbols: [...config.symbols].map((symbol) => symbol.sympy_symbol) });

            response = await this.sympy_evaluator.receive();
        }

        // at this point we should have a response that is solved.
        // if not, something has gone wrong somewhere.
        if (response.status === "success") {
            // Insert solution as a new math block, right after the current one.
            editor.replaceRange("\n$$" + response.result + "$$", editor.offsetToPos(equation.block_to));
            editor.setCursor(editor.offsetToPos(equation.to + response.result.length + 3));
        } else {
            console.error(response);
            new Notice("Unable to solve equation, unknown error");
        }
    }

    private async convertToSympyCommand(editor: Editor, view: MarkdownView) {
        // Extract the equation to convert
        const equation = EquationExtractor.extractEquation(editor.posToOffset(editor.getCursor()), editor);

        if (equation === null) {
            new Notice("You are not inside a math block");
            return;
        }
        
        const obsimat_env = ObsimatEnvironment.fromMarkdownView(this.app, view);

        await this.sympy_evaluator.send("convert-sympy", {
            expression: equation.contents,
            environment: obsimat_env
        });

        let response = await this.sympy_evaluator.receive();

        console.log(response);

        // place the convertet python code into a code block right below the math block.

        const sympy_code_block = "\n```python\n" + response.result + "\n```\n";

        editor.replaceRange(sympy_code_block, editor.offsetToPos(equation.block_to));
        editor.setCursor(editor.offsetToPos(equation.to + sympy_code_block.length));
    }

    private async renderObsimatCodeBlock(source: string, el: HTMLElement, ctx: MarkdownPostProcessorContext): Promise<void> {
        // Add the standard code block background div,
        // to ensure a consistent look with other code blocks.
        const div = el.createDiv("HyperMD-codeblock HyperMD-codeblock-bg")
        div.style.cssText = "overflow: auto;";
        // same goes with the code block flair
        const flair = div.createSpan("code-block-flair obsimat-block-flair");
        flair.innerText = "Obsimat";
        div.appendChild(flair);

        el.appendChild(div);

        // retreive to be rendered latex from python.
        await this.sympy_evaluator.send("symbolsets", { environment: ObsimatEnvironment.fromCodeBlock(source, {}) });
        const response = await this.sympy_evaluator.receive();
        
        // render the latex.
        div.appendChild(renderMath(response.result, true));
        finishRenderMath();
    }

    private sympy_evaluator: SympyEvaluator;
}