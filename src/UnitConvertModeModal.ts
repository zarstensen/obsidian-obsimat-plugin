import { App, Modal, Setting } from "obsidian";

// The UnitConvertModeModal provides a modal dialog to specify a list of units which should be converted to.
export class UnitConvertModeModal extends Modal {
    constructor(app: App)
    {
        super(app);

        this.target_units_promise = new Promise((resolve, _reject) => {
            this.target_units_resolve = resolve;
        });

        
        this.setTitle("Convert units");
        
        // setup units input
        new Setting(this.contentEl)
            .setName("Target units")
            .addText(text => {
                text.onChange((value) => {
                    this.target_units = value.split(' ').filter(unit => unit.trim() !== '');
        });});

        // add convert button.
        new Setting(this.contentEl)
            .addButton((btn) => {
                btn
                    .setButtonText("Convert")
                    .setCta()
                    .onClick(() => {
                        this.close();
                        this.target_units_resolve(this.target_units);
                    });
            });
    }

    public getTargetUnits(): Promise<string[]> {
        return this.target_units_promise;
    }

    private target_units: string[] = [];

    private target_units_promise: Promise<string[]>;
    private target_units_resolve: (value: string[] | PromiseLike<string[]>) => void;
}