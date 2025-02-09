import { App, FuzzySuggestModal } from "obsidian";

//
// The SymbolSelectorModal provides a modal dialog to select a single symbol from a list of symbols.
// Once opened, the getSelectedSymbolAsync method can be awaited to get the selected symbol.
export class SymbolSelectorModal extends FuzzySuggestModal<string> {
    constructor(public symbols: string[], app: App) {
        super(app);

        this.setPlaceholder("Choose symbol to solve for");
        this.resultPromise = new Promise<string>((resolve) => {
            this.resolvePromise = resolve;
        });
    }

    onChooseItem(item: string, _: MouseEvent | KeyboardEvent): void {
        this.resolvePromise(item);
        this.close();
    }

    getItemText = (item: string) => item;

    getItems = () => this.symbols;
    
    getSelectedSymbolAsync = () => this.resultPromise;

    private resolvePromise: (value: string | PromiseLike<string>) => void;
    private resultPromise: Promise<string>;
}