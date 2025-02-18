from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer
import shutil
from pathlib import Path

class CrosswordsRenderer(BaseRenderer):
    """Crosswords-specific browser renderer"""

    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)

    def get_state(self) -> dict:
        """Get Crosswords-specific state"""
        try:
            return {
                "board":  self.env.state.game_state["board"] if self.env.state else [],
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
                "clues": self.env.state.game_state["clues"] if self.env.state else []
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "board": [],
                "current_player": "Unknown",
                "clues": []
            }
        
    def get_custom_js(self) -> str:
        """
        Get Crosswords-specific JavaScript code
        """
        return """
        console.log('Loading Crosswords components...');

        const renderCrosswordsGameInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            return (
                <div>
                    <h3>Player</h3>
                    <div className="players">
                        {Object.entries(gameState.player_names).map(([id, name]) => (
                            <div key={id} className={id === '0' ? 'player0' : 'player1'}>
                                {name}
                            </div>
                        ))}
                    </div>
                    <h3>Clues</h3>
                    <div className="allowed-letters">
                        {gameState.clues.map((clue, index) => (
                            <div key={index} className="clue-item">
                                {clue}
                            </div>
                        ))}
                    </div>
                </div>
            );
        };

        const CrosswordsBoard = ({ board }) => {
            const [playerBoard, setPlayerBoard] = React.useState(board);

            const handleChange = (rowIndex, colIndex, value) => {
                // Allow only A-Z input
                if (/^[a-zA-Z]?$/.test(value)) {
                    const newBoard = playerBoard.map((row, rIdx) =>
                        row.map((cell, cIdx) =>
                            rIdx === rowIndex && cIdx === colIndex ? value.toUpperCase() : cell
                        )
                    );
                    setPlayerBoard(newBoard);
                }
            };

            React.useEffect(() => {
                // Update the board when receiving new state
                setPlayerBoard([...board.map(row => [...row])]);
            }, [board]); // Re-run this effect when `board` updates

            return (
                <div className="crosswords-board-container">
                    <table className="crosswords-board">
                        <tbody>
                            {playerBoard.map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                    {row.map((cell, colIndex) => (
                                        <td
                                            key={colIndex}
                                            className={`cell ${cell === '_' ? 'black-cell' : 'white-cell'}`}
                                        >
                                            {cell === '_' ? null : (
                                                <input
                                                    type="text"
                                                    maxLength="1"
                                                    className="cell-input"
                                                    value={cell !== '.' ? cell : ''}
                                                    onChange={(e) => handleChange(rowIndex, colIndex, e.target.value)}
                                                />
                                            )}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            );
        };

        const CrosswordsGame = () => {
            console.log('Initializing Crosswords');
            const [gameState, setGameState] = React.useState(null);

            React.useEffect(() => {
                const ws = new WebSocket(`ws://${window.location.host}/ws`);
                ws.onopen = () => console.log('WebSocket connected');
                ws.onmessage = (event) => {
                    try {
                        const state = JSON.parse(event.data);
                        console.log('Received state:', state);

                        // Ensure deep copy of the board so React detects changes
                        setGameState({
                            ...state,
                            board: state.board.map(row => [...row]) // Create new reference for React
                        });

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
                <BaseGameContainer className="Crosswords-layout" gameState={gameState} renderGameInfo={renderCrosswordsGameInfo}>
                    <div className="main-content">
                        <CrosswordsBoard board={gameState.board} />
                    </div>
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<CrosswordsGame />);
        console.log('Crosswords components loaded');
        """
    
    def get_custom_css(self) -> str:
        """Get DontSayIt-specific CSS"""
        return """
        .main-content {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }

        /* Board container */
        .crosswords-board-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 20px;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        /* Grid table */
        .crosswords-board {
            border-collapse: collapse;
            table-layout: fixed;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.2);
        }

        /* Crossword cells */
        .cell {
            width: 50px;
            height: 50px;
            text-align: center;
            vertical-align: middle;
            border: 2px solid #333; /* Darker border for clarity */
            font-size: 24px;
            font-weight: bold;
            font-family: "Merriweather", serif;
            text-transform: uppercase;
            box-sizing: border-box;
            position: relative;
            transition: background-color 0.3s ease-in-out;
        }

        /* Style for black (unplayable) cells */
        .black-cell {
            background-color: #333;
            border: 2px solid #000;
            box-shadow: inset 2px 2px 6px rgba(0, 0, 0, 0.5);
        }

        /* Style for white (playable) cells */
        .white-cell {
            background-color: #fdf7e3;
            border: 2px solid #bbb;
        }

        /* Input styling */
        .cell-input {
            width: 100%;
            height: 100%;
            font-size: 24px;
            font-family: "Merriweather", serif;
            font-weight: bold;
            text-transform: uppercase;
            text-align: center;
            border: none;
            outline: none;
            background: transparent;
            color: #333;
            cursor: pointer;
            transition: all 0.3s ease-in-out;
        }

        /* Focused cell effect */
        .cell-input:focus {
            background-color: #ffeb99;
            outline: 2px solid #ffb300;
            border-radius: 5px;
            box-shadow: 0px 0px 8px rgba(255, 179, 0, 0.7);
        }

        /* Player highlights */
        .active-player {
            background-color: #ffcc80 !important;
        }

        /* Chat and game status areas */
        #game-status, #game-chat {
            font-family: "Courier New", monospace;
            background-color: #eeeeee;
            padding: 12px;
            border-radius: 5px;
            font-size: 14px;
        }

        .clues-container {
            margin-top: 10px;
        }

        .clue-item {
            margin-bottom: 16px; /* Adds a line of space between clues */
            padding: 8px;
            background-color: #f9f9f9;
            border-left: 5px solid #ffcc00;
            font-size: 16px;
            line-height: 1.5; /* Improves readability */
        }



        """