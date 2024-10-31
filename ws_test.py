from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import sys
from ws_manager import WsConnectionManager, LogCapture

app = FastAPI()

# Instancia del manejador de WebSocket
ws_manager = WsConnectionManager()

# Instancia global de LogCapture
log_capture = LogCapture(ws_manager)

@app.get("/", response_class=HTMLResponse)
async def get():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Logs en tiempo real</title>
            <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
            <style>
                #logs {
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    height: 400px;
                    overflow-y: auto;
                    font-family: monospace;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    margin-top: 10px;
                }
                button {
                    margin: 10px 0;
                    padding: 8px 16px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }
                button:hover {
                    background-color: #45a049;
                }
                button:disabled {
                    background-color: #cccccc;
                    cursor: not-allowed;
                }
                .status {
                    margin-left: 10px;
                    font-size: 0.9em;
                }
                .status.connected {
                    color: #4CAF50;
                }
                .status.disconnected {
                    color: #f44336;
                }
            </style>
        </head>
        <body>
            <div x-data="{
                logs: [],
                isConnected: false,
                isExecuting: false,
                ws: null,
                
                init() {
                    this.connectWebSocket();
                },
                
                connectWebSocket() {
                    this.ws = new WebSocket('ws://localhost:8000/ws');
                    
                    this.ws.onopen = () => {
                        this.isConnected = true;
                    };
                    
                    this.ws.onmessage = (event) => {
                        this.logs.push(event.data);
                        this.$nextTick(() => {
                            const logsElement = this.$refs.logsContainer;
                            logsElement.scrollTop = logsElement.scrollHeight;
                        });
                    };
                    
                    this.ws.onclose = () => {
                        this.isConnected = false;
                        setTimeout(() => this.connectWebSocket(), 1000);
                    };
                    
                    this.ws.onerror = () => {
                        this.isConnected = false;
                        this.ws.close();
                    };
                },
                
                async ejecutarFuncion() {
                    if (this.isExecuting) return;
                    
                    this.isExecuting = true;
                    try {
                        const response = await fetch('/ejecutar');
                        const data = await response.text();
                        console.log('Función ejecutada:', data);
                    } catch (error) {
                        console.error('Error:', error);
                    } finally {
                        this.isExecuting = false;
                    }
                },
                
                clearLogs() {
                    this.logs = [];
                }
            }">
                <h1>Logs de la aplicación</h1>
                
                <div>
                    <button 
                        @click="ejecutarFuncion()" 
                        :disabled="!isConnected || isExecuting"
                        x-text="isExecuting ? 'Ejecutando...' : 'Ejecutar función'">
                    </button>
                    
                    <button 
                        @click="clearLogs()" 
                        :disabled="!isConnected || logs.length === 0">
                        Limpiar logs
                    </button>
                    
                    <span 
                        class="status"
                        :class="isConnected ? 'connected' : 'disconnected'"
                        x-text="isConnected ? '● Conectado' : '● Desconectado'">
                    </span>
                </div>
                
                <pre id="logs" x-ref="logsContainer">
                    <template x-for="(log, index) in logs" :key="index">
                        <span x-text="log"></span>
                    </template>
                </pre>
            </div>
        </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            try:
                # Mantener la conexión viva
                await asyncio.sleep(1)
            except WebSocketDisconnect:
                ws_manager.disconnect(websocket)
                break
    except Exception:
        ws_manager.disconnect(websocket)

@app.get("/ejecutar")
async def ejecutar_funcion():
    # Redirigir stdout a nuestra captura
    old_stdout = sys.stdout
    sys.stdout = log_capture
    
    try:
        # Aquí va tu función con prints
        print("Iniciando ejecución...")
        for i in range(3):
            print(f"Paso {i + 1}")
            await asyncio.sleep(1)
        print("Ejecución completada!")
        
        return "Función ejecutada"
    finally:
        # Asegurarse de restaurar stdout
        sys.stdout = old_stdout

# Restaurar stdout al cerrar la aplicación
@app.on_event("shutdown")
def shutdown_event():
    sys.stdout = sys.__stdout__
