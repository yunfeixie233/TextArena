# game_state_render.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import chess
import json
import asyncio
from typing import Dict, Optional, Set, Any
import uvicorn
import webbrowser
import threading
import time
from contextlib import asynccontextmanager

class GameStateRender:
    """Browser-based render wrapper for the Chess environment."""
    def __init__(self, env, player_names: Optional[Dict[int, str]] = None):
        self.env = env
        self.player_names = player_names or {0: "White", 1: "Black"}
        self.active_connections: Set[WebSocket] = set()
        self.app = self._create_app()
        self.server = None
        self._setup_complete = threading.Event()
        
    def _create_app(self):
        app = FastAPI()
        
        @app.on_event("startup")
        async def startup_event():
            self._setup_complete.set()
            
        @app.get("/")
        async def get_index():
            return HTMLResponse(self._get_index_html())
            
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.add(websocket)
            try:
                # Send initial state
                await self.broadcast_state()
                
                while True:
                    # Keep connection alive
                    try:
                        data = await websocket.receive_text()
                        # Echo back to confirm connection
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
            
        board = self.env.board
        state = {
            "fen": board.fen(),
            "current_player": "White" if board.turn else "Black",
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_stalemate": board.is_stalemate(),
            "is_insufficient_material": board.is_insufficient_material(),
            "move_stack": [move.uci() for move in board.move_stack],
            "player_names": self.player_names
        }
        
        message = json.dumps(state)
        dead_connections = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                dead_connections.add(connection)
                
        # Clean up dead connections
        self.active_connections -= dead_connections
    

    def _create_app(self):
        app = FastAPI()
        
        @app.get("/")
        async def get_index():
            return HTMLResponse(self._get_index_html())
            
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.add(websocket)
            try:
                # Send initial state
                await self.broadcast_state()
                
                while True:
                    try:
                        data = await websocket.receive_text()
                        # Echo back to confirm connection
                        await websocket.send_text('{"status": "ok"}')
                    except:
                        break
            finally:
                self.active_connections.remove(websocket)
                
        return app


    def _get_index_html(self):
        """Return the index.html content with embedded React application."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Chess Game</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.21.2/babel.min.js"></script>
    
    <style>
        body { 
            background-color: #2B2B2B;
            color: #FFFFFF;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .game-container {
            display: flex;
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .board-container {
            flex: 0 0 600px;
        }
        .chess-board {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            width: 600px;
            height: 600px;
            border: 2px solid #404040;
        }
        .square {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
        }
        .square.light {
            background-color: #EEEED2;
        }
        .square.dark {
            background-color: #769656;
        }
        .piece {
            width: 80%;
            height: 80%;
        }
        .info-container {
            flex: 1;
            background: #363636;
            padding: 20px;
            border-radius: 8px;
        }
        .move-history {
            height: 300px;
            overflow-y: auto;
            background: #2B2B2B;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .status {
            font-size: 1.2em;
            margin-bottom: 15px;
            padding: 10px;
            background: #2B2B2B;
            border-radius: 4px;
        }
        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        .connection-status.connected {
            background: #4CAF50;
        }
        .connection-status.disconnected {
            background: #F44336;
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef } = React;

        // Chess piece SVG components
        const PieceSVGs = {
            'K': (color) => (
                <svg viewBox="0 0 45 45" className="piece">
                    <g fill={color} stroke="#000" strokeWidth="1.5" strokeLinejoin="round">
                        <path d="M 22.5,11.63 L 22.5,6 M 20,8 L 25,8"/>
                        <path d="M 22.5,25 C 22.5,25 27,17.5 25.5,14.5 C 25.5,14.5 24.5,12 22.5,12 C 20.5,12 19.5,14.5 19.5,14.5 C 18,17.5 22.5,25 22.5,25" strokeLinecap="butt"/>
                        <path d="M 11.5,37 C 17,40.5 27,40.5 32.5,37 L 32.5,30 C 32.5,30 41.5,25.5 38.5,19.5 C 34.5,13 25,16 22.5,23.5 L 22.5,27 L 22.5,23.5 C 19,16 9.5,13 6.5,19.5 C 3.5,25.5 11.5,29.5 11.5,29.5 L 11.5,37 z"/>
                        <path d="M 11.5,30 C 17,27 27,27 32.5,30"/>
                        <path d="M 11.5,33.5 C 17,30.5 27,30.5 32.5,33.5"/>
                        <path d="M 11.5,37 C 17,34 27,34 32.5,37"/>
                    </g>
                </svg>
            ),
            'Q': (color) => (
                <svg viewBox="0 0 45 45" className="piece">
                    <g fill={color} stroke="#000" strokeWidth="1.5" strokeLinejoin="round">
                        <path d="M 9,26 C 17.5,24.5 30,24.5 36,26 L 38.5,13.5 L 31,25 L 30.7,10.9 L 25.5,24.5 L 22.5,10 L 19.5,24.5 L 14.3,10.9 L 14,25 L 6.5,13.5 L 9,26 z"/>
                        <path d="M 9,26 C 9,28 10.5,28 11.5,30 C 12.5,31.5 12.5,31 12,33.5 C 10.5,34.5 10.5,36 10.5,36 C 9,37.5 11,38.5 11,38.5 C 17.5,39.5 27.5,39.5 34,38.5 C 34,38.5 35.5,37.5 34,36 C 34,36 34.5,34.5 33,33.5 C 32.5,31 32.5,31.5 33.5,30 C 34.5,28 36,28 36,26 C 27.5,24.5 17.5,24.5 9,26 z"/>
                        <path d="M 11,38.5 A 35,35 1 0 0 34,38.5"/>
                        <path d="M 11,29 A 35,35 1 0 1 34,29"/>
                        <path d="M 12.5,31.5 L 32.5,31.5"/>
                        <path d="M 11.5,34.5 L 33.5,34.5"/>
                        <path d="M 10.5,37.5 L 34.5,37.5"/>
                    </g>
                </svg>
            ),
            'R': (color) => (
                <svg viewBox="0 0 45 45" className="piece">
                    <g fill={color} stroke="#000" strokeWidth="1.5" strokeLinejoin="round">
                        <path d="M 9,39 L 36,39 L 36,36 L 9,36 L 9,39 z"/>
                        <path d="M 12,36 L 12,32 L 33,32 L 33,36 L 12,36 z"/>
                        <path d="M 11,14 L 11,9 L 15,9 L 15,11 L 20,11 L 20,9 L 25,9 L 25,11 L 30,11 L 30,9 L 34,9 L 34,14"/>
                        <path d="M 34,14 L 31,17 L 14,17 L 11,14"/>
                        <path d="M 31,17 L 31,29.5 L 14,29.5 L 14,17"/>
                        <path d="M 11,14 L 34,14"/>
                    </g>
                </svg>
            ),
            'B': (color) => (
                <svg viewBox="0 0 45 45" className="piece">
                    <g fill={color} stroke="#000" strokeWidth="1.5" strokeLinejoin="round">
                        <g fill="none" strokeLinecap="butt">
                            <path d="M 9,36 C 12.39,35.03 19.11,36.43 22.5,34 C 25.89,36.43 32.61,35.03 36,36 C 36,36 37.65,36.54 39,38 C 38.32,38.97 37.35,38.99 36,38.5 C 32.61,37.53 25.89,38.96 22.5,37.5 C 19.11,38.96 12.39,37.53 9,38.5 C 7.646,38.99 6.677,38.97 6,38 C 7.354,36.06 9,36 9,36 z"/>
                            <path d="M 15,32 C 17.5,34.5 27.5,34.5 30,32 C 30.5,30.5 30,30 30,30 C 30,27.5 27.5,26 27.5,26 C 33,24.5 33.5,14.5 22.5,10.5 C 11.5,14.5 12,24.5 17.5,26 C 17.5,26 15,27.5 15,30 C 15,30 14.5,30.5 15,32 z"/>
                            <path d="M 25 8 A 2.5 2.5 0 1 1  20,8 A 2.5 2.5 0 1 1  25 8 z"/>
                        </g>
                        <path d="M 17.5,26 L 27.5,26 M 15,30 L 30,30 M 22.5,15.5 L 22.5,20.5 M 20,18 L 25,18" fill="none" strokeLinejoin="miter"/>
                    </g>
                </svg>
            ),
            'N': (color) => (
                <svg viewBox="0 0 45 45" className="piece">
                    <g fill={color} stroke="#000" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M 22,10 C 32.5,11 38.5,18 38,39 L 15,39 C 15,30 25,32.5 23,18"/>
                        <path d="M 24,18 C 24.38,20.91 18.45,25.37 16,27 C 13,29 13.18,31.34 11,31 C 9.958,30.06 12.41,27.96 11,28 C 10,28 11.19,29.23 10,30 C 9,30 5.997,31 6,26 C 6,24 12,14 12,14 C 12,14 13.89,12.1 14,10.5 C 13.27,9.506 13.5,8.5 13.5,7.5 C 14.5,6.5 16.5,10 16.5,10 L 18.5,10 C 18.5,10 19.28,8.008 21,7 C 22,7 22,10 22,10"/>
                        <path d="M 9.5 25.5 A 0.5 0.5 0 1 1 8.5,25.5 A 0.5 0.5 0 1 1 9.5 25.5 z" fill="#000"/>
                        <path d="M 15 15.5 A 0.5 1.5 0 1 1  14,15.5 A 0.5 1.5 0 1 1  15 15.5 z" transform="matrix(0.866,0.5,-0.5,0.866,9.693,-5.173)" fill="#000"/>
                    </g>
                </svg>
            ),
            'P': (color) => (
                <svg viewBox="0 0 45 45" className="piece">
                    <path d="m 22.5,9 c -2.21,0 -4,1.79 -4,4 0,0.89 0.29,1.71 0.78,2.38 C 17.33,16.5 16,18.59 16,21 c 0,2.03 0.94,3.84 2.41,5.03 C 15.41,27.09 11,31.58 11,39.5 H 34 C 34,31.58 29.59,27.09 26.59,26.03 28.06,24.84 29,23.03 29,21 29,18.59 27.67,16.5 25.72,15.38 26.21,14.71 26.5,13.89 26.5,13 c 0,-2.21 -1.79,-4 -4,-4 z" style={{fill: color, stroke: '#000000', strokeWidth: '1.5', strokeLinecap: 'round'}}/>
                </svg>
            )
        };

        const ChessBoard = ({ fen }) => {
            const pieces = fen ? parseFEN(fen) : new Array(64).fill(null);
            
            const renderSquare = (i) => {
                const file = i % 8;
                const rank = Math.floor(i / 8);
                const isLight = (file + rank) % 2 === 0;
                const piece = pieces[i];
                
                return (
                    <div key={i} className={`square ${isLight ? 'light' : 'dark'}`}>
                        {piece && (
                            piece.color === 'w' 
                                ? PieceSVGs[piece.type]('#fff')
                                : PieceSVGs[piece.type]('#000')
                        )}
                    </div>
                );
            };
            
            return (
                <div className="chess-board">
                    {Array(64).fill().map((_, i) => renderSquare(i))}
                </div>
            );
        };

        function parseFEN(fen) {
            const pieces = new Array(64).fill(null);
            const [position] = fen.split(' ');
            let square = 0;
            
            for (const char of position) {
                if (char === '/') {
                    continue;
                } else if (/\d/.test(char)) {
                    square += parseInt(char);
                } else{
                    const color = char === char.toUpperCase() ? 'w' : 'b';
                    const type = char.toUpperCase();
                    pieces[square] = { type, color };
                    square++;
                }
            }
            return pieces;
        }

        function ChessGame() {
            const [gameState, setGameState] = useState(null);
            const [connected, setConnected] = useState(false);
            const wsRef = useRef(null);
            
            const connectWebSocket = () => {
                wsRef.current = new WebSocket(`ws://${window.location.host}/ws`);
                
                wsRef.current.onopen = () => {
                    setConnected(true);
                    console.log('WebSocket Connected');
                };
                
                wsRef.current.onmessage = (event) => {
                    try {
                        const state = JSON.parse(event.data);
                        if (state.fen) {
                            setGameState(state);
                        }
                    } catch (e) {
                        console.error('Error parsing message:', e);
                    }
                };
                
                wsRef.current.onclose = () => {
                    setConnected(false);
                    console.log('WebSocket Disconnected');
                    setTimeout(connectWebSocket, 2000);
                };
                
                const pingInterval = setInterval(() => {
                    if (wsRef.current?.readyState === WebSocket.OPEN) {
                        wsRef.current.send('ping');
                    }
                }, 30000);
                
                return () => clearInterval(pingInterval);
            };
            
            useEffect(() => {
                connectWebSocket();
                
                return () => {
                    if (wsRef.current) wsRef.current.close();
                };
            }, []);
            
            const formatMove = (move, index) => {
                const moveNumber = Math.floor(index/2) + 1;
                return index % 2 === 0 ? `${moveNumber}. ${move}` : move;
            };
            
            return (
                <>
                    <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
                        {connected ? 'Connected' : 'Reconnecting...'}
                    </div>
                    <div className="game-container">
                        <div className="board-container">
                            <ChessBoard fen={gameState?.fen} />
                        </div>
                        <div className="info-container">
                            <h2>Game Info</h2>
                            {gameState && (
                                <>
                                    <div className="status">
                                        <div>Current Turn: {gameState.current_player}</div>
                                        {gameState.is_check && <div>Check!</div>}
                                        {gameState.is_checkmate && <div>Checkmate!</div>}
                                        {gameState.is_stalemate && <div>Stalemate!</div>}
                                        {gameState.is_insufficient_material && 
                                            <div>Draw (Insufficient Material)</div>}
                                    </div>
                                    <h3>Move History</h3>
                                    <div className="move-history">
                                        {gameState.move_stack.map((move, i) => (
                                            <span key={i} style={{marginRight: '10px'}}>
                                                {formatMove(move, i)}
                                            </span>
                                        ))}
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </>
            );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<ChessGame />);
    </script>
</body>
</html>
"""

    async def broadcast_state(self):
        """Broadcast current game state to all connected clients."""
        if not self.active_connections:
            return
            
        board = self.env.board
        state = {
            "fen": board.fen(),
            "current_player": "White" if board.turn else "Black",
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_stalemate": board.is_stalemate(),
            "is_insufficient_material": board.is_insufficient_material(),
            "move_stack": [move.uci() for move in board.move_stack],
        }
        
        message = json.dumps(state)
        dead_connections = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                dead_connections.add(connection)
                
        # Clean up dead connections
        self.active_connections -= dead_connections
    def draw_board(self):
        """Update the display with current game state."""
        async def _broadcast():
            await self.broadcast_state()
            
        if self.active_connections:
            asyncio.run(_broadcast())
    async def _run_server(self, port: int):
        """Run the FastAPI server asynchronously."""
        config = uvicorn.Config(
            self.app,
            host="127.0.0.1",
            port=port,
            log_level="error"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    def start_server(self, port: int = 8000):
        """Start the FastAPI server in a separate thread."""
        self.server_thread = threading.Thread(
            target=lambda: asyncio.run(self._run_server(port)),
            daemon=True
        )
        self.server_thread.start()
        # Give the server a moment to start
        time.sleep(1)