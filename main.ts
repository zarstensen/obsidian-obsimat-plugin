import { App, Editor, MarkdownView, Modal, Notice, Plugin, PluginSettingTab, Setting } from 'obsidian';
import { EditorState } from "@codemirror/state";
import { EquationExtractor } from "src/EquationExtractor";
import { spawn } from 'child_process';
import { join } from 'path';
import { WebSocketServer } from 'ws';
import getPort from 'get-port';
import { SympyEvaluator } from 'src/SympyEvaluator';
import { SymbolSelectorModal } from 'src/SymbolSelectorModal';
import { syntaxTree } from "@codemirror/language";

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

        this.sympy_evaluator.initialize(this.app.vault.adapter.basePath);

		// Add the evaluate command
		this.addCommand({
			id: 'evaluate-latex-expression-command',
			name: 'Evaluate LaTeX Expression (Sympy)',
			editorCallback: async (editor: Editor, view: MarkdownView) => {
                const equation = EquationExtractor.extractEquation(editor.posToOffset(editor.getCursor()), editor);

                if(equation === null) {
                    new Notice("You are not inside a math block");
                    return;
                }

                // now pipe it to python
                await this.sympy_evaluator.send("evaluate", { expression: equation.contents });
                const response = await this.sympy_evaluator.receive();
                
                editor.replaceRange(" = " + response.result, editor.offsetToPos(equation.to));
                editor.setCursor(editor.offsetToPos(equation.to + response.result.length + 3));
			}
		});

        // Add the solve command
		this.addCommand({
			id: 'solve-latex-expression-command',
			name: 'Solve LaTeX Expression (Sympy)',
			editorCallback: async (editor: Editor, view: MarkdownView) => {
                const equation = EquationExtractor.extractEquation(editor.posToOffset(editor.getCursor()), editor);

                if(equation === null) {
                    new Notice("You are not inside a math block");
                    return;
                }

                // now pipe it to python
                await this.sympy_evaluator.send("solve", { expression: equation.contents });
                const response = await this.sympy_evaluator.receive();

                if(response.status === "solved") {
                    editor.replaceRange(" $$" + response.result + "$$", editor.offsetToPos(equation.block_to));
                    editor.setCursor(editor.offsetToPos(equation.to + response.result.length + 3));
                } else {
                    // prompt user for variables, and try again.
                    const symbol_selector = new SymbolSelectorModal(response.symbols, this.app);
                    symbol_selector.open();
                    const symbol = await symbol_selector.getResultAsync();
                    await this.sympy_evaluator.send("solve", { expression: equation.contents, symbol: symbol });
                    const new_response = await this.sympy_evaluator.receive();

                    editor.replaceRange(" $$" + new_response.result + "$$", editor.offsetToPos(equation.block_to));
                    editor.setCursor(editor.offsetToPos(equation.to + new_response.result.length + 3));
                }
                
			}
		});

                
                editor.replaceRange("\n" + response.result, editor.offsetToPos(equation.block_to));
                editor.setCursor(editor.offsetToPos(equation.to + response.result.length + 3));
			}
		});
	}

	onunload() {

	}

    private sympy_evaluator: SympyEvaluator;
}