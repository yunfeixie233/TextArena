from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer

class TruthAndDeceptionRenderer(BaseRenderer):
    """TruthAndDeception-specific browser renderer"""

    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)

    def get_state(self) -> dict:
        """Get TruthAndDeception-specific state"""
        try:
            return {
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
                "correct_fact": self.env.state.game_state["correct_fact"] if self.env.state else "Unknown",
                "wrong_fact": self.env.state.game_state["wrong_fact"] if self.env.state else "Unknown",
                "max_turns": self.env.state.max_turns if self.env.state else "Unknown",
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "current_player": "Unknown",
                "correct_fact": "Unknown",
                "wrong_fact": "Unknown",
                "max_turns": "Unknown",
            }
        
    def get_custom_js(self) -> str:
        """
        Get TruthAndDeception-specific JavaScript code
        """
        return """
        console.log('Loading TruthAndDeception components...');

        const renderTruthAndDeceptionGameInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            return (
                <div>
                    <h3>Current Turn: {currentPlayerName}</h3>
                    <h3>Players</h3>
                    <div className="players">
                        {Object.entries(gameState.player_names).map(([id, name]) => (
                            <div key={id} className={id === '0' ? 'player0' : 'player1'}>
                                {name} ({id === '0' ? 'Deceiver' : 'Guesser'})
                            </div>
                        ))}
                    </div>

                    <h3>Facts</h3>
                    <div className="facts">
                        <div className="fact">
                            <span className="fact-title">Correct Fact:</span> {gameState.correct_fact}
                        </div>
                        <div className="fact">
                            <span className="fact-title">Wrong Fact:</span> {gameState.wrong_fact}
                        </div>
                    </div>

                    <h3>Max Turns: {gameState.max_turns}</h3>

                </div>
            );
        };
        
        const TruthAndDeceptionGame = () => {
            console.log('Initializing TruthAndDeceptionGame');
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
                    className="TruthAndDeception-layout" 
                    gameState={gameState} 
                    renderGameInfo={renderTruthAndDeceptionGameInfo} 
                >
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<TruthAndDeceptionGame />);
        console.log('TruthAndDeception components loaded');
        """
    
    def get_custom_css(self) -> str:
        """Get TruthAndDeception-specific CSS"""
        return """

        h3 {
            margin-bottom: 5px; /* Reduce space below the heading */
        }

        .players {
            margin-top: 0; /* Remove top margin for the content sections */
            padding-top: 0; /* Remove any top padding */
        }

        .player0 {
            margin-left: 10px; /* Adjust this value to control the amount of indentation */
            color: #ffffff; /* Red color for player 0 */
        }

        .player1 {
            margin-left: 10px; /* Adjust this value to control the amount of indentation */
            color: #000000; /* Blue color for player 1 */
        }

        .facts .fact {
            margin-left: 10px; /* Adjust this value to control the amount of indentation */
            margin-top: 0; /* Remove any default margin on the top of the heading */
            margin-bottom: 5px; /* Reduce the space between the Fact title and the paragraph */
        }

        .fact-title {
            font-weight: bold; /* Make the Fact title bold */
        }

        """