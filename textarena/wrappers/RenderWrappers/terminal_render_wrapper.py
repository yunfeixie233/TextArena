# # # import os
# # # import time
# # # from typing import Dict, Optional, Tuple, List, Callable, Any, Union, Set
# # # from io import StringIO
# # # import cv2
# # # import numpy as np

# # # from rich import box
# # # from rich.columns import Columns
# # # from rich.console import Console, RenderableType
# # # from rich.layout import Layout
# # # from rich.panel import Panel
# # # from rich.pretty import Pretty
# # # from rich.table import Table
# # # from rich.text import Text

# # # from textarena.core import Env, Message, Info, Rewards, RenderWrapper, State


# # # class TerminalRenderWrapper(RenderWrapper):
# # #     """
# # #     Enhanced terminal render wrapper for text-based game environments.
    
# # #     Supports:
# # #     - Single player, two-player, and multiplayer games
# # #     - Flexible layout (full-screen or half-screen modes)
# # #     - Custom ASCII board rendering
# # #     - Automatic player color assignment
# # #     - Configurable rendering of generic and player-specific game states
# # #     - Video recording capabilities
    
# # #     Usage:
# # #         env = YourGameEnvironment(...)
# # #         wrapped_env = TerminalRenderWrapper(
# # #             env,
# # #             player_names={0: "Alice", 1: "Bob"},
# # #             full_screen=True,
# # #             record_video=False
# # #         )
# # #     """
    
# # #     # Define a list of colors to assign to players
# # #     PLAYER_COLORS = [
# # #         "red",
# # #         "green", 
# # #         "blue",
# # #         "magenta",
# # #         "yellow",
# # #         "cyan",
# # #         "bright_red",
# # #         "bright_green",
# # #         "bright_blue",
# # #         "bright_magenta", 
# # #         "bright_yellow",
# # #         "bright_cyan",
# # #     ]
    
# # #     # Define color for game messages and keywords
# # #     GAME_MESSAGE_COLOR = "yellow"
# # #     GAME_KEYWORD_COLOR = "cyan"
# # #     INFO_COLOR = "bright_white"
# # #     WARNING_COLOR = "bright_yellow"
# # #     ERROR_COLOR = "bright_red"
    
# # #     def __init__(
# # #         self,
# # #         env: Env,
# # #         player_names: Optional[Dict[int, str]] = None,
# # #         full_screen: bool = True,
# # #         record_video: bool = False,
# # #         video_path: str = "game_recording.mp4",
# # #         video_fps: int = 1,
# # #         max_log_lines: int = 20,
# # #     ):
# # #         """
# # #         Initialize the TerminalRenderWrapper.
        
# # #         Args:
# # #             env (Env): The environment to wrap
# # #             player_names (Optional[Dict[int, str]]): Mapping from player IDs to display names
# # #             full_screen (bool): Whether to use full-screen layout (True) or half-screen (False)
# # #             record_video (bool): Whether to record a video of the gameplay
# # #             video_path (str): Path to save the recording (if record_video is True)
# # #             video_fps (int): Frames per second for the recorded video
# # #             max_log_lines (int): Maximum number of log lines to display
# # #         """
# # #         super().__init__(env)
# # #         self.full_screen = full_screen
# # #         self.record_video = record_video
# # #         self.video_path = video_path
# # #         self.video_fps = video_fps
# # #         self.max_log_lines = max_log_lines
# # #         self.player_names = player_names
        
# # #         # Initialize in reset_render
# # #         self.console = None
# # #         self.layout = None
# # #         self.player_color_map = {}
# # #         self.frames = []
# # #         self.last_render_time = 0
    
# # #     def reset_render(self):
# # #         """Reset and initialize the rendering components"""
# # #         # Get state from env
# # #         self.state = self.env.state
        
# # #         # Set up player names if none provided
# # #         if self.player_names is None:
# # #             self.player_names = {}
# # #             for player_id in range(self.state.num_players):
# # #                 self.player_names[player_id] = f"Player {player_id}"
# # #             # Include any role mappings from the state (if any)
# # #             if hasattr(self.state, 'role_mapping') and self.state.role_mapping:
# # #                 self.player_names.update(self.state.role_mapping)
        
# # #         # Initialize console
# # #         self.console = Console()
        
# # #         # Set up layout based on mode
# # #         self._setup_layout()
        
# # #         # Assign colors to players
# # #         self.player_color_map = self._assign_player_colors()
        
# # #         # Initialize video recording if enabled
# # #         if self.record_video:
# # #             self.frames = []
# # #             self._capture_and_store_frame()
        
# # #         # Record initial render time
# # #         self.last_render_time = time.time()
    
# # #     def _setup_layout(self):
# # #         """Configure the layout based on full_screen or half_screen mode"""
# # #         self.layout = Layout()
        
# # #         if self.full_screen:
# # #             # Full screen layout: 4 quadrants
# # #             self.layout.split_column(
# # #                 Layout(name="header", size=1),
# # #                 Layout(name="main", ratio=20)
# # #             )
            
# # #             self.layout["main"].split_row(
# # #                 Layout(name="left_column", ratio=1),
# # #                 Layout(name="right_column", ratio=1)
# # #             )
            
# # #             self.layout["left_column"].split_column(
# # #                 Layout(name="board", ratio=2),
# # #                 Layout(name="game_state", ratio=1)
# # #             )
            
# # #             self.layout["right_column"].split_column(
# # #                 Layout(name="player_state", ratio=1),
# # #                 Layout(name="game_log", ratio=2)
# # #             )
# # #         else:
# # #             # Half screen layout: 2 main sections
# # #             self.layout.split_column(
# # #                 Layout(name="header", size=1),
# # #                 Layout(name="upper", ratio=1),
# # #                 Layout(name="lower", ratio=1)
# # #             )
            
# # #             self.layout["upper"].split_row(
# # #                 Layout(name="board", ratio=1),
# # #                 Layout(name="game_state", ratio=1)
# # #             )
            
# # #             self.layout["lower"].split_row(
# # #                 Layout(name="player_state", ratio=1),
# # #                 Layout(name="game_log", ratio=1)
# # #             )
    
# # #     def _assign_player_colors(self) -> Dict[int, str]:
# # #         """Assign unique colors to each player based on their ID"""
# # #         color_map = {}
# # #         player_ids = list(self.player_names.keys())
# # #         player_ids.sort()  # Ensure consistent color assignment
        
# # #         num_colors = len(self.PLAYER_COLORS)
# # #         for idx, player_id in enumerate(player_ids):
# # #             color = self.PLAYER_COLORS[idx % num_colors]
# # #             color_map[player_id] = color
        
# # #         return color_map
    
# # #     def _process_logs(self, logs: List[Message]) -> Text:
# # #         """Process game logs with player name substitution and colorization"""
# # #         processed_lines = []
        
# # #         for role, message in logs:
# # #             message = str(message)  # Ensure message is a string
            
# # #             if role != -1:
# # #                 # Player message
# # #                 player_name = self.player_names.get(role, f"Player {role}")
# # #                 color = self.player_color_map.get(role, "white")
# # #                 player_name_colored = f"[{color}]{player_name}[/{color}]"
# # #                 log = f"{player_name_colored}: {message}"
# # #             else:
# # #                 # Game message
# # #                 log = f"[{self.GAME_MESSAGE_COLOR}][GAME]: {message}[/{self.GAME_MESSAGE_COLOR}]"
            
# # #             # Create Text object from log
# # #             log_text = Text.from_markup(log)
            
# # #             # Wrap the text to console width
# # #             if self.console:
# # #                 wrapped_lines = log_text.wrap(self.console, width=self.console.width)
# # #                 processed_lines.extend(wrapped_lines)
# # #             else:
# # #                 processed_lines.append(log_text)
        
# # #         # Limit to max_log_lines
# # #         if self.max_log_lines is not None and len(processed_lines) > self.max_log_lines:
# # #             processed_lines = processed_lines[-self.max_log_lines:]
        
# # #         # Join all lines with newlines
# # #         log_text = Text('\n').join(processed_lines)
# # #         return log_text
    
# # #     def _capture_frame(self):
# # #         """Capture the current terminal content as a frame"""
# # #         try:
# # #             # Use standard terminal dimensions for consistent frames
# # #             width, height = os.get_terminal_size()
            
# # #             # Render to string
# # #             string_io = StringIO()
# # #             temp_console = Console(
# # #                 file=string_io,
# # #                 width=width,
# # #                 height=height,
# # #                 record=True
# # #             )
# # #             temp_console.print(self.layout)
            
# # #             # Convert to image using OpenCV
# # #             text_content = string_io.getvalue()
# # #             lines = text_content.split('\n')
            
# # #             # Create a blank canvas
# # #             img = np.zeros((height * 20, width * 10, 3), dtype=np.uint8)
# # #             img.fill(255)  # White background
            
# # #             # Simple rendering of text
# # #             for i, line in enumerate(lines[:height]):
# # #                 cv2.putText(
# # #                     img, 
# # #                     line, 
# # #                     (10, (i + 1) * 20), 
# # #                     cv2.FONT_HERSHEY_SIMPLEX,
# # #                     0.5, 
# # #                     (0, 0, 0), 
# # #                     1
# # #                 )
            
# # #             return img
            
# # #         except Exception as e:
# # #             print(f"Error capturing frame: {e}")
# # #             return None
    
# # #     def _capture_and_store_frame(self):
# # #         """Capture current frame and add to frames list"""
# # #         if not self.record_video:
# # #             return
            
# # #         frame = self._capture_frame()
# # #         if frame is not None:
# # #             self.frames.append(frame)
    
# # #     def _save_video(self):
# # #         """Save recorded frames as a video file"""
# # #         if not self.record_video or not self.frames:
# # #             return
            
# # #         try:
# # #             height, width = self.frames[0].shape[:2]
# # #             fourcc = cv2.VideoWriter_fourcc(*'XVID')
# # #             out = cv2.VideoWriter(
# # #                 self.video_path,
# # #                 fourcc,
# # #                 self.video_fps,
# # #                 (width, height)
# # #             )
            
# # #             for frame in self.frames:
# # #                 out.write(frame)
                
# # #             out.release()
# # #             print(f"\nVideo saved to {self.video_path}")
            
# # #         except Exception as e:
# # #             print(f"Error saving video: {e}")
    
# # #     def _render_ascii_board(self) -> RenderableType:
# # #         """
# # #         Render the game board using ASCII art if the environment provides a render_board method,
# # #         otherwise display a placeholder.
# # #         """
# # #         if hasattr(self.env, "render_board") and callable(self.env.render_board):
# # #             board_str = self.env.render_board()
# # #             return Panel(
# # #                 board_str,
# # #                 title="Game Board",
# # #                 border_style="bright_blue",
# # #                 padding=(1, 1)
# # #             )
        
# # #         # Check if game_state contains a string board representation
# # #         game_state = self.state.game_state
# # #         if isinstance(game_state, dict):
# # #             for key in ['board', 'board_state', 'rendered_board', 'current_board']:
# # #                 if key in game_state and isinstance(game_state[key], str):
# # #                     return Panel(
# # #                         game_state[key],
# # #                         title=f"Game Board ({key})",
# # #                         border_style="bright_blue", 
# # #                         padding=(1, 1)
# # #                     )
        
# # #         # Fallback to a placeholder panel
# # #         return Panel(
# # #             "Board visualization not available",
# # #             title="Game Board",
# # #             border_style="bright_blue",
# # #             padding=(1, 1)
# # #         )
    
# # #     def _render_generic_game_state(self) -> RenderableType:
# # #         """Render general game state information"""
# # #         game_state = self.state.game_state
# # #         if not isinstance(game_state, dict):
# # #             return Panel(
# # #                 "Game state information not available",
# # #                 title="Game State",
# # #                 border_style="blue"
# # #             )
        
# # #         # Determine which keys to render
# # #         render_keys = getattr(self.env, "terminal_render_keys", [])
# # #         if not render_keys and isinstance(game_state, dict):
# # #             # Auto-select keys if none specified
# # #             render_keys = [
# # #                 k for k, v in game_state.items() 
# # #                 if not isinstance(v, (dict, list)) and k not in ['board', 'board_state', 'rendered_board']
# # #             ]
        
# # #         # Always include turn information
# # #         game_info = [
# # #             ("Turn", f"{self.state.turn}" + (f"/{self.state.max_turns}" if self.state.max_turns else "")),
# # #             ("Players", f"{self.state.num_players}")
# # #         ]
        
# # #         # Add game state items from render_keys
# # #         for key in render_keys:
# # #             if isinstance(key, str) and key in game_state:
# # #                 value = game_state[key]
# # #                 # Skip board representations that are handled elsewhere
# # #                 if key in ['board', 'board_state', 'rendered_board', 'current_board'] and isinstance(value, str):
# # #                     continue
                
# # #                 # Skip dictionary values that likely represent player attributes
# # #                 if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
# # #                     continue
                    
# # #                 # Format the value
# # #                 if isinstance(value, (dict, list)):
# # #                     formatted_value = "\n" + Pretty(value).__str__()
# # #                 else:
# # #                     formatted_value = str(value)
                    
# # #                 game_info.append((key, formatted_value))
        
# # #         # Create a table
# # #         table = Table(show_header=False, box=box.SIMPLE)
# # #         table.add_column("Property", style="cyan")
# # #         table.add_column("Value", style="green")
        
# # #         for name, value in game_info:
# # #             table.add_row(name, value)
            
# # #         return Panel(
# # #             table,
# # #             title="Game Information",
# # #             border_style="blue",
# # #             padding=(1, 1)
# # #         )
    
# # #     def _render_player_state(self) -> RenderableType:
# # #         """Render player-specific attributes and state information"""
# # #         game_state = self.state.game_state
# # #         if not isinstance(game_state, dict):
# # #             return Panel(
# # #                 "Player information not available",
# # #                 title="Player State",
# # #                 border_style="green"
# # #             )
        
# # #         # Find player-specific attributes (dicts with integer keys)
# # #         player_attributes = {}
# # #         for key, value in game_state.items():
# # #             if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
# # #                 player_attributes[key] = value
        
# # #         # If no player attributes found, check for nested player attributes
# # #         if not player_attributes:
# # #             nested_player_attributes = {}
# # #             for key, value in game_state.items():
# # #                 if isinstance(value, dict):
# # #                     for subkey, subvalue in value.items():
# # #                         if isinstance(subvalue, dict) and all(isinstance(k, int) for k in subvalue.keys()):
# # #                             nested_path = f"{key}.{subkey}"
# # #                             nested_player_attributes[nested_path] = subvalue
            
# # #             if nested_player_attributes:
# # #                 player_attributes = nested_player_attributes
        
# # #         if not player_attributes:
# # #             return Panel(
# # #                 "No player-specific attributes found",
# # #                 title="Player State",
# # #                 border_style="green"
# # #             )
        
# # #         # Create a table with players as rows and attributes as columns
# # #         table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAD)
        
# # #         # Add player column
# # #         table.add_column("Player", style="cyan", no_wrap=True)
        
# # #         # Add attribute columns
# # #         attribute_keys = list(player_attributes.keys())
# # #         for attr in attribute_keys:
# # #             table.add_column(str(attr), style="green")
        
# # #         # Get all player IDs
# # #         player_ids = set()
# # #         for attr_dict in player_attributes.values():
# # #             player_ids.update(attr_dict.keys())
# # #         player_ids = sorted(player_ids)
        
# # #         # Add rows for each player
# # #         for player_id in player_ids:
# # #             player_name = self.player_names.get(player_id, f"Player {player_id}")
# # #             color = self.player_color_map.get(player_id, "white")
            
# # #             # Indicate current player
# # #             if player_id == self.state.current_player_id:
# # #                 player_display = f"[{color}]➤ {player_name}[/{color}]"
# # #             else:
# # #                 player_display = f"[{color}]{player_name}[/{color}]"
                
# # #             row = [player_display]
            
# # #             # Add attribute values
# # #             for attr in attribute_keys:
# # #                 attr_value = player_attributes[attr].get(player_id, "")
# # #                 row.append(str(attr_value))
                
# # #             table.add_row(*row)
                
# # #         return Panel(
# # #             table,
# # #             title="Player State",
# # #             border_style="green",
# # #             padding=(1, 1)
# # #         )
    
# # #     def _render_header(self) -> RenderableType:
# # #         """Render a simple header with game name and turn information"""
# # #         env_name = self.env.__class__.__name__
# # #         turn_info = f"Turn {self.state.turn}"
# # #         if self.state.max_turns:
# # #             turn_info += f"/{self.state.max_turns}"
            
# # #         current_player = self.state.current_player_id
# # #         player_name = self.player_names.get(current_player, f"Player {current_player}")
# # #         color = self.player_color_map.get(current_player, "white")
            
# # #         header_text = f"Game: [bold]{env_name}[/bold] | {turn_info} | Current Player: [{color}]{player_name}[/{color}]"
        
# # #         return Text.from_markup(header_text)
    
# # #     def _render(self):
# # #         """Render the current game state to the terminal"""
# # #         if not self.console or not self.layout:
# # #             # Initialize if needed
# # #             self.reset_render()
        
# # #         # Update each section of the layout
# # #         self.layout["header"].update(self._render_header())
# # #         self.layout["board"].update(self._render_ascii_board())
# # #         self.layout["game_state"].update(self._render_generic_game_state())
# # #         self.layout["player_state"].update(self._render_player_state())
        
# # #         # Process and display logs
# # #         log_panel = Panel(
# # #             self._process_logs(self.state.logs),
# # #             title="Game Log",
# # #             border_style="yellow",
# # #             padding=(1, 1)
# # #         )
# # #         self.layout["game_log"].update(log_panel)
        
# # #         # Print the layout
# # #         self.console.clear()
# # #         self.console.print(self.layout)
        
# # #         # Capture frame for video if recording
# # #         if self.record_video:
# # #             # Limit frame rate
# # #             current_time = time.time()
# # #             if current_time - self.last_render_time >= 1.0/self.video_fps:
# # #                 self._capture_and_store_frame()
# # #                 self.last_render_time = current_time
    
# # #     def reset(self, *args, **kwargs):
# # #         """Reset the environment and rendering components"""
# # #         result = self.env.reset(*args, **kwargs)
# # #         self.reset_render()
# # #         self._render()
# # #         return result
    
# # #     def step(self, action: str) -> Tuple[Optional[Rewards], bool, bool, Optional[Info]]:
# # #         """Process a step in the environment and update the rendering"""
# # #         step_results = self.env.step(action=action)
# # #         self._render()
# # #         return step_results
    
# # #     def close(self):
# # #         """Clean up resources and save video if recording"""
# # #         if self.record_video and self.frames:
# # #             self._save_video()
# # #         return self.env.close()
# # import os
# # import time
# # from typing import Dict, Optional, Tuple, List, Callable, Any, Union, Set
# # from io import StringIO
# # import cv2
# # import numpy as np

# # from rich import box
# # from rich.columns import Columns
# # from rich.console import Console, RenderableType
# # from rich.layout import Layout
# # from rich.panel import Panel
# # from rich.pretty import Pretty
# # from rich.table import Table
# # from rich.text import Text

# # from textarena.core import Env, Message, Info, Rewards, RenderWrapper, State


# # class TerminalRenderWrapper(RenderWrapper):
# #     """
# #     Enhanced terminal render wrapper for text-based game environments.
    
# #     Supports:
# #     - Single player, two-player, and multiplayer games
# #     - Flexible layout (full-screen or half-screen modes)
# #     - Custom ASCII board rendering
# #     - Automatic player color assignment
# #     - Configurable rendering of generic and player-specific game states
# #     - Video recording capabilities
    
# #     Usage:
# #         env = YourGameEnvironment(...)
# #         wrapped_env = TerminalRenderWrapper(
# #             env,
# #             player_names={0: "Alice", 1: "Bob"},
# #             full_screen=True,
# #             record_video=False
# #         )
# #     """
    
# #     # Define a list of colors to assign to players
# #     PLAYER_COLORS = [
# #         "red",
# #         "green", 
# #         "blue",
# #         "magenta",
# #         "yellow",
# #         "cyan",
# #         "bright_red",
# #         "bright_green",
# #         "bright_blue",
# #         "bright_magenta", 
# #         "bright_yellow",
# #         "bright_cyan",
# #     ]
    
# #     # Define color for game messages and keywords
# #     GAME_MESSAGE_COLOR = "yellow"
# #     GAME_KEYWORD_COLOR = "cyan"
# #     INFO_COLOR = "bright_white"
# #     WARNING_COLOR = "bright_yellow"
# #     ERROR_COLOR = "bright_red"
    
# #     def __init__(
# #         self,
# #         env: Env,
# #         player_names: Optional[Dict[int, str]] = None,
# #         full_screen: bool = True,
# #         record_video: bool = False,
# #         video_path: str = "game_recording.mp4",
# #         video_fps: int = 1,
# #         max_log_lines: int = 20,
# #     ):
# #         """
# #         Initialize the TerminalRenderWrapper.
        
# #         Args:
# #             env (Env): The environment to wrap
# #             player_names (Optional[Dict[int, str]]): Mapping from player IDs to display names
# #             full_screen (bool): Whether to use full-screen layout (True) or half-screen (False)
# #             record_video (bool): Whether to record a video of the gameplay
# #             video_path (str): Path to save the recording (if record_video is True)
# #             video_fps (int): Frames per second for the recorded video
# #             max_log_lines (int): Maximum number of log lines to display
# #         """
# #         super().__init__(env)
# #         self.full_screen = full_screen
# #         self.record_video = record_video
# #         self.video_path = video_path
# #         self.video_fps = video_fps
# #         self.max_log_lines = max_log_lines
# #         self.player_names = player_names
        
# #         # Initialize in reset_render
# #         self.console = None
# #         self.layout = None
# #         self.player_color_map = {}
# #         self.frames = []
# #         self.last_render_time = 0
    
# #     def reset_render(self):
# #         """Reset and initialize the rendering components"""
# #         # Get state from env
# #         self.state = self.env.state
        
# #         # Set up player names if none provided
# #         if self.player_names is None:
# #             self.player_names = {}
# #             for player_id in range(self.state.num_players):
# #                 self.player_names[player_id] = f"Player {player_id}"
# #             # Include any role mappings from the state (if any)
# #             if hasattr(self.state, 'role_mapping') and self.state.role_mapping:
# #                 if isinstance(self.state.role_mapping, dict):
# #                     self.player_names.update(self.state.role_mapping)
        
# #         # Initialize console with appropriate settings
# #         self.console = Console(highlight=False)  # Disable auto-highlighting for better control
        
# #         # Assign colors to players before setting up layout
# #         # (layout setup might need player colors for visualization)
# #         self.player_color_map = self._assign_player_colors()
        
# #         # Set up layout based on mode and available game state
# #         self._setup_layout()
        
# #         # Initialize video recording if enabled
# #         if self.record_video:
# #             self.frames = []
# #             self._capture_and_store_frame()
        
# #         # Record initial render time
# #         self.last_render_time = time.time()
    
# #     def _setup_layout(self):
# #         """
# #         Configure the layout based on full_screen or half_screen mode.
# #         The layout is dynamically adjusted based on whether player state exists.
# #         """
# #         self.layout = Layout()
        
# #         # Always start with a header
# #         self.layout.split_column(
# #             Layout(name="header", size=1),
# #             Layout(name="main", ratio=20)
# #         )
        
# #         # Determine if we have player-specific attributes to display
# #         has_player_state = False
# #         if hasattr(self, 'state') and hasattr(self.state, 'game_state'):
# #             game_state = self.state.game_state
# #             if isinstance(game_state, dict):
# #                 for key, value in game_state.items():
# #                     if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
# #                         has_player_state = True
# #                         break
        
# #         if self.full_screen:
# #             # Full screen layout with conditional player state
# #             self.layout["main"].split_row(
# #                 Layout(name="left_column", ratio=1),
# #                 Layout(name="right_column", ratio=1)
# #             )
            
# #             # Left column always has board and game state
# #             self.layout["left_column"].split_column(
# #                 Layout(name="board", ratio=2),
# #                 Layout(name="game_state", ratio=1)
# #             )
            
# #             # Right column depends on whether we have player state
# #             if has_player_state:
# #                 self.layout["right_column"].split_column(
# #                     Layout(name="player_state", ratio=1),
# #                     Layout(name="game_log", ratio=2)
# #                 )
# #             else:
# #                 # No player state, game log takes the full right column
# #                 self.layout["right_column"].update(Layout(name="game_log"))
# #         else:
# #             # Half screen layout with conditional player state
# #             self.layout["main"].split_column(
# #                 Layout(name="upper", ratio=1),
# #                 Layout(name="lower", ratio=1)
# #             )
            
# #             # Upper section always has board and game state
# #             self.layout["upper"].split_row(
# #                 Layout(name="board", ratio=1),
# #                 Layout(name="game_state", ratio=1)
# #             )
            
# #             # Lower section depends on whether we have player state
# #             if has_player_state:
# #                 self.layout["lower"].split_row(
# #                     Layout(name="player_state", ratio=1),
# #                     Layout(name="game_log", ratio=1)
# #                 )
# #             else:
# #                 # No player state, game log takes the full lower section
# #                 self.layout["lower"].update(Layout(name="game_log"))
                
# #         # Ensure all required layout sections exist
# #         if "player_state" not in self.layout:
# #             # Add a hidden player_state layout that won't be rendered
# #             self.layout.add_slot("player_state")
    
# #     def _assign_player_colors(self) -> Dict[int, str]:
# #         """Assign unique colors to each player based on their ID"""
# #         color_map = {}
# #         player_ids = list(self.player_names.keys())
# #         player_ids.sort()  # Ensure consistent color assignment
        
# #         num_colors = len(self.PLAYER_COLORS)
# #         for idx, player_id in enumerate(player_ids):
# #             color = self.PLAYER_COLORS[idx % num_colors]
# #             color_map[player_id] = color
        
# #         return color_map
    
# #     def _process_logs(self, logs: List[Message]) -> Text:
# #         """Process game logs with player name substitution and colorization"""
# #         processed_lines = []
        
# #         for role, message in logs:
# #             message = str(message)  # Ensure message is a string
            
# #             if role != -1:
# #                 # Player message
# #                 player_name = self.player_names.get(role, f"Player {role}")
# #                 color = self.player_color_map.get(role, "white")
# #                 player_name_colored = f"[{color}]{player_name}[/{color}]"
# #                 log = f"{player_name_colored}: {message}"
# #             else:
# #                 # Game message
# #                 log = f"[{self.GAME_MESSAGE_COLOR}][GAME]: {message}[/{self.GAME_MESSAGE_COLOR}]"
            
# #             # Create Text object from log
# #             log_text = Text.from_markup(log)
            
# #             # Wrap the text to console width
# #             if self.console:
# #                 wrapped_lines = log_text.wrap(self.console, width=self.console.width)
# #                 processed_lines.extend(wrapped_lines)
# #             else:
# #                 processed_lines.append(log_text)
        
# #         # Limit to max_log_lines
# #         if self.max_log_lines is not None and len(processed_lines) > self.max_log_lines:
# #             processed_lines = processed_lines[-self.max_log_lines:]
        
# #         # Join all lines with newlines
# #         log_text = Text('\n').join(processed_lines)
# #         return log_text
    
# #     def _capture_frame(self):
# #         """Capture the current terminal content as a frame"""
# #         try:
# #             # Use standard terminal dimensions for consistent frames
# #             width, height = os.get_terminal_size()
            
# #             # Render to string
# #             string_io = StringIO()
# #             temp_console = Console(
# #                 file=string_io,
# #                 width=width,
# #                 height=height,
# #                 record=True
# #             )
# #             temp_console.print(self.layout)
            
# #             # Convert to image using OpenCV
# #             text_content = string_io.getvalue()
# #             lines = text_content.split('\n')
            
# #             # Create a blank canvas
# #             img = np.zeros((height * 20, width * 10, 3), dtype=np.uint8)
# #             img.fill(255)  # White background
            
# #             # Simple rendering of text
# #             for i, line in enumerate(lines[:height]):
# #                 cv2.putText(
# #                     img, 
# #                     line, 
# #                     (10, (i + 1) * 20), 
# #                     cv2.FONT_HERSHEY_SIMPLEX,
# #                     0.5, 
# #                     (0, 0, 0), 
# #                     1
# #                 )
            
# #             return img
            
# #         except Exception as e:
# #             print(f"Error capturing frame: {e}")
# #             return None
    
# #     def _capture_and_store_frame(self):
# #         """Capture current frame and add to frames list"""
# #         if not self.record_video:
# #             return
            
# #         frame = self._capture_frame()
# #         if frame is not None:
# #             self.frames.append(frame)
    
# #     def _save_video(self):
# #         """Save recorded frames as a video file"""
# #         if not self.record_video or not self.frames:
# #             return
            
# #         try:
# #             height, width = self.frames[0].shape[:2]
# #             fourcc = cv2.VideoWriter_fourcc(*'XVID')
# #             out = cv2.VideoWriter(
# #                 self.video_path,
# #                 fourcc,
# #                 self.video_fps,
# #                 (width, height)
# #             )
            
# #             for frame in self.frames:
# #                 out.write(frame)
                
# #             out.release()
# #             print(f"\nVideo saved to {self.video_path}")
            
# #         except Exception as e:
# #             print(f"Error saving video: {e}")
    
# #     def _render_ascii_board(self) -> RenderableType:
# #         """
# #         Render the game board using ASCII art if the environment provides a render_board method,
# #         otherwise display a placeholder. The board is centered within its panel.
# #         """
# #         # Get the board content
# #         if hasattr(self.env, "render_board") and callable(self.env.render_board):
# #             board_str = self.env.render_board()
# #         else:
# #             # Check if game_state contains a string board representation
# #             game_state = self.state.game_state
# #             board_str = None
# #             if isinstance(game_state, dict):
# #                 for key in ['board', 'board_state', 'rendered_board', 'current_board']:
# #                     if key in game_state and isinstance(game_state[key], str):
# #                         board_str = game_state[key]
# #                         break
            
# #             # Fallback if no board found
# #             if board_str is None:
# #                 return Panel(
# #                     "Board visualization not available",
# #                     title="Game Board",
# #                     border_style="bright_blue",
# #                     padding=(1, 1)
# #                 )
        
# #         # Center the board text (assuming monospace font)
# #         centered_lines = []
# #         lines = board_str.splitlines()
        
# #         if lines:
# #             # Find the width of the console panel
# #             console_width = self.console.width
# #             # For a two-column layout, estimate the panel width
# #             if "left_column" in self.layout:
# #                 estimated_panel_width = console_width // 2 - 4  # account for borders
# #             else:
# #                 estimated_panel_width = console_width - 4
                
# #             max_line_length = max(len(line) for line in lines)
            
# #             for line in lines:
# #                 # Center each line if it's shorter than the panel
# #                 if len(line) < estimated_panel_width:
# #                     padding = (estimated_panel_width - len(line)) // 2
# #                     centered_lines.append(" " * padding + line)
# #                 else:
# #                     centered_lines.append(line)
        
# #         centered_board = "\n".join(centered_lines)
        
# #         # Determine appropriate title
# #         title = "Game Board"
# #         if not hasattr(self.env, "render_board") and board_str is not None:
# #             for key in ['board', 'board_state', 'rendered_board', 'current_board']:
# #                 if key in game_state and game_state[key] == board_str:
# #                     title = f"Game Board ({key})"
# #                     break
        
# #         return Panel(
# #             centered_board,
# #             title=title,
# #             border_style="bright_blue",
# #             padding=(1, 1)
# #         )
    
# #     def _render_generic_game_state(self) -> RenderableType:
# #         """Render general game state information"""
# #         game_state = self.state.game_state
# #         if not isinstance(game_state, dict):
# #             return Panel(
# #                 "Game state information not available",
# #                 title="Game State",
# #                 border_style="blue"
# #             )
        
# #         # Determine which keys to render
# #         render_keys = getattr(self.env, "terminal_render_keys", [])
# #         if not render_keys and isinstance(game_state, dict):
# #             # Auto-select keys if none specified
# #             render_keys = [
# #                 k for k, v in game_state.items() 
# #                 if not isinstance(v, (dict, list)) and k not in ['board', 'board_state', 'rendered_board']
# #             ]
        
# #         # Always include turn information
# #         game_info = [
# #             ("Turn", f"{self.state.turn}" + (f"/{self.state.max_turns}" if self.state.max_turns else "")),
# #             ("Players", f"{self.state.num_players}")
# #         ]
        
# #         # Add game state items from render_keys
# #         for key in render_keys:
# #             if isinstance(key, str) and key in game_state:
# #                 value = game_state[key]
# #                 # Skip board representations that are handled elsewhere
# #                 if key in ['board', 'board_state', 'rendered_board', 'current_board'] and isinstance(value, str):
# #                     continue
                
# #                 # Skip dictionary values that likely represent player attributes
# #                 if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
# #                     continue
                    
# #                 # Format the value
# #                 if isinstance(value, (dict, list)):
# #                     formatted_value = "\n" + Pretty(value).__str__()
# #                 else:
# #                     formatted_value = str(value)
                    
# #                 game_info.append((key, formatted_value))
        
# #         # Create a table
# #         table = Table(show_header=False, box=box.SIMPLE)
# #         table.add_column("Property", style="cyan")
# #         table.add_column("Value", style="green")
        
# #         for name, value in game_info:
# #             table.add_row(name, value)
            
# #         return Panel(
# #             table,
# #             title="Game Information",
# #             border_style="blue",
# #             padding=(1, 1)
# #         )
    
# #     def _render_player_state(self) -> RenderableType:
# #         """Render player-specific attributes and state information"""
# #         game_state = self.state.game_state
# #         if not isinstance(game_state, dict):
# #             return Panel(
# #                 "Player information not available",
# #                 title="Player State",
# #                 border_style="green"
# #             )
        
# #         # Find player-specific attributes (dicts with integer keys)
# #         player_attributes = {}
# #         for key, value in game_state.items():
# #             if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
# #                 player_attributes[key] = value
        
# #         # If no player attributes found, check for nested player attributes
# #         if not player_attributes:
# #             nested_player_attributes = {}
# #             for key, value in game_state.items():
# #                 if isinstance(value, dict):
# #                     for subkey, subvalue in value.items():
# #                         if isinstance(subvalue, dict) and all(isinstance(k, int) for k in subvalue.keys()):
# #                             nested_path = f"{key}.{subkey}"
# #                             nested_player_attributes[nested_path] = subvalue
            
# #             if nested_player_attributes:
# #                 player_attributes = nested_player_attributes
        
# #         if not player_attributes:
# #             return Panel(
# #                 "No player-specific attributes found",
# #                 title="Player State",
# #                 border_style="green"
# #             )
        
# #         # Create a table with players as rows and attributes as columns
# #         table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAD)
        
# #         # Add player column
# #         table.add_column("Player", style="cyan", no_wrap=True)
        
# #         # Add attribute columns
# #         attribute_keys = list(player_attributes.keys())
# #         for attr in attribute_keys:
# #             table.add_column(str(attr), style="green")
        
# #         # Get all player IDs
# #         player_ids = set()
# #         for attr_dict in player_attributes.values():
# #             player_ids.update(attr_dict.keys())
# #         player_ids = sorted(player_ids)
        
# #         # Add rows for each player
# #         for player_id in player_ids:
# #             player_name = self.player_names.get(player_id, f"Player {player_id}")
# #             color = self.player_color_map.get(player_id, "white")
            
# #             # Indicate current player
# #             if player_id == self.state.current_player_id:
# #                 player_display = f"[{color}]➤ {player_name}[/{color}]"
# #             else:
# #                 player_display = f"[{color}]{player_name}[/{color}]"
                
# #             row = [player_display]
            
# #             # Add attribute values
# #             for attr in attribute_keys:
# #                 attr_value = player_attributes[attr].get(player_id, "")
# #                 row.append(str(attr_value))
                
# #             table.add_row(*row)
                
# #         return Panel(
# #             table,
# #             title="Player State",
# #             border_style="green",
# #             padding=(1, 1)
# #         )
    
# #     def _render_header(self) -> RenderableType:
# #         """Render a simple header with game name and turn information"""
# #         env_name = self.env.__class__.__name__
# #         turn_info = f"Turn {self.state.turn}"
# #         if self.state.max_turns:
# #             turn_info += f"/{self.state.max_turns}"
            
# #         current_player = self.state.current_player_id
# #         player_name = self.player_names.get(current_player, f"Player {current_player}")
# #         color = self.player_color_map.get(current_player, "white")
            
# #         header_text = f"Game: [bold]{env_name}[/bold] | {turn_info} | Current Player: [{color}]{player_name}[/{color}]"
        
# #         return Text.from_markup(header_text)
    
# #     def _render(self):
# #         """
# #         Render the current game state to the terminal.
# #         Dynamically handles layout based on available content.
# #         """
# #         if not self.console or not self.layout:
# #             # Initialize if needed
# #             self.reset_render()
        
# #         # Check if we need to update the layout (player state might have changed)
# #         has_player_state = False
# #         if hasattr(self, 'state') and hasattr(self.state, 'game_state'):
# #             game_state = self.state.game_state
# #             if isinstance(game_state, dict):
# #                 for key, value in game_state.items():
# #                     if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
# #                         has_player_state = True
# #                         break
        
# #         # Recreate layout if player state visibility has changed
# #         current_has_player_state = "player_state" in self.layout and "parent" in self.layout["player_state"].__dict__
# #         if has_player_state != current_has_player_state:
# #             self._setup_layout()
        
# #         # Update each section of the layout
# #         self.layout["header"].update(self._render_header())
# #         self.layout["board"].update(self._render_ascii_board())
# #         self.layout["game_state"].update(self._render_generic_game_state())
        
# #         # Only render player_state if it's visible in the layout
# #         if has_player_state:
# #             self.layout["player_state"].update(self._render_player_state())
        
# #         # Process and display logs
# #         log_panel = Panel(
# #             self._process_logs(self.state.logs),
# #             title="Game Log",
# #             border_style="yellow", 
# #             padding=(1, 1)
# #         )
# #         self.layout["game_log"].update(log_panel)
        
# #         # Print the layout
# #         self.console.clear()
# #         self.console.print(self.layout)
        
# #         # Capture frame for video if recording
# #         if self.record_video:
# #             # Limit frame rate
# #             current_time = time.time()
# #             if current_time - self.last_render_time >= 1.0/self.video_fps:
# #                 self._capture_and_store_frame()
# #                 self.last_render_time = current_time
    
# #     def reset(self, *args, **kwargs):
# #         """Reset the environment and rendering components"""
# #         result = self.env.reset(*args, **kwargs)
# #         self.reset_render()
# #         self._render()
# #         return result
    
# #     def step(self, action: str) -> Tuple[Optional[Rewards], bool, bool, Optional[Info]]:
# #         """Process a step in the environment and update the rendering"""
# #         step_results = self.env.step(action=action)
# #         self._render()
# #         return step_results
    
# #     def close(self):
# #         """Clean up resources and save video if recording"""
# #         if self.record_video and self.frames:
# #             self._save_video()
# #         return self.env.close()
# import os
# import time
# from typing import Dict, Optional, Tuple, List, Callable, Any, Union, Set
# from io import StringIO
# import cv2
# import numpy as np

# from rich import box
# from rich.columns import Columns
# from rich.console import Console, RenderableType
# from rich.layout import Layout
# from rich.panel import Panel
# from rich.pretty import Pretty
# from rich.table import Table
# from rich.text import Text

# from textarena.core import Env, Message, Info, Rewards, RenderWrapper, State


# class TerminalRenderWrapper(RenderWrapper):
#     """
#     Enhanced terminal render wrapper for text-based game environments.
    
#     Supports:
#     - Single player, two-player, and multiplayer games
#     - Flexible layout (full-screen or half-screen modes)
#     - Custom ASCII board rendering
#     - Automatic player color assignment
#     - Configurable rendering of generic and player-specific game states
#     - Video recording capabilities
    
#     Usage:
#         env = YourGameEnvironment(...)
#         wrapped_env = TerminalRenderWrapper(
#             env,
#             player_names={0: "Alice", 1: "Bob"},
#             full_screen=True,
#             record_video=False
#         )
#     """
    
#     # Define a list of colors to assign to players
#     PLAYER_COLORS = [
#         "red",
#         "green", 
#         "blue",
#         "magenta",
#         "yellow",
#         "cyan",
#         "bright_red",
#         "bright_green",
#         "bright_blue",
#         "bright_magenta", 
#         "bright_yellow",
#         "bright_cyan",
#     ]
    
#     # Define color for game messages and keywords
#     GAME_MESSAGE_COLOR = "yellow"
#     GAME_KEYWORD_COLOR = "cyan"
#     INFO_COLOR = "bright_white"
#     WARNING_COLOR = "bright_yellow"
#     ERROR_COLOR = "bright_red"
    
#     def __init__(
#         self,
#         env: Env,
#         player_names: Optional[Dict[int, str]] = None,
#         full_screen: bool = True,
#         record_video: bool = False,
#         video_path: str = "game_recording.mp4",
#         video_fps: int = 1,
#         max_log_lines: int = 20,
#     ):
#         """
#         Initialize the TerminalRenderWrapper.
        
#         Args:
#             env (Env): The environment to wrap
#             player_names (Optional[Dict[int, str]]): Mapping from player IDs to display names
#             full_screen (bool): Whether to use full-screen layout (True) or half-screen (False)
#             record_video (bool): Whether to record a video of the gameplay
#             video_path (str): Path to save the recording (if record_video is True)
#             video_fps (int): Frames per second for the recorded video
#             max_log_lines (int): Maximum number of log lines to display
#         """
#         super().__init__(env)
#         self.full_screen = full_screen
#         self.record_video = record_video
#         self.video_path = video_path
#         self.video_fps = video_fps
#         self.max_log_lines = max_log_lines
#         self.player_names = player_names
        
#         # Initialize in reset_render
#         self.console = None
#         self.layout = None
#         self.player_color_map = {}
#         self.frames = []
#         self.last_render_time = 0
    
#     def reset_render(self):
#         """Reset and initialize the rendering components"""
#         # Get state from env
#         self.state = self.env.state
        
#         # Set up player names if none provided
#         if self.player_names is None:
#             self.player_names = {}
#             for player_id in range(self.state.num_players):
#                 self.player_names[player_id] = f"Player {player_id}"
#             # Include any role mappings from the state (if any)
#             if hasattr(self.state, 'role_mapping') and self.state.role_mapping:
#                 if isinstance(self.state.role_mapping, dict):
#                     self.player_names.update(self.state.role_mapping)
        
#         # Initialize console with appropriate settings
#         self.console = Console(highlight=False)  # Disable auto-highlighting for better control
        
#         # Assign colors to players before setting up layout
#         # (layout setup might need player colors for visualization)
#         self.player_color_map = self._assign_player_colors()
        
#         # Set up layout based on mode and available game state
#         self._setup_layout()
        
#         # Initialize video recording if enabled
#         if self.record_video:
#             self.frames = []
#             self._capture_and_store_frame()
        
#         # Record initial render time
#         self.last_render_time = time.time()
    
#     def _setup_layout(self):
#         """
#         Configure the layout based on full_screen or half_screen mode.
#         The layout is dynamically adjusted based on whether player state exists.
#         """
#         self.layout = Layout()
        
#         # Always start with a header
#         self.layout.split_column(
#             Layout(name="header", size=1),
#             Layout(name="main", ratio=20)
#         )
        
#         # Determine if we have player-specific attributes to display
#         has_player_state = False
#         if hasattr(self, 'state') and hasattr(self.state, 'game_state'):
#             game_state = self.state.game_state
#             if isinstance(game_state, dict):
#                 for key, value in game_state.items():
#                     if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
#                         has_player_state = True
#                         break
        
#         if self.full_screen:
#             # Full screen layout with conditional player state
#             self.layout["main"].split_row(
#                 Layout(name="left_column", ratio=1),
#                 Layout(name="right_column", ratio=1)
#             )
            
#             # Left column always has board and game state
#             self.layout["left_column"].split_column(
#                 Layout(name="board", ratio=2),
#                 Layout(name="game_state", ratio=1)
#             )
            
#             # Right column depends on whether we have player state
#             if has_player_state:
#                 self.layout["right_column"].split_column(
#                     Layout(name="player_state", ratio=1),
#                     Layout(name="game_log", ratio=2)
#                 )
#             else:
#                 # No player state, game log takes the full right column
#                 self.layout["right_column"].update(Layout(name="game_log"))
#         else:
#             # Half screen layout with conditional player state
#             self.layout["main"].split_column(
#                 Layout(name="upper", ratio=1),
#                 Layout(name="lower", ratio=1)
#             )
            
#             # Upper section always has board and game state
#             self.layout["upper"].split_row(
#                 Layout(name="board", ratio=1),
#                 Layout(name="game_state", ratio=1)
#             )
            
#             # Lower section depends on whether we have player state
#             if has_player_state:
#                 self.layout["lower"].split_row(
#                     Layout(name="player_state", ratio=1),
#                     Layout(name="game_log", ratio=1)
#                 )
#             else:
#                 # No player state, game log takes the full lower section
#                 self.layout["lower"].update(Layout(name="game_log"))
        
#         # Create a mapping of what layout sections exist
#         self._layout_sections = set(self._collect_layout_names(self.layout))
    
#     def _collect_layout_names(self, layout):
#         """Collect all layout section names recursively"""
#         names = [layout.name] if layout.name else []
#         for child in getattr(layout, 'children', []):
#             names.extend(self._collect_layout_names(child))
#         return names
    
#     def _assign_player_colors(self) -> Dict[int, str]:
#         """Assign unique colors to each player based on their ID"""
#         color_map = {}
#         player_ids = list(self.player_names.keys())
#         player_ids.sort()  # Ensure consistent color assignment
        
#         num_colors = len(self.PLAYER_COLORS)
#         for idx, player_id in enumerate(player_ids):
#             color = self.PLAYER_COLORS[idx % num_colors]
#             color_map[player_id] = color
        
#         return color_map
    
#     def _process_logs(self, logs: List[Message]) -> Text:
#         """Process game logs with player name substitution and colorization"""
#         processed_lines = []
        
#         for role, message in logs:
#             message = str(message)  # Ensure message is a string
            
#             if role != -1:
#                 # Player message
#                 player_name = self.player_names.get(role, f"Player {role}")
#                 color = self.player_color_map.get(role, "white")
#                 player_name_colored = f"[{color}]{player_name}[/{color}]"
#                 log = f"{player_name_colored}: {message}"
#             else:
#                 # Game message
#                 log = f"[{self.GAME_MESSAGE_COLOR}][GAME]: {message}[/{self.GAME_MESSAGE_COLOR}]"
            
#             # Create Text object from log
#             log_text = Text.from_markup(log)
            
#             # Wrap the text to console width
#             if self.console:
#                 wrapped_lines = log_text.wrap(self.console, width=self.console.width)
#                 processed_lines.extend(wrapped_lines)
#             else:
#                 processed_lines.append(log_text)
        
#         # Limit to max_log_lines
#         if self.max_log_lines is not None and len(processed_lines) > self.max_log_lines:
#             processed_lines = processed_lines[-self.max_log_lines:]
        
#         # Join all lines with newlines
#         log_text = Text('\n').join(processed_lines)
#         return log_text
    
#     def _capture_frame(self):
#         """Capture the current terminal content as a frame"""
#         try:
#             # Use standard terminal dimensions for consistent frames
#             width, height = os.get_terminal_size()
            
#             # Render to string
#             string_io = StringIO()
#             temp_console = Console(
#                 file=string_io,
#                 width=width,
#                 height=height,
#                 record=True
#             )
#             temp_console.print(self.layout)
            
#             # Convert to image using OpenCV
#             text_content = string_io.getvalue()
#             lines = text_content.split('\n')
            
#             # Create a blank canvas
#             img = np.zeros((height * 20, width * 10, 3), dtype=np.uint8)
#             img.fill(255)  # White background
            
#             # Simple rendering of text
#             for i, line in enumerate(lines[:height]):
#                 cv2.putText(
#                     img, 
#                     line, 
#                     (10, (i + 1) * 20), 
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.5, 
#                     (0, 0, 0), 
#                     1
#                 )
            
#             return img
            
#         except Exception as e:
#             print(f"Error capturing frame: {e}")
#             return None
    
#     def _capture_and_store_frame(self):
#         """Capture current frame and add to frames list"""
#         if not self.record_video:
#             return
            
#         frame = self._capture_frame()
#         if frame is not None:
#             self.frames.append(frame)
    
#     def _save_video(self):
#         """Save recorded frames as a video file"""
#         if not self.record_video or not self.frames:
#             return
            
#         try:
#             height, width = self.frames[0].shape[:2]
#             fourcc = cv2.VideoWriter_fourcc(*'XVID')
#             out = cv2.VideoWriter(
#                 self.video_path,
#                 fourcc,
#                 self.video_fps,
#                 (width, height)
#             )
            
#             for frame in self.frames:
#                 out.write(frame)
                
#             out.release()
#             print(f"\nVideo saved to {self.video_path}")
            
#         except Exception as e:
#             print(f"Error saving video: {e}")
    
#     def _render_ascii_board(self) -> RenderableType:
#         """
#         Render the game board using ASCII art if the environment provides a render_board method,
#         otherwise display a placeholder. The board is centered within its panel.
#         """
#         # Get the board content
#         if hasattr(self.env, "render_board") and callable(self.env.render_board):
#             board_str = self.env.render_board()
#         else:
#             # Check if game_state contains a string board representation
#             game_state = self.state.game_state
#             board_str = None
#             if isinstance(game_state, dict):
#                 for key in ['board', 'board_state', 'rendered_board', 'current_board']:
#                     if key in game_state and isinstance(game_state[key], str):
#                         board_str = game_state[key]
#                         break
            
#             # Fallback if no board found
#             if board_str is None:
#                 return Panel(
#                     "Board visualization not available",
#                     title="Game Board",
#                     border_style="bright_blue",
#                     padding=(1, 1)
#                 )
        
#         # Center the board text (assuming monospace font)
#         centered_lines = []
#         lines = board_str.splitlines()
        
#         if lines:
#             # Find the width of the console panel
#             console_width = self.console.width
#             # For a two-column layout, estimate the panel width
#             if "left_column" in self.layout:
#                 estimated_panel_width = console_width // 2 - 4  # account for borders
#             else:
#                 estimated_panel_width = console_width - 4
                
#             max_line_length = max(len(line) for line in lines)
            
#             for line in lines:
#                 # Center each line if it's shorter than the panel
#                 if len(line) < estimated_panel_width:
#                     padding = (estimated_panel_width - len(line)) // 2
#                     centered_lines.append(" " * padding + line)
#                 else:
#                     centered_lines.append(line)
        
#         centered_board = "\n".join(centered_lines)
        
#         # Determine appropriate title
#         title = "Game Board"
#         if not hasattr(self.env, "render_board") and board_str is not None:
#             for key in ['board', 'board_state', 'rendered_board', 'current_board']:
#                 if key in game_state and game_state[key] == board_str:
#                     title = f"Game Board ({key})"
#                     break
        
#         return Panel(
#             centered_board,
#             title=title,
#             border_style="bright_blue",
#             padding=(1, 1)
#         )
    
#     def _render_generic_game_state(self) -> RenderableType:
#         """Render general game state information"""
#         game_state = self.state.game_state
#         if not isinstance(game_state, dict):
#             return Panel(
#                 "Game state information not available",
#                 title="Game State",
#                 border_style="blue"
#             )
        
#         # Determine which keys to render
#         render_keys = getattr(self.env, "terminal_render_keys", [])
#         if not render_keys and isinstance(game_state, dict):
#             # Auto-select keys if none specified
#             render_keys = [
#                 k for k, v in game_state.items() 
#                 if not isinstance(v, (dict, list)) and k not in ['board', 'board_state', 'rendered_board']
#             ]
        
#         # Always include turn information
#         game_info = [
#             ("Turn", f"{self.state.turn}" + (f"/{self.state.max_turns}" if self.state.max_turns else "")),
#             ("Players", f"{self.state.num_players}")
#         ]
        
#         # Add game state items from render_keys
#         for key in render_keys:
#             if isinstance(key, str) and key in game_state:
#                 value = game_state[key]
#                 # Skip board representations that are handled elsewhere
#                 if key in ['board', 'board_state', 'rendered_board', 'current_board'] and isinstance(value, str):
#                     continue
                
#                 # Skip dictionary values that likely represent player attributes
#                 if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
#                     continue
                    
#                 # Format the value
#                 if isinstance(value, (dict, list)):
#                     formatted_value = "\n" + Pretty(value).__str__()
#                 else:
#                     formatted_value = str(value)
                    
#                 game_info.append((key, formatted_value))
        
#         # Create a table
#         table = Table(show_header=False, box=box.SIMPLE)
#         table.add_column("Property", style="cyan")
#         table.add_column("Value", style="green")
        
#         for name, value in game_info:
#             table.add_row(name, value)
            
#         return Panel(
#             table,
#             title="Game Information",
#             border_style="blue",
#             padding=(1, 1)
#         )
    
#     def _render_player_state(self) -> RenderableType:
#         """Render player-specific attributes and state information"""
#         game_state = self.state.game_state
#         if not isinstance(game_state, dict):
#             return Panel(
#                 "Player information not available",
#                 title="Player State",
#                 border_style="green"
#             )
        
#         # Find player-specific attributes (dicts with integer keys)
#         player_attributes = {}
#         for key, value in game_state.items():
#             if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
#                 player_attributes[key] = value
        
#         # If no player attributes found, check for nested player attributes
#         if not player_attributes:
#             nested_player_attributes = {}
#             for key, value in game_state.items():
#                 if isinstance(value, dict):
#                     for subkey, subvalue in value.items():
#                         if isinstance(subvalue, dict) and all(isinstance(k, int) for k in subvalue.keys()):
#                             nested_path = f"{key}.{subkey}"
#                             nested_player_attributes[nested_path] = subvalue
            
#             if nested_player_attributes:
#                 player_attributes = nested_player_attributes
        
#         if not player_attributes:
#             return Panel(
#                 "No player-specific attributes found",
#                 title="Player State",
#                 border_style="green"
#             )
        
#         # Create a table with players as rows and attributes as columns
#         table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAD)
        
#         # Add player column
#         table.add_column("Player", style="cyan", no_wrap=True)
        
#         # Add attribute columns
#         attribute_keys = list(player_attributes.keys())
#         for attr in attribute_keys:
#             table.add_column(str(attr), style="green")
        
#         # Get all player IDs
#         player_ids = set()
#         for attr_dict in player_attributes.values():
#             player_ids.update(attr_dict.keys())
#         player_ids = sorted(player_ids)
        
#         # Add rows for each player
#         for player_id in player_ids:
#             player_name = self.player_names.get(player_id, f"Player {player_id}")
#             color = self.player_color_map.get(player_id, "white")
            
#             # Indicate current player
#             if player_id == self.state.current_player_id:
#                 player_display = f"[{color}]➤ {player_name}[/{color}]"
#             else:
#                 player_display = f"[{color}]{player_name}[/{color}]"
                
#             row = [player_display]
            
#             # Add attribute values
#             for attr in attribute_keys:
#                 attr_value = player_attributes[attr].get(player_id, "")
#                 row.append(str(attr_value))
                
#             table.add_row(*row)
                
#         return Panel(
#             table,
#             title="Player State",
#             border_style="green",
#             padding=(1, 1)
#         )
    
#     def _render_header(self) -> RenderableType:
#         """Render a simple header with game name and turn information"""
#         env_name = self.env.__class__.__name__
#         turn_info = f"Turn {self.state.turn}"
#         if self.state.max_turns:
#             turn_info += f"/{self.state.max_turns}"
            
#         current_player = self.state.current_player_id
#         player_name = self.player_names.get(current_player, f"Player {current_player}")
#         color = self.player_color_map.get(current_player, "white")
            
#         header_text = f"Game: [bold]{env_name}[/bold] | {turn_info} | Current Player: [{color}]{player_name}[/{color}]"
        
#         return Text.from_markup(header_text)
    
#     def _render(self):
#         """
#         Render the current game state to the terminal.
#         Dynamically handles layout based on available content.
#         """
#         if not self.console or not self.layout:
#             # Initialize if needed
#             self.reset_render()
        
#         # Check if we need to update the layout (player state might have changed)
#         has_player_state = False
#         if hasattr(self, 'state') and hasattr(self.state, 'game_state'):
#             game_state = self.state.game_state
#             if isinstance(game_state, dict):
#                 for key, value in game_state.items():
#                     if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
#                         has_player_state = True
#                         break
        
#         # Recreate layout if player state visibility has changed
#         has_player_state_layout = "player_state" in self._layout_sections
#         if has_player_state != has_player_state_layout:
#             self._setup_layout()
        
#         # Update each section of the layout
#         self.layout["header"].update(self._render_header())
#         self.layout["board"].update(self._render_ascii_board())
#         self.layout["game_state"].update(self._render_generic_game_state())
        
#         # Only render player_state if it's visible in the layout
#         if "player_state" in self._layout_sections:
#             self.layout["player_state"].update(self._render_player_state())
        
#         # Process and display logs
#         log_panel = Panel(
#             self._process_logs(self.state.logs),
#             title="Game Log",
#             border_style="yellow", 
#             padding=(1, 1)
#         )
#         self.layout["game_log"].update(log_panel)
        
#         # Print the layout
#         self.console.clear()
#         self.console.print(self.layout)
        
#         # Capture frame for video if recording
#         if self.record_video:
#             # Limit frame rate
#             current_time = time.time()
#             if current_time - self.last_render_time >= 1.0/self.video_fps:
#                 self._capture_and_store_frame()
#                 self.last_render_time = current_time
    
#     def reset(self, *args, **kwargs):
#         """Reset the environment and rendering components"""
#         result = self.env.reset(*args, **kwargs)
#         self.reset_render()
#         self._render()
#         return result
    
#     def step(self, action: str) -> Tuple[Optional[Rewards], bool, bool, Optional[Info]]:
#         """Process a step in the environment and update the rendering"""
#         step_results = self.env.step(action=action)
#         self._render()
#         return step_results
    
#     def close(self):
#         """Clean up resources and save video if recording"""
#         if self.record_video and self.frames:
#             self._save_video()
#         return self.env.close()
import os
import time
from typing import Dict, Optional, Tuple, List, Callable, Any, Union, Set
from io import StringIO
import cv2
import numpy as np

from rich import box
from rich.columns import Columns
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table
from rich.text import Text

from textarena.core import Env, Message, Info, Rewards, RenderWrapper, State


class TerminalRenderWrapper(RenderWrapper):
    """
    Enhanced terminal render wrapper for text-based game environments.
    
    Supports:
    - Single player, two-player, and multiplayer games
    - Flexible layout (full-screen or half-screen modes)
    - Custom ASCII board rendering
    - Automatic player color assignment
    - Configurable rendering of generic and player-specific game states
    - Video recording capabilities
    
    Usage:
        env = YourGameEnvironment(...)
        wrapped_env = TerminalRenderWrapper(
            env,
            player_names={0: "Alice", 1: "Bob"},
            full_screen=True,
            record_video=False
        )
    """
    
    # Define a list of colors to assign to players
    PLAYER_COLORS = [
        "red",
        "green", 
        "blue",
        "magenta",
        "yellow",
        "cyan",
        "bright_red",
        "bright_green",
        "bright_blue",
        "bright_magenta", 
        "bright_yellow",
        "bright_cyan",
    ]
    
    # Define color for game messages and keywords
    GAME_MESSAGE_COLOR = "yellow"
    GAME_KEYWORD_COLOR = "cyan"
    INFO_COLOR = "bright_white"
    WARNING_COLOR = "bright_yellow"
    ERROR_COLOR = "bright_red"
    
    def __init__(
        self,
        env: Env,
        player_names: Optional[Dict[int, str]] = None,
        full_screen: bool = True,
        record_video: bool = False,
        video_path: str = "game_recording.mp4",
        video_fps: int = 1,
        max_log_lines: int = 20,
    ):
        """
        Initialize the TerminalRenderWrapper.
        
        Args:
            env (Env): The environment to wrap
            player_names (Optional[Dict[int, str]]): Mapping from player IDs to display names
            full_screen (bool): Whether to use full-screen layout (True) or half-screen (False)
            record_video (bool): Whether to record a video of the gameplay
            video_path (str): Path to save the recording (if record_video is True)
            video_fps (int): Frames per second for the recorded video
            max_log_lines (int): Maximum number of log lines to display
        """
        super().__init__(env)
        self.full_screen = full_screen
        self.record_video = record_video
        self.video_path = video_path
        self.video_fps = video_fps
        self.max_log_lines = max_log_lines
        self.player_names = player_names
        
        # Initialize in reset_render
        self.console = None
        self.layout = None
        self.player_color_map = {}
        self.frames = []
        self.last_render_time = 0
    
    def reset_render(self):
        """Reset and initialize the rendering components"""
        # Get state from env
        self.state = self.env.state
        
        # Set up player names if none provided
        if self.player_names is None:
            self.player_names = {}
            for player_id in range(self.state.num_players):
                self.player_names[player_id] = f"Player {player_id}"
            # Include any role mappings from the state (if any)
            if hasattr(self.state, 'role_mapping') and self.state.role_mapping:
                if isinstance(self.state.role_mapping, dict):
                    self.player_names.update(self.state.role_mapping)
        
        # Initialize console with appropriate settings
        self.console = Console(highlight=False)  # Disable auto-highlighting for better control
        
        # Assign colors to players before setting up layout
        # (layout setup might need player colors for visualization)
        self.player_color_map = self._assign_player_colors()
        
        # Set up layout based on mode and available game state
        self._setup_layout()
        
        # Initialize video recording if enabled
        if self.record_video:
            self.frames = []
            self._capture_and_store_frame()
        
        # Record initial render time
        self.last_render_time = time.time()
    
    def _setup_layout(self):
        """
        Configure the layout based on full_screen or half_screen mode.
        The layout is dynamically adjusted based on whether player state exists.
        """
        self.layout = Layout()
        
        # Always start with a header
        self.layout.split_column(
            Layout(name="header", size=1),
            Layout(name="main", ratio=20)
        )
        
        # Determine if we have player-specific attributes to display
        has_player_state = False
        if hasattr(self, 'state') and hasattr(self.state, 'game_state'):
            game_state = self.state.game_state
            if isinstance(game_state, dict):
                for key, value in game_state.items():
                    if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
                        has_player_state = True
                        break
        
        if self.full_screen:
            # Full screen layout with conditional player state
            self.layout["main"].split_row(
                Layout(name="left_column", ratio=1),
                Layout(name="right_column", ratio=1)
            )
            
            # Left column always has board and game state
            self.layout["left_column"].split_column(
                Layout(name="board", ratio=2),
                Layout(name="game_state", ratio=1)
            )
            
            # Right column depends on whether we have player state
            if has_player_state:
                self.layout["right_column"].split_column(
                    Layout(name="player_state", ratio=1),
                    Layout(name="game_log", ratio=2)
                )
            else:
                # No player state, game log takes the full right column
                self.layout["right_column"].update(Layout(name="game_log"))
        else:
            # Half screen layout with conditional player state
            self.layout["main"].split_column(
                Layout(name="upper", ratio=1),
                Layout(name="lower", ratio=1)
            )
            
            # Upper section always has board and game state
            self.layout["upper"].split_row(
                Layout(name="board", ratio=1),
                Layout(name="game_state", ratio=1)
            )
            
            # Lower section depends on whether we have player state
            if has_player_state:
                self.layout["lower"].split_row(
                    Layout(name="player_state", ratio=1),
                    Layout(name="game_log", ratio=1)
                )
            else:
                # No player state, game log takes the full lower section
                self.layout["lower"].update(Layout(name="game_log"))
        
        # Create a mapping of what layout sections exist
        self._layout_sections = set(self._collect_layout_names(self.layout))
    
    def _collect_layout_names(self, layout):
        """Collect all layout section names recursively"""
        names = [layout.name] if layout.name else []
        for child in getattr(layout, 'children', []):
            names.extend(self._collect_layout_names(child))
        return names
    
    def _assign_player_colors(self) -> Dict[int, str]:
        """Assign unique colors to each player based on their ID"""
        color_map = {}
        player_ids = list(self.player_names.keys())
        player_ids.sort()  # Ensure consistent color assignment
        
        num_colors = len(self.PLAYER_COLORS)
        for idx, player_id in enumerate(player_ids):
            color = self.PLAYER_COLORS[idx % num_colors]
            color_map[player_id] = color
        
        return color_map
    
    def _process_logs(self, logs: List[Message]) -> Text:
        """Process game logs with player name substitution and colorization"""
        processed_lines = []
        
        for role, message in logs:
            message = str(message)  # Ensure message is a string
            
            if role != -1:
                # Player message
                player_name = self.player_names.get(role, f"Player {role}")
                color = self.player_color_map.get(role, "white")
                player_name_colored = f"[{color}]{player_name}[/{color}]"
                log = f"{player_name_colored}: {message}"
            else:
                # Game message
                log = f"[{self.GAME_MESSAGE_COLOR}][GAME]: {message}[/{self.GAME_MESSAGE_COLOR}]"
            
            # Create Text object from log
            log_text = Text.from_markup(log)
            
            # Wrap the text to console width
            if self.console:
                wrapped_lines = log_text.wrap(self.console, width=self.console.width)
                processed_lines.extend(wrapped_lines)
            else:
                processed_lines.append(log_text)
        
        # Limit to max_log_lines
        if self.max_log_lines is not None and len(processed_lines) > self.max_log_lines:
            processed_lines = processed_lines[-self.max_log_lines:]
        
        # Join all lines with newlines
        log_text = Text('\n').join(processed_lines)
        return log_text
    
    def _capture_frame(self):
        """Capture the current terminal content as a frame"""
        try:
            # Use standard terminal dimensions for consistent frames
            width, height = os.get_terminal_size()
            
            # Render to string
            string_io = StringIO()
            temp_console = Console(
                file=string_io,
                width=width,
                height=height,
                record=True
            )
            temp_console.print(self.layout)
            
            # Convert to image using OpenCV
            text_content = string_io.getvalue()
            lines = text_content.split('\n')
            
            # Create a blank canvas
            img = np.zeros((height * 20, width * 10, 3), dtype=np.uint8)
            img.fill(255)  # White background
            
            # Simple rendering of text
            for i, line in enumerate(lines[:height]):
                cv2.putText(
                    img, 
                    line, 
                    (10, (i + 1) * 20), 
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, 
                    (0, 0, 0), 
                    1
                )
            
            return img
            
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None
    
    def _capture_and_store_frame(self):
        """Capture current frame and add to frames list"""
        if not self.record_video:
            return
            
        frame = self._capture_frame()
        if frame is not None:
            self.frames.append(frame)
    
    def _save_video(self):
        """Save recorded frames as a video file"""
        if not self.record_video or not self.frames:
            return
            
        try:
            height, width = self.frames[0].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(
                self.video_path,
                fourcc,
                self.video_fps,
                (width, height)
            )
            
            for frame in self.frames:
                out.write(frame)
                
            out.release()
            print(f"\nVideo saved to {self.video_path}")
            
        except Exception as e:
            print(f"Error saving video: {e}")
    
    def _render_ascii_board(self) -> RenderableType:
        """
        Render the game board using ASCII art if the environment provides a render_board method,
        otherwise display a placeholder. The board is centered within its panel.
        """
        # Get the board content
        if hasattr(self.env, "render_board") and callable(self.env.render_board):
            board_str = self.env.render_board()
        else:
            # Check if game_state contains a string board representation
            game_state = self.state.game_state
            board_str = None
            if isinstance(game_state, dict):
                for key in ['board', 'board_state', 'rendered_board', 'current_board']:
                    if key in game_state and isinstance(game_state[key], str):
                        board_str = game_state[key]
                        break
            
            # Fallback if no board found
            if board_str is None:
                return Panel(
                    "Board visualization not available",
                    title="Game Board",
                    border_style="bright_blue",
                    padding=(1, 1)
                )
        
        # Center the board text (assuming monospace font)
        centered_lines = []
        lines = board_str.splitlines()
        
        if lines:
            # Find the width of the console panel
            console_width = self.console.width
            # For a two-column layout, estimate the panel width
            if "left_column" in self.layout:
                estimated_panel_width = console_width // 2 - 4  # account for borders
            else:
                estimated_panel_width = console_width - 4
                
            max_line_length = max(len(line) for line in lines)
            
            for line in lines:
                # Center each line if it's shorter than the panel
                if len(line) < estimated_panel_width:
                    padding = (estimated_panel_width - len(line)) // 2
                    centered_lines.append(" " * padding + line)
                else:
                    centered_lines.append(line)
        
        centered_board = "\n".join(centered_lines)
        
        # Determine appropriate title
        title = "Game Board"
        if not hasattr(self.env, "render_board") and board_str is not None:
            for key in ['board', 'board_state', 'rendered_board', 'current_board']:
                if key in game_state and game_state[key] == board_str:
                    title = f"Game Board ({key})"
                    break
        
        return Panel(
            centered_board,
            title=title,
            border_style="bright_blue",
            padding=(1, 1)
        )
    
    def _render_generic_game_state(self) -> RenderableType:
        """Render general game state information"""
        game_state = self.state.game_state
        if not isinstance(game_state, dict):
            return Panel(
                "Game state information not available",
                title="Game State",
                border_style="blue"
            )
        
        # Determine which keys to render
        render_keys = getattr(self.env, "terminal_render_keys", [])
        if not render_keys and isinstance(game_state, dict):
            # Auto-select keys if none specified
            render_keys = [
                k for k, v in game_state.items() 
                if not isinstance(v, (dict, list)) and k not in ['board', 'board_state', 'rendered_board']
            ]
        
        # Always include turn information
        game_info = [
            ("Turn", f"{self.state.turn}" + (f"/{self.state.max_turns}" if self.state.max_turns else "")),
            ("Players", f"{self.state.num_players}")
        ]
        
        # Add game state items from render_keys
        for key in render_keys:
            if isinstance(key, str) and key in game_state:
                value = game_state[key]
                # Skip board representations that are handled elsewhere
                if key in ['board', 'board_state', 'rendered_board', 'current_board'] and isinstance(value, str):
                    continue
                
                # Skip dictionary values that likely represent player attributes
                if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
                    continue
                    
                # Format the value
                if isinstance(value, (dict, list)):
                    formatted_value = "\n" + Pretty(value).__str__()
                else:
                    formatted_value = str(value)
                    
                game_info.append((key, formatted_value))
        
        # Create a table
        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for name, value in game_info:
            table.add_row(name, value)
            
        return Panel(
            table,
            title="Game Information",
            border_style="blue",
            padding=(1, 1)
        )
    
    def _render_player_state(self) -> RenderableType:
        """Render player-specific attributes and state information"""
        game_state = self.state.game_state
        if not isinstance(game_state, dict):
            return Panel(
                "Player information not available",
                title="Player State",
                border_style="green"
            )
        
        # Find player-specific attributes (dicts with integer keys)
        player_attributes = {}
        for key, value in game_state.items():
            if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
                player_attributes[key] = value
        
        # If no player attributes found, check for nested player attributes
        if not player_attributes:
            nested_player_attributes = {}
            for key, value in game_state.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, dict) and all(isinstance(k, int) for k in subvalue.keys()):
                            nested_path = f"{key}.{subkey}"
                            nested_player_attributes[nested_path] = subvalue
            
            if nested_player_attributes:
                player_attributes = nested_player_attributes
        
        if not player_attributes:
            return Panel(
                "No player-specific attributes found",
                title="Player State",
                border_style="green"
            )
        
        # Create a table with players as rows and attributes as columns
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAD)
        
        # Add player column
        table.add_column("Player", style="cyan", no_wrap=True)
        
        # Add attribute columns
        attribute_keys = list(player_attributes.keys())
        for attr in attribute_keys:
            table.add_column(str(attr), style="green")
        
        # Get all player IDs
        player_ids = set()
        for attr_dict in player_attributes.values():
            player_ids.update(attr_dict.keys())
        player_ids = sorted(player_ids)
        
        # Add rows for each player
        for player_id in player_ids:
            player_name = self.player_names.get(player_id, f"Player {player_id}")
            color = self.player_color_map.get(player_id, "white")
            
            # Indicate current player
            if player_id == self.state.current_player_id:
                player_display = f"[{color}]➤ {player_name}[/{color}]"
            else:
                player_display = f"[{color}]{player_name}[/{color}]"
                
            row = [player_display]
            
            # Add attribute values
            for attr in attribute_keys:
                attr_value = player_attributes[attr].get(player_id, "")
                row.append(str(attr_value))
                
            table.add_row(*row)
                
        return Panel(
            table,
            title="Player State",
            border_style="green",
            padding=(1, 1)
        )
    
    def _render_header(self) -> RenderableType:
        """Render a simple header with game name and turn information"""
        env_name = self.env.__class__.__name__
        turn_info = f"Turn {self.state.turn}"
        if self.state.max_turns:
            turn_info += f"/{self.state.max_turns}"
            
        current_player = self.state.current_player_id
        player_name = self.player_names.get(current_player, f"Player {current_player}")
        color = self.player_color_map.get(current_player, "white")
            
        header_text = f"Game: [bold]{env_name}[/bold] | {turn_info} | Current Player: [{color}]{player_name}[/{color}]"
        
        return Text.from_markup(header_text)
    
    def _render(self):
        """
        Render the current game state to the terminal.
        Dynamically handles layout based on available content.
        """
        if not self.console or not self.layout:
            # Initialize if needed
            self.reset_render()
        
        # Check if we need to update the layout (player state might have changed)
        has_player_state = False
        if hasattr(self, 'state') and hasattr(self.state, 'game_state'):
            game_state = self.state.game_state
            if isinstance(game_state, dict):
                for key, value in game_state.items():
                    if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
                        has_player_state = True
                        break
        
        # Recreate layout if player state visibility has changed
        has_player_state_layout = "player_state" in self._layout_sections
        if has_player_state != has_player_state_layout:
            self._setup_layout()
        
        # Update each section of the layout
        self.layout["header"].update(self._render_header())
        self.layout["board"].update(self._render_ascii_board())
        self.layout["game_state"].update(self._render_generic_game_state())
        
        # Only render player_state if it's visible in the layout
        if "player_state" in self._layout_sections:
            self.layout["player_state"].update(self._render_player_state())
        
        # Process and display logs
        log_panel = Panel(
            self._process_logs(self.state.logs),
            title="Game Log",
            border_style="yellow", 
            padding=(1, 1)
        )
        self.layout["game_log"].update(log_panel)
        
        # Print the layout
        self.console.clear()
        self.console.print(self.layout)
        
        # Capture frame for video if recording
        if self.record_video:
            # Limit frame rate
            current_time = time.time()
            if current_time - self.last_render_time >= 1.0/self.video_fps:
                self._capture_and_store_frame()
                self.last_render_time = current_time
    
    def reset(self, *args, **kwargs):
        """Reset the environment and rendering components"""
        result = self.env.reset(*args, **kwargs)
        self.reset_render()
        self._render()
        return result
    
    def step(self, action: str) -> Tuple[Optional[Rewards], bool, bool, Optional[Info]]:
        """Process a step in the environment and update the rendering"""
        step_results = self.env.step(action=action)
        self._render()
        return step_results
    
    def close(self):
        """Clean up resources and save video if recording"""
        if self.record_video and self.frames:
            self._save_video()
        return self.env.close()