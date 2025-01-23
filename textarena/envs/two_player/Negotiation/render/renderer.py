from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer
import shutil
from pathlib import Path

class NegotiationRenderer(BaseRenderer):
    """
    Negotiation-specific browser renderer
    """
    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)
        self._setup_piece_images()

    def _setup_piece_images(self):
        """
        Copy the negotiation piece images to the render directory
        """
        pieces_dir = self.static_dir / "pieces"
        pieces_dir.mkdir(exist_ok=True)

        ## Path to the assets directory containing .png files
        assets_dir = Path(__file__).parent / "assets" / "pieces"

        if assets_dir.exists():
            ## List all .png files in the assets directory
            for png_file in assets_dir.glob("*.png"):
                piece = png_file.stem  
                src = assets_dir / f"{piece}.png"
                if src.exists():
                    ## Copy file and save as .png in the destination directory
                    shutil.copy(src, pieces_dir / f"{piece}.png")

    def get_state(self) -> dict:
        """
        Get Negotiation-specific state
        """
        try:
            return {
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
                "player_resources": self.env.state.game_state["player_resources"] if self.env.state else {},
                "inventory_value": self.env.state.game_state["inventory_value"] if self.env.state else {},
                "current_offer": self.env.state.game_state["current_offer"] if self.env.state else None,
                "trade_history": self.env.state.game_state["trade_history"] if self.env.state else [],
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "current_player": "Unknown",
                "player_resources": {},
                "inventory_value": {},
                "current_offer": None,
                "trade_history": [],
            }
        
    def get_custom_js(self) -> str:
        """
        Get Negotiation-specific JavaScript code
        """
        return """
        console.log('Loading Negotiation components...');

        // Component to display a single resource cell
        const ResourceCell = React.memo(({ resource, count, resourceImages }) => (
            <div className="resource-cell">
                <img
                    src={`/static/pieces/${resourceImages[resource]}`}
                    alt={`${resource} icon`}
                    className="resource-img"
                />
                <div className="resource-count">{count}</div>
            </div>
        ));

        // Component to display the inventory table for a player
        const InventoryTable = React.memo(({ inventory }) => {
            const changeColor = inventory.change > 0 ? 'green' : 'red';
            return (
                <div className="inventory-table-container">
                    <table className="inventory-table">
                        <thead>
                            <tr>
                                <th>Resource</th>
                                <th>Initial Value</th>
                                <th>Current Value</th>
                                <th>Change</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Total Value</td>
                                <td>{inventory.initial}</td>
                                <td>{inventory.current}</td>
                                <td style={{ color: changeColor }}>{inventory.change}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            );
        });

        // Component for each player's resources and inventory
        const PlayerResources = ({ playerName, playerResources, inventory, resourceImages }) => (
            <div className="player-resources">
                <h3 className="player-header">{playerName}</h3>
                <div className="resource-row">
                    {Object.entries(playerResources).map(([resource, count]) => (
                        <ResourceCell key={resource} resource={resource} count={count} resourceImages={resourceImages} />
                    ))}
                    <InventoryTable inventory={inventory} />
                </div>
            </div>
        );

        // Main ResourceBoard component
        const ResourceBoard = ({ gameState }) => {
            const resourceImages = {
                Wheat: 'wheat.png',
                Wood: 'wood.png',
                Sheep: 'sheep.png',
                Brick: 'brick.png',
                Ore: 'ore.png',
            };

            return (
                <div className="board-container">
                    <div className="game-board">
                        <PlayerResources
                            playerName={gameState.player_names[0]}
                            playerResources={gameState.player_resources[0]}
                            inventory={gameState.inventory_value[0]}
                            resourceImages={resourceImages}
                        />
                        <PlayerResources
                            playerName={gameState.player_names[1]}
                            playerResources={gameState.player_resources[1]}
                            inventory={gameState.inventory_value[1]}
                            resourceImages={resourceImages}
                        />
                    </div>
                </div>
            );
        };

        const renderNegotiationInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            // Reference to the trade history container
            const tradeHistoryRef = React.useRef(null);

            // Scroll to the bottom when trade history updates
            React.useEffect(() => {
                if (tradeHistoryRef.current) {
                    tradeHistoryRef.current.scrollTop = tradeHistoryRef.current.scrollHeight;
                }
            }, [gameState.trade_history]); // Re-run whenever trade history updates

            return (
                <div>
                    <h3>Current Turn: {currentPlayerName}</h3>
                    <h3>Current Offer</h3>
                    <div className="current-offer">
                        {gameState.current_offer ? (
                            <div>
                                <h4 className="resource-row-header">{gameState.player_names[gameState.current_offer.from_player]} offers these resources:</h4>
                                <div className="resource-row">
                                    {Object.entries(gameState.current_offer.offered_resources).map(([resource, count]) => (
                                        <div key={resource}>
                                            {resource}: {count}
                                        </div>
                                    ))}
                                </div>
                                <h4 className="resource-row-header">And requests these resources:</h4>
                                <div className="resource-row">
                                    {Object.entries(gameState.current_offer.requested_resources).map(([resource, count]) => (
                                        <div key={resource}>
                                            {resource}: {count}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div>No current offer</div>
                        )}
                    </div>

                    {/* Scrollable Trade History */}
                    <h3>Trade History</h3>
                    <div
                        className="trade-history"
                        ref={tradeHistoryRef} // Reference to scroll container
                        style={{
                            height: '200px',
                            overflowY: 'scroll',
                            border: '1px solid #ccc',
                            padding: '10px',
                            borderRadius: '8px',
                        }}
                    >
                        {gameState.trade_history.length > 0 ? (
                            gameState.trade_history.map((trade, index) => {
                                const offeredResources = Object.entries(trade.offered_resources)
                                    .map(([resource, count]) => `${count} ${resource}`)
                                    .join(", ");
                                const requestedResources = Object.entries(trade.requested_resources)
                                    .map(([resource, count]) => `${count} ${resource}`)
                                    .join(", ");

                                const tradeOutcomeClass = trade.outcome === "Accepted" ? 'accepted' : 'normal'; // Add class based on outcome
                                const tradeText = trade.outcome === "Accepted"
                                    ? `${gameState.player_names[trade.to_player]} accepted ${offeredResources} for ${requestedResources} from ${gameState.player_names[trade.from_player]}`
                                    : `${gameState.player_names[trade.from_player]} offered ${offeredResources} for ${requestedResources} to ${gameState.player_names[trade.to_player]}`;

                                return (
                                    <div key={index} className={`trade-history-entry ${tradeOutcomeClass}`} style={{ marginBottom: '10px' }}>
                                        <strong>Transaction {index + 1}: </strong>
                                        {tradeText}
                                    </div>
                                );
                            })
                        ) : (
                            <div>No trade history available.</div>
                        )}
                    </div>
                </div>
            );
        };


        const Negotiation = () => {
            console.log('Initializing Negotiation');
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
                <BaseGameContainer className="Negotiation-layout" gameState={gameState} renderGameInfo={renderNegotiationInfo}>
                    <div className="main-content">
                        <ResourceBoard gameState={gameState} />
                    </div>
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<Negotiation />);
        console.log('Negotiation components loaded');
        """
    
    def get_custom_css(self) -> str:
        """
        Get Negotiation-specific CSS code
        """
        return """
        .board-container {
    display: flex;
    justify-content: center;
    padding: 5px;
    background: #8B5D33; /* Oak color for the background */
    border-radius: 10px;
    width: 90%;
    margin: auto;
    box-sizing: border-box; /* Ensure padding/border doesn't cause overflow */
}

.game-board {
    display: flex;
    flex-direction: column; /* Stack player boards vertically */
    justify-content: center; /* Center the content vertically */
    width: 100%;
    background: #8B5D33; /* Oak color for the container */
    padding: 10px;
    border-radius: 10px;
}

.player-resources {
    width: 100%; /* Full width for each player board */
    padding: 15px;
    background-color: rgba(255, 255, 255, 0.7); /* Semi-transparent background */
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-sizing: border-box; /* Prevents overflow */
    margin-bottom: 10px; /* Space between the player boards */
}

h3 {
    text-align: center;
    color: #000;
    margin-bottom: 10px;
}

.resource-row {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    width: 100%;
    box-sizing: border-box; /* Ensure no overflow */
}

.resource-cell {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 10px;
}

.resource-img {
    width: 70px; /* Larger image */
    height: 70px; /* Larger image */
    object-fit: contain;
    margin-bottom: 5px;
}

.resource-count {
    font-size: 1.5em; /* Increase font size */
    font-weight: bold;
    color: #000000;
}

/* Inventory Value Table Styling */
.inventory-table-container {
    margin-top: 10px;
    width: 100%; /* Full width of player board */
    background-color: #5C4033;
    padding: 10px;
    border-radius: 8px;
    box-sizing: border-box; /* Prevent overflow */
}

.inventory-table-container table {
    width: 100%; /* Table width set to 100% of the container */
    border-collapse: collapse;
    box-sizing: border-box; /* Ensure padding/borders are accounted for */
}

.inventory-table-container th, .inventory-table-container td {
    padding: 6px 10px; /* Reduced padding for a tighter fit */
    text-align: center;
    border: 1px solid #ddd;
}

.inventory-table-container th {
    background-color: #8B5D33; /* Oak color for table header */
    color: white;
}

.inventory-table-container td {
    background-color: #C4A484;
}

.inventory-table-container td[style] {
    font-weight: bold;
}

/* Responsive Design */
@media (max-width: 500px) {
    .resource-row {
        flex-direction: column;
        align-items: center;
    }

    .resource-cell {
        margin: 10px 0;
    }

    .resource-img {
        width: 50px;
        height: 50px;
    }

    .resource-count {
        font-size: 1.2em;
    }

    .inventory-table-container {
        padding: 5px; /* Reduced padding on smaller screens */
    }

    .inventory-table-container td, .inventory-table-container th {
        font-size: 0.9em;
    }
}

.inventory-table {
    width: 100%; /* Ensure the table fills the width of the container */
    border-collapse: collapse;
}

.trade-history {
    background-color: #222d37;
}

.trade-history-entry {
    font-size: 0.9em; /* Smaller font size for condensed view */
    color: #fff;
}

.trade-history-entry span {
    font-weight: bold;
    color: #8B5D33; /* Oak color for the outcome */
}

.trade-history-entry.accepted {
    color: #39FF14; /* Green color for accepted trades */
}

.trade-history-entry.normal {
    color: #fff; /* Normal color for other trades */
}

/* Add some spacing between the trade history entries */
.trade-history-entry {
    margin-bottom: 5px;
}

.current-offer {
    height: 200px;
    overflow: auto;
    display: flex;
    flex-direction: column; /* Align children vertically */
    justify-content: center; /* Vertically center the content */
    align-items: center; /* Horizontally center the content */
    padding: 5px; /* Optional padding */
    border: 1px solid #ddd; /* Optional border */
    background-color: #f9f9f9; /* Optional background */
    border-radius: 8px; /* Optional rounded corners */
}

.resource-row-header {
    text-align: center;
    font-weight: bold; /* Optional, if you want to make the headers bold */
    margin-top: 10px; /* Optional, to add some spacing */
    margin-bottom: 10px; /* Optional, to add some spacing */
}


        """