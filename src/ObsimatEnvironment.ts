import { App, Editor, EditorPosition, MarkdownView } from "obsidian";
import * as toml from "toml";

// The ObsimatEnvironment class represents an environment detailing how mathematical expressions,
// should be evaluated.
// it contains information about symbol assumptions, variable definitions, units, and solution domains.
export class ObsimatEnvironment {

    // symbols is a map of a symbols name and a list of all the assumptions,
    // which sympy will take into account when evaluating any expression, containing this symbol.
    public symbols: { [symbol: string]: string[] } | undefined;
    // variables is a map of variable names and their corresponding substitutable values.
    // these values should be substituted into any expression before evaluation.
    public variables: { [variable: string]: string } | undefined;

    // the units which any expression in this environment should handle.
    public units: string[] | undefined;
    // the base_units list specifies a list of units which any expression result should convert its own units to.
    public base_units: string[] | undefined;
    // the domain is a sympy expression, evaluating to the default solution domain of any equation solutions.
    public domain: string | undefined;

    public static fromCodeBlock(code_block: string | undefined, variables: { [variable: string]: string }) {
        if(!code_block) {
            return new ObsimatEnvironment(undefined, variables);
        }

        const parsed_obsimat_block = toml.parse(code_block);

        // prioritize domain name over domain expression.


        return new ObsimatEnvironment(
            parsed_obsimat_block.symbols,
            variables,
            parsed_obsimat_block.units?.units,
            parsed_obsimat_block.units?.['base-units'],
            parsed_obsimat_block.domain?.domain
        );
    }

    // construct an ObsimatEnvironment class from the given active document, and cursor position.
    // this environment is constructed based on the closest obsimat code block to the cursor (ignoring any blocks after the cursor).
    // variables are parsed from the text between the code block and the cursor.
    public static fromMarkdownView(app: App, markdown_view: MarkdownView, position?: EditorPosition): ObsimatEnvironment {
        // start by finding all obsimat code block.
        position ??= markdown_view.editor.getCursor();

        if (!markdown_view.file) {
            throw new Error("No file found in the given markdown view");
        }

        let sections = app.metadataCache.getFileCache(markdown_view.file)?.sections;

        if (!sections) {
            throw new Error("No sections found in the given file");
        }

        const editor = markdown_view.editor;

        // filter out any non obsimat code block sections
        sections = sections
            .filter((section) => section.type === "code")
            .filter((section) => {
                const code_block_contents = editor.getRange(editor.offsetToPos(section.position.start.offset), editor.offsetToPos(section.position.end.offset));
                return this.OBSIMAT_BLOCK_REGEX.test(code_block_contents);
            });
        
        // find the closest obsimat code block

        let closest_section = undefined;

        for(const section of sections) {
            if(section.position.end.offset < editor.posToOffset(position)) {
                closest_section = section;
            } else {
                break;
            }
        }

        if(!closest_section) {
            return new ObsimatEnvironment(undefined, this.parseVariables(editor.offsetToPos(0), position, editor));
        }

        // now generate obsimat environment based on section contents.

        const obsimat_block = editor.getRange(editor.offsetToPos(closest_section.position.start.offset), editor.offsetToPos(closest_section.position.end.offset));
        const obsimat_block_content = obsimat_block.match(this.OBSIMAT_BLOCK_REGEX)?.[1];
        const obsimat_variables = this.parseVariables(editor.offsetToPos(closest_section.position.end.offset), position, editor);

        return ObsimatEnvironment.fromCodeBlock(obsimat_block_content, obsimat_variables);
    }

    // regex for extracting the contents of an obsimat code block.
    private static readonly OBSIMAT_BLOCK_REGEX = /^```obsimat\s*(?:\r\n|\r|\n)([\s\S]*?)```$/;
    // regex for finding variable definitions in markdown code.
    private static readonly OBSIMAT_VARIABLE_DEF_REGEX = /\$\s*(?:\\math\w*{(?<symbol_math_encapsulated>[^=\s$]*)}|(?<symbol>[^=\s$]*))\s*:=\s*(?<value>[^=$]*?)\s*\$/g;

    private constructor(symbols?: { [symbol: string]: string[] }, variables?: { [variable: string]: string }, units?: string[], base_units?: string[], domain?: string) {
        this.symbols = symbols;
        this.variables = variables;
        this.units = units;
        this.base_units = base_units;
        this.domain = domain;
    }

    // find all variable definitions in the given document interval,
    // and parse them into a variables map.
    private static parseVariables(from: EditorPosition, to: EditorPosition, editor: Editor) {
        const variables: { [variable: string]: string } = {};

        const search_range = editor.getRange(from, to);
        const variable_definitions = search_range.matchAll(this.OBSIMAT_VARIABLE_DEF_REGEX);

        for(const variable_definition of variable_definitions) {
            if((!variable_definition.groups?.symbol && !variable_definition.groups?.symbol_math_encapsulated) || !variable_definition.groups?.value) {
                continue;
            }

            variables[variable_definition.groups.symbol ?? variable_definition.groups.symbol_math_encapsulated ] = variable_definition.groups.value;
        }

        return variables;
    }
}