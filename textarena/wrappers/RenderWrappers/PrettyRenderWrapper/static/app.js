console.log('Loading base components...');

// Base components
function EndGameOverlay({ endGameState, onClose }) {
    return (
        <div className="end-game-overlay" onClick={(e) => {
            if (e.target.className === 'end-game-overlay') {
                onClose();
            }
        }}>
            <div className="end-game-content">
                <button className="close-button" onClick={onClose}>×</button>
                <h1>Game Over</h1>
                <p className="winner-text">{endGameState.winner_text}</p>
                <p className="reason-text">{endGameState.reason}</p>
            </div>
        </div>
    );
}

const ChatHistory = ({ chatHistory, currentPlayerId, messageFunction }) => {
    const chatContainerRef = React.useRef(null);

    // Scroll to the bottom when chat updates
    React.useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [chatHistory]);


    return (
        <div className="chat-container">
            <h2>Game Chat</h2>
            <div className="chat-messages" ref={chatContainerRef}>
                {chatHistory.map((msg, i) => {
                    const isCurrentPlayer = msg.player_id === currentPlayerId;
                    const messageContent = messageFunction 
                        ? messageFunction(msg.message)  // Apply messageFunction if passed
                        : msg.message; // Use default if not passed

                    return (
                        <div
                            key={i}
                            className={`chat-bubble ${isCurrentPlayer ? "right" : "left"}`}
                            style={{ backgroundColor: msg.color }}
                        >
                            <div className="player-name">{msg.player_name}</div>
                            <div className="message-content" dangerouslySetInnerHTML={{ __html: messageContent }} />
                            <div className="timestamp">{msg.timestamp}</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};



const BaseGameContainer = ({ children, gameState, renderGameInfo, messageFunction }) => {
    const [showEndGame, setShowEndGame] = React.useState(false);

    React.useEffect(() => {
        if (gameState.end_game_state) {
            setShowEndGame(true);
        }
    }, [gameState.end_game_state]);

    return (
        <div className="page-container">
            <header className="main-header">
                <h1 className="textarena-title">
                    <a href="https://github.com/LeonGuertler/TextArena" target="_blank" rel="noopener noreferrer">
                        <img 
                            src="http://127.0.0.1:8000/static/assets/textarena-logo1.png" 
                            alt="TextArena Logo"
                            style={{ cursor: "pointer" }} 
                        />
                    </a>
                </h1>
                <h2 className="game-env-id">
                        {gameState.env_id ? `${gameState.env_id}` : "No Environment ID"} ({gameState.num_player_class} Edition)
                </h2>
                <a href={gameState.github_link}
                   className="github-link" 
                   target="_blank" 
                   rel="noopener noreferrer">
                    <img
                        src="http://127.0.0.1:8000/static/assets/github-mark-white.png"
                        alt="GitHub Logo"
                        className="github-logo"
                    />
                    View on GitHub
                </a>
            </header>

            <div className="game-instructions-layout">
                <h2 className="game-gameplay-header">Gameplay Instructions</h2>
                    <div className="game-gameplay-container">
                        <div className="game-gameplay-content">
                            <div className="game-desc" dangerouslySetInnerHTML={{ __html: gameState.gameplay_instructions }}></div>
                        </div>
                    </div>
            </div>

            <div className="game-layout">
                {/* Main children components */}
                <div className="game-main-content">
                    {children}
                </div>

                {/* Game Info Section */}
                <div className="game-info-wrapper">
                    <h2 className="game-info-header">Game Status</h2>
                    <div className="game-info-container">
                        <div className="game-info-content">
                            {renderGameInfo && renderGameInfo(gameState)}
                        </div>
                    </div>
                </div>
            </div>

            {/* End Game Overlay */}
            {gameState.end_game_state && showEndGame && 
                <EndGameOverlay 
                    endGameState={gameState.end_game_state} 
                    onClose={() => setShowEndGame(false)}
                />
            }

            {/* Chat History */}
            {gameState.chat_history && (
                <ChatHistory chatHistory={gameState.chat_history} messageFunction={messageFunction}/>
            )}
        </div>
    );
};

console.log('Base components loaded');