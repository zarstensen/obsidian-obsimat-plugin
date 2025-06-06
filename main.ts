import { FileSystemAdapter, finishRenderMath, MarkdownPostProcessorContext, MarkdownView, Notice, Plugin, renderMath } from 'obsidian';
import { SympyEvaluator } from 'src/SympyEvaluator';
import { LmatEnvironment } from 'src/LmatEnvironment';
import { ExecutableSpawner, SourceCodeSpawner } from 'src/SympyClientSpawner';
import { LatexMathSettingsTab } from 'src/LatexMathSettingsTab';
import { ILatexMathCommand } from 'src/commands/ILatexMathCommand';
import { EvaluateCommand } from 'src/commands/EvaluateCommand';
import { SolveCommand } from 'src/commands/SolveCommand';
import { SympyConvertCommand } from 'src/commands/SympyConvertCommand';
import { UnitConvertCommand } from 'src/commands/UnitConvertCommand';
import { SympyClientExtractor } from 'src/SympyClientExtractor';
import path from 'path';

interface LatexMathPluginSettings {
    dev_mode: boolean;
}

const DEFAULT_SETTINGS: LatexMathPluginSettings = {
    dev_mode: false
};

export default class LatexMathPlugin extends Plugin {
    settings: LatexMathPluginSettings;

    async onload() {
        console.log(`Loading Latex Math (${this.manifest.version})`);

        await this.loadSettings();
        this.addSettingTab(new LatexMathSettingsTab(this.app, this));

        
        if(!this.manifest.dir) {
            new Notice("Latex Math could not determine its plugin directory, aborting load.");
            return;
        }

        this.sympy_evaluator = new SympyEvaluator();

        this.sympy_evaluator.onError((error) => {
            // limit error message to 4 lines,
            // need to check the developer console to see the full message.
            const maxLines = 4;
            const errorLines = error.split('\n');
            const truncatedError = errorLines.slice(0, maxLines).join('\n') + (errorLines.length > maxLines ? '\n...' : '');
            new Notice("Error\n" + truncatedError);
        });
        
        this.registerMarkdownCodeBlockProcessor("lmat", this.renderLmatCodeBlock.bind(this));

        // Add commands

        this.addCommands(new Map([
            [ new EvaluateCommand("eval"), 'Evaluate LaTeX expression' ],
            [ new EvaluateCommand("evalf"), 'Evalf LaTeX expression' ],
            [ new EvaluateCommand("expand"), 'Expand LaTeX expression' ],
            [ new EvaluateCommand("factor"), 'Factor LaTeX expression' ],
            [ new EvaluateCommand("apart"), 'Partial fraction decompose LaTeX expression' ],
            [ new SolveCommand(), 'Solve LaTeX expression' ],
            [ new SympyConvertCommand(), 'Convert LaTeX expression to Sympy' ],
            [ new UnitConvertCommand(), 'Convert units in LaTeX expression' ]
        ]));

        // spawn sympy client
        this.spawn_sympy_client_promise = this.spawnSympyClient(this.manifest.dir);
        this.spawn_sympy_client_promise.catch((err) => {
            new Notice(`Latex Math could not start the Sympy client, aborting load.\n${err.message}`);
            throw err;
        });
    }

    // sets up the given map of commands as obsidian commands.
    // the provided values for each command will be set as the command description.
    addCommands(commands: Map<ILatexMathCommand, string>) {
        commands.forEach((description, cmd) => {
          this.addCommand({
            id: cmd.id,
            name: description,
            editorCallback: async (e, v) => { 
                await this.spawn_sympy_client_promise;
                cmd.functionCallback(this.sympy_evaluator, this.app, e, v as MarkdownView, {});
            }
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

    private async renderLmatCodeBlock(source: string, el: HTMLElement, ctx: MarkdownPostProcessorContext): Promise<void> {
        await this.spawn_sympy_client_promise;
        // Add the standard code block background div,
        // to ensure a consistent look with other code blocks.
        const div = el.createDiv("HyperMD-codeblock HyperMD-codeblock-bg lmat-block-container-flair");
        // same goes with the code block flair
        const flair = div.createSpan("code-block-flair lmat-block-flair");
        flair.innerText = "Latex Math";
        div.appendChild(flair);

        el.appendChild(div);

        // retreive to be rendered latex from python.
        await this.sympy_evaluator.send("symbolsets", { environment: LmatEnvironment.fromCodeBlock(source, {}, {}) });
        const response = await this.sympy_evaluator.receive();

        // render the latex.
        div.appendChild(renderMath(response.result, true));
        finishRenderMath();
    }

    private async spawnSympyClient(plugin_dir: string) {
        if(!(this.app.vault.adapter instanceof FileSystemAdapter)) {
            throw new Error(`Expected FileSystemAdapter, got ${this.app.vault.adapter}`);
        }
        const file_system_adapter: FileSystemAdapter = this.app.vault.adapter;

        const full_plugin_dir = path.join(file_system_adapter.getBasePath(), plugin_dir);
        const asset_extractor = new SympyClientExtractor(full_plugin_dir);

        // spawn sympy client process.
        const sympy_client_spawner = this.settings.dev_mode ? new SourceCodeSpawner(full_plugin_dir) : new ExecutableSpawner(asset_extractor);

        await this.sympy_evaluator.initializeAsync(sympy_client_spawner);
    }

    private sympy_evaluator: SympyEvaluator;
    private spawn_sympy_client_promise: Promise<void>;
}