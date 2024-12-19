from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer
import shutil
from pathlib import Path

class StrategoRenderer(BaseRenderer):
    """Stratego-specific browser renderer"""

    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)
        self._setup_piece_images()

    def _setup_piece_images(self):
        """Copy Stratego piece images to the render directory"""
        pieces_dir = self.static_dir / "pieces"
        pieces_dir.mkdir(exist_ok=True)

        ## Path to the assets directory containing .svg files
        assets_dir = Path(__file__).parent / "assets" / "pieces"

        if assets_dir.exists():
            ## List all .svg files in the assets directory
            for svg_file in assets_dir.glob("*.svg"):
                piece = svg_file.stem  ## Extract filename without extension (e.g., "Bomb0")
                src = assets_dir / f"{piece}.svg"
                if src.exists():
                    ## Copy file and save as .png in the destination directory
                    shutil.copy(src, pieces_dir / f"{piece}.svg")


    def get_state(self) -> dict:
        """Get Stratego-specific state"""
        try:
            board = self.env.board
            return {
                "board": board or [],  # Assuming board is a nested list
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "board": [],
                "current_player": "Unknown",
            }
        
    def get_custom_js(self) -> str:
        """Get Stratego-specific JavaScript code"""
        return """
        console.log('Loading Stratego components...');

        const StrategoBoard = ({ board }) => {
            return (
                <div className="stratego-board-container">
                    <table className="stratego-board">
                        <tbody>
                            {board.map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                    {row.map((cell, colIndex) => (
                                        <td
                                            key={colIndex}
                                            className={`cell ${
                                                (rowIndex + colIndex) % 2 === 0 ? 'light' : 'dark'
                                            }`}
                                        >
                                            <div className="cell-content">
                                                {getPiece(cell)} {/* Fetch and display piece image */}
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
            if (cell && cell.rank && cell.player !== undefined) {
                // Construct the file path for the image
                const filePath = `/static/pieces/${cell.rank}${cell.player}.svg`;
                return (
                    <img
                        src={filePath}
                        alt={`${cell.rank} of player ${cell.player}`}
                        className="piece-img"
                    />
                );
            }

            // Default: If the cell is empty, return a placeholder or null
            return null;
        };


        const renderStrategoInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            return (
                <div>
                    <h3>Current Turn: {currentPlayerName}</h3>
                    <h3>Players</h3>
                    <div className="players">
                        {Object.entries(gameState.player_names).map(([id, name]) => (
                            <div key={id} className={id === '0' ? 'white-player' : 'black-player'}>
                                {name} ({id === '0' ? 'white' : 'black'})
                            </div>
                        ))}
                    </div>
                </div>
            );
        };

        
        const Stratego = () => {
            console.log('Initializing Stratego');
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
                <BaseGameContainer className="Stratego-layout" gameState={gameState} renderGameInfo={renderStrategoInfo}>
                    <div className="main-content">
                        <StrategoBoard board={gameState.board} />
                    </div>
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<Stratego />);
        console.log('Stratego components loaded');
        """
    
    def get_custom_css(self) -> str:
        """Get Stratego-specific CSS"""
        return """

        .main-content {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        /* Board container for centering and dynamic sizing */
        .ultimate-board-container {
            flex: 0 0 600px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: auto;
            overflow: hidden;
        }

        .stratego-board-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 20px;
        }

        .stratego-board {
            border-collapse: collapse;
            width: 800px;
            height: 800px;
            table-layout: fixed; /* Ensures cells are equal width/height */
        }

        .cell {
            width: 80px;
            height: 80px;
            text-align: center;
            vertical-align: middle;
            border: 1px solid #000; /* Add borders for clarity */
            box-sizing: border-box; /* Includes padding and borders in width/height */
        }

        .cell-content {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            width: 100%;
            overflow: hidden; /* Prevent images from overflowing the cell */
        }

        .piece-img {
            max-width: 60%; /* Scale the image to fit within the cell */
            max-height: 60%; /* Maintain aspect ratio */
            object-fit: contain; /* Ensures images are contained without stretching */
        }


        .light {
            background-color: #d7b899;
        }

        .dark {
            background-color: #a97d55;
        }

        .players {
            margin-bottom: 20px;
        }

        .white-player { color: #ffffff; }
        .black-player { color: #000000; }

        """