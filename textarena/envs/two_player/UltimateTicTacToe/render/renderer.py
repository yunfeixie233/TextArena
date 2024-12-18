from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer
import shutil
from pathlib import Path

class UltimateTicTacToeRenderer(BaseRenderer):
    """UltimateTicTacToe-specific browser renderer"""

    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)

    def get_state(self) -> dict:
        """Get UltimateTicTacToe-specific state"""
        try:
            board = self.env.board
            return {
                "board": board or [],  # Assuming board is a nested list
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
                "move_history": self.env.move_history,
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "board": [],
                "current_player": "Unknown",
                "move_history": [],
            }
        
    def get_custom_js(self) -> str:
        """
        Get UltimateTicTacToe-specific JavaScript code
        """
        return """
        console.log('Loading UltimateTicTacToe components...');

        const UltimateTicTacToeBoard = ({ board }) => {
            return (
                <div className="ultimate-board-container">
                    <table className="ultimate-tic-tac-toe-board">
                        <tbody>
                            {Array(3).fill(0).map((_, macroRow) => (
                                <tr key={macroRow}>
                                    {Array(3).fill(0).map((_, macroCol) => (
                                        <td key={macroCol} className="macro-cell">
                                            <table className="micro-board">
                                                <tbody>
                                                    {board[macroRow * 3 + macroCol].map((microRow, microRowIndex) => (
                                                        <tr key={microRowIndex}>
                                                            {microRow.map((cell, microColIndex) => (
                                                                <td
                                                                    key={microColIndex}
                                                                    className={`micro-cell ${
                                                                        (microRowIndex + microColIndex) % 2 === 0 ? 'light' : 'dark'
                                                                    }`}
                                                                >
                                                                    <div className="cell-content">{cell}</div>
                                                                </td>
                                                            ))}
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            );
        };

        const MoveHistory = ({ moveHistory, playerNames }) => {
            const moveHistoryRef = React.useRef(null);

            // Scroll to the bottom when move history updates
            React.useEffect(() => {
                if (moveHistoryRef.current) {
                    moveHistoryRef.current.scrollTop = moveHistoryRef.current.scrollHeight;
                }
            }, [moveHistory]);

            return (
                <div>
                    <h3>Move History</h3>
                    <div className="move-history" ref={moveHistoryRef}>
                        {moveHistory.map((move, index) => {
                            const player = playerNames[index % 2]; // Alternate between players
                            return (
                                <div key={index} className="move-entry">
                                    <span className="move-number">{index + 1}. </span>
                                    <span className="move">
                                        {player}: {formatMove(move)}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            );
        };

        const renderUltimateTicTacToeGameInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            return (
                <div>
                    <h3>Current Turn: {currentPlayerName}</h3>
                    <h3>Players</h3>
                    <div className="players">
                        {Object.entries(gameState.player_names).map(([id, name]) => (
                            <div key={id} className={id === '0' ? 'O-player' : 'X-player'}>
                                {name} ({id === '0' ? 'O' : 'X'})
                            </div>
                        ))}
                    </div>
        
                    {/* Render the MoveHistory component */}
                    <MoveHistory
                        moveHistory={gameState.move_history}
                        playerNames={gameState.player_names}
                    />
                </div>
            );
        };


        // Helper function to format a move
        const formatMove = (move) => {
            if (!move) return '';
            const [microBoard, row, col] = move;
            return `Micro Board ${microBoard}, Row ${row}, Col ${col}`;
        };


        const UltimateTicTacToeGame = () => {
            console.log('Initializing UltimateTicTacToeGame');
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
                <BaseGameContainer className="UltimateTicTacToe-layout" gameState={gameState} renderGameInfo={renderUltimateTicTacToeGameInfo}>
                    <div className="main-content">
                        <UltimateTicTacToeBoard board={gameState.board} />
                    </div>
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<UltimateTicTacToeGame />);
        console.log('UltimateTicTacToe components loaded');
        """
    
    def get_custom_css(self) -> str:
        """Get UltimateTicTacToe-specific CSS"""
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

        /* Main macro board */
        .ultimate-tic-tac-toe-board {
            border-collapse: collapse;
            width: 600px; /* Full board width */
            height: 600px; /* Full board height */
            table-layout: fixed;
        }

        /* Macro board cells (3x3 grid of micro boards) */
        .ultimate-tic-tac-toe-board .macro-cell {
            border: 2px solid #000;
            padding: 0;
            height: 200px; /* Adjust for 3x3 grid */
            width: 200px;
        }

        /* Micro board */
        .micro-board {
            border-collapse: collapse;
            width: 100%;
            height: 100%;
            table-layout: fixed;
        }

        /* Micro board cells (individual tic-tac-toe cells) */
        .micro-board .micro-cell {
            border: 1px solid #555;
            position: relative;
            text-align: center;
            vertical-align: middle;
            background-color: #d7b899; /* Light square */
        }

        .micro-board .micro-cell.light {
            background-color: #d7b899; /* Light square color */
        }

        .micro-board .micro-cell.dark {
            background-color: #a97d55; /* Dark square color */
        }

        /* Ensures cells remain square */
        .micro-board .micro-cell::before {
            content: "";
            display: block;
            padding-top: 100%; /* Maintain aspect ratio */
        }

        .cell-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1rem;
            font-weight: bold;
            color: #333;
        }

        /* Scrollable move history container */
        .move-history {
            max-height: 200px; /* Set the desired height of the scrollable area */
            overflow-y: auto; /* Enable vertical scrolling */
            border: 1px solid #ccc; /* Add a border for clarity */
            padding: 10px;
            background-color: #222d37; /* Dark background for contrast */
            color: #fff;
        }

        /* Move entry styling */
        .move-entry {
            margin-bottom: 5px; /* Add spacing between entries */
        }

        /* Smooth scrolling experience */
        .move-history::-webkit-scrollbar {
            width: 8px; /* Width of the scrollbar */
        }

        .move-history::-webkit-scrollbar-thumb {
            background-color: #aaa; /* Color of the scrollbar thumb */
            border-radius: 4px; /* Rounded scrollbar thumb */
        }

        .move-history::-webkit-scrollbar-track {
            background: #f0f0f0; /* Background of the scrollbar track */
        }

        
        """