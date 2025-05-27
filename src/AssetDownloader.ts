import * as fs from "fs";
import { requestUrl } from "obsidian";
import path from "path";
import AdmZip from "adm-zip";
import { platform } from "os";

// AssetDownloader is responsible for downloading and extracting assets specific versions of this plugin requires. 
export class AssetDownloader {

    constructor(private required_version: string) { }

    // Check if the currently downloaded assets at the given dir match the required version specified in the constructor.
    // also returns false if no assets have ever been downloaded.
    public async hasRequiredAssets(dir: string): Promise<boolean> {
        
        const version_file = path.join(dir, AssetDownloader.LATEST_VERSION_FILE);

        // first check if the file has even been created yet.
        if(!fs.existsSync(version_file)) {
            return false;
        }

        // now check if the version we currently have matches the required version.
        const fileContent = fs.readFileSync(version_file, "utf-8");

        const latest_asset_version: { version: string } = JSON.parse(fileContent);

        return latest_asset_version.version == this.required_version;
    }

    // download the required assets to the given destination directory.
    public async downloadAssets(dest_dir: string) {

        // construct the download url

        let platform_str: string | undefined = undefined;

        switch(platform()) {
            case "win32":
                platform_str = "win";
                break;
            case "darwin":
                platform_str = "macos";
                break;
            case "linux":
                platform_str = "linux";
                break;
            default:
                throw new Error(`Unsupported platform "${platform()}"`);
        }
        
        const download_url = AssetDownloader.ASSET_DOWNLOAD_URL
                                            .replaceAll("${VERSION}", this.required_version)
                                            .replaceAll("${PLATFORM}", platform_str);

        // download the asset file
        const response = await requestUrl(download_url);
        const buffer = Buffer.from(response.arrayBuffer);

        // try to extract the files

        const zip_contents = new AdmZip(buffer);
        const zip_entries = zip_contents.getEntries();

        for(const entry of zip_entries) {
            // ignore files automatically downloaded by obsidian.
            if(entry.entryName === "main.js" || entry.entryName === "styles.css" || entry.entryName === "manifest.json") {
                continue;
            }
            
            const res = await new Promise<Buffer>(resolve => { entry.getDataAsync((data, err) => { resolve(data); }); });

            const file_path = path.join(dest_dir, entry.entryName);

            fs.mkdirSync(path.dirname(file_path), { recursive: true });
            fs.writeFileSync(file_path, res);
        }

        // if successfull update latest_asset_version file
        fs.writeFileSync(path.join(dest_dir, AssetDownloader.LATEST_VERSION_FILE), JSON.stringify({
            version: this.required_version
        }));
    }

    private static readonly LATEST_VERSION_FILE = "latest_asset_version.json";
    private static readonly ASSET_DOWNLOAD_URL = "https://github.com/zarstensen/obsidian-latex-math/releases/download/${VERSION}/obsidian-latex-math-${VERSION}-${PLATFORM}.zip";
}