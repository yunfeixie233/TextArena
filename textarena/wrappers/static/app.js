
function GameUI({ gameState }) {
    const { fen, chat_history, player_names, current_player, is_check, is_checkmate, 
            is_stalemate, is_insufficient_material, move_stack } = gameState;

    return (
        <div>
            <div className="game-container">
                <ChessBoard fen={fen} />
                <div className="info-container">
                    <h2>Game Status</h2>
                    <div>
                        <p>Current Turn: {current_player}</p>
                        {is_check && <p className="text-red-500">Check!</p>}
                        {is_checkmate && <p className="text-red-500">Checkmate!</p>}
                        {is_stalemate && <p className="text-yellow-500">Stalemate</p>}
                        {is_insufficient_material && 
                            <p className="text-yellow-500">Draw (Insufficient Material)</p>}
                    </div>
                    
                    <h3>Players</h3>
                    <div>
                        {Object.entries(player_names).map(([id, name]) => (
                            <div key={id}>
                                {name} ({id === '0' ? 'White' : 'Black'})
                            </div>
                        ))}
                    </div>
                    
                    <h3>Move History</h3>
                    <div className="move-history">
                        {move_stack.map((move, i) => (
                            <span key={i} style={{marginRight: '10px'}}>
                                {i % 2 === 0 ? `${Math.floor(i/2) + 1}. ` : ''}{move}
                            </span>
                        ))}
                    </div>
                </div>
            </div>
            <ChatHistory messages={chat_history} playerNames={player_names} />
        </div>
    );
}

function ChessBoard({ fen }) {
    if (!fen) return <div className="board-container">Loading...</div>;

    const renderSquare = (i) => {
        const file = i % 8;
        const rank = Math.floor(i / 8);
        const isLight = (file + rank) % 2 === 0;
        const piece = getPiece(fen, i);
        
        return (
            <div key={i} className={`square ${isLight ? 'light' : 'dark'}`}>
                {piece && <img 
                    src={`/static/pieces/${piece}.png`}
                    alt={piece}
                    className="piece-img"
                />}
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
                return char;
            }
            currentFile++;
        } else {
            currentFile += parseInt(char);
        }
        if (currentFile > file) break;
    }
    return null;
}

function ChatHistory({ messages, playerNames }) {
    const messagesEndRef = React.useRef(null);
    
    React.useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    if (!messages || messages.length === 0) return null;

    return (
        <div className="chat-container">
            <h2>Game Conversation</h2>
            <div className="chat-messages">
                {messages.map((msg, index) => {
                    const isGameMessage = msg.player_id === -1;
                    const className = msg.player_id === 0 ? 'white' : 'black';
                    return (
                        <div key={index} className={`chat-message ${className}`}>
                            <div className="player-name">
                                {isGameMessage ? 'Game' : playerNames[msg.player_id]}:
                            </div>
                            <div>{msg.message}</div>
                        </div>
                    );
                })}
                <div ref={messagesEndRef} />
            </div>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<GameUI gameState={window.initialGameState || {
    fen: '',
    chat_history: [],
    player_names: {},
    current_player: '',
    move_stack: []
}} />);
