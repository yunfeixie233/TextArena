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

// Game-specific components

        console.log('Loading chess components...');

        // Chess components
        const ChessBoard = ({ fen }) => {
            const renderSquare = (i) => {
                const file = i % 8;
                const rank = Math.floor(i / 8);
                const isLight = (file + rank) % 2 === 0;
                
                return (
                    <div key={i} className={`square ${isLight ? 'light' : 'dark'}`}>
                        {getPiece(fen, i)}
                    </div>
                );
            };

            return (
                <div className="board-container">
                    <div className="chess-board">
                        {[...Array(64)].map((_, i) => renderSquare(i))}
                    </div>
                </div>
            );
        };

        const getPiece = (fen, squareIndex) => {
            const [position] = fen.split(' ');
            const rows = position.split('/');
            const rank = Math.floor(squareIndex / 8);
            const file = squareIndex % 8;
            
            let currentFile = 0;
            const row = rows[7 - rank];
            
            for (let i = 0; i < row.length; i++) {
                const char = row[i];
                if (isNaN(char)) {
                    if (currentFile === file) {
                        return (
                            <img 
                                src={`/static/pieces/${char}.png`}
                                alt={char}
                                className="piece-img"
                            />
                        );
                    }
                    currentFile++;
                } else {
                    currentFile += parseInt(char);
                }
                if (currentFile > file) break;
            }
            return null;
        };

        function GameInfo({ gameState }) {
            const moveHistoryRef = React.useRef(null);
            
            React.useEffect(() => {
                if (moveHistoryRef.current) {
                    moveHistoryRef.current.scrollTop = moveHistoryRef.current.scrollHeight;
                }
            }, [gameState.move_stack]);

            // Group moves into pairs (white and black)
            const moveGroups = [];
            for (let i = 0; i < gameState.move_stack.length; i += 2) {
                moveGroups.push({
                    number: Math.floor(i/2) + 1,
                    white: gameState.move_stack[i],
                    black: gameState.move_stack[i + 1]
                });
            }

            return (
                <div className="info-container">
                    <h2>Game Status</h2>
                    <div className="status">
                        <div>Current Turn: {gameState.current_player}</div>
                        {gameState.is_check && <div className="alert">Check!</div>}
                        {gameState.is_checkmate && <div className="alert">Checkmate!</div>}
                        {gameState.is_stalemate && <div className="alert">Stalemate</div>}
                    </div>
                    
                    <h3>Players</h3>
                    <div className="players">
                        {Object.entries(gameState.player_names).map(([id, name]) => (
                            <div key={id} className={id === '0' ? 'white-player' : 'black-player'}>
                                {name} ({id === '0' ? 'White' : 'Black'})
                            </div>
                        ))}
                    </div>
                    
                    <h3>Move History</h3>
                    <div className="move-history" ref={moveHistoryRef}>
                        {moveGroups.map((group, i) => (
                            <div key={i} className="move-pair">
                                <span className="move-number">{group.number}.</span>
                                <span className="move white">{group.white}</span>
                                {group.black && <span className="move black">{group.black}</span>}
                            </div>
                        ))}
                    </div>
                </div>
            );
        }

        const ChatHistory = ({ gameState }) => {
            const messagesEndRef = React.useRef(null);
            
            React.useEffect(() => {
                messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
            }, [gameState.chat_history]);

            return (
                <div className="chat-container">
                    <h2>Game Chat</h2>
                    <div className="chat-messages">
                        {gameState.chat_history.map((msg, i) => (
                            <div key={i} className={`chat-message ${msg.player_id === 0 ? 'white' : 'black'}`}>
                                <div className="player-name">
                                    {gameState.player_names[msg.player_id]}:
                                </div>
                                <div>{msg.message}</div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </div>
            );
        };

        // Main app
        const ChessGame = () => {
            console.log('Initializing ChessGame');
            const [gameState, setGameState] = React.useState(null);
            
            React.useEffect(() => {
                const ws = new WebSocket(`ws://${window.location.host}/ws`);
                ws.onopen = () => console.log('WebSocket connected');
                ws.onmessage = (event) => {
                    const state = JSON.parse(event.data);
                    console.log('Received state:', state);
                    setGameState(state);
                };
                return () => ws.close();
            }, []);

            if (!gameState) {
                console.log('Waiting for game state...');
                return <div>Loading game state...</div>;
            }

            return (
                <BaseGameContainer gameState={gameState}>
                    <div className="chess-layout">
                        <div className="main-content">
                            <ChessBoard fen={gameState.fen} />
                            <GameInfo gameState={gameState} />
                        </div>
                        <ChatHistory gameState={gameState} />
                    </div>
                </BaseGameContainer>
            );
        };

        // Initialize the app
        console.log('Initializing React app');
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<ChessGame />);
        console.log('Chess components loaded');
        