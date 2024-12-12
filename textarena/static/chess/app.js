
        function ChessGame() {
            const [gameState, setGameState] = React.useState(null);
            
            React.useEffect(() => {
                const ws = new WebSocket(`ws://${window.location.host}/ws`);
                ws.onmessage = (event) => {
                    const state = JSON.parse(event.data);
                    setGameState(state);
                };
                return () => ws.close();
            }, []);

            if (!gameState) return <div>Loading...</div>;

            return (
                <div className="game-container">
                    <div className="main-content">
                        <ChessBoard fen={gameState.fen} />
                        <GameInfo gameState={gameState} />
                    </div>
                    <ChatHistory gameState={gameState} />
                </div>
            );
        }

        function ChessBoard({ fen }) {
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
        }

        function getPiece(fen, squareIndex) {
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
                                src={`/static/chess/pieces/${char}.png`}
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
        }

        function GameInfo({ gameState }) {
            return (
                <div className="info-container">
                    <h2>Game Status</h2>
                    <div>Current Turn: {gameState.current_player}</div>
                    {gameState.is_check && <div className="text-red-500">Check!</div>}
                    {gameState.is_checkmate && <div className="text-red-500">Checkmate!</div>}
                    {gameState.is_stalemate && <div className="text-yellow-500">Stalemate</div>}
                    
                    <h3>Players</h3>
                    <div>
                        {Object.entries(gameState.player_names).map(([id, name]) => (
                            <div key={id} className={id === '0' ? 'white-player' : 'black-player'}>
                                {name} ({id === '0' ? 'White' : 'Black'})
                            </div>
                        ))}
                    </div>
                    
                    <h3>Move History</h3>
                    <div className="move-history">
                        {gameState.move_stack.map((move, i) => (
                            <span key={i} style={{marginRight: '10px'}}>
                                {i % 2 === 0 ? `${Math.floor(i/2) + 1}. ` : ''}{move}
                            </span>
                        ))}
                    </div>
                </div>
            );
        }

        function ChatHistory({ gameState }) {
            const messagesEndRef = React.useRef(null);
            
            React.useEffect(() => {
                messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
            }, [gameState.chat_history]);

            return (
                <div className="chat-container">
                    <h2>Game Chat</h2>
                    <div className="chat-messages">
                        {gameState.chat_history.map((msg, i) => (
                            <div key={i} className="chat-message">
                                <span className={
                                    msg.player_id === -1 ? 'game-message' :
                                    msg.player_id === 0 ? 'white-player' : 'black-player'
                                }>
                                    {msg.player_id === -1 ? 'Game' : gameState.player_names[msg.player_id]}:
                                </span>
                                <div>{msg.message}</div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </div>
            );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<ChessGame />);
        