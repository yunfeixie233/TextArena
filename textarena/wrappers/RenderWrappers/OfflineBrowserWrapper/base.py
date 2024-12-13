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
import shutil

class BaseRenderer(ABC):
    def __init__(self, env: Any, player_names: Optional[Dict[int, str]] = None, port: int = 8000, host: str = "127.0.0.1"):
        self.env = env
        self.player_names = player_names or {i: f"Player {i}" for i in range(env.state.num_players)}
        self.port = port
        self.host = host
        self.active_connections: Set[WebSocket] = set()
        self.chat_history = []
        self.end_game_state = None
        
        # Set up directories
        self.base_dir = Path(__file__).parent
        self.template_dir = self.base_dir / "templates"
        
        # Create a temporary static directory for serving files
        self.static_dir = Path(__file__).parent.parent.parent.parent / "static" / "temp"
        self.static_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the app and server
        self._setup_static_files()
        self.app = self._create_app()
        
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        time.sleep(1)

    def _create_app(self) -> FastAPI:
        """Create and configure the FastAPI app"""
        app = FastAPI()
        app.mount("/static", StaticFiles(directory=str(self.static_dir)), name="static")

        @app.get("/")
        async def index():
            with open(self.template_dir / "index.html") as f:
                template = f.read()
            return HTMLResponse(template)

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.add(websocket)
            try:
                await self.broadcast_state()
                while True:
                    await websocket.receive_text()
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
            host=self.host,
            port=self.port,
            log_level="error"
        )
        server = uvicorn.Server(config)
        server.run()

    def _setup_static_files(self):
        """Set up static files for the UI"""
        # Clear existing files in temp directory
        if self.static_dir.exists():
            for file in self.static_dir.glob("*"):
                if file.is_file():
                    file.unlink()
        else:
            self.static_dir.mkdir(parents=True, exist_ok=True)
        
        # Read base files
        base_static = self.base_dir / "static"
        if base_static.exists():
            base_js = (base_static / "app.js").read_text() if (base_static / "app.js").exists() else ""
            base_css = (base_static / "style.css").read_text() if (base_static / "style.css").exists() else ""
        else:
            base_js = ""
            base_css = ""
        
        # Get custom content
        custom_js = self.get_custom_js()
        custom_css = self.get_custom_css()
        
        # Combine and write files
        with open(self.static_dir / "app.js", "w") as f:
            f.write(base_js)
            if custom_js:
                f.write("\n\n// Game-specific components\n")
                f.write(custom_js)
        
        with open(self.static_dir / "style.css", "w") as f:
            f.write(base_css)
            if custom_css:
                f.write("\n\n/* Game-specific styles */\n")
                f.write(custom_css)
        
        print(f"\nStatic files written to: {self.static_dir}")
        print(f"Checking files:")
        print(f"app.js exists: {(self.static_dir / 'app.js').exists()}")
        print(f"style.css exists: {(self.static_dir / 'style.css').exists()}")

    def set_end_game_state(self, rewards: Dict[int, float], info: Dict[str, Any]):
        """Set the end game state"""
        # Determine winner from rewards
        winner_text = ""
        if rewards:
            max_reward = max(rewards.values())
            winners = [pid for pid, r in rewards.items() if r == max_reward]
            if len(winners) > 1:
                winner_text = "Game ended in a draw"
            else:
                winner = winners[0]
                winner_text = f"Winner: {self.player_names[winner]}"

        # Get reason from info
        reason = info.get('reason', 'Game Over')

        # add role mapping in message
        for pid, player_name in self.player_names.items():
            reason = reason.replace(f"Player {pid}", player_name)

 

        self.end_game_state = {
            "winner_text": winner_text,
            "reason": reason
        }
        self.draw()


    def draw(self):
        """Update the display"""
        if self.active_connections:
            asyncio.run(self.broadcast_state())

    async def broadcast_state(self):
        """Broadcast the current state to all connected clients"""
        if not self.active_connections:
            return
            
        try:
            state = self.get_state()
            state["player_names"] = self.player_names
            state["chat_history"] = self.chat_history
            state["end_game_state"] = self.end_game_state
            
            await asyncio.gather(*[
                conn.send_json(state) 
                for conn in list(self.active_connections)
            ])
        except Exception as e:
            print(f"Error broadcasting state: {e}")

    @abstractmethod
    def get_state(self) -> dict:
        """Get game-specific state"""
        pass

    def get_custom_css(self) -> str:
        """Get game-specific CSS"""
        return ""

    def get_custom_js(self) -> str:
        """Get game-specific JavaScript"""
        return ""