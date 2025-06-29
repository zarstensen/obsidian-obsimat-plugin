import { App, Editor, MarkdownView, Notice } from "obsidian";
import { SympyServer } from "src/SympyServer";
import { ILatexMathCommand } from "./ILatexMathCommand";
import { EquationExtractor } from "src/EquationExtractor";
import { LmatEnvironment } from "src/LmatEnvironment";
import { SolveModeModal } from "src/SolveModeModal";
import { formatLatex } from "src/FormatLatex";

export enum TruthTableFormat {
    MARKDOWN = "md",
    LATEX_ARRAY = "latex-array",
}

export class TruthTableCommand implements ILatexMathCommand {
    readonly id: string;

    constructor(public format: TruthTableFormat) {
        this.truth_table_format = format;
        this.id = `generate-${this.truth_table_format}-truth-table`;
    }

    async functionCallback(evaluator: SympyServer, app: App, editor: Editor, view: MarkdownView, message: Record<string, any> = {}): Promise<void> {
        // Extract the equation to generate truth table for
        const equation = EquationExtractor.extractEquation(editor.posToOffset(editor.getCursor()), editor);

        if (equation === null) {
            new Notice("You are not inside a math block");
            return;
        }

        const lmat_env = LmatEnvironment.fromMarkdownView(app, view);

        // Send it to python.
        await evaluator.send("truth-table", {
            expression: equation.contents,
            environment: lmat_env,
            table_format: this.truth_table_format
        });

        const response = await evaluator.receive();

        console.log(response);

        // at this point we should have a response that is solved.
        // if not, something has gone wrong somewhere.
        if (response.status === "success") {
            // Insert solution right after the current math block.
            let insert_content: string = '\n' + response.result.truth_table;

            if(this.format == TruthTableFormat.LATEX_ARRAY) {
                insert_content = "$$\n" + await formatLatex(insert_content) + "\n$$";
            }

            editor.replaceRange(insert_content, editor.offsetToPos(equation.block_to));
            editor.setCursor(editor.offsetToPos(equation.to + insert_content.length));
        } else {
            console.error(response);
            new Notice("Unable to generate truth table, unknown error");
        }
    }
 
    private readonly truth_table_format: TruthTableFormat;
}
