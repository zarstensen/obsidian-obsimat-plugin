import { WebSocket, WebSocketServer } from 'ws';
import getPort from 'get-port';
import { ChildProcessWithoutNullStreams } from 'child_process';
import { SympyClientSpawner } from './SympyClientSpawner';
import { assert } from 'console';

interface ServerMessage {
    type: string;
    uid: string;
    payload: Record<string, unknown>;
}

interface ClientMessage {
    status: string;
    uid: string;
    result: Record<string, unknown>;
}

interface ClientErrorMessage {
    status: "error";
    uid: string;
    result: { message: string };
}

interface MessagePromiseEntry {
    resolve: (value: ClientMessage | PromiseLike<ClientMessage>) => void;
    reject: (reason?: any) => void;
}

// The SympyServer class manages a connection as well as message encoding and handling, with an SympyClient script instance.
// Also manages the python process itself.
export class SympyServer {
    // Start the SympyClient python process, and establish an connection to it.
    // vault_dir: the directory of the vault, which thsi plugin is installed in.
    // python_exec: the python executable to use to start the SympyClient process.
    public async initializeAsync(sympy_client_spawner: SympyClientSpawner): Promise<void> {
        // Start by setting up the web socket server, so we can get a port to give to the python program.
        const server_port = await getPort();

        this.ws_python_server = new WebSocketServer({ 
            port: server_port
        });

        // now start the python process
        this.python_process = await sympy_client_spawner.spawnClient(server_port);
        
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

    public async shutdown(): Promise<void> {
        const result = await this.send("exit", {});

        assert(result.status === "exit");

        this.ws_python.close();
        this.ws_python_server.close();
    }

    // Assign an error callback handler.
    // This callback is called any time an error message is received from the SympyClient process.
    public onError(callback: (error: string) => void): void {
        this.error_callback = callback;
    }

    // Send a message to the SympyClient process.
    public async send(type: string, data: Record<string, unknown>): Promise<ClientMessage> {
        const server_message: ServerMessage = {
            type: type,
            uid: crypto.randomUUID(),
            payload: data,
        };
        
        
        const result_promise =  new Promise<ClientMessage>((resolve, reject) => {
            this.message_promises[server_message.uid] = {
                resolve: resolve,
                reject: reject,
            };
        });

        this.ws_python.send(JSON.stringify(server_message));
        
        return await result_promise;
    }

    // Receive a result from the SympyClient process.
    // Returns a promise that resolves to the result object, parsed from the received json payload.
    public async receive(): Promise<void> {
        return new Promise((resolve, _reject) => {
            this.ws_python.once('message', (result_buffer) => {
                const result: ClientMessage = JSON.parse(result_buffer.toString());
                
                // first retreive the message promise to resolve (if present).

                let message_promise: MessagePromiseEntry | null = null;
                
                if (this.message_promises[result.uid] !== undefined) {
                    message_promise = this.message_promises[result.uid];
                    delete this.message_promises[result.uid];
                }
                
                // first some special cases.

                if (result.status === "error") {
                    
                    const err = result as ClientErrorMessage;

                    if(this.error_callback) {
                        this.error_callback(err.result.message);
                    }
                    
                    message_promise?.reject(err.result.message);
                    
                    resolve();
                } else {
                    message_promise?.resolve(result);
                    resolve();
                }
            });
        });
    }

    private python_process: ChildProcessWithoutNullStreams;
    private ws_python: WebSocket;
    private ws_python_server: WebSocketServer;
    private error_callback: (error: string) => void;

    private message_promises: Record<string, MessagePromiseEntry> = { };

    private resolveConnection(resolve: (value: WebSocket) => void, reject: (reason: string) => void) {
        this.ws_python_server.once('connection', (ws) => {
            resolve(ws);
        });
    }
}