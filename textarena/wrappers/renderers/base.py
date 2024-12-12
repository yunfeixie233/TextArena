from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from typing import Dict, Optional, Set, Any
import uvicorn
import threading
from pathlib import Path
import time
from abc import ABC, abstractmethod

class BaseRenderer(ABC):
    """Base class for all game renderers"""
    
    def __init__(self, env: Any, player_names: Optional[Dict[int, str]] = None, port: int = 8000):
        self.env = env
        self.player_names = player_names or {i: f"Player {i}" for i in range(env.state.num_players)}
        self.port = port
        self.active_connections: Set[WebSocket] = set()
        
        # Setup static files directory
        self.static_dir = Path(__file__).parent.parent.parent / "static"
        self.static_dir.mkdir(exist_ok=True)
        
        # Initialize FastAPI app
        self.app = self._create_app()
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        time.sleep(1)  # Wait for server to start

    def _create_app(self) -> FastAPI:
        app = FastAPI()
        app.mount("/static", StaticFiles(directory=str(self.static_dir)), name="static")

        @app.get("/")
        async def index():
            return HTMLResponse(self._get_html())

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.add(websocket)
            try:
                await self.broadcast_state()
                while True:
                    data = await websocket.receive_text()
                    await websocket.send_json({"status": "ok"})
            except:
                pass
            finally:
                self.active_connections.remove(websocket)

        return app

    def _run_server(self):
        """Run the FastAPI server"""
        config = uvicorn.Config(
            self.app,
            host="127.0.0.1",
            port=self.port,
            log_level="error"
        )
        server = uvicorn.Server(config)
        server.run()

    @abstractmethod
    def get_state(self) -> dict:
        """Get the current game state"""
        pass

    async def broadcast_state(self):
        """Broadcast the current state to all connected clients"""
        if not self.active_connections:
            return
            
        try:
            state = self.get_state()
            state["player_names"] = self.player_names
            await asyncio.gather(*[
                conn.send_json(state) 
                for conn in list(self.active_connections)
            ])
        except Exception as e:
            print(f"Error broadcasting state: {e}")

    def draw(self):
        """Update the game display"""
        if self.active_connections:
            asyncio.run(self.broadcast_state())

    def _get_html(self) -> str:
        """Get the HTML template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Chess Game</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.21.2/babel.min.js"></script>
            <link rel="stylesheet" href="/static/chess/style.css">
        </head>
        <body>
            <div id="root"></div>
            <script type="text/babel" src="/static/chess/app.js"></script>
        </body>
        </html>
        """