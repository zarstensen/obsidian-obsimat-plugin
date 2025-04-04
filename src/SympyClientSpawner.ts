import { ChildProcessWithoutNullStreams, spawn } from "child_process";
import { join } from "path";
import { platform } from "os";

const EXECUTABLE_NAME = platform() === "win32" ? "SympyClient.exe" : "SympyClient";

// Interface for spawning a sympy client process.
export interface SympyClientSpawner {
    spawnClient(plugin_dir: string, port: number): ChildProcessWithoutNullStreams
}

// Spawns a sympy client process with python source files in the given virtual environment, with the given python executable.
export class SourceCodeSpawner implements SympyClientSpawner{
    constructor(protected python_exe="python", protected venv=".venv") { }

    public spawnClient(plugin_dir: string, port: number): ChildProcessWithoutNullStreams {
        
        return spawn(join(plugin_dir, ".venv/scripts", this.python_exe), [join(plugin_dir, "sympy-client/src/SympyClient.py"), port.toString()]);
    }   
}

// Spawns a sympy client with a pyinstalled executable.
export class ExecutableSpawner implements SympyClientSpawner{
    constructor() {}

    public spawnClient(plugin_dir: string, port: number): ChildProcessWithoutNullStreams {
        return spawn(join(plugin_dir, EXECUTABLE_NAME), [port.toString()]);
    }   
}
