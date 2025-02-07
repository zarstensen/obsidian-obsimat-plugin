import { WebSocket, WebSocketServer } from 'ws';
import getPort from 'get-port';
import { join } from 'path';
import { ChildProcessWithoutNullStreams, spawn } from 'child_process';

// The PythonEvalServer class manages a connection as well as message encoding and handling, with an SympyEvaluator script instance.
// Also manages the python process itself.
export class SympyEvaluator {

    public initialize(vault_dir: string, python_exec = "python"): Promise<void> {
        this.initialized_promise = this.initializeAsync(vault_dir, python_exec);
        return this.initialized_promise
    }

    // Assign an error callback handler.
    // This callback is called any time an error message is received from the SympyEvaluator process.
    public onError(callback: (error: string) => void): void {
        this.error_callback = callback;
    }

    // Send a message to the SympyEvaluator process.
    public async send(mode: string, data: any): Promise<void> {
        await this.initialized_promise
        this.ws_python.send(mode + "|" + JSON.stringify(data));
    }

    // Receive a result from the SympyEvaluator process.
    // Returns a promise that resolves to the result object, parsed from the received json payload.
    public async receive(): Promise<any> {
        return new Promise((resolve, reject) => {
            this.ws_python.once('message', (result_buffer) => {
                const result = result_buffer.toString();
                const separator_index = result.indexOf("|");
                
                const status = result.substring(0, separator_index);
                const payload = JSON.parse(result.substring(separator_index + 1));

                if (status === "error") {
                    
                    if(this.error_callback) {
                        this.error_callback(payload.message);
                    }

                    reject(payload.message);
                } else {
                    resolve(payload);
                }
            });
        });
    }

    private initialized_promise: Promise<void>
    private python_process: ChildProcessWithoutNullStreams
    private ws_python: WebSocket;
    private ws_python_server: WebSocketServer;
    private error_callback: (error: string) => void;

    private resolveConnection(resolve: (value: WebSocket) => void, reject: (reason: string) => void) {
        this.ws_python_server.once('connection', (ws) => {
            resolve(ws);
        });
    }

    // Start the SympyEvaluator python process, and establish an connection to it.
    // vault_dir: the directory of the vault, which thsi plugin is installed in.
    // python_exec: the python executable to use to start the SympyEvaluator process.
    private async initializeAsync(vault_dir: string, python_exec = "python"): Promise<void> {
        // Start by setting up the web socket server, so we can get a port to give to the python program.
        const server_port = await getPort();

        this.ws_python_server = new WebSocketServer({ 
            port: server_port
        });

        // now start the python process
        this.python_process = spawn(python_exec, [join(vault_dir, '.obsidian/plugins/obsimat-plugin/src/evaluator/SympyEvaluator.py'), server_port.toString()]);

        // setup output to be logged in the developer console
        this.python_process.stdout.on('data', (data) => {
            console.log(`stdout: ${data}`);
        });

        this.python_process.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });

        this.python_process.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
            // TODO: do something here
        });

        // wait for the process to establish an connection
        this.ws_python = await new Promise(this.resolveConnection.bind(this));


    }
}