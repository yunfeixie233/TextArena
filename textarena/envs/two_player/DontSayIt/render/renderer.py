from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer
import shutil
from pathlib import Path

class DontSayItRenderer(BaseRenderer):
    """DontSayIt-specific browser renderer"""

    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)

    def get_state(self) -> dict:
        """Get DontSayIt-specific state"""
        try:
            return {
                "target_words": self.env.state.game_state["target_words"] if self.env.state else [],  # Assuming target_words is a nested list
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "target_words": [],
                "current_player": "Unknown",
            }
        
    def get_custom_js(self) -> str:
        """
        Get DontSayIt-specific JavaScript code
        """
        return """
        console.log('Loading DontSayIt components...');

        // Define the highlightWordsInMessage function
        const highlightWordsInMessage = (message, wordsToHighlight) => {
            // Create a dynamic regex pattern from the array of words to highlight
            const regexPattern = `(${wordsToHighlight.join('|')})`; // Match the target words as substrings
            const regex = new RegExp(regexPattern, 'gi'); // 'g' for global and 'i' for case-insensitive

            // Replace matching words with wrapped span
            return message.replace(regex, (match) => {
                return `<span class="highlighted-word">${match}</span>`; // Wrap the matched word in span with class 'highlighted-word'
            });
        };

        const renderDontSayItGameInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            return (
                <div>
                    <h3>Current Turn: {currentPlayerName}</h3>
                    <h3>Players</h3>
                    <div className="players">
                        {Object.entries(gameState.player_names).map(([id, name]) => (
                            <div key={id} className={id === '0' ? 'player0' : 'player1'}>
                                {name} (Secret Word: {gameState.target_words[id]})
                            </div>
                        ))}
                    </div>
                </div>
            );
        };


        const DontSayItGame = () => {
            console.log('Initializing DontSayItGame');
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

            // Extract the target words as an array
            const targetWords = Object.values(gameState.target_words);

            return (
                <BaseGameContainer 
                    className="DontSayIt-layout" 
                    gameState={gameState} 
                    renderGameInfo={renderDontSayItGameInfo} 
                    messageFunction={(message) => highlightWordsInMessage(message, targetWords)}
                >
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<DontSayItGame />);
        console.log('DontSayIt components loaded');
        """
    
    def get_custom_css(self) -> str:
        """Get DontSayIt-specific CSS"""
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

        .player0 {
            color: #ffffff; /* Red color for player 0 */
        }

        .player1 {
            color: #000000; /* Blue color for player 1 */
        }

        .highlighted-word {
            background-color: maroon;
            font-weight: bold; /* Optional: make it bold */
        }
        """