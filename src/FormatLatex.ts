import * as Prettier from "prettier/standalone";
import * as prettierPluginLatex from "prettier-plugin-latex";

// Indent and format the given string of latex source code, for prettier printing.
export async function formatLatex(latex_string: string): Promise<string> {
    return await Prettier.format(latex_string, {
        printWidth: 80,
        useTabs: false,
        parser: "latex-parser",
        plugins: [ prettierPluginLatex ]
    });
}

