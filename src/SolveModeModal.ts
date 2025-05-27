import { App, finishRenderMath, Modal, Notice, renderMath, Setting } from "obsidian";

type ObsimatSymbol = { sympy_symbol: string, latex_symbol: string };
type SolveConfig = { domain: string, symbols: ObsimatSymbol[] };

// The SymbolSelectorModal provides a modal dialog to select a single symbol from a list of symbols.
// Once opened, the getSelectedSymbolAsync method can be awaited to get the selected symbol.
export class SolveModeModal extends Modal {
    constructor(symbols: ObsimatSymbol[],
        protected equation_count: number,
        protected domain: string,
        app: App)
    {
        super(app);

        // setup model data

        for(const symbol of symbols) {
            this.symbol_selection.set(symbol, false);
        }

        this.solve_config_promise = new Promise((resolve, _reject) => {
            this.solve_config_resolve = resolve;
        });

        // setup view

        this.setTitle("Solve equations");
        
        new Setting(this.contentEl)
            .setName("Solution domain")
            .addText(text => {
                text.setValue(this.domain);
                text.onChange((value) => {
                    this.domain = value;
        });});

        // create list of selectable symbols.
        const symbols_div = this.contentEl.createDiv("prompt-results");
        this.contentEl.appendChild(symbols_div);
        
        for(const symbol of symbols) {
            const symbol_entry = symbols_div.createDiv("suggestion-item");
            symbols_div.appendChild(symbol_entry);

            // render latex symbols.
            symbol_entry.appendChild(renderMath(symbol.latex_symbol, true));
            
            symbol_entry.onclick = () => {
                this.symbol_selection.set(symbol, !this.symbol_selection.get(symbol));
                symbol_entry.toggleClass("is-selected", this.symbol_selection.get(symbol) ?? false);
            };
        }
        
        finishRenderMath();

        // add solve button.
        new Setting(this.contentEl)
            .addButton((btn) => {
                btn
                    .setButtonText("Solve")
                    .setCta()
                    .onClick(() => {
                        const selected_symbols = this.getSelectedSymbols();

                        if(selected_symbols.length !== this.equation_count) {
                            new Notice(`Please select ${this.equation_count} symbols.`);
                            return;
                        }

                        this.close();
                        this.solve_config_resolve({ domain: this.domain, symbols: selected_symbols });
                    });
            });
    }

    // returns a promise that resolves to the user selected solve configuration.
    public async getSolveConfig(): Promise<SolveConfig> { return this.solve_config_promise; }

    protected getSelectedSymbols(): ObsimatSymbol[] {
        return [...this.symbol_selection].filter(([_, selected]) => selected).map(([symbol, _]) => symbol);
    }

    private symbol_selection: Map<ObsimatSymbol, boolean> = new Map();

    private solve_config_promise: Promise<SolveConfig>;
    private solve_config_resolve: (value: SolveConfig | PromiseLike<SolveConfig>) => void;
}