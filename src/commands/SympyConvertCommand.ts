import { App, Editor, MarkdownView, Notice } from "obsidian";
import { SympyEvaluator } from "src/SympyEvaluator";
import { IObsimatCommand } from "./IObsimatCommand";
import { EquationExtractor } from "src/EquationExtractor";
import { ObsimatEnvironment } from "src/ObsimatEnvironment";

export class SympyConvertCommand implements IObsimatCommand {
    readonly id: string = 'convert-to-sympy-command';

    async functioncallback(app: App, evaluator: SympyEvaluator, editor: Editor, view: MarkdownView): Promise<void> {
        let equation: { from: number, to: number, block_to: number, contents: string } | null = null;
        
        // Extract equation to evaluate
        if(editor.getSelection().length <= 0) {
            equation = EquationExtractor.extractEquation(editor.posToOffset(editor.getCursor()), editor);
        } else {
            equation = {
              from: editor.posToOffset(editor.getCursor('from')),
              to: editor.posToOffset(editor.getCursor('to')),
              block_to: editor.posToOffset(editor.getCursor('to')),
              contents: editor.getSelection()  
            } ;
        }

        if (equation === null) {
            new Notice("You are not inside a math block");
            return;
        }
        
        const obsimat_env = ObsimatEnvironment.fromMarkdownView(app, view);

        await evaluator.send("convert-sympy", {
            expression: equation.contents,
            environment: obsimat_env
        });

        const response = await evaluator.receive();

        console.log(response);

        // place the convertet python code into a code block right below the math block.

        const sympy_code_block = "\n```python\n" + response.result + "\n```\n";

        editor.replaceRange(sympy_code_block, editor.offsetToPos(equation.block_to));
        editor.setCursor(editor.offsetToPos(equation.to + sympy_code_block.length));
    }
    
}