import { Editor, finishRenderMath, MarkdownPostProcessorContext, MarkdownView, Notice, Plugin, renderMath } from 'obsidian';
import { EquationExtractor } from "src/EquationExtractor";
import { SympyEvaluator } from 'src/SympyEvaluator';
import { SymbolSelectorModal } from 'src/SymbolSelectorModal';
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


        // Add the evaluate command
        this.addCommand({
            id: 'evaluate-latex-expression-command',
            name: 'Evaluate LaTeX Expression (Sympy)',
            hotkeys: [ { modifiers: ["Alt"], key: "b" } ],
            editorCallback: this.evaluateCommand.bind(this)
        });
        
        // Add the solve command
        this.addCommand({
            id: 'solve-latex-expression-command',
            name: 'Solve LaTeX Expression (Sympy)',
            hotkeys: [ { modifiers: ["Alt"], key: "l" } ],
            editorCallback: this.solveCommand.bind(this)
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

        // insert result at the end of the equation.
        editor.replaceRange(" = " + response.result, editor.offsetToPos(equation.to));
        editor.setCursor(editor.offsetToPos(equation.to + response.result.length + 3));
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
            const symbol_selector = new SymbolSelectorModal(response.symbols, this.app);
            symbol_selector.open();
            const symbol = await symbol_selector.getSelectedSymbolAsync();

            await this.sympy_evaluator.send("solve", { expression: equation.contents, environment: obsimat_env, symbol: symbol });

            response = await this.sympy_evaluator.receive();
        }

        // at this point we should have a response that is solved.
        // if not, something has gone wrong somewhere.
        if (response.status === "solved") {
            // Insert solution as a new math block, right after the current one.
            editor.replaceRange("\n$$" + response.result + "$$", editor.offsetToPos(equation.block_to));
            editor.setCursor(editor.offsetToPos(equation.to + response.result.length + 3));
        } else {
            console.error(response);
            new Notice("Unable to solve equation, unknown error");
        }
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