import { syntaxTree } from "@codemirror/language";
import { EditorState } from "@codemirror/state";
import { Editor } from "obsidian";

export class EquationExtractor {
    
    // Extract the contents of the equation block, which the given position offset is currently inside.
    // Returns null if the position is not inside an equation.
    public static extractEquation(position: number, editor: Editor) : { from: number; to: number, block_from: number, block_to: number, contents: string} | null {
        const state = (editor as any).cm.state as EditorState;
        
        // we cannot extract an equation if we are not currently within one.
        if(!this.isWithinEquation(position, state)) {
            return null;
        }
        
        // simply travel left and right until we are no longer inside an equation.
        
        let from = position;
        let to = position;

        while(this.isWithinEquation(from, state)) {
            from--;
        }

        from++;

        while(this.isWithinEquation(to, state)) {
            to++;
        }

        to--;

        let block_from = from - 1;
        let block_to = to + 1;

        if(editor.getRange(editor.offsetToPos(from), editor.offsetToPos(from + 1)) === "$") {
            from++;

            block_from = from - 2;
            block_to = to + 2;
        }

        return {
            from: from,
            to: to,
            block_from: block_from,
            block_to: block_to,
            contents: editor.getRange(editor.offsetToPos(from), editor.offsetToPos(to))
        };
    }

    // Check if the given cursor offset is inside an equation.
    // Taken from obsidian latex suite plugin:
    // https://github.com/artisticat1/obsidian-latex-suite/blob/main/src/utils/context.ts#L157
    public static isWithinEquation(position: number, state: EditorState) : boolean {
        const tree = syntaxTree(state);

        let syntaxNode = tree.resolveInner(position, -1);
        if (syntaxNode.name.contains("math-end")) return false;

        if (!syntaxNode.parent) {
            syntaxNode = tree.resolveInner(position, 1);
            if (syntaxNode.name.contains("math-begin")) return false;
        }

        // Account/allow for being on an empty line in a equation
        if (!syntaxNode.parent) {
            const left = tree.resolveInner(position - 1, -1);
            const right = tree.resolveInner(position + 1, 1);

            return (left.name.contains("math") && right.name.contains("math") && !(left.name.contains("math-end")));
        }

        return (syntaxNode.name.contains("math"));
    }
}