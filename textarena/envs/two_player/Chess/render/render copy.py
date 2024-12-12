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
        # [Previous init code remains the same...]
        self.chat_history = []  # Store chat messages

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
            "chat_history": self.chat_history,  # Include chat history in state
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

    def _get_index_html(self):
        return """
<!DOCTYPE html>
<html>
<head>
    <!-- [Previous head content remains the same...] -->
    <style>
        /* [Previous styles remain the same...] */
        .chat-container {
            margin-top: 20px;
            background: #363636;
            padding: 20px;
            border-radius: 8px;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }
        .chat-messages {
            height: 300px;
            overflow-y: auto;
            background: #2B2B2B;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .chat-message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 4px;
            background: #404040;
        }
        .chat-message .player-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .chat-message.white .player-name {
            color: #FFFFFF;
        }
        .chat-message.black .player-name {
            color: #A0A0A0;
        }
    </style>
</head>
<body>
    <!-- [Previous body content remains the same until ChessGame component...] -->
    <script type="text/babel">
        // [Previous React components remain the same until ChessGame...]

        function ChatHistory({ messages, playerNames }) {
            const messagesEndRef = useRef(null);

            const scrollToBottom = () => {
                messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
            };

            useEffect(() => {
                scrollToBottom();
            }, [messages]);

            return (
                <div className="chat-container">
                    <h2>Game Conversation</h2>
                    <div className="chat-messages">
                        {messages.map((msg, index) => (
                            <div 
                                key={index} 
                                className={`chat-message ${msg.player_id === 0 ? 'white' : 'black'}`}
                            >
                                <div className="player-name">
                                    {playerNames[msg.player_id]}:
                                </div>
                                <div>{msg.message}</div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </div>
            );
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
                    {gameState?.chat_history && (
                        <ChatHistory 
                            messages={gameState.chat_history} 
                            playerNames={gameState.player_names}
                        />
                    )}
                </>
            );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<ChessGame />);
    </script>
</body>
</html>
"""

    def add_chat_message(self, player_id: int, message: str):
        """Add a chat message to the history."""
        self.chat_history.append({
            "player_id": player_id,
            "message": message
        })
        
        async def _broadcast():
            await self.broadcast_state()
            
        if self.active_connections:
            asyncio.run(_broadcast())

    
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




class GameStateRender:
    """Browser-based render wrapper for the Chess environment."""
    def __init__(self, env, player_names: Optional[Dict[int, str]] = None):
        self.env = env
        self.player_names = player_names or {0: "White", 1: "Black"}
        self.active_connections: Set[WebSocket] = set()
        self.app = self._create_app()
        self.server = None
        self.chat_history = []
        print("GameStateRender initialized")


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
        app = FastAPI()
        
        @app.get("/")
        async def get_index():
            print("Index page requested")
            return HTMLResponse(self._get_index_html())
            
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            print("New WebSocket connection attempt")
            await websocket.accept()
            print("WebSocket connection accepted")
            self.active_connections.add(websocket)
            try:
                # Send initial state
                print("Broadcasting initial state")
                await self.broadcast_state()
                
                while True:
                    try:
                        data = await websocket.receive_text()
                        print(f"Received WebSocket message: {data}")
                        await websocket.send_text('{"status": "ok"}')
                    except Exception as e:
                        print(f"WebSocket error: {e}")
                        break
            finally:
                self.active_connections.remove(websocket)
                print("WebSocket connection closed")

        return app

    async def broadcast_state(self):
        """Broadcast current game state to all connected clients."""
        print("Broadcasting state")
        if not self.active_connections:
            print("No active connections")
            return
            
        board = self.env.board
        print(f"Current board state: {board.fen()}")
        
        state = {
            "fen": board.fen(),
            "current_player": "White" if board.turn else "Black",
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_stalemate": board.is_stalemate(),
            "is_insufficient_material": board.is_insufficient_material(),
            "move_stack": [move.uci() for move in board.move_stack],
            "chat_history": self.chat_history,
            "player_names": self.player_names
        }
        
        message = json.dumps(state)
        print(f"Broadcasting message: {message[:100]}...")  # Print first 100 chars to avoid clutter
        
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                print("Message sent successfully")
            except Exception as e:
                print(f"Failed to send message: {e}")
                dead_connections.add(connection)
                
        # Clean up dead connections
        self.active_connections -= dead_connections

    def draw_board(self):
        """Update the display with current game state."""
        print("draw_board called")
        async def _broadcast():
            await self.broadcast_state()
            
        if self.active_connections:
            print("Broadcasting in draw_board")
            asyncio.run(_broadcast())
        else:
            print("No active connections in draw_board")

    def start_server(self, port: int = 8000):
        """Start the FastAPI server."""
        print(f"Starting server on port {port}")
        config = uvicorn.Config(
            self.app,
            host="127.0.0.1",
            port=port,
            log_level="info"  # Changed to info for more visibility
        )
        self.server = uvicorn.Server(config)
        print("Server created, starting...")
        self.server.run()
        print("Server started")

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
            background: #363636;
            padding: 20px;
            border-radius: 8px;
        }
        .chess-board {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            width: 600px;
            height: 600px;
            border: 2px solid #404040;
        }
        .square {
            width: 75px;
            height: 75px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .square.light {
            background-color: #EEEED2;
        }
        .square.dark {
            background-color: #769656;
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
        .chat-container {
            margin-top: 20px;
            background: #363636;
            padding: 20px;
            border-radius: 8px;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }
        .chat-messages {
            height: 300px;
            overflow-y: auto;
            background: #2B2B2B;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .chat-message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 4px;
            background: #404040;
        }
        .chat-message .player-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .chat-message.white .player-name {
            color: #FFFFFF;
        }
        .chat-message.black .player-name {
            color: #A0A0A0;
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
        // Debug console output
        console.log('Script starting...');

        function ChessBoard({ fen }) {
            console.log('Rendering ChessBoard with FEN:', fen);
            
            if (!fen) {
                console.log('No FEN provided');
                return <div className="board-container">Loading...</div>;
            }

            const renderSquare = (i) => {
                const file = i % 8;
                const rank = Math.floor(i / 8);
                const isLight = (file + rank) % 2 === 0;
                
                return (
                    <div key={i} className={`square ${isLight ? 'light' : 'dark'}`}>
                        {getPieceChar(fen, i)}
                    </div>
                );
            };

            return (
                <div className="board-container">
                    <div className="chess-board">
                        {[...Array(64)].map((_, i) => renderSquare(i))}
                    </div>
                </div>
            );
        }

        function getPieceChar(fen, squareIndex) {
            const [position] = fen.split(' ');
            const rows = position.split('/');
            const rank = Math.floor(squareIndex / 8);
            const file = squareIndex % 8;
            
            let currentFile = 0;
            const row = rows[7 - rank];
            
            for (let i = 0; i < row.length; i++) {
                const char = row[i];
                if (isNaN(char)) {
                    if (currentFile === file) {
                        return <div style={{fontSize: '40px'}}>{getPieceSymbol(char)}</div>;
                    }
                    currentFile++;
                } else {
                    currentFile += parseInt(char);
                }
                if (currentFile > file) break;
            }
            return null;
        }

        function getPieceSymbol(piece) {
            const symbols = {
                'k': '♔', 'q': '♕', 'r': '♖', 'b': '♗', 'n': '♘', 'p': '♙',
                'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟'
            };
            return symbols[piece];
        }

        function ChatHistory({ messages, playerNames }) {
            const messagesEndRef = React.useRef(null);

            React.useEffect(() => {
                messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
            }, [messages]);

            if (!messages || messages.length === 0) {
                return null;
            }

            return (
                <div className="chat-container">
                    <h2>Game Conversation</h2>
                    <div className="chat-messages">
                        {messages.map((msg, index) => (
                            <div key={index} className={`chat-message ${msg.player_id === 0 ? 'white' : 'black'}`}>
                                <div className="player-name">
                                    {playerNames[msg.player_id]}:
                                </div>
                                <div>{msg.message}</div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </div>
            );
        }

        function ChessGame() {
            console.log('Rendering ChessGame');
            const [gameState, setGameState] = React.useState(null);
            const [connected, setConnected] = React.useState(false);
            const wsRef = React.useRef(null);

            React.useEffect(() => {
                console.log('ChessGame useEffect running');
                const connectWebSocket = () => {
                    console.log('Connecting WebSocket...');
                    wsRef.current = new WebSocket(`ws://${window.location.host}/ws`);
                    
                    wsRef.current.onopen = () => {
                        console.log('WebSocket Connected');
                        setConnected(true);
                    };
                    
                    wsRef.current.onmessage = (event) => {
                        try {
                            const state = JSON.parse(event.data);
                            console.log('Received state:', state);
                            if (state.fen) {
                                setGameState(state);
                            }
                        } catch (e) {
                            console.error('Error parsing message:', e);
                        }
                    };
                    
                    wsRef.current.onclose = () => {
                        console.log('WebSocket Disconnected');
                        setConnected(false);
                        setTimeout(connectWebSocket, 2000);
                    };
                };
                
                connectWebSocket();
                return () => wsRef.current?.close();
            }, []);

            if (!gameState) {
                console.log('No game state yet');
                return <div>Loading game...</div>;
            }

            console.log('Rendering game with state:', gameState);
            return (
                <>
                    <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
                        {connected ? 'Connected' : 'Reconnecting...'}
                    </div>
                    <div className="game-container">
                        <ChessBoard fen={gameState.fen} />
                        <div className="info-container">
                            <h2>Game Info</h2>
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
                                        {i % 2 === 0 ? `${Math.floor(i/2) + 1}. ` : ''}{move}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                    <ChatHistory 
                        messages={gameState.chat_history} 
                        playerNames={gameState.player_names}
                    />
                </>
            );
        }

        // Debug console output
        console.log('Starting React render...');
        
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<ChessGame />);
        
        console.log('React render complete');
    </script>
</body>
</html>
"""