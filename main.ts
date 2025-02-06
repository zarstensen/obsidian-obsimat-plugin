import { App, Editor, MarkdownView, Modal, Notice, Plugin, PluginSettingTab, Setting } from 'obsidian';
import { EditorState } from "@codemirror/state";
import { EquationExtractor } from "src/EquationExtractor";
import { spawn } from 'child_process';
import { join } from 'path';
import { WebSocketServer } from 'ws';
import getPort from 'get-port';
import { PythonEvalServer } from 'src/PythonEvalServer';

export default class ObsiMatPlugin extends Plugin {

	async onload() {
        const python_eval_server = new PythonEvalServer();
        python_eval_server.onError((error) => { new Notice("Error\n" + error)});
        await python_eval_server.initialize(this.app.vault.adapter.basePath);

		// This adds an editor command that can perform some operation on the current editor instance
		this.addCommand({
			id: 'evaluate-latex-expression-command',
			name: 'Evaluate LaTeX Expression (Sympy)',
			editorCallback: (editor: Editor, view: MarkdownView) => {
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

                // and await result
                python_eval_server.receive().then((result) => {
                    editor.replaceRange(" = " + result, editor.offsetToPos(equation_range.to));
                });
                
                // now pipe it to python
                python_eval_server.send("evaluate", equation);
			}
		});
	}

	onunload() {

	}
}