import { App, Editor, EditorPosition, MarkdownView } from "obsidian";
import * as toml from "toml";

// The ObsimatEnvironment class represents an environment detailing how mathematical expressions,
// should be evaluated.
// it contains information about symbol assumptions, variable definitions, units, and solution domains.
export class ObsimatEnvironment {

    public static fromCodeBlock(code_block: string | undefined, variables: { [variable: string]: string }, functions: { [func: string]: { args: string[], expr: string } }) {
        if(!code_block) {
            return new ObsimatEnvironment({}, variables, functions);
        }

        const parsed_obsimat_block = toml.parse(code_block);

        // prioritize domain name over domain expression.

        return new ObsimatEnvironment(
            parsed_obsimat_block.symbols,
            variables,
            functions,
            parsed_obsimat_block.units?.system,
            parsed_obsimat_block.units?.exclude,
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
            return new ObsimatEnvironment(undefined, this.parseVariables(editor.offsetToPos(0), position, editor), this.parseFunctions(editor.offsetToPos(0), position, editor));
        }

        // now generate obsimat environment based on section contents.

        const obsimat_block = editor.getRange(editor.offsetToPos(closest_section.position.start.offset), editor.offsetToPos(closest_section.position.end.offset));
        const obsimat_block_content = obsimat_block.match(this.OBSIMAT_BLOCK_REGEX)?.[1];
        const obsimat_functions = this.parseFunctions(editor.offsetToPos(closest_section.position.end.offset), position, editor);
        const obsimat_variables = this.parseVariables(editor.offsetToPos(closest_section.position.end.offset), position, editor);

        return ObsimatEnvironment.fromCodeBlock(obsimat_block_content, obsimat_variables, obsimat_functions);
    }

    // regex for extracting the contents of an obsimat code block.
    private static readonly OBSIMAT_BLOCK_REGEX = /^```obsimat\s*(?:\r\n|\r|\n)([\s\S]*?)```$/;
    private static readonly OBSIMAT_VARIABLE_REGEX = /\s*(?:\\math\w*{(?<symbol_math_encapsulated>[^=\s$]*)}|(?<symbol>[^=\s$]*))\s*/;
    // regex for finding variable definitions in markdown code.
    private static readonly OBSIMAT_VARIABLE_DEF_REGEX = new RegExp(String.raw`\$${this.OBSIMAT_VARIABLE_REGEX.source}:=\s*(?<value>[^=$]*?)\s*\$`, 'g');
    private static readonly OBSIMAT_FUNCTION_DEF_REGEX = new RegExp(String.raw`\$${this.OBSIMAT_VARIABLE_REGEX.source}\((?<args>(?:[^=$]*?\s*))\)\s*:=\s*(?<expr>[^=$]*?)\s*\$`, 'g');

    private constructor(
        /**
         * symbols is a map of a symbols name and a list of all the assumptions,
         * which sympy will take into account when evaluating any expression, containing this symbol.
         */
        public symbols: { [symbol: string]: string[] } = {},
        /**
         * variables is a map of variable names and their corresponding substitutable values.
         * these values should be substituted into any expression before evaluation.
         */
        public variables: { [variable: string]: string } = {},
        public functions: { [func: string]: { args: string[], expr: string } } = {},
        /**
         * the unit system to use when converting between units.
         * if left undefined, no unit conversion takes place.
         */
        public unit_system: string | undefined = undefined,
        /**
         * the excluded_symbols list specifies a list symbols which should not be converted to units.
         * if left undefined, a default list of commonly excluded symbols will be used instead.
         */
        public excluded_symbols: string[] | undefined = undefined,
        /**
         * the domain is a sympy expression, evaluating to the default solution domain of any equation solutions.
         */
        public domain: string | undefined = undefined
    ) { }

    // find all variable definitions in the given document interval,
    // and parse them into a variables map.
    private static parseVariables(from: EditorPosition, to: EditorPosition, editor: Editor) {
        const variables: { [variable: string]: string } = {};
        
        const search_range = editor.getRange(from, to);
        const variable_definitions = search_range.matchAll(this.OBSIMAT_VARIABLE_DEF_REGEX);

        for(const var_def of variable_definitions) {

            const var_name = var_def.groups?.symbol ?? var_def.groups?.symbol_math_encapsulated;

            if(var_name == undefined) {
                continue;
            }
            
            const value = var_def.groups?.value;

            if(value == undefined || value?.trim() === "") {
                delete variables[var_name];
                continue;
            }

            variables[var_name] = value;
        }

        return variables;
    }

    private static parseFunctions(from: EditorPosition, to: EditorPosition, editor: Editor) {
        const functions: { [func: string]: { args: string[], expr: string } } = {};
        
        const search_range = editor.getRange(from, to);
        const function_definitions = search_range.matchAll(this.OBSIMAT_FUNCTION_DEF_REGEX);

        
        for(const func_def of function_definitions) {
            const func_name = func_def.groups?.symbol ?? func_def.groups?.symbol_math_encapsulated;
            const func_args = func_def.groups?.args; 
            
            if(func_name == undefined || func_args == undefined) {
                continue;
            }
            
            const func_expr = func_def.groups?.expr;

            if(func_expr == undefined || func_expr?.trim() === "") {
                delete functions[func_name];
                continue;
            }


            functions[func_name] = {
                args: func_args.split(',').map(arg => arg.trim()),
                expr: func_expr
            };
        }

        return functions;
    }
}