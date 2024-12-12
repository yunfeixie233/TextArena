console.log('Script starting...');

function ChessBoard({ fen }) {
    console.log('Rendering ChessBoard with FEN:', fen);
    
    if (!fen) {
        console.log('No FEN provided');
        return <div className="board-container">Loading...</div>;
    }

    const renderSquare = (i) => {
        const file = i % 8;
        const rank = Math.floor(i / 8);
        const isLight = (file + rank) % 2 === 0;
        
        return (
            <div key={i} className={`square ${isLight ? 'light' : 'dark'}`}>
                {getPieceChar(fen, i)}
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

function getPieceChar(fen, squareIndex) {
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
                return <div style={{fontSize: '40px'}}>{getPieceSymbol(char)}</div>;
            }
            currentFile++;
        } else {
            currentFile += parseInt(char);
        }
        if (currentFile > file) break;
    }
    return null;
}

function getPieceSymbol(piece) {
    const symbols = {
        'k': '♔', 'q': '♕', 'r': '♖', 'b': '♗', 'n': '♘', 'p': '♙',
        'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟'
    };
    return symbols[piece];
}

function ChatHistory({ messages, playerNames }) {
    const messagesEndRef = React.useRef(null);

    React.useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    if (!messages || messages.length === 0) {
        return null;
    }

    return (
        <div className="chat-container">
            <h2>Game Conversation</h2>
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`chat-message ${msg.player_id === 0 ? 'white' : 'black'}`}>
                        <div className="player-name">
                            {playerNames[msg.player_id]}:
                        </div>
                        <div>{msg.message}</div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>
        </div>
    );
}

function ChessGame() {
    console.log('Rendering ChessGame');
    const [gameState, setGameState] = React.useState(null);
    const [connected, setConnected] = React.useState(false);
    const wsRef = React.useRef(null);

    React.useEffect(() => {
        console.log('ChessGame useEffect running');
        const connectWebSocket = () => {
            console.log('Connecting WebSocket...');
            wsRef.current = new WebSocket(`ws://${window.location.host}/ws`);
            
            wsRef.current.onopen = () => {
                console.log('WebSocket Connected');
                setConnected(true);
            };
            
            wsRef.current.onmessage = (event) => {
                try {
                    const state = JSON.parse(event.data);
                    console.log('Received state:', state);
                    if (state.fen) {
                        setGameState(state);
                    }
                } catch (e) {
                    console.error('Error parsing message:', e);
                }
            };
            
            wsRef.current.onclose = () => {
                console.log('WebSocket Disconnected');
                setConnected(false);
                setTimeout(connectWebSocket, 2000);
            };
        };
        
        connectWebSocket();
        return () => wsRef.current?.close();
    }, []);

    if (!gameState) {
        console.log('No game state yet');
        return <div>Loading game...</div>;
    }

    console.log('Rendering game with state:', gameState);
    return (
        <>
            <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
                {connected ? 'Connected' : 'Reconnecting...'}
            </div>
            <div className="game-container">
                <ChessBoard fen={gameState.fen} />
                <div className="info-container">
                    <h2>Game Info</h2>
                    <div className="status">
                        <div>Current Turn: {gameState.current_player}</div>
                        {gameState.is_check && <div>Check!</div>}
                        {gameState.is_checkmate && <div>Checkmate!</div>}
                        {gameState.is_stalemate && <div>Stalemate!</div>}
                        {gameState.is_insufficient_material && 
                            <div>Draw (Insufficient Material)</div>}
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
            </div>
            <ChatHistory 
                messages={gameState.chat_history} 
                playerNames={gameState.player_names}
            />
        </>
    );
}

console.log('Starting React render...');
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<ChessGame />);
console.log('React render complete');