from pathlib import Path
import shutil
from .base import BaseRenderer

class ChessRenderer(BaseRenderer):
    """Chess-specific renderer implementation"""
    
    def __init__(self, env, player_names=None, port=8000):
        super().__init__(env, player_names, port)
        self._setup_static_files()
        self.chat_history = []  # Initialize chat history

    def get_state(self) -> dict:
        """Get current chess game state"""
        try:
            board = self.env.board
            return {
                "fen": board.fen() if board else "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "current_player": "White" if board and board.turn else "White",
                "is_check": board.is_check() if board else False,
                "is_checkmate": board.is_checkmate() if board else False,
                "is_stalemate": board.is_stalemate() if board else False,
                "move_stack": [move.uci() for move in board.move_stack] if board else [],
                "valid_moves": [move.uci() for move in board.legal_moves] if board else [],
                "chat_history": self.chat_history,  # Now using the stored chat history
                "player_names": self.player_names
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "current_player": "White",
                "is_check": False,
                "is_checkmate": False,
                "is_stalemate": False,
                "move_stack": [],
                "valid_moves": [],
                "chat_history": [],
                "player_names": self.player_names
            }

    def _setup_static_files(self):
        """Set up static files for the chess UI"""
        # Create chess directory
        chess_dir = self.static_dir / "chess"
        chess_dir.mkdir(exist_ok=True)
        
        # Copy CSS file
        (chess_dir / "style.css").write_text(self._get_css())
        
        # Copy JavaScript file
        (chess_dir / "app.js").write_text(self._get_js())
        
        # Setup piece images
        pieces_dir = chess_dir / "pieces"
        pieces_dir.mkdir(exist_ok=True)
        
        # Copy piece images from the current pieces directory
        source_pieces_dir = Path(__file__).parent.parent / "static" / "pieces"
        if source_pieces_dir.exists():
            for piece in ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']:
                src = source_pieces_dir / f"{piece}.png"
                if src.exists():
                    shutil.copy(src, pieces_dir / f"{piece}.png")

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
            flex-direction: column;
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .main-content {
            display: flex;
            gap: 20px;
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

        .square.light { background-color: #EEEED2; }
        .square.dark { background-color: #769656; }

        .piece-img {
            width: 60px;
            height: 60px;
            user-select: none;
        }

        .info-container {
            flex: 1;
            background: #363636;
            padding: 20px;
            border-radius: 8px;
        }

        .chat-container {
            background: #363636;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
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
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 4px;
            background: #404040;
        }

        .white-player { color: #FFFFFF; }
        .black-player { color: #A0A0A0; }
        .game-message { color: #4CAF50; }

        .move-history {
            font-family: monospace;
            margin-top: 10px;
        }
        """

    def _get_js(self) -> str:
        return """
        function ChessGame() {
            const [gameState, setGameState] = React.useState(null);
            
            React.useEffect(() => {
                const ws = new WebSocket(`ws://${window.location.host}/ws`);
                ws.onmessage = (event) => {
                    const state = JSON.parse(event.data);
                    setGameState(state);
                };
                return () => ws.close();
            }, []);

            if (!gameState) return <div>Loading...</div>;

            return (
                <div className="game-container">
                    <div className="main-content">
                        <ChessBoard fen={gameState.fen} />
                        <GameInfo gameState={gameState} />
                    </div>
                    <ChatHistory gameState={gameState} />
                </div>
            );
        }

        function ChessBoard({ fen }) {
            const renderSquare = (i) => {
                const file = i % 8;
                const rank = Math.floor(i / 8);
                const isLight = (file + rank) % 2 === 0;
                
                return (
                    <div key={i} className={`square ${isLight ? 'light' : 'dark'}`}>
                        {getPiece(fen, i)}
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

        function getPiece(fen, squareIndex) {
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
                        return (
                            <img 
                                src={`/static/chess/pieces/${char}.png`}
                                alt={char}
                                className="piece-img"
                            />
                        );
                    }
                    currentFile++;
                } else {
                    currentFile += parseInt(char);
                }
                if (currentFile > file) break;
            }
            return null;
        }

        function GameInfo({ gameState }) {
            return (
                <div className="info-container">
                    <h2>Game Status</h2>
                    <div>Current Turn: {gameState.current_player}</div>
                    {gameState.is_check && <div className="text-red-500">Check!</div>}
                    {gameState.is_checkmate && <div className="text-red-500">Checkmate!</div>}
                    {gameState.is_stalemate && <div className="text-yellow-500">Stalemate</div>}
                    
                    <h3>Players</h3>
                    <div>
                        {Object.entries(gameState.player_names).map(([id, name]) => (
                            <div key={id} className={id === '0' ? 'white-player' : 'black-player'}>
                                {name} ({id === '0' ? 'White' : 'Black'})
                            </div>
                        ))}
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
            );
        }

        function ChatHistory({ gameState }) {
            const messagesEndRef = React.useRef(null);
            
            React.useEffect(() => {
                messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
            }, [gameState.chat_history]);

            return (
                <div className="chat-container">
                    <h2>Game Chat</h2>
                    <div className="chat-messages">
                        {gameState.chat_history.map((msg, i) => (
                            <div key={i} className="chat-message">
                                <span className={
                                    msg.player_id === -1 ? 'game-message' :
                                    msg.player_id === 0 ? 'white-player' : 'black-player'
                                }>
                                    {msg.player_id === -1 ? 'Game' : gameState.player_names[msg.player_id]}:
                                </span>
                                <div>{msg.message}</div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </div>
            );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<ChessGame />);
        """