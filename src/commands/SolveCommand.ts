import { App, Editor, MarkdownView, Notice } from "obsidian";
import { SympyEvaluator } from "src/SympyEvaluator";
import { ILatexMathCommand } from "./ILatexMathCommand";
import { EquationExtractor } from "src/EquationExtractor";
import { LmatEnvironment } from "src/LmatEnvironment";
import { SolveModeModal } from "src/SolveModeModal";
import { formatLatex } from "src/FormatLatex";

export class SolveCommand implements ILatexMathCommand {
    readonly id: string = 'solve-latex-expression';

    async functionCallback(evaluator: SympyEvaluator, app: App, editor: Editor, view: MarkdownView, message: Record<string, any> = {}): Promise<void> {
        // Extract the equation to solve
        const equation = EquationExtractor.extractEquation(editor.posToOffset(editor.getCursor()), editor);

        if (equation === null) {
            new Notice("You are not inside a math block");
            return;
        }

        const lmat_env = LmatEnvironment.fromMarkdownView(app, view);

        // Send it to python.
        await evaluator.send("solve", {
            expression: equation.contents,
            environment: lmat_env
        });

        let response = await evaluator.receive();

        // response may have different statuses depending on the equation.
        // if the equation is multivariate, then we need to prompt the user for which symbols should be solved for.

        if (response.status === "multivariate_equation") {
            const symbol_selector = new SolveModeModal(
                response.result['symbols'],
                response.result['equation_count'],
                lmat_env.domain ?? "",
                app);
            symbol_selector.open();
            
            // wait for the solve configuration.
            const config = await symbol_selector.getSolveConfig();
            lmat_env.domain = config.domain;

            await evaluator.send("solve", { expression: equation.contents, environment: lmat_env, symbols: [...config.symbols].map((symbol) => symbol.sympy_symbol) });

            response = await evaluator.receive();
        }

        // at this point we should have a response that is solved.
        // if not, something has gone wrong somewhere.
        if (response.status === "success") {
            // Insert solution as a new math block, right after the current one.
            editor.replaceRange("\n$$" + await formatLatex(response.result) + "$$", editor.offsetToPos(equation.block_to));
            editor.setCursor(editor.offsetToPos(equation.to + response.result.length + 3));
        } else {
            console.error(response);
            new Notice("Unable to solve equation, unknown error");
        }
    }
    
}
