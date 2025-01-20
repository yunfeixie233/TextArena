from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer
from pathlib import Path
import shutil

class LiarsDiceRenderer(BaseRenderer):
    """LiarsDiceRenderer class for rendering Liars Dice game environment."""

    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)
        self._setup_piece_images()

    def _setup_piece_images(self):
        """
        Copy the LiarsDice die images to the render directory
        """
        pieces_dir = self.static_dir / "pieces"
        pieces_dir.mkdir(exist_ok=True)

        ## Path to the assets directory containing .svg files
        assets_dir = Path(__file__).parent / "assets" / "pieces"

        if assets_dir.exists():
            ## List all .svg files in the assets directory
            for svg_file in assets_dir.glob("*.svg"):
                piece = svg_file.stem  
                src = assets_dir / f"{piece}.svg"
                if src.exists():
                    ## Copy file and save as .svg in the destination directory
                    shutil.copy(src, pieces_dir / f"{piece}.svg")

    def get_state(self) -> dict:
        """Get the current state of the environment."""
        try:          
            return {
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
                "dice_rolls_0": self.env.state.game_state["dice_rolls"][0] if self.env.state else [],
                "dice_rolls_1": self.env.state.game_state["dice_rolls"][1] if self.env.state else [],
                "quantity": self.env.state.game_state["current_bid"]["quantity"] if self.env.state else 0,
                "face_value": self.env.state.game_state["current_bid"]["face_value"] if self.env.state else 0,
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "current_player": "Unknown",
                "dice_rolls_0": [],
                "dice_rolls_1": [],
                "quantity": 0,
                "face_value": 0,
            }
        
    def get_custom_js(self) -> str:
        """
        Get the custom JavaScript code for the renderer.
        Returns:
            str: The custom JavaScript code.
        """
        return """
        console.log('Loading LiarsDice components...');

        // Component to display a single die
        const Die = ({ value, resourceImages }) => (
            <img
                src={`/static/pieces/${resourceImages[value]}`}
                alt={`Die ${value}`}
                className="die-img"
            />
            );

            // Helper function to split an array into chunks
            const chunkArray = (array, chunkSize) => {
            const result = [];
            for (let i = 0; i < array.length; i += chunkSize) {
                result.push(array.slice(i, i + chunkSize));
            }
            return result;
            };

            // Component to display a player's dice
            const PlayerDice = ({ playerName, diceRolls, resourceImages }) => {
            const rows = chunkArray(diceRolls, 6); // Split diceRolls into chunks of 6

            return (
                <div className="player-dice">
                <h4>{playerName} Dice:</h4>
                {rows.map((row, rowIndex) => (
                    <div className="dice-row" key={rowIndex}>
                    {row.map((value, index) => (
                        <Die key={index} value={value} resourceImages={resourceImages} />
                    ))}
                    </div>
                ))}
                </div>
            );
            };


            // Component to display game info (current player, bid details)
            const GameInfo = ({ currentPlayer, quantity, faceValue }) => (
            <div className="game-info">
                <p>
                Current Bid Quantity: <span>{quantity}</span>
                </p>
                <p>
                Current Bid Face Value: <span>{faceValue}</span>
                </p>
            </div>
            );

            // Main Liar's Dice component
            const LiarsDice = ({ gameState }) => {
            const resourceImages = {
                1: "1.svg",
                2: "2.svg",
                3: "3.svg",
                4: "4.svg",
                5: "5.svg",
                6: "6.svg",
            };

            return (
                <div className="liars-dice-container">
                <h2 className="header">Liar's Dice Game</h2>
                <div className="game-board">
                    <PlayerDice
                    playerName={gameState.player_names[0]}
                    diceRolls={gameState.dice_rolls_0}
                    resourceImages={resourceImages}
                    />
                    <PlayerDice
                    playerName={gameState.player_names[1]}
                    diceRolls={gameState.dice_rolls_1}
                    resourceImages={resourceImages}
                    />
                </div>
                <GameInfo
                    currentPlayer={gameState.current_player}
                    quantity={gameState.quantity}
                    faceValue={gameState.face_value}
                />
                </div>
            );
        };

        const renderLiarsDiceGameInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            return (
                <div>
                    <h3>Current Turn: {currentPlayerName}</h3>
                </div>
            );
        };


        const LiarsDiceGame = () => {
            console.log('Initializing LiarsDiceGame');
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
                    className="LiarsDice-layout" 
                    gameState={gameState} 
                    renderGameInfo={renderLiarsDiceGameInfo} 
                >

                    <LiarsDice gameState={gameState} />

                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<LiarsDiceGame />);
        console.log('LiarsDice components loaded');
        """

    def get_custom_css(self) -> str:
        """Get IteratedPrisonersDilemma-specific CSS"""
        return """

.liars-dice-container {
  max-width: 700px;
  margin: 20px auto;
  padding: 20px;
  background-color: #C4A484;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  text-align: center;
}

.header {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.game-board {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.player-dice {
  flex: 1;
  margin: 0 10px;
}

.player-dice h4 {
  margin-bottom: 10px;
  color: #555;
}

.dice-row {
  display: flex;
  justify-content: center;
}

.die-img {
  width: 50px;
  height: 50px;
  margin: 5


        """