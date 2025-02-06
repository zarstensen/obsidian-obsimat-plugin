import { WebSocket, WebSocketServer } from 'ws';
import getPort from 'get-port';
import { join } from 'path';
import { ChildProcessWithoutNullStreams, spawn } from 'child_process';

export class PythonEvalServer {

    constructor() {}

    public async initialize(vault_dir: string, python_exec = "python"): Promise<void> {
        // Start by setting up the web socket server, so we can get a port to give to the python program.
        const server_port = await getPort();

        this.ws_python_server = new WebSocketServer({ 
            port: server_port
        });

        // now start the python process
        this.python_process = spawn(python_exec, [join(vault_dir, '.obsidian/plugins/obsimat-plugin/src/sympy_evaluator.py'), server_port.toString()]);


        this.python_process.stdout.on('data', (data) => {
            console.log(`stdout: ${data}`);
        });

        this.python_process.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });

        this.python_process.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
        });

        // wait for the process to establish an connection
        this.ws_python = await new Promise(this.resolveConnection.bind(this));
    }

    public onError(callback: (error: string) => void): void {
        this.error_callback = callback;
    }

    public send(mode: string, data: string): void {
        this.ws_python.send(mode + "|" + data);
    }

    public async receive(): Promise<string> {
        return new Promise((resolve, reject) => {
            this.ws_python.once('message', (result_buffer) => {
                const result = result_buffer.toString();
                const separator_index = result.indexOf("|");
                
                const status = result.substring(0, separator_index);
                const payload = result.substring(separator_index + 1);

                if (status === "error") {
                    
                    if(this.error_callback) {
                        this.error_callback(payload);
                    }

                    reject(payload);
                } else {
                    resolve(payload);
                }
            });
        });
    }

    private python_process: ChildProcessWithoutNullStreams
    private ws_python: WebSocket;
    private ws_python_server: WebSocketServer;
    private error_callback: (error: string) => void;

    private resolveConnection(resolve: (value: WebSocket) => void, reject: (reason: string) => void) {
        this.ws_python_server.once('connection', (ws) => {
            resolve(ws);
        });
    }
}