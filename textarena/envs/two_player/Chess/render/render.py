from pathlib import Path
from typing import Dict, Optional, Set
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import json
import asyncio
from textarena.wrappers.render_wrappers import BaseBrowserRenderer

class ChessRenderer(BaseBrowserRenderer):
    """Chess-specific browser renderer."""
    
    def __init__(self, env, player_names: Optional[Dict[int, str]] = None):
        # Initialize base class first to ensure all attributes are set
        super().__init__(env, player_names)
        
        # Create necessary directories and setup files
        self._setup_piece_images()
        self._setup_frontend_files()

    def _setup_piece_images(self):
        """Copy piece images from the Chess render_assets to static directory."""
        # Create pieces directory in static
        pieces_dir = self.static_dir / "pieces"
        pieces_dir.mkdir(exist_ok=True)
        
        # Path to the original piece images
        source_dir = Path(__file__).parent / "render_assets"
        
        # Copy each piece image
        for piece in ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']:
            source = source_dir / f"{piece}.png"
            if source.exists():
                shutil.copy(source, pieces_dir / f"{piece}.png")

    def get_state(self) -> dict:
        """Get the current chess game state."""
        board = self.env.board
        return {
            "fen": board.fen(),
            "current_player": "White" if board.turn else "Black",
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_stalemate": board.is_stalemate(),
            "is_insufficient_material": board.is_insufficient_material(),
            "move_stack": [move.uci() for move in board.move_stack],
            "chat_history": self.chat_history,  # Base class provides this
            "player_names": self.player_names
        }

    def _setup_frontend_files(self):
        """Write chess-specific frontend files to static directory."""
        # Write CSS
        with open(self.static_dir / "chess.css", "w") as f:
            f.write(self._get_css())
            
        # Write JavaScript
        with open(self.static_dir / "chess.js", "w") as f:
            f.write(self._get_js())

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


    def _get_index_html(self) -> str:
        return """<!DOCTYPE html>
<html>
<head>
    <title>Chess Game</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.21.2/babel.min.js"></script>
    <link rel="stylesheet" href="/static/chess.css">
</head>
<body>
    <div id="root"></div>
    <script type="text/babel" src="/static/chess.js"></script>
</body>
</html>"""

    def _get_css(self) -> str:
        return """
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
.piece-img {
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
}"""

    def _get_js(self) -> str:
        return """
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
                {getPieceImage(fen, i)}
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

function getPieceImage(fen, squareIndex) {
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
                return <img 
                    className="piece-img" 
                    src={`/static/pieces/${char}.png`} 
                    alt={char}
                />;
            }
            currentFile++;
        } else {
            currentFile += parseInt(char);
        }
        if (currentFile > file) break;
    }
    return null;
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

console.log('Starting React render...');
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<ChessGame />);
console.log('React render complete');"""