import { App, Editor, MarkdownView } from "obsidian";
import { SympyServer } from "src/SympyServer";

// Interface for a latex math command
// The id will be used to set the resulting obsidian command id.
// function callback is called whenever the command has been invoked by the user.
export interface ILatexMathCommand {
    readonly id: string;

    functionCallback(evaluator: SympyServer, app: App, editor: Editor, view: MarkdownView, message: Record<string, any>): Promise<void>; // Method to execute the command
}