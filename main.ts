import { App, Editor, MarkdownView, Modal, Notice, Plugin, PluginSettingTab, Setting } from 'obsidian';
import { EditorState } from "@codemirror/state";
import { EquationExtractor } from "./src/EquationExtractor";
import { spawn } from 'child_process';
import { join } from 'path';

export default class ObsiMatPlugin extends Plugin {

	async onload() {

        // Start python sympy connection
        const pythonProcess = spawn('python', [join(this.app.vault.adapter.basePath, '.obsidian/plugins/obsimat-plugin/sympy_evaluator.py')]);

        // pythonProcess.stdout.on('data', (data) => {
        //     console.log(`stdout: ${data}`);
        // });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });

        pythonProcess.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
        });

		// This adds an editor command that can perform some operation on the current editor instance
		this.addCommand({
			id: 'evaluate-latex-expression-command',
			name: 'Evaluate LaTeX Expression (Sympy)',
			editorCallback: (editor: Editor, view: MarkdownView) => {
                console.log(editor);
                const editor_state = (editor as any).cm.state as EditorState;

                const equation_range = EquationExtractor.extractEquation(editor.posToOffset(editor.getCursor()), editor_state);

                if(equation_range === null) {
                    new Notice("You are not inside a math block");
                    return;
                }

                let equation = editor.getRange(editor.offsetToPos(equation_range.from), editor.offsetToPos(equation_range.to));

                if(equation.startsWith("$")) {
                    equation = equation.substring(1);
                }

                // now pipe it to python
                pythonProcess.stdin.write("BEGIN_EVALUATE\n");
                pythonProcess.stdin.write(equation + "\n");
                pythonProcess.stdin.write("END_EVALUATE\n");
                
                pythonProcess.stdout.once('data', (data) => {
                    const result = data.toString();
                    const regex = /BEGIN_RESULT([\s\S]*?)END_RESULT/;
                    const match = regex.exec(result);
                    const extractedResult = match ? match[1].trim() : "No result found";
                    editor.replaceRange(" = " + extractedResult, editor.offsetToPos(equation_range.to));
                    console.log(data.toString());
                    console.log("NEW ENTRY");
                    new Notice(data.toString());
                });
			}
		});
	}

	onunload() {

	}
}