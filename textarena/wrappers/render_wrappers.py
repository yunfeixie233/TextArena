from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from typing import Dict, Optional, Set, Any
import uvicorn
import threading
from pathlib import Path
from abc import ABC, abstractmethod


import time
import webbrowser
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from typing import Dict, Optional, Set, Any
import uvicorn
import threading
from pathlib import Path
from abc import ABC, abstractmethod

class BaseBrowserRenderer(ABC):
    """Base class for browser-based game renderers."""
    
    def __init__(self, env, player_names: Optional[Dict[int, str]] = None):
        self.env = env
        self.player_names = player_names or {0: "Player 0", 1: "Player 1"}
        self.active_connections: Set[WebSocket] = set()
        self.chat_history = []  # Initialize chat history
        
        # Ensure static directory exists
        self.static_dir = Path(__file__).parent / "static"
        self.static_dir.mkdir(exist_ok=True)
        
        # Initialize FastAPI app
        self.app = self._create_app()
        self.server = None

    def add_chat_message(self, player_id: int, message: str):
        """Add a chat message to the history and broadcast update."""
        print(f"Adding chat message from player {player_id}: {message}")
        self.chat_history.append({
            "player_id": player_id,
            "message": message,
            "timestamp": time.time()
        })
        
        # Broadcast the update
        async def _broadcast():
            await self.broadcast_state()
            
        if self.active_connections:
            asyncio.run(_broadcast())
            print("Chat message broadcast complete")

    def _create_app(self):
        """Create the FastAPI application with basic routes."""
        app = FastAPI()
        
        app.mount("/static", StaticFiles(directory=str(self.static_dir)), name="static")
        
        @app.get("/")
        async def get_index():
            return HTMLResponse(self._get_index_html())
            
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.add(websocket)
            try:
                await self.broadcast_state()
                while True:
                    try:
                        await websocket.receive_text()
                        await websocket.send_text('{"status": "ok"}')
                    except:
                        break
            finally:
                self.active_connections.remove(websocket)

        return app

    async def broadcast_state(self):
        """Broadcast current game state to all connected clients."""
        if not self.active_connections:
            return
            
        state = self.get_state()
        message = json.dumps(state)
        
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                dead_connections.add(connection)
                
        self.active_connections -= dead_connections

    def draw(self):
        """Update the display with current game state."""
        async def _broadcast():
            await self.broadcast_state()
            
        if self.active_connections:
            asyncio.run(_broadcast())

    def start_server(self, port: int = 8000):
        """Start the FastAPI server."""
        config = uvicorn.Config(
            self.app,
            host="127.0.0.1",
            port=port,
            log_level="error"
        )
        server = uvicorn.Server(config)
        server.run()

    @abstractmethod
    def get_state(self) -> dict:
        """Get the current game state as a dictionary for sending to the client."""
        pass

    @abstractmethod
    def _get_index_html(self) -> str:
        """Get the index.html content. Must be implemented by each game renderer."""
        pass


class BrowserRenderWrapper:
    """Generic wrapper for browser-based rendering."""
    
    def __init__(
        self,
        env: Any,
        player_names: Optional[Dict[int, str]] = None,
        port: int = 8000
    ):
        self.env = env
        self.port = port
        
        # Check if environment has a browser renderer class
        if not hasattr(self.env, 'offline_renderer'):
            raise AttributeError(
                "Environment must specify a 'browser_renderer' attribute "
                "that implements BaseBrowserRenderer"
            )
        
        # Initialize environment
        self.env.reset()
        
        # Create renderer instance
        self.game_render = self.env.offline_renderer(env, player_names)
        
        # Start server thread
        self.server_thread = threading.Thread(
            target=self.game_render.start_server,
            args=(port,),
            daemon=True
        )
        self.server_thread.start()

        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser window
        webbrowser.open(f"http://localhost:{port}")
        print(f"Game server started at http://localhost:{port}")
        
        # Initial
        
        # Initial state broadcast
        self.game_render.draw()
        
    def step(self, action: str):
        """Execute a step and update display."""
        result = self.env.step(action)
        self.game_render.draw()
        return result
        
    def reset(self, seed: Optional[int] = None):
        """Reset the environment and update display."""
        result = self.env.reset(seed)
        self.game_render.draw()
        return result
        
    def close(self):
        """Clean up resources."""
        if hasattr(self.game_render, 'server'):
            self.game_render.server.should_exit = True
            
    def __getattr__(self, name):
        """Delegate unknown attributes to wrapped env."""
        return getattr(self.env, name)