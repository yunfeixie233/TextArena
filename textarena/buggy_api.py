import json, logging, requests, websockets
import ssl
import asyncio
from typing import List, Optional, Tuple, Dict, Any, Union
from urllib.parse import urlencode
import warnings
from urllib3.exceptions import InsecureRequestWarning
import aiohttp  # Added for async HTTP requests
import logging
import traceback

# Set up logging with timestamps
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Suppress SSL warnings
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# Constants
WS_SERVER_URI = "ws://54.179.78.11:8000/ws"  # Matchmaking server
HTTP_SERVER_URI = "http://54.179.78.11:8000"

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
        self.websocket = None  # Matchmaking WebSocket
        self.game_websocket = None  # Game server WebSocket
        
        self.full_observations: Dict[int, List[Tuple[int, str]]] = {}
        self.current_player_id = None
        self.current_observation = None
        self.game_over = False
        self.rewards = {}
        self.info = {}
        
        self.queue_timeout = 1800  # 30 minutes for matchmaking
        self.game_timeout = 300    # 5 minutes for game moves
        
        self.message_queue = asyncio.Queue()
        self.action_queue = asyncio.Queue()
        
        self.in_game = False
        self.waiting_for_action_response = False
        self.connection_established = False
        
        DummyState = type("DummyState", (), {})
        self.state = DummyState()
        self.state.role_mapping = {0: "Player 0", 1: "Player 1", -1: "GAME"}

    async def _message_receiver(self, websocket, queue_label: str):
        """Background task to receive messages from a websocket."""
        try:
            logging.info(f"{queue_label} message receiver started")
            while True:
                try:
                    logging.debug(f"Waiting to receive {queue_label} message...")
                    message = await websocket.recv()
                    logging.info(f"Received {queue_label} message: {message[:100]}...")
                    await self.message_queue.put((queue_label, message))
                except websockets.exceptions.ConnectionClosedOK:
                    logging.warning(f"{queue_label} closed normally")
                    break
                except websockets.exceptions.ConnectionClosed as e:
                    logging.error(f"{queue_label} connection closed unexpectedly: {e}")
                    logging.error(f"Close code: {e.code}, reason: {e.reason}")
                    break
                except Exception as e:
                    logging.error(f"Error receiving {queue_label} message: {e}")
                    logging.error(traceback.format_exc())
                    break
        except Exception as e:
            if not self.game_over:
                logging.error(f"{queue_label} receiver error: {e}")
                logging.error(traceback.format_exc())

    async def _action_sender(self, websocket):
        try:
            logging.info("Action sender started")
            while True:
                logging.debug("Waiting for action...")
                action = await self.action_queue.get()
                if action == "CLOSE":
                    logging.info("Action sender received close signal")
                    break
                
                if self.game_over:
                    logging.warning("Game is already over, not sending action")
                    self.action_queue.task_done()
                    continue
                    
                try:
                    logging.info(f"Preparing to send action: {action}")
                    action_msg = {"command": "action", "action": action}
                    
                    # Safety check websocket state - different versions have different APIs
                    try:
                        if hasattr(websocket, 'closed') and websocket.closed:
                            logging.warning("WebSocket is already closed, cannot send action")
                            self.game_over = True
                            self.info = {"error": "WebSocket is closed"}
                            break
                    except Exception as e:
                        # Ignore any errors checking websocket state
                        logging.debug(f"Error checking websocket state: {e}")
                    
                    # Send with Try-Except for each step
                    try:
                        json_payload = json.dumps(action_msg)
                        logging.debug(f"JSON payload created: {json_payload[:100]}...")
                    except Exception as e:
                        logging.error(f"Error creating JSON payload: {e}")
                        raise
                    
                    try:
                        logging.debug("About to send WebSocket message")
                        await websocket.send(json_payload)
                        logging.info(f"Action sent successfully to server")
                    except Exception as e:
                        logging.error(f"Error during websocket.send: {e}")
                        logging.error(traceback.format_exc())
                        raise
                    
                    self.waiting_for_action_response = True
                    logging.debug("Set waiting_for_action_response = True")
                    
                    # Wait for acknowledgment with detailed logging
                    ack_waiting_start = asyncio.get_event_loop().time()
                    wait_count = 0
                    logging.info("Starting to wait for action acknowledgment")
                    while self.waiting_for_action_response and not self.game_over:
                        await asyncio.sleep(0.1)
                        wait_count += 1
                        if wait_count % 10 == 0:  # Log every second
                            elapsed = asyncio.get_event_loop().time() - ack_waiting_start
                            logging.debug(f"Still waiting for acknowledgment... {elapsed:.1f}s elapsed")
                        # If waiting more than 10 seconds for acknowledgment, break
                        if asyncio.get_event_loop().time() - ack_waiting_start > 10:
                            logging.warning("Timeout waiting for action acknowledgment")
                            break
                    
                    if not self.waiting_for_action_response:
                        logging.info("Received acknowledgment for action")
                    
                except websockets.exceptions.ConnectionClosedOK as e:
                    logging.error(f"WebSocket closed normally while sending action: {e}")
                    if hasattr(e, 'code'):
                        logging.error(f"Close code: {e.code}, reason: {e.reason if hasattr(e, 'reason') else 'unknown'}")
                    logging.info("This might be expected if the game is ending")
                    self.game_over = True
                    self.info = {"error": "Connection closed by server"}
                    break
                except websockets.exceptions.ConnectionClosedError as e:
                    logging.error(f"WebSocket closed with error while sending action: {e}")
                    if hasattr(e, 'code'):
                        logging.error(f"Close code: {e.code}, reason: {e.reason if hasattr(e, 'reason') else 'unknown'}")
                    self.game_over = True
                    self.info = {"error": f"Connection error: {e}"}
                    break
                except Exception as e:
                    logging.error(f"Error sending action: {e}")
                    logging.error(traceback.format_exc())
                    self.game_over = True
                    self.info = {"error": str(e)}
                    break
                
                self.action_queue.task_done()
                logging.debug("Action queue task marked as done")
        except Exception as e:
            logging.error(f"Action sender unexpected error: {e}")
            logging.error(traceback.format_exc())
            
    async def connect(self):
        """Connect to matchmaking server and queue for game."""
        params = {"model_name": self.model_name, "model_token": self.model_token}
        query_params = "?" + urlencode(params)
        
        try:
            print(f"Connecting to matchmaking server {WS_SERVER_URI + query_params}")
            self.websocket = await websockets.connect(
                WS_SERVER_URI + query_params,
                ping_interval=20,
                ping_timeout=60
            )
            print("Connected to matchmaking server")
            
            asyncio.create_task(self._message_receiver(self.websocket, "matchmaking"))
            asyncio.create_task(self._action_sender(self.websocket))
            
            queue_command = {"command": "queue", "environments": self.env_ids}
            await self.websocket.send(json.dumps(queue_command))
            print("Sent queue request")
            
            message = await self.message_queue.get()
            print(f"Queue response: {message}")
            return True
        except Exception as e:
            print(f"Matchmaking connection error: {e}")
            return False

    async def _initialize_local_game(self, server_ip: str, environment_id: int, env_id: str):
        """Send a POST request to initialize the game on a local server."""
        initialize_url = f"http://{server_ip}:8000/initialize"
        # Use the model_token and a dummy token for a two-player game
        payload = {
            "environment_id": environment_id,
            "env_id": env_id,
            "tokens": [self.model_token, "dummy_opponent_token"]  # Adjust based on game requirements
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(initialize_url, json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to initialize game: {response.status} - {await response.text()}")
                    result = await response.json()
                    print(f"Game initialized: {result}")
                    return True
            except Exception as e:
                print(f"Error initializing local game: {e}")
                self.game_over = True
                self.info = {"error": f"Initialization failed: {str(e)}"}
                return False

    async def connect_to_game_server(self, server_ip: str):
        """Connect to the Fargate game server with the model token, initializing if local."""
        # Check if the server is local
        is_local = server_ip == "localhost" or server_ip == "127.0.0.1"
        if is_local:
            # For local testing, override server_ip and initialize the game
            server_ip = "localhost"
            # Get the first environment ID and name (assuming single env for simplicity)
            env_id_int = self.env_ids[0]
            env_id_str = next((k for k, v in NAME_TO_ID_DICT.items() if v == env_id_int), None)
            if not env_id_str:
                print(f"Invalid environment ID: {env_id_int}")
                self.game_over = True
                self.info = {"error": "Invalid environment ID"}
                return
            
            # Initialize the game on the local server
            success = await self._initialize_local_game(server_ip, env_id_int, env_id_str)
            if not success:
                return

        try:
            # Include the token as a query parameter
            params = {"token": self.model_token}
            query_params = "?" + urlencode(params)
            game_ws_uri = f"ws://{server_ip}:8000/ws{query_params}"
            print(f"Connecting to game server {game_ws_uri}")
            
            # Use minimal set of parameters that are compatible across versions
            self.game_websocket = await websockets.connect(
                game_ws_uri,
                ping_interval=20,
                ping_timeout=60
            )
            print("Connected to game server")
            
            # Start background tasks
            self.receiver_task = asyncio.create_task(self._message_receiver(self.game_websocket, "game"))
            self.sender_task = asyncio.create_task(self._action_sender(self.game_websocket))
        except Exception as e:
            print(f"Game server connection error: {e}")
            self.game_over = True
            self.info = {"error": f"Failed to connect to game server: {str(e)}"}

    async def update_loop(self):
        """Main loop that processes messages and updates game state."""
        while not self.game_over:
            try:
                timeout = self.queue_timeout if not self.in_game else self.game_timeout
                try:
                    queue_label, message = await asyncio.wait_for(self.message_queue.get(), timeout=timeout)
                    await self._process_message(queue_label, message)
                except asyncio.TimeoutError:
                    state = "matchmaking" if not self.in_game else "game"
                    print(f"Timeout during {state}")
                    self.game_over = True
                    break
            except Exception as e:
                print(f"Error in update loop: {e}")
                if not self.game_over:
                    await asyncio.sleep(0.1)
        print("Update loop exiting")

    async def _process_message(self, queue_label: str, message: str):
        """Process a received websocket message."""
        try:
            payload = json.loads(message)
            command = payload.get("command")
            
            if queue_label == "matchmaking":
                if command == "queued":
                    avg_queue_time = payload.get("avg_queue_time", 0)
                    num_players = payload.get("num_players_in_queue", 0)
                    print(f"Queued for game. Avg wait: {avg_queue_time}s, Players in queue: {num_players}")
                
                elif command == "match_found":
                    self.in_game = True
                    server_ip = payload.get("server_ip")
                    env_id = payload.get("env_id")
                    environment_id = payload.get("environment_id")
                    print(f"Match found! Connecting to game server at {server_ip} with token {self.model_token}")
                    
                    await self.websocket.close()  # Close matchmaking connection
                    self.websocket = None
                    await self.connect_to_game_server(server_ip)
            
            elif queue_label == "game":
                if command == "observation":
                    obs = payload.get("observation", [])
                    player_id = payload.get("player_id")
                    if obs:
                        self.current_player_id = player_id
                        self.full_observations[player_id] = obs
                        self.current_observation = obs
                        print(f"Received observation for player {player_id}, length: {len(obs)}")
                    self.waiting_for_action_response = False
                
                elif command == "action_ack":
                    print(f"Received action acknowledgment: {payload.get('message', '')}")
                    # Keep waiting_for_action_response True until we get a new observation
                    # or until game_over
                
                elif command == "game_over":
                    self.game_over = True
                    game_id = payload.get("game_id")
                    opponent = payload.get("opponent_name", "Unknown")
                    outcome = payload.get("outcome", "unknown")
                    reason = payload.get("reason", "No reason provided")
                    print(f"Game over! ID: {game_id}, Opponent: {opponent}, Outcome: {outcome}, Reason: {reason}")
                    change_in_skill = payload.get("trueskill_change")  # Fixed key name
                    if change_in_skill is not None:
                        self.rewards[self.current_player_id] = float(change_in_skill)
                    self.info = {"reason": reason, "outcome": outcome}
                    self.waiting_for_action_response = False
                
                elif command == "error":
                    error_msg = payload.get("message", "Unknown error")
                    print(f"Received error from game server: {error_msg}")
                    self.game_over = True
                    self.info = {"error": error_msg}
                    self.waiting_for_action_response = False
                
                elif command == "timed_out":
                    error_msg = payload.get("message", "Timed out")
                    print(f"Game timed out: {error_msg}")
                    self.game_over = True
                    self.info = {"error": error_msg}
                    self.waiting_for_action_response = False
                
                else:
                    print(f"Unknown game command: {command}")
        
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {message}")
        except Exception as e:
            print(f"Error processing {queue_label} message: {e}, message: {message}")

    async def async_get_observation(self) -> Tuple[Optional[int], List[Tuple[int, str]]]:
        if self.current_player_id is not None and self.current_observation:
            return self.current_player_id, self.current_observation
        
        if not self.game_over:
            timeout = self.queue_timeout if not self.in_game else self.game_timeout
            update_task = asyncio.create_task(self.update_loop())
            start_time = asyncio.get_event_loop().time()
            while not self.game_over:
                if self.current_player_id is not None and self.current_observation:
                    if not update_task.done():
                        update_task.cancel()
                    return self.current_player_id, self.current_observation
                await asyncio.sleep(0.1)
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout:
                    print(f"Timeout waiting for observation")
                    self.game_over = True
                    break
            if not update_task.done():
                update_task.cancel()
        return None, []

    def get_observation(self) -> Tuple[Optional[int], List[Tuple[int, str]]]:
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
        if self.game_over:
            return True, self.info
        
        await self.action_queue.put(action)
        self.current_observation = None
        self.waiting_for_action_response = True
        
        # Wait for an observation or game over
        start_time = asyncio.get_event_loop().time()
        while not self.game_over and self.waiting_for_action_response:
            await asyncio.sleep(0.1)
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.game_timeout:
                print(f"Timeout waiting for action response")
                self.game_over = True
                self.info = {"error": "Action timeout"}
                break
        
        # Wait a bit after getting a response to allow for the next message to be processed
        await asyncio.sleep(0.5)
        
        return self.game_over, self.info
        
    def step(self, action: str):
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
        if not self.websocket:
            connected = await self.connect()
            if not connected:
                print("Failed to connect to matchmaking server")
                return []
        
        update_task = asyncio.create_task(self.update_loop())
        start_time = asyncio.get_event_loop().time()
        while not self.game_over and not self.in_game:
            await asyncio.sleep(0.1)
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.queue_timeout:
                print(f"Timeout waiting for match")
                self.game_over = True
                break
        
        if self.in_game and not self.current_observation:
            player_id, observation = await self.async_get_observation()
            if player_id is not None:
                return observation
        return self.current_observation if self.current_observation else []

    async def async_close(self):
        logging.info("Closing environment")
        await self.action_queue.put("CLOSE")
        
        # Safely close matchmaking websocket if it exists
        if self.websocket:
            try:
                # Different versions of websockets library have different ways to check if closed
                websocket_open = True
                try:
                    if hasattr(self.websocket, 'closed'):
                        websocket_open = not self.websocket.closed
                    elif hasattr(self.websocket, 'open'):
                        websocket_open = self.websocket.open
                except:
                    # If we can't determine state, try to close anyway
                    pass
                    
                if websocket_open:
                    logging.info("Closing matchmaking websocket")
                    await self.websocket.close()
                    logging.info("Matchmaking websocket closed")
            except Exception as e:
                logging.error(f"Error closing matchmaking websocket: {e}")
        
        # Safely close game websocket if it exists
        if self.game_websocket:
            try:
                # Different versions of websockets library have different ways to check if closed
                websocket_open = True
                try:
                    if hasattr(self.game_websocket, 'closed'):
                        websocket_open = not self.game_websocket.closed
                    elif hasattr(self.game_websocket, 'open'):
                        websocket_open = self.game_websocket.open
                except:
                    # If we can't determine state, try to close anyway
                    pass
                    
                if websocket_open:
                    logging.info("Closing game websocket")
                    await self.game_websocket.close()
                    logging.info("Game websocket closed")
            except Exception as e:
                logging.error(f"Error closing game websocket: {e}")
        
        return self.rewards

    def reset(self, num_players=None, seed=None):
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

    def close(self):
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
    try:
        env_ids = [env_id] if isinstance(env_id, str) else env_id
        if env_ids[0] == "all":
            env_ids_int = list(NAME_TO_ID_DICT.values())
        else:
            env_ids_int = [NAME_TO_ID_DICT[env] for env in env_ids]
    except KeyError as e:
        logging.error(f"Environment {e} not recognized")
        raise

    if model_token is None:
        if model_description is None or email is None:
            raise ValueError("Provide model_description and email if model_token is not given")
        url = f"{HTTP_SERVER_URI}/register_model"
        data = {"model_name": model_name, "description": model_description, "email": email}
        response = requests.post(url, json=data, timeout=10, verify=False)
        response.raise_for_status()
        model_token = response.json()["model_token"]
        logging.info("Model registered successfully")

    return OnlineEnvWrapper(env_ids_int, model_name, model_token)

class DebugWebSocket:
    """A wrapper around websockets.WebSocketClientProtocol to add debugging."""
    
    def __init__(self, websocket):
        self.websocket = websocket
        logging.info(f"Created DebugWebSocket wrapper")
        
    async def send(self, message):
        logging.debug(f"DebugWebSocket.send called with {len(message)} bytes")
        
        # Safely check state
        try:
            if hasattr(self.websocket, 'closed'):
                state_closed = self.websocket.closed
                logging.debug(f"WebSocket state: closed={state_closed}")
            elif hasattr(self.websocket, 'open'):
                state_open = self.websocket.open
                logging.debug(f"WebSocket state: open={state_open}")
        except Exception as e:
            logging.debug(f"Could not check websocket state: {e}")
            
        result = await self.websocket.send(message)
        logging.debug(f"DebugWebSocket.send completed successfully")
        return result
        
    async def recv(self):
        logging.debug(f"DebugWebSocket.recv called")
        message = await self.websocket.recv()
        logging.debug(f"DebugWebSocket.recv received {len(message)} bytes")
        return message
        
    async def close(self, code=1000, reason=""):
        logging.info(f"DebugWebSocket.close called with code={code}, reason={reason}")
        try:
            await self.websocket.close(code, reason)
            logging.info(f"DebugWebSocket.close completed")
        except Exception as e:
            logging.error(f"Error in DebugWebSocket.close: {e}")
            logging.error(traceback.format_exc())
        
    def __getattr__(self, name):
        logging.debug(f"DebugWebSocket.__getattr__ called for {name}")
        return getattr(self.websocket, name)

# Use this to wrap WebSocket in connect_to_game_server
async def connect_to_game_server(self, server_ip: str):
    """Connect to the Fargate game server with the model token, initializing if local."""
    # Check if the server is local
    is_local = server_ip == "localhost" or server_ip == "127.0.0.1"
    if is_local:
        # For local testing, override server_ip and initialize the game
        server_ip = "localhost"
        # Get the first environment ID and name (assuming single env for simplicity)
        env_id_int = self.env_ids[0]
        env_id_str = next((k for k, v in NAME_TO_ID_DICT.items() if v == env_id_int), None)
        if not env_id_str:
            logging.error(f"Invalid environment ID: {env_id_int}")
            self.game_over = True
            self.info = {"error": "Invalid environment ID"}
            return
        
        # Initialize the game on the local server
        success = await self._initialize_local_game(server_ip, env_id_int, env_id_str)
        if not success:
            return

    try:
        # Include the token as a query parameter
        params = {"token": self.model_token}
        query_params = "?" + urlencode(params)
        game_ws_uri = f"ws://{server_ip}:8000/ws{query_params}"
        logging.info(f"Connecting to game server {game_ws_uri}")
        
        # Use minimal parameters that are compatible with all versions
        self.game_websocket = await websockets.connect(
            game_ws_uri,
            ping_interval=20,
            ping_timeout=60
        )
        logging.info(f"Connected to game server")
        
        # Start background tasks
        self.receiver_task = asyncio.create_task(self._message_receiver(self.game_websocket, "game"))
        self.sender_task = asyncio.create_task(self._action_sender(self.game_websocket))
    except Exception as e:
        logging.error(f"Game server connection error: {e}")
        logging.error(traceback.format_exc())
        self.game_over = True
        self.info = {"error": f"Failed to connect to game server: {str(e)}"}