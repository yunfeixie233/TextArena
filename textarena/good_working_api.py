import json, logging, requests, websockets
import ssl
import asyncio
from typing import List, Optional, Tuple, Dict, Any, Union
from urllib.parse import urlencode
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# Server URLs - Change these to match your server
WS_SERVER_URI = "ws://localhost:8000/ws"
HTTP_SERVER_URI = "http://localhost:8000"

# Environment ID mapping
NAME_TO_ID_DICT = {
    "Chess-v0": 0,
    "ConnectFour-v0": 1,
    "DontSayIt-v0": 3,
    "Battleship-v0": 5,
    "LiarsDice-v0": 6,
    "SimpleNegotiation-v0": 8,
    "Poker-v0": 9,
    "SpellingBee-v0": 10,
    "SpiteAndMalice-v0": 11,
    "Stratego-v0": 12,
    "Tak-v0": 13,
    "TruthAndDeception-v0": 14,
    "UltimateTicTacToe-v0": 15,
    "TicTacToe-v0": 35,
    "Breakthrough-v0": 37,
    "Checkers-v0": 38,
    "KuhnPoker-v0": 46,
    "LetterAuction-v0": 47,
    "Nim-v0": 50,
    "Othello-v0": 51,
    "PigDice-v0": 52,
    "Snake-v0": 69
}

class OnlineEnvWrapper:
    def __init__(self, env_ids: List[int], model_name: str, model_token: str):
        self.env_ids = env_ids
        self.model_name = model_name
        self.model_token = model_token
        self.websocket = None
        
        # The full observations are stored as a dictionary mapping player id -> list of (sender_id, message) tuples
        self.full_observations = {}
        
        # Game state tracking
        self.current_player_id = None
        self.current_observation = None
        self.game_over = False
        self.rewards = {}
        self.info = {}
        
        # Timeouts
        self.move_timeout = 180     # Move deadline in server
        
        # Message and action queues
        self.message_queue = asyncio.Queue()
        self.action_queue = asyncio.Queue()
        
        # State tracking
        self.in_game = False
        self.pending_action = False
        self.update_task = None  # Reference to the main update loop task
        
        # For compatibility
        DummyState = type("DummyState", (), {})
        self.state = DummyState()
        self.state.role_mapping = {0: "Player 0", 1: "Player 1", -1: "GAME"}

    async def _message_receiver(self):
        """Task to receive and queue messages from websocket."""
        try:
            while True:
                try:
                    message = await self.websocket.recv()
                    print(f"Received: {message[:100]}...")
                    await self.message_queue.put(message)
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed")
                    self.game_over = True
                    break
                except Exception as e:
                    print(f"Error receiving message: {e}")
                    break
        except Exception as e:
            print(f"Message receiver error: {e}")
            self.game_over = True

    async def _action_sender(self):
        """Task to send actions to the websocket."""
        try:
            while True:
                action = await self.action_queue.get()
                if action == "CLOSE":
                    break
                
                try:
                    action_msg = {"command": "action", "action": action}
                    await self.websocket.send(json.dumps(action_msg))
                    print(f"Sent action: {action[:100]}...")
                    self.pending_action = True
                except Exception as e:
                    print(f"Error sending action: {e}")
                
                self.action_queue.task_done()
        except Exception as e:
            print(f"Action sender error: {e}")
            self.game_over = True

    async def _ping_sender(self):
        """Task to send periodic pings to keep connection alive."""
        try:
            while not self.game_over:
                try:
                    await self.websocket.send(json.dumps({"command": "ping"}))
                    await asyncio.sleep(25)  # Send ping every 25 seconds
                except Exception as e:
                    print(f"Ping error: {e}")
                    break
        except Exception as e:
            print(f"Ping sender error: {e}")
            self.game_over = True

    async def connect(self):
        """Connect to server and queue for game."""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # For our implementation, we'll connect directly with the token
        ws_uri = f"{WS_SERVER_URI}?token={self.model_token}"
        print(f"Connecting to WebSocket: {ws_uri}")
        
        try:
            # Create WebSocket connection
            self.websocket = await websockets.connect(
                ws_uri,
                # ssl=ssl_context,  # Uncomment for HTTPS
                ping_interval=20,
                ping_timeout=60
            )
            
            # Start background tasks
            asyncio.create_task(self._message_receiver())
            asyncio.create_task(self._action_sender())
            asyncio.create_task(self._ping_sender())
            
            print("Connected to game server")
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    async def _process_message(self, message_str: str):
        """Process incoming WebSocket messages."""
        try:
            message = json.loads(message_str)
            command = message.get("command")
            
            if command == "observation":
                # Received game state - our turn to act
                observation = message.get("observation")
                player_id = message.get("player_id")
                
                print(f"Received observation for player {player_id}")
                self.current_player_id = player_id
                self.current_observation = observation
                self.full_observations[player_id] = observation
                self.pending_action = False
                self.in_game = True
                
            elif command == "game_over":
                # Game has completed
                print("Game over received")
                self.game_over = True
                outcome = message.get("outcome", "unknown")
                reason = message.get("reason", "No reason provided")
                
                # Extract reward info if available
                trueskill_change = message.get("trueskill_change", 0)
                if self.current_player_id is not None:
                    self.rewards[self.current_player_id] = trueskill_change
                
                self.info = {"reason": reason, "outcome": outcome}
                print(f"Game over: {outcome}, reason: {reason}")
                
            elif command == "timed_out":
                # Someone timed out
                timeout_msg = message.get("message", "Unknown timeout")
                print(f"Game timeout: {timeout_msg}")
                self.game_over = True
                self.info = {"reason": "timeout", "message": timeout_msg}
                
            elif command == "error":
                # Server error
                error_msg = message.get("message", "Unknown error")
                print(f"Server error: {error_msg}")
                self.info = {"error": error_msg}
                
            elif command == "action_ack":
                # Action acknowledged
                print("Action acknowledged by server")
                
            elif command == "pong":
                # Response to our ping
                pass
                
            elif command == "ping":
                # Server ping - respond with pong
                try:
                    await self.websocket.send(json.dumps({"command": "pong"}))
                except Exception as e:
                    print(f"Error sending pong: {e}")
                    
            elif command == "server_shutdown":
                # Server is shutting down
                print("Server is shutting down")
                self.game_over = True
                
            else:
                print(f"Unknown command received: {command}")
                
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {message_str}")
        except Exception as e:
            print(f"Error processing message: {e}")

    async def update_loop(self):
        """Main loop that processes messages."""
        while not self.game_over:
            try:
                # Process incoming messages with timeout
                try:
                    message = await asyncio.wait_for(self.message_queue.get(), timeout=self.move_timeout)
                    await self._process_message(message)
                except asyncio.TimeoutError:
                    print(f"Timeout while waiting for messages")
                    self.game_over = True
                    
            except Exception as e:
                print(f"Error in update loop: {e}")
                await asyncio.sleep(0.1)
                
        print("Update loop exiting")

    async def async_get_observation(self) -> Tuple[Optional[int], List]:
        """Get the current observation."""
        # If we already have an observation, return it
        if self.current_player_id is not None and self.current_observation:
            observation = self.current_observation
            player_id = self.current_player_id
            return player_id, observation
        
        # Otherwise, wait for an observation
        if not self.game_over:
            # Make sure we're not starting the update loop multiple times
            if self.update_task is None or self.update_task.done():
                self.update_task = asyncio.create_task(self.update_loop())
            
            try:
                # Wait until we get an observation or game ends
                start_time = asyncio.get_event_loop().time()
                
                while not self.game_over:
                    # Check if we have an observation
                    if self.current_player_id is not None and self.current_observation:
                        return self.current_player_id, self.current_observation
                    
                    await asyncio.sleep(0.1)
                    
                    # Check for timeout
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > self.move_timeout:
                        print("Timeout waiting for observation")
                        self.game_over = True
                        break
                        
            except Exception as e:
                print(f"Error waiting for observation: {e}")
                    
        # If game is over or we timed out
        return None, []

    def get_observation(self) -> Tuple[Optional[int], List]:
        """Synchronous wrapper for async_get_observation."""
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                new_loop = True
            else:
                new_loop = False
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            new_loop = True
            
        try:
            return loop.run_until_complete(self.async_get_observation())
        finally:
            if new_loop:
                loop.close()

    async def async_step(self, action: str):
        """Take an action in the game."""
        if self.game_over:
            return True, self.info
        
        # Queue action to be sent
        await self.action_queue.put(action)
        
        # Clear current observation - the key fix!
        # We need to clear this AFTER we successfully send the action
        # but we don't want to clear it until we've actually sent it
        await self.action_queue.join()  # Wait for action to be sent
        self.current_observation = None
        
        # Wait for response (new observation or game over)
        start_time = asyncio.get_event_loop().time()
        while not self.game_over and self.pending_action:
            await asyncio.sleep(0.1)
            
            # Check for timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.move_timeout:
                print("Timeout waiting for server response")
                self.game_over = True
                break
                
        return self.game_over, self.info

    def step(self, action: str):
        """Synchronous wrapper for async_step."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                new_loop = True
            else:
                new_loop = False
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            new_loop = True
            
        try:
            return loop.run_until_complete(self.async_step(action))
        finally:
            if new_loop:
                loop.close()

    async def async_reset(self, num_players=None, seed=None):
        """Connect to server and wait for game to start."""
        # Reset state
        self.current_player_id = None
        self.current_observation = None
        self.game_over = False
        self.rewards = {}
        self.info = {}
        self.full_observations = {}
        self.in_game = False
        self.update_task = None
        
        # Connect to server
        if not self.websocket:
            connected = await self.connect()
            if not connected:
                print("Failed to connect to server")
                return []
                
        # Wait for game to start and get initial observation
        self.update_task = asyncio.create_task(self.update_loop())
        
        try:
            # Wait until we either get an observation or the game ends
            start_time = asyncio.get_event_loop().time()
            while not self.game_over and not self.in_game:
                await asyncio.sleep(0.1)
                
                # Check if we have an observation
                if self.current_player_id is not None and self.current_observation:
                    self.in_game = True
                    return self.current_observation
                
                # Check for timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > self.move_timeout:
                    print("Timeout waiting for game to start")
                    break
                    
        except Exception as e:
            print(f"Error waiting for game start: {e}")
                
        # Return current observation or empty list
        return self.current_observation if self.current_observation else []

    def reset(self, num_players=None, seed=None):
        """Synchronous wrapper for async_reset."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                new_loop = True
            else:
                new_loop = False
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            new_loop = True
            
        try:
            return loop.run_until_complete(self.async_reset(num_players))
        finally:
            if new_loop:
                loop.close()

    async def async_close(self):
        """Clean up resources."""
        # Signal action sender to stop
        try:
            await self.action_queue.put("CLOSE")
        except:
            pass
            
        # Close websocket
        if self.websocket and not getattr(self.websocket, 'closed', True):
            try:
                await self.websocket.close()
            except:
                pass
            
        # Cancel update task if running
        if self.update_task and not self.update_task.done():
            try:
                self.update_task.cancel()
            except:
                pass
                
        return self.rewards

    def close(self):
        """Synchronous wrapper for async_close."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                new_loop = True
            else:
                new_loop = False
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            new_loop = True
            
        try:
            return loop.run_until_complete(self.async_close())
        finally:
            if new_loop:
                loop.close()


def make_online(
    env_id: Union[str, List[str]],
    model_name: str,
    model_token: Optional[str] = None,
    model_description: Optional[str] = None,
    email: Optional[str] = None,
) -> OnlineEnvWrapper:
    """Create and return the online environment wrapper.
    
    Args:
        env_id: The environment ID (e.g., "SpellingBee-v0") or a list of environment IDs
        model_name: The name of the model
        model_token: Optional token for the model (if already registered)
        model_description: Description of the model (required if model_token is None)
        email: Email address (required if model_token is None)
    
    Returns:
        An OnlineEnvWrapper instance
    """
    # Convert env_id to a list if it's a single string
    env_ids = [env_id] if isinstance(env_id, str) else env_id
    
    # Convert environment names to IDs
    env_ids_int = []
    if env_ids[0] == "all":
        env_ids_int = list(NAME_TO_ID_DICT.values())
    else:
        for env_name in env_ids:
            if env_name in NAME_TO_ID_DICT:
                env_ids_int.append(NAME_TO_ID_DICT[env_name])
            else:
                raise ValueError(f"Environment {env_name} not recognized")
    
    # Generate token if not provided
    if model_token is None:
        if model_description is None or email is None:
            raise ValueError("Provide model_description and email if model_token is not given")
            
        # Create a simple token based on email and model name
        import hashlib
        import uuid
        
        # For testing, we'll use a UUID as the token which is more compatible with the server
        model_token = str(uuid.uuid4())
        print(f"Generated token: {model_token}")

    # For testing - initializing the game isn't needed here
    # The client code should just connect to the websocket
    # The initialization is handled separately before running the clients
    # For example:
    # curl -X POST http://localhost:8000/initialize -H "Content-Type: application/json" -d '{"environment_id": 3, "env_id": "DontSayIt-v0", "tokens": ["token1", "token2"]}'
    # Then start two clients with those tokens
    
    # Print instructions for testing
    print("NOTE: To test properly, you need to:")
    print("1. Initialize the game with two tokens:")
    print(f'   curl -X POST {HTTP_SERVER_URI}/initialize -H "Content-Type: application/json" -d \'{{"environment_id": {env_ids_int[0]}, "env_id": "env-name", "tokens": ["{model_token}", "second-player-token"]}}\'')
    print("2. Run two instances of this client with the two tokens")
    print(f"   This instance is using token: {model_token}")
        
    return OnlineEnvWrapper(env_ids_int, model_name, model_token)