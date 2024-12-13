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

const BaseGameContainer = ({ children, gameState }) => {
    const [showEndGame, setShowEndGame] = React.useState(true);
    
    React.useEffect(() => {
        if (gameState.end_game_state) {
            setShowEndGame(true);
        }
    }, [gameState.end_game_state]);

    return (
        <div className="page-container">
            <header className="main-header">
                <h1 className="title">TextArena</h1>
                <a href="https://github.com/LeonGuertler/TextArena" 
                   className="github-link" 
                   target="_blank" 
                   rel="noopener noreferrer">
                    View on GitHub
                </a>
            </header>
            <div className="game-container">
                {children}
                {gameState.end_game_state && showEndGame && 
                    <EndGameOverlay 
                        endGameState={gameState.end_game_state} 
                        onClose={() => setShowEndGame(false)}
                    />
                }
            </div>
        </div>
    );
};

console.log('Base components loaded');