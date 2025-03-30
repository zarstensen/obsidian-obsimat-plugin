import { App, Editor, MarkdownView } from "obsidian";
import { SympyEvaluator } from "src/SympyEvaluator";
import { EvaluateCommand } from "./EvaluateCommand";
import { UnitConvertModeModal } from "src/UnitConvertModeModal";

export class UnitConvertCommand extends EvaluateCommand {
    constructor() {
        super('convert-units');
    }
    
    public override async functionCallback(evaluator: SympyEvaluator, app: App, editor: Editor, view: MarkdownView, message: Record<string, any> = {}): Promise<void> {
        const modal = new UnitConvertModeModal(app);
        modal.open();

        message.target_units = await modal.getTargetUnits();

        await super.functionCallback(evaluator, app, editor, view, message);
    }
}