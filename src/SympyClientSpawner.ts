import { ChildProcessWithoutNullStreams, spawn } from "child_process";
import { join } from "path";


// Interface for spawning a sympy client process.
export interface SympyClientSpawner {
    spawnClient(plugin_dir: string, port: number): ChildProcessWithoutNullStreams
}

// Spawns a sympy client process with python source files in the given virtual environment, with the given python executable.
export class SourceCodeSpawner implements SympyClientSpawner{
    constructor(protected python_exe="python", protected venv=".venv") { }

    public spawnClient(plugin_dir: string, port: number): ChildProcessWithoutNullStreams {
        
        return spawn(join(plugin_dir, this.venv, "scripts", this.python_exe), [join(plugin_dir, "sympy-client/SympyClient.py"), port.toString()]);
    }   
}

// Spawns a sympy client with a pyinstalled executable.
export class ExecutableSpawner implements SympyClientSpawner{
    private static readonly EXECUTABLE_NAME = "SympyClient";

    constructor() {}

    public spawnClient(plugin_dir: string, port: number): ChildProcessWithoutNullStreams {
        return spawn(join(plugin_dir, ExecutableSpawner.EXECUTABLE_NAME), [port.toString()]);
    }   
}
