import * as fs from "fs/promises";
import path from "path";
import { platform } from "os";
import SympyClientWin from "../bundle-bin/SympyClient-win/SympyClient-win.bin";
import SympyClientMacos from "../bundle-bin/SympyClient-macos/SympyClient-macos.bin";
import SympyClientLinux from "../bundle-bin/SympyClient-linux/SympyClient-linux.bin";


// AssetExtractor is responsible for extracting and detecting already extracted sympy clients bundled with this plugin.. 
export class SympyClientExtractor {

    constructor(private asset_dir: string) { }

    // Check if the currently extracted clients match the required version specified in the constructor.
    // also returns false if no clients have ever been extracted.
    public async hasBundledClients(): Promise<boolean> {
        return SympyClientWin === "" && SympyClientMacos === "" && SympyClientLinux === "";
    }

    // extract all the bundled clients.
    public async extractClients() {
        await fs.mkdir(path.join(this.asset_dir, "bin"), { recursive: true });

        await this.extractClient(SympyClientWin, this.getPlatformClientPath("win"));
        await this.extractClient(SympyClientMacos, this.getPlatformClientPath("macos"));
        await this.extractClient(SympyClientLinux, this.getPlatformClientPath("linux"));
    }

    // retreive the location of the client relevant for the current platform.
    public getClientPath(): string {
        return this.getPlatformClientPath(this.getPlatformStr());
    }

    private getPlatformStr(): "win" | "macos" | "linux" {
            switch(platform()) {
                case "win32":
                    return "win";
                case "darwin":
                    return "macos";
                case "linux":
                    return "linux";
                default:
                    throw new Error(`Unsupported platform "${platform()}"`);
            }
    }

    private async extractClient(client_base64: string, extract_path: string) {
        const client_buffer = Buffer.from(client_base64, "base64");

        await fs.writeFile(extract_path, client_buffer);
        const main_path = path.join(this.asset_dir, SympyClientExtractor.MAIN_JS_FILE);

        let main_content = await fs.readFile(main_path, "utf-8");
        main_content = main_content.replace(client_base64, "");
        await fs.writeFile(main_path, main_content, "utf-8");
    }

    private getPlatformClientPath(platform: "win" | "macos" | "linux") {
        return path.join(this.asset_dir, `bin/SympyClient-${platform}.bin`);
    }

    private static readonly MAIN_JS_FILE = "main.js";
}