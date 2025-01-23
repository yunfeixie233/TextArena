from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer

class SpellingBeeRenderer(BaseRenderer):
    """
    SpellingBee-specific browser renderer
    """
    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)
    
    def get_state(self) -> dict:
        """
        Get SpellingBee-specific state
        """
        try:
            return {
                "allowed_letters": self.env.state.game_state["allowed_letters"] if self.env.state else [],  # Assuming board is a nested list
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "allowed_letters": [],
                "current_player": "Unknown",
            }
    
    def get_custom_js(self) -> str:
        """
        Get SpellingBee-specific JavaScript code
        """
        return """
        console.log('Loading SpellingBee components...');

        const renderSpellingBeeGameInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            return (
                <div>
                    <h3>Current Turn: {currentPlayerName} </h3>
                    <h3>Players</h3>
                    <div className="players">
                        {Object.entries(gameState.player_names).map(([id, name]) => (
                            <div key={id} className={id === '0' ? 'player0' : 'player1'}>
                                {name}
                            </div>
                        ))}
                    </div>
                    <h3>Allowed Letters</h3>
                    <div className="allowed-letters">
                        {gameState.allowed_letters.map((letter, index) => (
                            <div key={index} className="letter">
                                {letter}
                            </div>
                        ))}
                    </div>
                </div>
            );
        };


        const SpellingBeeGame = () => {
            console.log('Initializing SpellingBeeGame');
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
                    className="SpellingBee-layout" 
                    gameState={gameState} 
                    renderGameInfo={renderSpellingBeeGameInfo} 
                >
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<SpellingBeeGame />);
        console.log('SpellingBee components loaded');
        """
    
    def get_custom_css(self) -> str:
        """Get DontSayIt-specific CSS"""
        return """
        
        .allowed-letters {
            display: flex;
            gap: 10px; /* Adds spacing between letters */
            justify-content: center; /* Center aligns the letters */
            margin-top: 10px; /* Adds spacing above the section */
        }

        .letter {
            padding: 10px;
            width: 40px; /* Ensures consistent box size */
            height: 40px;
            display: flex;
            align-items: center; /* Centers the text vertically */
            justify-content: center; /* Centers the text horizontally */
            border: 2px solid #ccc;
            border-radius: 6px; /* Rounded corners */
            background-color: #fff; /* Clean white background */
            font-size: 1.5em; /* Bigger and clearer font */
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s, background-color 0.2s;
        }

        .letter:hover {
            transform: scale(1.1); /* Slightly enlarges on hover */
            background-color: #f0f0f0; /* Subtle background change */
            cursor: pointer;
        }

        .player0 {
            color: #ffffff; 
        }

        .player1 {
            color: #000000;
        }

        """