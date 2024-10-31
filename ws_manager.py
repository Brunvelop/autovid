from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import sys
from io import StringIO

class WsConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._original_stdout = sys.stdout
        self._enabled = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        if not self._enabled:
            return
            
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)
            except Exception:
                self.disconnect(connection)

    def start_capture(self):
        """Inicia la captura de logs"""
        self._enabled = True
        sys.stdout = LogCapture(self)

    def stop_capture(self):
        """Detiene la captura de logs"""
        self._enabled = False
        sys.stdout = self._original_stdout

class LogCapture:
    def __init__(self, connection_manager):
        self.original_stdout = sys.stdout
        self.string_buffer = StringIO()
        self.connection_manager = connection_manager
    
    def write(self, text):
        self.original_stdout.write(text)
        self.string_buffer.write(text)
        if text.strip():  # Solo enviar si no está vacío
            asyncio.create_task(self.connection_manager.broadcast(text))
    
    def flush(self):
        self.original_stdout.flush()
