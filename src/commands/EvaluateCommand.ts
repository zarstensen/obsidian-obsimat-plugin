import { App, Editor, EditorPosition, MarkdownView, Notice } from "obsidian";
import { SympyEvaluator } from "src/SympyEvaluator";
import { ILatexMathCommand } from "./ILatexMathCommand";
import { EquationExtractor } from "src/EquationExtractor";
import { LmatEnvironment } from "src/LmatEnvironment";
import { formatLatex } from "src/FormatLatex";

export class EvaluateCommand implements ILatexMathCommand {
    readonly id: string;

    constructor(evaluate_mode: string) {
        this.id = `${evaluate_mode}-latex-expression`;
        this.evaluate_mode = evaluate_mode;
    }
    
    public async functionCallback(evaluator: SympyEvaluator, app: App, editor: Editor, view: MarkdownView, message: Record<string, any> = {}): Promise<void> {
                
        let equation: { from: number, to: number, contents: string } | null = null;
        
        // Extract equation to evaluate
        if(editor.getSelection().length <= 0) {
            equation = EquationExtractor.extractEquation(editor.posToOffset(editor.getCursor()), editor);
        } else {
            equation = {
              from: editor.posToOffset(editor.getCursor('from')),
              to: editor.posToOffset(editor.getCursor('to')),
              contents: editor.getSelection()  
            } ;
        }

        if (equation === null) {
            new Notice("You are not inside a math block");
            return;
        }

        message.expression = equation.contents;
        message.environment = LmatEnvironment.fromMarkdownView(app, view);

        // send it to python and wait for response.
        await evaluator.send(this.evaluate_mode, message);
        const response = await evaluator.receive();

        const insert_pos: EditorPosition = editor.offsetToPos(equation.to);
        const insert_content = " = " + await formatLatex(response.result);


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
    
    private evaluate_mode: string;
}