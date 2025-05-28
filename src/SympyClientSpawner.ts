import { ChildProcessWithoutNullStreams, spawn } from "child_process";
import { join } from "path";
import { SympyClientExtractor } from "./SympyClientExtractor";

// Interface for spawning a sympy client process.
export interface SympyClientSpawner {
    spawnClient(port: number): Promise<ChildProcessWithoutNullStreams>
}

// Spawns a sympy client process with python source files in the given virtual environment, with the given python executable.
export class SourceCodeSpawner implements SympyClientSpawner{
    constructor(protected plugin_dir: string, protected python_exe="python", protected venv=".venv") { }

    public async spawnClient(port: number): Promise<ChildProcessWithoutNullStreams> {
        
        return spawn(join(this.plugin_dir, this.venv, "scripts", this.python_exe), [join(this.plugin_dir, "sympy-client/SympyClient.py"), port.toString()]);
    }   
}

// Spawns a sympy client with a pyinstalled executable.
export class ExecutableSpawner implements SympyClientSpawner{
    constructor(private asset_extractor: SympyClientExtractor) {}

    public async spawnClient(port: number): Promise<ChildProcessWithoutNullStreams> {
        if(!(await this.asset_extractor.hasRequiredClients())) {
            await this.asset_extractor.extractClients();
        }

        // check if .bin file exists, if not i guess we do stuff.
        return spawn(this.asset_extractor.getClientPath(), [port.toString()]);
    }   
}
