from textarena.wrappers.RenderWrappers.PrettyRenderWrapper.base import BaseRenderer
import shutil
from pathlib import Path

class PokerRenderer(BaseRenderer):
    """
    Renderer for the Poker environment
    """
    def __init__(self, env, player_names=None, port=8000, host="127.0.0.1"):
        super().__init__(env, player_names, port, host)
        self._setup_card_images()
        
    def _setup_card_images(self):
        """
        Copy the Poker piece images to the render directory
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
        Get the current state of the Poker environment
        """
        try:
            return {
                "current_player": self.env.state.current_player_id if self.env.state else "Unknown",
                "player_hands": self.env.state.game_state["player_hands"] if self.env.state else {},
                "visible_community_cards": self.env.state.game_state["visible_community_cards"] if self.env.state else [],
                "player_chips": self.env.state.game_state["player_chips"] if self.env.state else {},
                "player_bets": self.env.state.game_state["player_bets"] if self.env.state else {},
                "round": self.env.state.game_state["round"] if self.env.state else 0,
                "num_rounds": self.env.num_rounds if self.env else 0,
                "betting_round": self.env.state.game_state["betting_round"] if self.env.state else 0,
                "pot": self.env.state.game_state["pot"] if self.env.state else 0,
                "round_turn": self.env.state.game_state["round_turn"] if self.env.state else 0,
                "folded_players": list(self.env.state.game_state["folded_players"]) if self.env.state else [],
                "all_in_players": list(self.env.state.game_state["all_in_players"]) if self.env.state else [],
                "checked_players": list(self.env.state.game_state["checked_players"]) if self.env.state else [],
            }
        except Exception as e:
            print(f"Error getting state: {e}")
            return {
                "current_player": "Unknown",
                "player_hands": {},
                "visible_community_cards": [],
                "player_chips": {},
                "player_bets": {},
                "round": 0,
                "num_rounds": 0,
                "betting_round": 0,
                "pot": 0,
                "round_turn": 0,
                "folded_players": [],
                "all_in_players": [],
                "checked_players": [],
            }
        
    def get_custom_js(self) -> str:
        """
        Get the custom JavaScript for the Poker environment
        """
        return """
        console.log("Loading Poker components");

        // Component to display a single card
        const CardCell = React.memo(({ rank, suit }) => {

            const filePath = `/static/pieces/${rank}_of_${suit}.png`;
            return (
                <div className="card-cell">
                    <img
                        src={filePath}
                        alt={`${rank} of ${suit}`}
                        className="card-img"
                    />
                </div>
            );
        });

        // Component to display each player's hand, chips, and bets
        const PlayerResources = ({ playerName, playerHand, playerChips, playerBet, status }) => (
            <div className="player-resources">
                <div className="cards-section">
                    <h3 className="player-header">{playerName}</h3>
                    <div className="player-info-inline">
                        <p>Chips: <span className="info-value">{playerChips}</span> | Bet: <span className="info-value">{playerBet}</span> </p>
                        <p className="player-status">{status}</p> {/* Moved status here */}
                    </div>
                    <div className="card-row">
                        {playerHand.map((card, index) => (
                            <CardCell key={index} rank={card.rank} suit={card.suit} />
                        ))}
                    </div>
                </div>
            </div>
        );


        // Component to display the community cards
        const CommunityCards = ({ communityCards }) => (
            <div className="community-cards">
                <div className="community-header">
                    <h3>Table Cards</h3>
                </div>
                <div className="card-row community-card-row">
                    {communityCards.length > 0 ? (
                        communityCards.map((card, index) => (
                            <CardCell key={index} rank={card.rank} suit={card.suit} />
                        ))
                    ) : (
                        <p className="no-card-message">No Cards on the Board.</p>
                    )}
                </div>
            </div>
        );



        // Poker Board
        const PokerBoard = ({ gameState }) => (
            <div className="board-container">
                {/* Player 1 Section */}
                <div className="player-section">
                    <PlayerResources
                        playerName={gameState.player_names[0]}
                        playerHand={gameState.player_hands[0]}
                        playerChips={gameState.player_chips[0]}
                        playerBet={gameState.player_bets[0]}
                        status={
                            gameState.folded_players.includes(0)  // Check if player 0 is folded
                                ? "Folded"
                                : gameState.all_in_players.includes(0) // Check if player 0 is all-in
                                ? "All-In"
                                : gameState.checked_players.includes(0) // Check if player 0 is checked
                                ? "Checked"
                                : "Playing"
                        }
                    />
                </div>

                {/* Community Cards Section */}
                <div className="community-cards-section">
                    <CommunityCards communityCards={gameState.visible_community_cards} />
                </div>

                {/* Player 2 Section */}
                <div className="player-section">
                    <PlayerResources
                        playerName={gameState.player_names[1]}
                        playerHand={gameState.player_hands[1]}
                        playerChips={gameState.player_chips[1]}
                        playerBet={gameState.player_bets[1]}
                        status={
                            gameState.folded_players.includes(1)  // Check if player 1 is folded
                                ? "Folded"
                                : gameState.all_in_players.includes(1) // Check if player 1 is all-in
                                ? "All-In"
                                : gameState.checked_players.includes(1) // Check if player 1 is checked
                                ? "Checked"
                                : "Playing"
                        }
                    />
                </div>
            </div>
        );


        const renderPokerInfo = (gameState) => {
            const currentPlayerName = gameState.player_names[gameState.current_player];

            return (
                <div>
                    <h3>Current Turn: {currentPlayerName}</h3>
                    {/* General Game Info */}
                    <div className="game-info">
                        <p>Round: <span className="game-info-value">{gameState.round} of {gameState.num_rounds}</span></p>
                        <p>Betting Round: <span className="game-info-value">{gameState.betting_round}</span></p>
                        <p>Pot: <span className="game-info-value">{gameState.pot} Chips</span></p>
                        <p>Turn: <span className="game-info-value">{gameState.round_turn}</span></p>
                    </div>
                </div>
            );
        };


        const Poker = () => {
            console.log('Initializing Poker');
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
                <BaseGameContainer className="Poker-layout" gameState={gameState} renderGameInfo={renderPokerInfo}>
                    <div className="main-content">
                        <PokerBoard gameState={gameState} />
                    </div>
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<Poker />);
        console.log('Poker components loaded');
        """

    def get_custom_css(self) -> str:
        """
        Get Negotiation-specific CSS code
        """
        return """
        /* General board styling */
.board-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(180deg, #0b6623 0%, #054d19 100%);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
    width: 600px; /* Fixed width */
    margin: auto;
    min-height: 500px; /* Adjusted to reduce overall height */
    border: 4px solid #2b2b2b;
}

/* Player and table card sections */
.player-section {
    border: 2px solid white; /* White boundary */
    border-radius: 10px; /* Rounded corners */
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 10px; /* Reduced padding for compact layout */
    margin: 0px 0; /* Reduced spacing between sections */
    width: 400px; /* Fixed width */
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
}

/* Player Header */
.player-header {
    font-family: 'Roboto', sans-serif;
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    margin: 5px 0; /* Reduced margin for less vertical space */
    text-align: center; /* Center align the title */
}

/* Table Cards Section */
.table-cards-section {
    display: flex;
    flex-direction: column; /* Stack header and cards vertically */
    align-items: center; /* Center align content horizontally */
    justify-content: flex-start; /* Fix the header to the top */
    text-align: center;
    background: rgba(255, 255, 255, 0.05); /* Subtle background for depth */
    border-radius: 15px;
    padding: 10px; /* Padding around the content */
    margin: 10px 0; /* Reduced spacing for compact layout */
    width: 400px; /* Fixed width */
    height: 200px; /* Fixed height to ensure stability */
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
    position: relative; /* Use relative positioning for inner elements */
}

/* Table Cards Header */
.table-cards-header {
    font-family: 'Roboto', sans-serif;
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    margin-bottom: 10px; /* Consistent spacing below the header */
    position: absolute; /* Position the header at the top of the container */
    top: 10px; /* Distance from the top of the container */
    left: 50%; /* Center the header horizontally */
    transform: translateX(-50%); /* Adjust for centering */
}

/* Community Cards Section */
.community-cards-section {
    display: flex;
    flex-direction: column;
    align-items: center
    justify-content: flex-start; /* Ensures content starts from the top */
    text-align: center;
    border-radius: 15px;
    padding: 10px;
    margin: 10px 0; /* Reduced spacing for compact layout */
    width: 430px; /* Fixed width */
    height: 150px; /* Fixed height */
    position: relative;
}

/* Community Cards Header */
.community-header {
    position: absolute; /* Make the header fixed within the section */
    top: 10px; /* Position at the top of the section */
    left: 50%; /* Center align horizontally */
    transform: translateX(-50%); /* Adjust for proper centering */
    width: 100%; /* Take the full width for consistency */
    text-align: center;
}

.community-header h3 {
    font-family: 'Roboto', sans-serif;
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    margin: 0; /* Remove default margin */
}

/* Player Cards Section */
.cards-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    border-radius: 10px;
    padding: 5px; /* Reduced padding to make the layout more compact */
    width: 400px; /* Fixed width for player cards */
}

/* Card Row */
.card-row {
    display: flex;
    justify-content: center; /* Center align cards */
    gap: 10px; /* Consistent spacing between cards */
    align-items: center; /* Vertically align cards */
    margin-top: 30px; /* Ensure cards are below the header */
    height: 100%; /* Fill the remaining space below the header */
}

.community-card-row {
    justify-content: flex-start; /* Align table cards to the left */
}

.community-card-row p {
    justify-content: center; /* Center the message */
}


/* Individual card styling */
.card-cell {
    position: relative;
    margin: 0px 5px;
}

.card-img {
    width: 70px; /* Consistent size for player and table cards */
    height: 100px;
    border-radius: 4px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.5);
    transition: transform 0.2s, box-shadow 0.2s;
}

.card-img:hover {
    transform: scale(1.1);
    box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.7);
}

/* Player info container */
.player-info {
    margin: 10px 0;
    font-size: 0.9rem;
    color: white;
    text-align: center; /* Align chips and bet in the center */
}

/* Player info container */
.player-info-inline {
    display: flex;
    flex-direction: column; /* Stack items vertically */
    align-items: center; /* Center the text */
    gap: 2px; /* Reduce the gap between the lines */
    margin-bottom: 0px; /* Reduce spacing between this and the cards */
    font-size: 0.9rem; /* Keep the font size concise */
}

/* General text adjustments */
.player-info-inline p {
    margin: 0; /* Remove extra margin around paragraphs */
    padding: 0; /* Remove extra padding */
}

/* Highlight important values */
.info-value {
    font-weight: bold;
    color: lightgreen;
}

/* Player status */
.player-status {
    font-size: 0.85rem; /* Slightly smaller text for status */
    font-weight: bold;
    color: lightblue;
    background-color: rgba(0, 0, 0, 0.5); /* Subtle background for emphasis */
    padding: 2px 5px; /* Compact padding */
    border-radius: 3px; /* Rounded corners for a sleek look */
    margin-top: 3px; /* Adjust spacing from previous line */
}

.no-card-message {
    font-size: 16px; /* Keep the text size consistent */
    color: white; /* Maintain contrast with the background */
    text-align: center; /* Center-align the text */
    width: 100%; /* Ensure the message spans the full width of the container */
    font-style: italic; /* Optional: Retain the poker-themed styling */
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .board-container {
        width: 90%;
    }

    .player-section,
    .table-cards-section {
        width: 90%;
    }

    .card-img {
        width: 60px;
        height: 80px;
    }
}
        """
