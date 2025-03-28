import { finishRenderMath, MarkdownPostProcessorContext, Notice, Plugin, renderMath } from 'obsidian';
import { SympyEvaluator } from 'src/SympyEvaluator';
import { ObsimatEnvironment } from 'src/ObsimatEnvironment';
import { ExecutableSpawner, SourceCodeSpawner } from 'src/SympyClientSpawner';
import { ObsimatSettingsTab } from 'src/ObsimatSettingsTab';
import { IObsimatCommand } from 'src/commands/IObsimatCommand';
import { EvaluateCommand } from 'src/commands/EvaluateCommand';
import { SolveCommand } from 'src/commands/SolveCommand';
import { SympyConvertCommand } from 'src/commands/SympyConvertCommand';

interface ObsimatPluginSettings {
    dev_mode: boolean;
}

const DEFAULT_SETTINGS: ObsimatPluginSettings = {
    dev_mode: false
};

export default class ObsiMatPlugin extends Plugin {
    settings: ObsimatPluginSettings;

    async onload() {
        await this.loadSettings();
        this.addSettingTab(new ObsimatSettingsTab(this.app, this));

        this.sympy_evaluator = new SympyEvaluator();

        this.sympy_evaluator.onError((error) => {
            // limit error message to 4 lines,
            // need to check the developer console to see the full message.
            const maxLines = 4;
            const errorLines = error.split('\n');
            const truncatedError = errorLines.slice(0, maxLines).join('\n') + (errorLines.length > maxLines ? '\n...' : '');
            new Notice("Error\n" + truncatedError);
        });

        if(!this.manifest.dir) {
            new Notice("Obsimat could not determine its plugin directory, aborting load.");
            return;
        }
        
        const sympy_client_spawner = this.settings.dev_mode ? new SourceCodeSpawner() : new ExecutableSpawner();

        this.sympy_evaluator.initialize(this.app.vault, this.manifest.dir, sympy_client_spawner);

        this.registerMarkdownCodeBlockProcessor("obsimat", this.renderObsimatCodeBlock.bind(this));

        // Add commands

        this.addObsimatCommands(new Map([
            [ new EvaluateCommand("eval"), 'Evaluate LaTeX Expression (Sympy)' ],
            [ new EvaluateCommand("expand"), 'Expand LaTeX Expression (Sympy)' ],
            [ new EvaluateCommand("factor"), 'Factor LaTeX Expression (Sympy)' ],
            [ new EvaluateCommand("apart"), 'Partial Fraction Decomposition On LaTeX Expression (Sympy)' ],
            [ new SolveCommand(), 'Solve LaTeX Expression (Sympy)' ],
            [ new SympyConvertCommand(), 'Convert LaTeX Expression To Sympy' ],
        ]));
    }


    addObsimatCommands(commands: Map<IObsimatCommand, string>) {
        commands.forEach((description, command) => {
          this.addCommand({
            id: command.id,
            name: description,
            editorCallback: command.functioncallback.bind(command, this.app, this.sympy_evaluator)
            });
        });
    }

    onunload() {
        this.sympy_evaluator.shutdown();
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }

    private async renderObsimatCodeBlock(source: string, el: HTMLElement, ctx: MarkdownPostProcessorContext): Promise<void> {
        // Add the standard code block background div,
        // to ensure a consistent look with other code blocks.
        const div = el.createDiv("HyperMD-codeblock HyperMD-codeblock-bg");
        div.style.cssText = "overflow: auto;";
        // same goes with the code block flair
        const flair = div.createSpan("code-block-flair obsimat-block-flair");
        flair.innerText = "Obsimat";
        div.appendChild(flair);

        el.appendChild(div);

        // retreive to be rendered latex from python.
        await this.sympy_evaluator.send("symbolsets", { environment: ObsimatEnvironment.fromCodeBlock(source, {}) });
        const response = await this.sympy_evaluator.receive();

        // render the latex.
        div.appendChild(renderMath(response.result, true));
        finishRenderMath();
    }

    private sympy_evaluator: SympyEvaluator;
}