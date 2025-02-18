from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer
import shutil
from pathlib import Path

class IteratedPrisonersDilemmaRenderer(BaseRenderer):
    """IteratedPrisonersDilemma-specific browser renderer"""

    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)

    def get_state(self) -> dict:
        """Get IteratedPrisonersDilemma-specific state"""
        try:
            return {
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
                "current_round": self.env.state.game_state["current_round"] if self.env.state else 0,
                "num_rounds": self.env.num_rounds,
                "history": self.env.state.game_state["history"] if self.env.state else [],
                "cooperate_reward": self.env.cooperate_reward,
                "defect_reward": self.env.defect_reward,
                "sucker_reward": self.env.sucker_reward,
                "mutual_defect_reward": self.env.mutual_defect_reward,
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "current_player": "Unknown",
                "current_round": 0,
                "num_rounds": 0,
                "history": [],
                "cooperate_reward": 0,
                "defect_reward": 0,
                "sucker_reward": 0,
                "mutual_defect_reward": 0,
            }
        
    def get_custom_js(self) -> str:
        """
        Get IteratedPrisonersDilemma-specific JavaScript code
        """
        return """
        console.log('Loading IteratedPrisonersDilemma components...');

        const PrisonersDilemmaTable = ({ gameState }) => {
            let cumulativePlayer1Score = 0; // Initialize cumulative scores
            let cumulativePlayer2Score = 0;

            const scrollContainerRef = React.useRef(null); // Reference for the scrollable container

            // Scroll to the bottom of the table body when gameState.history changes
            React.useEffect(() => {
                if (scrollContainerRef.current) {
                    scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
                }
            }, [gameState.history]); // Trigger when the game history changes

            return (
                <div className="game-table-container">
                    <table className="game-table">
                        <thead>
                            <tr>
                                <th>Round</th>
                                <th>P0 Choice</th>
                                <th>P1 Choice</th>
                                <th>P0 Score</th>
                                <th>P1 Score</th>
                                <th>P0 Total</th>
                                <th>P1 Total</th>
                            </tr>
                        </thead>
                    </table>
                    {/* Wrapping tbody rows in a scrollable div */}
                    <div ref={scrollContainerRef} className="scrollable-rows">
                        <table className="game-table">
                            <tbody>
                                {gameState.history.map((entry, index) => {
                                    const round = entry.round;
                                    const decisions = entry.decisions;
                                    const player1Choice = decisions["0"];
                                    const player2Choice = decisions["1"];

                                    // Initialize round scores
                                    let player1Score = 0;
                                    let player2Score = 0;

                                    // Determine scores and outcome based on the payoff matrix
                                    if (player1Choice === "cooperate" && player2Choice === "cooperate") {
                                        player1Score = gameState.cooperate_reward;
                                        player2Score = gameState.cooperate_reward;
                                    } else if (player1Choice === "cooperate" && player2Choice === "defect") {
                                        player1Score = gameState.sucker_reward;
                                        player2Score = gameState.defect_reward;
                                    } else if (player1Choice === "defect" && player2Choice === "cooperate") {
                                        player1Score = gameState.defect_reward;
                                        player2Score = gameState.sucker_reward;
                                    } else if (player1Choice === "defect" && player2Choice === "defect") {
                                        player1Score = gameState.mutual_defect_reward;
                                        player2Score = gameState.mutual_defect_reward;
                                    }

                                    // Update cumulative scores
                                    cumulativePlayer1Score += player1Score;
                                    cumulativePlayer2Score += player2Score;

                                    // Determine styles for cumulative scores
                                    const player1CumulativeStyle =
                                        cumulativePlayer1Score > cumulativePlayer2Score
                                            ? { color: "green", fontWeight: "bold" }
                                            : cumulativePlayer1Score < cumulativePlayer2Score
                                            ? { color: "red", fontWeight: "bold" }
                                            : { fontWeight: "bold" }; // Default color for tie

                                    const player2CumulativeStyle =
                                        cumulativePlayer2Score > cumulativePlayer1Score
                                            ? { color: "green", fontWeight: "bold" }
                                            : cumulativePlayer2Score < cumulativePlayer1Score
                                            ? { color: "red", fontWeight: "bold" }
                                            : { fontWeight: "bold" }; // Default color for tie

                                    return (
                                        <tr key={index}>
                                            <td style={{ fontWeight: "bold", color: "#ffcc00" }}>{round}</td> {/* Highlight the first column */}
                                            <td>{player1Choice.charAt(0).toUpperCase()}</td>
                                            <td>{player2Choice.charAt(0).toUpperCase()}</td>
                                            <td>{player1Score}</td>
                                            <td>{player2Score}</td>
                                            <td style={player1CumulativeStyle}>{cumulativePlayer1Score}</td> {/* Highlight Player 1 Cumulative */}
                                            <td style={player2CumulativeStyle}>{cumulativePlayer2Score}</td> {/* Highlight Player 2 Cumulative */}
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            );
        };


        const renderIteratedPrisonersDilemmaGameInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            return (
                <div>
                    <h3>Current Turn: {currentPlayerName}</h3>
                    <h3>Current Round: {gameState.current_round} of {gameState.num_rounds}</h3>
                </div>
            );
        };


        const IteratedPrisonersDilemmaGame = () => {
            console.log('Initializing IteratedPrisonersDilemmaGame');
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
                <BaseGameContainer 
                    className="IteratedPrisonersDilemma-layout" 
                    gameState={gameState} 
                    renderGameInfo={renderIteratedPrisonersDilemmaGameInfo} 
                >
                    <div className="main-content">
                        <PrisonersDilemmaTable gameState={gameState} />
                    </div>
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<IteratedPrisonersDilemmaGame />);
        console.log('IteratedPrisonersDilemma components loaded');
        """
    
    def get_custom_css(self) -> str:
        """Get IteratedPrisonersDilemma-specific CSS"""
        return """
        /* Main layout styling */
        .IteratedPrisonersDilemma-layout {
            display: flex;
            flex-direction: row;
            justify-content: space-between; /* Properly distribute space between elements */
            align-items: flex-start;
            gap: 20px; /* Add spacing between elements */
            margin: 0; /* Remove unnecessary margins */
            padding: 0; /* Remove unnecessary padding */
        }

        .game-info {
            flex: 1; /* Smaller space for the Game Status */
            background-color: #ccc; /* Light gray background for the status box */
            padding: 10px; /* Add some padding inside the box */
            border-radius: 5px; /* Rounded corners */
            text-align: center; /* Center align the text */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow for a polished look */
        }

        /* Main content styling */
        .main-content {
            width: 100%; /* Ensure the main content area spans full width */
            padding: 0; /* Remove unnecessary padding */
            margin: 0; /* Remove unnecessary margin */
            overflow-x: auto; /* Handle horizontal overflow gracefully */
        }

        /* Table container styling */
        .table-container {
            margin: 20px auto; /* Center the table horizontally */
            font-family: "Arial", sans-serif;
            width: 100%; /* Ensure the table container takes full width */
            padding: 0; /* Remove any padding that could create gaps */
            height: 100px; /* Fixed height for the table */
        }

        /* Table styling */
        .game-table-container {
            width: auto; /* Ensure the container size matches the table's content */
            margin: 0 auto; /* Center the table horizontally */
            overflow-x: auto; /* Allow horizontal scrolling if needed */
        }

        .game-table {
            width: 100%; 
            max-width: 650px; /* Ensure the table spans the full width */
            border-collapse: collapse; /* Collapse borders for a clean look */
            background-color: #1c1c1c; /* Dark background for the table */
            color: #eaeaea; /* Light text for contrast */
            margin: 0; /* Remove unnecessary margins */
            table-layout: fixed; /* Ensure consistent column widths for the entire table */
        }

        /* Fixed header with sticky positioning */
        .game-table thead th {
            position: sticky; /* Fix the header */
            top: 0; /* Stick to the top of the container */
            z-index: 2; /* Ensure it stays above the rows */
            background-color: #2b2b2b; /* Match the header background */
            color: #f4f4f4; /* Off-white text */
            font-weight: bold;
            font-size: 14px; /* Slightly larger font for headers */
            text-transform: uppercase; /* Professional look */
            border: 1px solid #333; /* Header border for separation */
            padding: 12px 8px; /* Add padding for readability */
            text-align: center; /* Center-align the text */
        }

        /* Table cells */
        .game-table td {
            padding: 10px 8px; /* Add padding for readability */
            text-align: center; /* Center-align the text */
            border: 1px solid #333; /* Subtle borders for separation */
            font-size: 14px; /* Slightly smaller font for content */
        }

        /* Scrollable rows */
        .scrollable-rows {
            height: 200px; /* Fixed height for scrollable rows */
            overflow-y: auto; /* Enable vertical scrolling */
            overflow-x: hidden; /* Prevent horizontal scrolling */
            width: 100%; /* Ensure the scrollable container spans the full width */
        }

        /* Table rows inside the scrollable div */
        .scrollable-rows table {
            width: 100%; /* Ensure the table spans the full width */
            max-width: 650px; /* Limit the width to prevent overflow */
            table-layout: fixed; /* Ensure consistent column widths */
        }

        /* Alternating row colors */
        .scrollable-rows tbody tr:nth-child(even) {
            background-color: #252525; /* Slightly lighter row color for even rows */
        }

        .scrollable-rows tbody tr:nth-child(odd) {
            background-color: #1c1c1c; /* Darker row color for odd rows */
        }

        /* Hover effect for rows */
        .scrollable-rows tbody tr:hover {
            background-color: #333333; /* Highlight row on hover */
            transition: background-color 0.2s ease-in-out;
        }

        /* Style scrollbars for the rows */
        .scrollable-rows::-webkit-scrollbar {
            width: 8px; /* Width of the scrollbar */
        }

        .scrollable-rows::-webkit-scrollbar-thumb {
            background-color: #444; /* Dark gray scrollbar */
            border-radius: 4px; /* Rounded scrollbar */
        }

        .scrollable-rows::-webkit-scrollbar-track {
            background: #1c1c1c; /* Scrollbar track matches background */
        }


        /* Responsive design */
        @media (max-width: 768px) {
            .IteratedPrisonersDilemma-layout {
                flex-direction: column; /* Stack items vertically on smaller screens */
                gap: 10px; /* Reduce spacing */
            }

            .main-content {
                width: 100%; /* Ensure the table takes up full width */
            }

            .game-info {
                width: 100%; /* Ensure the status box takes up full width */
            }

            .game-table-container {
                width: 100%; /* Allow table to take full width of its container */
                overflow-x: auto; /* Enable horizontal scrolling on smaller screens */
            }
        }


        """