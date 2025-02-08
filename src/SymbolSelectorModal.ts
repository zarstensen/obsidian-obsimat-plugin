import { App, FuzzySuggestModal } from "obsidian";

export class SymbolSelectorModal extends FuzzySuggestModal<string> {
    private resolvePromise: (value: string | PromiseLike<string>) => void;
    private resultPromise: Promise<string>;

    constructor(public symbols: string[], app: App) {
        super(app);
        this.setPlaceholder("Choose symbol to solve for");
        this.resultPromise = new Promise<string>((resolve) => {
            this.resolvePromise = resolve;
        });
    }

    onChooseItem(item: string, _: MouseEvent | KeyboardEvent): void {
        console.log(item);
        this.resolvePromise(item);
        this.close();
    }

    getItemText(item: string): string {
        return item;
    }

    getItems(): string[] {
        return this.symbols;
    }

    getResultAsync(): Promise<string> {
        return this.resultPromise;
    }
}