import React, { useState, useEffect, useRef } from 'react';

// Base wrapper component that handles common functionality
function GameUI({ children }) {
  const [gameState, setGameState] = useState(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(`ws://${window.location.host}/ws`);
      wsRef.current = ws;
      
      ws.onopen = () => setConnected(true);
      
      ws.onmessage = (event) => {
        try {
          const state = JSON.parse(event.data);
          setGameState(state);
        } catch (e) {
          console.error('Error parsing message:', e);
        }
      };
      
      ws.onclose = () => {
        setConnected(false);
        setTimeout(connectWebSocket, 2000);
      };
    };
    
    connectWebSocket();
    return () => wsRef.current?.close();
  }, []);

  if (!gameState) {
    return <div className="text-white p-4">Loading game...</div>;
  }

  return (
    <div className="min-h-screen p-4">
      {/* Connection status */}
      <div 
        className={`fixed top-4 right-4 px-3 py-1 rounded text-sm ${
          connected ? 'bg-green-600' : 'bg-red-600'
        }`}
      >
        {connected ? 'Connected' : 'Reconnecting...'}
      </div>

      {/* Game-specific content */}
      <div className="mb-8">
        {React.cloneElement(children, { gameState })}
      </div>
      
      {/* Chat section */}
      <ChatHistory 
        messages={gameState.chat_history || []}
        playerNames={gameState.player_names || {}}
      />
    </div>
  );
}

function ChatHistory({ messages, playerNames }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (!messages || messages.length === 0) {
    return null;
  }

  const getMessageColor = (playerId) => {
    if (playerId === -1) return 'text-blue-400';  // Game messages
    return playerId === 0 ? 'text-white' : 'text-neutral-400';  // Players
  };

  return (
    <div className="bg-neutral-800 p-5 rounded-lg max-w-7xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Game Chat</h2>
      <div className="bg-neutral-900 p-4 rounded-lg h-[300px] overflow-y-auto">
        {messages.map((msg, index) => (
          <div key={index} className="mb-4 p-3 bg-neutral-800 rounded">
            <div className={`font-bold mb-1 ${getMessageColor(msg.player_id)}`}>
              {msg.player_id === -1 ? 'Game' : playerNames[msg.player_id]}:
            </div>
            <div>{msg.message}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default GameUI;