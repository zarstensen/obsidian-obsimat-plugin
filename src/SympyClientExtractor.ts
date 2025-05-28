import * as fsSync from "fs";
import * as fs from "fs/promises";
import path from "path";
import { platform } from "os";
import SympyClientWin from "../bundle-bin/SympyClient-win.bin"
import SympyClientMacos from "../bundle-bin/SympyClient-macos.bin"
import SympyClientLinux from "../bundle-bin/SympyClient-linux.bin"


// AssetExtractor is responsible for extracting and detecting already extracted sympy clients bundled with this plugin.. 
export class SympyClientExtractor {

    constructor(private required_version: string, private asset_dir: string) { }

    // Check if the currently extracted clients match the required version specified in the constructor.
    // also returns false if no clients have ever been extracted.
    public async hasRequiredClients(): Promise<boolean> {
        
        const version_file = path.join(this.asset_dir, SympyClientExtractor.LATEST_VERSION_FILE);

        // first check if the file has even been created yet.
        if(!fsSync.existsSync(version_file)) {
            return false;
        }

        // now check if the version we currently have matches the required version.
        const fileContent = await fs.readFile(version_file, "utf-8");

        const latest_asset_version: { version: string } = JSON.parse(fileContent);

        return latest_asset_version.version == this.required_version && fsSync.existsSync(this.getClientPath());
    }

    // extract all the bundled clients.
    public async extractClients() {

        await fs.mkdir(path.join(this.asset_dir, "bin"), { recursive: true });

        await fs.writeFile(this.getPlatformClientPath("win"), SympyClientWin);
        await fs.writeFile(this.getPlatformClientPath("macos"), SympyClientMacos);
        await fs.writeFile(this.getPlatformClientPath("linux"), SympyClientLinux);

        // if successfull update latest_asset_version file
        await fs.writeFile(path.join(this.asset_dir, SympyClientExtractor.LATEST_VERSION_FILE), JSON.stringify({
            version: this.required_version
        }));
    }

    // retreive the location of the client relevant for the current platform.
    public getClientPath(): string {
        return this.getPlatformClientPath(this.getPlatformStr());
    }

    private static readonly LATEST_VERSION_FILE = "latest_asset_version.json";

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

    private getPlatformClientPath(platform: "win" | "macos" | "linux") {
        return path.join(this.asset_dir, `bin/SympyClient-${platform}.bin`);
    }
}