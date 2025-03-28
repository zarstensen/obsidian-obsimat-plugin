import { App, Editor, MarkdownView } from "obsidian";
import { SympyEvaluator } from "src/SympyEvaluator";

export interface IObsimatCommand {
    readonly id: string;

    functioncallback(app: App, evaluator: SympyEvaluator, editor: Editor, view: MarkdownView): Promise<void>; // Method to execute the command
}