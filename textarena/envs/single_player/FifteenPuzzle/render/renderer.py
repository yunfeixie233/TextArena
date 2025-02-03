from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer
import shutil
from pathlib import Path

class FifteenPuzzleRenderer(BaseRenderer):
    """FifteenPuzzle-specific browser renderer"""

    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)

    def get_state(self) -> dict:
        """Get FifteenPuzzle-specific state"""
        try:
            return {
                "board":  self.env.state.game_state["board"] if self.env.state else [],
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "board": [],
                "current_player": "Unknown",
            }
        
    def get_custom_js(self) -> str:
        """
        Get FifteenPuzzle-specific JavaScript code
        """
        return """
        console.log('Loading FifteenPuzzle components...');

        const renderFifteenPuzzleGameInfo = (gameState) => {
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
                </div>
            );
        };

        const FifteenPuzzleBoard = ({ board }) => {
    return (
        <div className="fifteen-puzzle-board-container">
            <table className="fifteen-puzzle-board">
                <tbody>
                    {board.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                            {row.map((cell, colIndex) => (
                                <td
                                    key={colIndex}
                                    className={`tile ${cell === null ? 'empty-tile' : 'number-tile'}`}
                                >
                                    {cell !== null ? cell : ''}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

const FifteenPuzzleGame = () => {
    console.log('Initializing Fifteen Puzzle');
    const [gameState, setGameState] = React.useState(null);

    React.useEffect(() => {
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        ws.onopen = () => console.log('WebSocket connected');
        ws.onmessage = (event) => {
            try {
                const state = JSON.parse(event.data);
                console.log('Received state:', state);

                setGameState({
                    ...state,
                    board: state.board.map(row => [...row]) // Ensure React detects changes
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
        <BaseGameContainer className="FifteenPuzzle-layout" gameState={gameState} renderGameInfo={renderFifteenPuzzleGameInfo}>
            <div className="main-content">
                <FifteenPuzzleBoard board={gameState.board} />
            </div>
        </BaseGameContainer>
    );
};

// Initialize the app
console.log('Initializing React app');
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<FifteenPuzzleGame />);
console.log('Fifteen Puzzle components loaded');
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
.fifteen-puzzle-board-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px;
    background-color: #f5f5f5;
    border-radius: 10px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    width: 500px; /* Increased board size */
    height: 500px;
}

/* Grid structure */
.fifteen-puzzle-board {
    border-collapse: collapse;
    width: 100%; /* Ensure it expands */
    height: 100%;
    box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.2);
}

/* Tile styles */
.tile {
    width: 90px; /* Bigger tiles */
    height: 90px;
    text-align: center;
    vertical-align: middle;
    border: 3px solid #333;
    font-size: 28px; /* Bigger font */
    font-weight: bold;
    font-family: "Merriweather", serif;
    box-sizing: border-box;
    transition: all 0.2s ease-in-out;
}

/* Numbered tiles */
.number-tile {
    background-color: #ffcc66;
    color: #333;
    box-shadow: inset 3px 3px 6px rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    cursor: pointer;
}

/* Empty tile */
.empty-tile {
    background-color: #ddd;
    border: 3px solid #bbb;
}

/* Hover effect */
.number-tile:hover {
    background-color: #ffb347;
    transform: scale(1.1);
}

        """