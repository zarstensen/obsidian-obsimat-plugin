import LatexMathPlugin from 'main';
import { App, PluginSettingTab, Setting} from 'obsidian';

// Settings tab for Latex Math plugin.
export class LatexMathSettingsTab extends PluginSettingTab {
    plugin: LatexMathPlugin;

    constructor(app: App, plugin: LatexMathPlugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display(): void {
        this.containerEl.empty();

        new Setting(this.containerEl)
            .setName('Developer mode')
            .setDesc('Use python source files and venv instead of bundled executable.\nReload Obsidian to apply.')
            .addToggle((toggle) => {
                toggle.setValue(this.plugin.settings.dev_mode)
                    .onChange(async (value) => {
                        this.plugin.settings.dev_mode = value;
                        await this.plugin.saveSettings();
                    });
            });
    }

}
