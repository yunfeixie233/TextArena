from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer
import shutil
from pathlib import Path

class TakRenderer(BaseRenderer):
    """Tak-specific browser renderer"""

    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)
        self._setup_piece_images()

    def _setup_piece_images(self):
        """Copy Tak piece images to the render directory"""
        pieces_dir = self.static_dir / "pieces"
        pieces_dir.mkdir(exist_ok=True)

        # Copy piece images to the render directory
        assets_dir = Path(__file__).parent / "assets" / "pieces"
        if assets_dir.exists():
            for piece in ["F0","F1","W0","W1","C0","C1"]:
                src = assets_dir / f"{piece}.png"
                if src.exists():
                    shutil.copy(src, pieces_dir / f"{piece}.png")

    def get_state(self) -> dict:
        """Get Tak-specific state"""
        try:
            board = self.env.board
            return {
                "board": board or [],  # Assuming board is a nested list
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
                "player_pieces": self.env.players or {},
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "board": [],
                "current_player": "Unknown",
                "player_pieces": {},
            }

    def get_custom_js(self) -> str:
        """Get Tak-specific JavaScript code"""
        return """
        console.log('Loading Tak components...');

        const TakBoard = ({ board }) => {
            return (
                <div className="board-container">
                    <table className="tak-board">
                        <tbody>
                            {board.map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                    {row.map((cell, cellIndex) => (
                                        <td key={cellIndex} className={`cell ${((rowIndex + cellIndex) % 2 === 0) ? "light" : "dark"}`}>
                                            <div className="cell-content">
                                                {getPiece(cell)}
                                            </div>
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            );
        };

        const getPiece = (cell) => {
            // Base Case: If cell is a single piece, return its image
            if (typeof cell === 'string') {
                return (
                    <img
                        src={`/static/pieces/${cell}.png`}
                        alt={cell}
                        className="piece-img"
                    />
                );
            }

            // Recursive Case: If cell is an array, recursively render pieces
            if (Array.isArray(cell)) {
                return (
                    <div className="stacked-pieces">
                        {cell.slice().reverse().map((item, index) => (
                            <div key={index} className="piece">
                                {getPiece(item)}
                            </div>
                        ))}
                    </div>
                );
            }

            // Default Case: Return null for empty cells
            return null;
        };



        
        const renderTakGameInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            return (
                <div>
                    <h3>Current Turn: {currentPlayerName}</h3>
                    <h3>Player Pieces</h3>
                    <div className="players">
                         {Object.entries(gameState.player_names).map(([id, name]) => (
                            <div key={id} className={id === '0' ? 'white-player' : 'black-player'}>
                                {name} ({id === '0' ? 'White' : 'Black'}) - 
                                Stones: {gameState.player_pieces[id]?.stones}, 
                                Capstones: {gameState.player_pieces[id]?.capstones}
                            </div>
                        ))}
                    </div>
                </div>
            );
        }


        const TakGame = () => {
            console.log('Initializing TakGame');
            const [gameState, setGameState] = React.useState(null);

            React.useEffect(() => {
                const ws = new WebSocket(`ws://${window.location.host}/ws`);
                ws.onopen = () => console.log('WebSocket connected');
                ws.onmessage = (event) => {
                    try {
                        const state = JSON.parse(event.data);
                        console.log('Received state:', state);
                        setGameState(state);
                    } catch (err) {
                        console.error('Error parsing WebSocket message:', err);
                    }
                };
                ws.onclose = () => console.log('WebSocket connection closed');
                return () => ws.close();
            }, []);

            if (!gameState) {
                console.log('Waiting for game state...');
                return <div>Loading game state...</div>;
            }

            return (
                <BaseGameContainer className="tak-layout" gameState={gameState} renderGameInfo={renderTakGameInfo}>
                    <div className="main-content">
                        <TakBoard board={gameState.board} />
                    </div>
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<TakGame />);
        console.log('Tak components loaded');
        """

    def get_custom_css(self) -> str:
        """Get custom CSS styles for Tak game"""
        return """
        .main-content {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }

        /* Board container for dynamic, centered sizing */
        .board-container {
            flex: 0 0 600px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: auto;
            overflow: hidden;
        }

        /* Main board table */
        .tak-board {
            border-collapse: collapse;
            width: 600px; /* Fill container */
            height: 600px; /* Ensure square grid */
            table-layout: fixed; /* Ensure fixed column width */
        }

        /* Individual cells */
        .tak-board td {
            border: 1px solid #555;
            position: relative;
            text-align: center;
            vertical-align: middle;
            background-color: #d7b899; /* Default light square */
        }

        .tak-board td.light {
            background-color: #d7b899; /* Light square */
        }

        .tak-board td.dark {
            background-color: #a97d55; /* Dark square */
        }

        /* Ensures cells remain square */
        .tak-board td::before {
            content: "";
            display: block;
            padding-top: 100%; /* Maintains aspect ratio */
        }

        .cell-content {
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            flex-direction: column-reverse; /* Stack items in reverse order */
            align-items: center;            /* Center horizontally */
            font-size: 1.3rem;
            font-weight: bold;
            color: #333;
        }


        .cell-list {
            display: flex;       /* Use flexbox */
            flex-direction: column-reverse; /* Stack items vertically */
            justify-content: flex-end; /* Optional: Center items vertically */
            align-items: bottom; /* Optional: Center items horizontally */
        }

        .cell-item {
            display: block; /* Ensure each item takes its own line */
            margin: 2px 0; /* Optional: Add vertical spacing between items */
        }

        .piece-img {
            height: 25px;
            object-fit: contain;
        }

        .players {
            margin-bottom: 20px;
        }

        .white-player { color: #ffffff; }
        .black-player { color: #000000; }

        """