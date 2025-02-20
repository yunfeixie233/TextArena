# # import curses

# # def hex_to_rgb(hex_color):
# #     """Convert a hex string like '#0B2D2E' to (r, g, b) in curses range (0-1000)."""
# #     hex_color = hex_color.lstrip('#')
# #     rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
# #     return tuple(int(c * 1000 / 255) for c in rgb)

# # def draw_chess_board(win, width, height):
# #     """Draws a dynamically centered, checkered chessboard with black chess symbols."""
# #     win.clear()
# #     win.box()  # Reapply border
    
# #     # Fill the entire window with background color
# #     max_y, max_x = win.getmaxyx()
# #     for y in range(1, max_y-1):
# #         win.addstr(y, 1, " " * (max_x-2), curses.color_pair(1))
    
# #     # Chess pieces using Unicode symbols (all black color)
# #     # Black pieces: solid symbols, White pieces: outlined symbols
# #     pieces = [
# #         ["♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜"],
# #         ["♟", "♟", "♟", "♟", "♟", "♟", "♟", "♟"],
# #         [" ", " ", " ", " ", " ", " ", " ", " "],
# #         [" ", " ", " ", " ", " ", " ", " ", " "],
# #         [" ", " ", " ", " ", " ", " ", " ", " "],
# #         [" ", " ", " ", " ", " ", " ", " ", " "],
# #         ["♙", "♙", "♙", "♙", "♙", "♙", "♙", "♙"],
# #         ["♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖"]
# #     ]
    
# #     # Calculate the starting position to center the board
# #     start_x = max((width - 16) // 2, 1)  # Each square is 2 chars wide
# #     start_y = max((height - 8) // 2, 1)   # Each square is 1 char tall

# #     # Draw the checkered board
# #     for row in range(8):
# #         for col in range(8):
# #             # Determine square color (alternate between LIGHT_SQUARE and DARK_SQUARE)
# #             is_light_square = (row + col) % 2 == 0
# #             square_pair = 2 if is_light_square else 3
            
# #             # Calculate position
# #             pos_x = start_x + col * 2
# #             pos_y = start_y + row
            
# #             # Draw square with or without piece
# #             if pos_y < height - 1 and pos_x < width - 2:
# #                 piece = pieces[row][col]
# #                 if piece.strip():  # If there's a piece
# #                     # For white pieces (bottom rows), use white text on squares
# #                     if row > 5:
# #                         win.addstr(pos_y, pos_x, piece + " ", curses.color_pair(square_pair) | curses.COLOR_WHITE)
# #                     else:  # For black pieces (top rows), use bold black
# #                         win.addstr(pos_y, pos_x, piece + " ", curses.color_pair(square_pair) | curses.A_BOLD)
# #                 else:  # Empty square
# #                     win.addstr(pos_y, pos_x, "  ", curses.color_pair(square_pair))
    
# #     win.refresh()

# # def draw_game_state(win):
# #     """Displays the game state information safely."""
# #     win.clear()
# #     win.box()  # Ensure borders remain visible
# #     max_y, max_x = win.getmaxyx()
    
# #     # Fill the entire window with background color
# #     for y in range(1, max_y-1):
# #         win.addstr(y, 1, " " * (max_x-2), curses.color_pair(1))
    
# #     if max_y < 10 or max_x < 20:
# #         return  # Prevent drawing if window is too small
    
# #     try:
# #         win.addstr(2, 2, "Game State:", curses.color_pair(4) | curses.A_BOLD)
# #         win.addstr(4, 2, "Turn: 20 / 50", curses.color_pair(5) | curses.A_BOLD)
# #         win.addstr(6, 2, "Player 1: White", curses.color_pair(6))
# #         win.addstr(7, 2, "Player 2: Black", curses.color_pair(7))
# #     except curses.error:
# #         pass  # Ignore errors when writing out of bounds

# #     win.refresh()

# # def draw_chat_history(win):
# #     """Renders chat messages in styled bubbles."""
# #     win.clear()
# #     win.box()  # Ensure borders remain visible
    
# #     max_y, max_x = win.getmaxyx()
    
# #     # Fill the entire window with background color
# #     for y in range(1, max_y-1):
# #         win.addstr(y, 1, " " * (max_x-2), curses.color_pair(1))
    
# #     messages = [
# #         ("Player 1", "Pawn to E4", "left"),
# #         ("Player 2", "Knight to C6", "right"),
# #         ("Game", "Player 1's turn", "center"),
# #         ("Player 1", "Queen to H5", "left"),
# #         ("Game", "Check!", "center"),
# #     ]
    
# #     y = 2
# #     for sender, text, align in messages:
# #         if y < max_y - 1:
# #             if sender == "Game":
# #                 message = f"{sender}: {text}"
# #                 win.addstr(y, max(2, (max_x // 2) - (len(message) // 2)), message, curses.color_pair(5) | curses.A_BOLD)
# #             elif sender == "Player 1":
# #                 win.addstr(y, 2, f"{sender}: {text}", curses.color_pair(6) | curses.A_BOLD)
# #             elif sender == "Player 2":
# #                 message = f"{sender}: {text}"
# #                 win.addstr(y, max(2, max_x - len(message) - 2), message, curses.color_pair(7) | curses.A_BOLD)
# #             y += 2
    
# #     win.refresh()

# # def main(stdscr):
# #     # Initialize curses
# #     curses.start_color()
# #     curses.curs_set(0)  # Hide cursor
# #     curses.noecho()
# #     curses.cbreak()
# #     stdscr.keypad(True)

# #     # Color definitions - Theme-matched color scheme
# #     # 1: BACKGROUND - Main application background (dark teal)
# #     # 2: LIGHT_SQUARE - Light squares on chess board (light teal)
# #     # 3: DARK_SQUARE - Dark squares on chess board (dark teal)
# #     # 4: BORDER - Border and headers (teal accent)
# #     # 5: GAME_MSG - Game messages and turn indicator (purple)
# #     # 6: PLAYER1 - Player 1 (White) color (blue)
# #     # 7: PLAYER2 - Player 2 (Black) color (orange)
    
# #     # Define custom colors if supported
# #     if curses.can_change_color():
# #         # Background color (dark teal from --background)
# #         bg_color = hex_to_rgb("#031317")  # Matches your --background: 183 75% 7%
# #         curses.init_color(10, bg_color[0], bg_color[1], bg_color[2])
        
# #         # Border color (teal accent from --sidebar-primary)
# #         border_color = hex_to_rgb("#0D7269")  # Matches your --sidebar-primary: 168 47% 30%
# #         curses.init_color(11, border_color[0], border_color[1], border_color[2])
        
# #         # Light square (slightly lighter teal)
# #         light_square = hex_to_rgb("#133b2f")  # Lighter version of secondary
# #         curses.init_color(12, light_square[0], light_square[1], light_square[2])
        
# #         # Dark square (deeper teal from --card)
# #         dark_square = hex_to_rgb("#030E0A")  # Matches your --card: 168 47% 4%
# #         curses.init_color(13, dark_square[0], dark_square[1], dark_square[2])
        
# #         # Player colors (from your chart colors)
# #         player1_color = hex_to_rgb("#2673E6")  # Matches your --chart-1: 220 70% 50%
# #         curses.init_color(14, player1_color[0], player1_color[1], player1_color[2])
        
# #         player2_color = hex_to_rgb("#E68618")  # Matches your --chart-3: 30 80% 55%
# #         curses.init_color(15, player2_color[0], player2_color[1], player2_color[2])
        
# #         game_msg_color = hex_to_rgb("#A742E6")  # Matches your --chart-4: 280 65% 60%
# #         curses.init_color(16, game_msg_color[0], game_msg_color[1], game_msg_color[2])
        
# #         # Initialize standard color pairs
# #         curses.init_pair(1, curses.COLOR_WHITE, 10)    # Background
# #         curses.init_pair(2, curses.COLOR_WHITE, 12)    # Light square with white text 
# #         curses.init_pair(3, curses.COLOR_WHITE, 13)    # Dark square with white text
# #         curses.init_pair(4, 11, 10)                    # Border/header
# #         curses.init_pair(5, 16, 10)                    # Game messages
# #         curses.init_pair(6, 14, 10)                    # Player 1
# #         curses.init_pair(7, 15, 10)                    # Player 2
# #     else:
# #         # Fallback colors for terminals with limited color support
# #         curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Background
# #         curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Light square
# #         curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Dark square
# #         curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Border/header
# #         curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Game messages
# #         curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Player 1
# #         curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Player 2

# #     # Set background
# #     stdscr.bkgd(' ', curses.color_pair(1))
# #     stdscr.refresh()

# #     while True:
# #         # Get current screen size dynamically
# #         height, width = stdscr.getmaxyx()
# #         half_width = max(width // 2, 20)
# #         half_height = max(height // 2, 10)

# #         # Prevent blank screen: Clear and Reapply Background
# #         stdscr.erase()
# #         stdscr.bkgd(' ', curses.color_pair(1))
        
# #         # Fill entire screen with background color
# #         for y in range(height):
# #             stdscr.addstr(y, 0, " " * (width-1), curses.color_pair(1))
            
# #         stdscr.refresh()

# #         # Create new windows for each section
# #         game_board = curses.newwin(half_height, half_width, 0, 0)
# #         game_state = curses.newwin(half_height, half_width, half_height, 0)
# #         chat_history = curses.newwin(height, half_width, 0, half_width)
        
# #         # Set background for all windows
# #         game_board.bkgd(' ', curses.color_pair(1))
# #         game_state.bkgd(' ', curses.color_pair(1))
# #         chat_history.bkgd(' ', curses.color_pair(1))

# #         # Redraw borders with the border color
# #         game_board.box()
# #         game_state.box()
# #         chat_history.box()

# #         # Add section labels with border/header color
# #         game_board.addstr(0, 2, " Game Board ", curses.color_pair(4) | curses.A_BOLD)
# #         game_state.addstr(0, 2, " Game State ", curses.color_pair(4) | curses.A_BOLD)
# #         chat_history.addstr(0, 2, " Chat History ", curses.color_pair(4) | curses.A_BOLD)

# #         # Redraw UI elements dynamically
# #         draw_chess_board(game_board, half_width, half_height)
# #         draw_game_state(game_state)
# #         draw_chat_history(chat_history)

# #         # Handle input and check for resize
# #         key = stdscr.getch()
# #         if key == ord('q'):
# #             break
# #         elif key == curses.KEY_RESIZE:
# #             stdscr.erase()  # Prevent full wipeout but clear previous elements
# #             stdscr.refresh()  # Ensure UI is updated

# # curses.wrapper(main)

# import curses
# from typing import Dict, Optional, Tuple, List, Any, Union


# class DummyState:
#     """Simple state class for testing the renderer"""
#     def __init__(self):
#         self.game_state = {
#             "turn": 1,
#             "max_turns": 30,
#             "current_player": "Player 1",
#             "scores": {0: 10, 1: 5},
#             "status": "In Progress"
#         }
#         self.turn = 1
#         self.max_turns = 30
#         self.num_players = 2
#         self.current_player_id = 0
#         self.logs = [
#             (-1, "Game started"),
#             (0, "Player 1 moves pawn to e4"),
#             (1, "Player 2 moves knight to c6"),
#             (-1, "Turn 1 completed")
#         ]


# class DummyEnv:
#     """Simple environment class for testing the renderer"""
#     def __init__(self):
#         self.state = DummyState()
        
#     def render_keys(self):
#         """Return keys that should be rendered in the game state panel"""
#         return ["turn", "max_turns", "current_player", "status"]
    
#     def create_board_str(self):
#         """Return a simple 'Hello World' board string"""
#         return "Hello World!\nThis is a test board."


# class CursesTerminalRenderer:
#     """
#     Terminal renderer using curses for text-based game environments.
    
#     This renderer creates a responsive layout with sections for:
#     - Game board
#     - Game state information
#     - Player statistics
#     - Game logs
#     """
    
#     # Color definitions in RGB (0-255 range)
#     # These will be converted to curses color ranges (0-1000)
#     COLORS = {
#         "background": (3, 19, 23),      # Dark teal
#         "border": (13, 114, 105),       # Teal accent
#         "light_square": (19, 59, 47),   # Light teal
#         "dark_square": (3, 14, 10),     # Dark teal
#         "game_message": (167, 66, 230), # Purple
#         "player_1": (38, 115, 230),     # Blue
#         "player_2": (230, 134, 24),     # Orange
#         "player_3": (230, 77, 51),      # Red
#         "player_4": (94, 230, 60),      # Green
#         "player_5": (230, 196, 24),     # Yellow
#     }
    
#     # Color pair assignments
#     COLOR_PAIRS = {
#         "background": 1,    # Background color
#         "border": 2,        # Border/header color
#         "light_square": 3,  # Light squares on chess board
#         "dark_square": 4,   # Dark squares on chess board
#         "game_message": 5,  # Game messages
#         "player_1": 6,      # Player 1 (usually current player)
#         "player_2": 7,      # Player 2
#         "player_3": 8,      # Player 3
#         "player_4": 9,      # Player 4
#         "player_5": 10,     # Player 5
#     }
    
#     def __init__(self, env):
#         """
#         Initialize the terminal renderer
        
#         Args:
#             env: The game environment to render
#         """
#         self.env = env
#         self.stdscr = None
#         self.has_custom_board = hasattr(env, "create_board_str") and callable(env.create_board_str)
#         self.has_render_keys = hasattr(env, "render_keys") and callable(env.render_keys)
        
#     def hex_to_rgb(self, hex_color):
#         """Convert a hex string like '#0B2D2E' to (r, g, b) in curses range (0-1000)."""
#         hex_color = hex_color.lstrip('#')
#         rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
#         return tuple(int(c * 1000 / 255) for c in rgb)
    
#     def _setup_colors(self):
#         """Initialize color pairs for curses"""
#         if curses.can_change_color():
#             # Convert RGB values to curses range (0-1000)
#             for idx, (name, rgb) in enumerate(self.COLORS.items(), start=10):
#                 r, g, b = rgb
#                 curses.init_color(idx, int(r * 1000 / 255), int(g * 1000 / 255), int(b * 1000 / 255))
            
#             # Define color pairs
#             curses.init_pair(1, curses.COLOR_WHITE, 10)     # Background
#             curses.init_pair(2, 11, 10)                     # Border/header
#             curses.init_pair(3, curses.COLOR_WHITE, 12)     # Light square
#             curses.init_pair(4, curses.COLOR_WHITE, 13)     # Dark square
#             curses.init_pair(5, 14, 10)                     # Game messages
#             curses.init_pair(6, 15, 10)                     # Player 1
#             curses.init_pair(7, 16, 10)                     # Player 2
#             curses.init_pair(8, 17, 10)                     # Player 3
#             curses.init_pair(9, 18, 10)                     # Player 4
#             curses.init_pair(10, 19, 10)                    # Player 5
#         else:
#             # Fallback colors for terminals with limited color support
#             curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Background
#             curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Border/header
#             curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Light square
#             curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Dark square
#             curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Game messages
#             curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)      # Player 1
#             curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Player 2
#             curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)       # Player 3
#             curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Player 4
#             curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Player 5
    
#     def _center_text(self, window, text, y_offset=0):
#         """Center text in a window, handling multiline strings"""
#         height, width = window.getmaxyx()
#         lines = text.split('\n')
        
#         for i, line in enumerate(lines):
#             if i + y_offset < height - 1:  # Avoid writing at bottom-right corner
#                 x = max(0, (width - len(line)) // 2)
#                 try:
#                     window.addstr(i + y_offset, x, line)
#                 except curses.error:
#                     # Catch errors when trying to write at bottom-right corner
#                     pass
    

#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game Board "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get board string from environment if available
#         if self.has_custom_board:
#             board_str = self.env.create_board_str()
#         else:
#             board_str = "Board visualization\nnot available"
        
#         # Center the board in the window
#         self._center_text(win, board_str, y_offset=2)
        
#         win.refresh()
    
#     def draw_game_state(self, win):
#         """Draw game state information"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game State "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get state information
#         game_state = self.env.state.game_state
        
#         # Determine which keys to render
#         render_keys = []
#         if self.has_render_keys:
#             render_keys = self.env.render_keys()
#         else:
#             # Use some basic keys by default
#             render_keys = ["turn", "max_turns", "current_player", "status"]
        
#         # Display the state information
#         y = 2
#         for key in render_keys:
#             if key in game_state and y < height - 1:
#                 value = str(game_state[key])
#                 display_str = f"{key}: {value}"
#                 if len(display_str) > width - 4:
#                     display_str = display_str[:width-7] + "..."
#                 win.addstr(y, 2, display_str, curses.color_pair(5))
#                 y += 1
        
#         # Always show turn information even if not in render_keys
#         if "turn" not in render_keys and y < height - 1:
#             turn_str = f"Turn: {self.env.state.turn}"
#             if hasattr(self.env.state, "max_turns") and self.env.state.max_turns:
#                 turn_str += f"/{self.env.state.max_turns}"
#             win.addstr(y, 2, turn_str, curses.color_pair(5) | curses.A_BOLD)
        
#         win.refresh()
    
#     def draw_player_stats(self, win):
#         """Draw player statistics"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Player Stats "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Find player-specific attributes
#         game_state = self.env.state.game_state
#         player_attributes = {}
        
#         # Look for dictionaries with integer keys (player IDs)
#         for key, value in game_state.items():
#             if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
#                 player_attributes[key] = value
        
#         # Display player information
#         y = 2
#         current_player = self.env.state.current_player_id if hasattr(self.env.state, "current_player_id") else None
        
#         # For each player
#         for player_id in range(self.env.state.num_players):
#             if y >= height - 1:
#                 break
                
#             # Highlight current player
#             color_pair = self.COLOR_PAIRS.get(f"player_{player_id+1}", 6)
#             attributes = curses.A_BOLD if player_id == current_player else 0
            
#             player_str = f"Player {player_id}"
#             if player_id == current_player:
#                 player_str = f"► {player_str}"
                
#             win.addstr(y, 2, player_str, curses.color_pair(color_pair) | attributes)
#             y += 1
            
#             # Display player attributes
#             for attr, values in player_attributes.items():
#                 if player_id in values and y < height - 1:
#                     attr_str = f"  {attr}: {values[player_id]}"
#                     if len(attr_str) > width - 4:
#                         attr_str = attr_str[:width-7] + "..."
#                     win.addstr(y, 2, attr_str)
#                     y += 1
                    
#             y += 1  # Add space between players
        
#         win.refresh()
    
#     def draw_game_log(self, win):
#         """Draw game log messages"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game Log "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get game logs
#         logs = self.env.state.logs if hasattr(self.env.state, "logs") else []
        
#         # Display logs (most recent first, up to window height)
#         max_logs = height - 3
#         recent_logs = logs[-max_logs:] if len(logs) > max_logs else logs
        
#         for i, (sender, message) in enumerate(recent_logs):
#             if i >= max_logs:
#                 break
                
#             y = max_logs - i + 1  # Display from bottom up
            
#             # Format by sender type
#             if sender == -1:  # Game message
#                 prefix = "GAME: "
#                 color = curses.color_pair(5)  # Game message color
#             else:
#                 prefix = f"P{sender}: "
#                 color_pair = self.COLOR_PAIRS.get(f"player_{sender+1}", 6)
#                 color = curses.color_pair(color_pair)
            
#             # Format and display message
#             log_str = f"{prefix}{message}"
#             if len(log_str) > width - 4:
#                 log_str = log_str[:width-7] + "..."
                
#             try:
#                 win.addstr(y, 2, log_str, color)
#             except curses.error:
#                 # Handle potential curses errors
#                 pass
        
#         win.refresh()
    
#     def render(self, stdscr):
#         """Main render function"""
#         self.stdscr = stdscr
        
#         # Initialize curses
#         curses.start_color()
#         curses.curs_set(0)  # Hide cursor
#         curses.noecho()
#         curses.cbreak()
#         stdscr.keypad(True)
        
#         # Setup colors
#         self._setup_colors()
        
#         # Set background
#         stdscr.bkgd(' ', curses.color_pair(1))
#         stdscr.refresh()
        
#         # Main rendering loop
#         while True:
#             # Get current screen size
#             height, width = stdscr.getmaxyx()
#             half_width = max(width // 2, 20)
#             half_height = max(height // 2, 10)
            
#             # Clear screen and reapply background
#             stdscr.erase()
#             stdscr.bkgd(' ', curses.color_pair(1))
            
#             # Fill screen with background color
#             for y in range(height):
#                 try:
#                     stdscr.addstr(y, 0, " " * (width-1), curses.color_pair(1))
#                 except curses.error:
#                     # Handle potential curses errors at screen edges
#                     pass
                    
#             stdscr.refresh()
            
#             # Create windows for each section
#             if self.has_custom_board:
#                 # Split left column for board and game state
#                 game_board = curses.newwin(half_height, half_width, 0, 0)
#                 game_state = curses.newwin(half_height, half_width, half_height, 0)
#                 right_column_height = height
#             else:
#                 # Use full left column for game state
#                 game_board = None
#                 game_state = curses.newwin(height, half_width, 0, 0)
#                 right_column_height = height
            
#             # Create right column windows
#             player_stats = curses.newwin(half_height, half_width, 0, half_width)
#             game_log = curses.newwin(height - half_height, half_width, half_height, half_width)
            
#             # Set background for all windows
#             game_state.bkgd(' ', curses.color_pair(1))
#             player_stats.bkgd(' ', curses.color_pair(1))
#             game_log.bkgd(' ', curses.color_pair(1))
#             if game_board:
#                 game_board.bkgd(' ', curses.color_pair(1))
            
#             # Draw content in each window
#             if game_board:
#                 self.draw_game_board(game_board)
#             self.draw_game_state(game_state)
#             self.draw_player_stats(player_stats)
#             self.draw_game_log(game_log)
            
#             # Handle input
#             key = stdscr.getch()
#             if key == ord('q'):
#                 break
#             elif key == curses.KEY_RESIZE:
#                 # Handle terminal resize
#                 stdscr.erase()
#                 stdscr.refresh()


# def main():
#     """Test the renderer with dummy environment"""
#     env = DummyEnv()
#     renderer = CursesTerminalRenderer(env)
#     curses.wrapper(renderer.render)


# if __name__ == "__main__":
#     main()
import textarena as ta
import curses
from typing import Dict, Optional, Tuple, List, Any, Union


class DummyState:
    """Simple state class for testing the renderer"""
    def __init__(self):
        self.game_state = {
            "turn": 1,
            "max_turns": 30,
            "current_player": "Player 1",
            "scores": {0: 10, 1: 5},
            "status": "In Progress"
        }
        self.turn = 1
        self.max_turns = 30
        self.num_players = 2
        self.current_player_id = 0
        self.logs = [
            (-1, "Game started"),
            (0, "Player 1 moves pawn to e4"),
            (1, "Player 2 moves knight to c6"),
            (-1, "Turn 1 completed")
        ]


class DummyEnv:
    """Simple environment class for testing the renderer"""
    def __init__(self):
        self.state = DummyState()
        
    def render_keys(self):
        """Return keys that should be rendered in the game state panel"""
        return ["turn", "max_turns", "current_player", "status"]
    
    def create_board_str(self):
        """Return a simple 'Hello World' board string"""
        return "Hello World!\nThis is a test board."


# class CursesTerminalRenderer:
#     """
#     Terminal renderer using curses for text-based game environments.
    
#     This renderer creates a responsive layout with sections for:
#     - Game board
#     - Game state information
#     - Player statistics
#     - Game logs
#     """
    
#     # Color definitions in RGB (0-255 range)
#     # These will be converted to curses color ranges (0-1000)
#     COLORS = {
#         "background": (3, 19, 23),      # Dark teal
#         "border": (13, 114, 105),       # Teal accent
#         "light_square": (19, 59, 47),   # Light teal
#         "dark_square": (3, 14, 10),     # Dark teal
#         "game_message": (167, 66, 230), # Purple
#         "player_1": (38, 115, 230),     # Blue
#         "player_2": (230, 134, 24),     # Orange
#         "player_3": (230, 77, 51),      # Red
#         "player_4": (94, 230, 60),      # Green
#         "player_5": (230, 196, 24),     # Yellow
#     }
    
#     # Color pair assignments
#     COLOR_PAIRS = {
#         "background": 1,    # Background color
#         "border": 2,        # Border/header color
#         "light_square": 3,  # Light squares on chess board
#         "dark_square": 4,   # Dark squares on chess board
#         "game_message": 5,  # Game messages
#         "player_1": 6,      # Player 1 (usually current player)
#         "player_2": 7,      # Player 2
#         "player_3": 8,      # Player 3
#         "player_4": 9,      # Player 4
#         "player_5": 10,     # Player 5
#     }
    
#     def __init__(self, env):
#         """
#         Initialize the terminal renderer
        
#         Args:
#             env: The game environment to render
#         """
#         self.env = env
#         self.stdscr = None
#         self.has_custom_board = hasattr(env, "create_board_str") and callable(env.create_board_str)
#         self.has_render_keys = hasattr(env, "render_keys") and callable(env.render_keys)
        
#     def hex_to_rgb(self, hex_color):
#         """Convert a hex string like '#0B2D2E' to (r, g, b) in curses range (0-1000)."""
#         hex_color = hex_color.lstrip('#')
#         rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
#         return tuple(int(c * 1000 / 255) for c in rgb)
    
#     def _setup_colors(self):
#         """Initialize color pairs for curses"""
#         if curses.can_change_color():
#             # Convert RGB values to curses range (0-1000)
#             for idx, (name, rgb) in enumerate(self.COLORS.items(), start=10):
#                 r, g, b = rgb
#                 curses.init_color(idx, int(r * 1000 / 255), int(g * 1000 / 255), int(b * 1000 / 255))
            
#             # Define color pairs
#             curses.init_pair(1, curses.COLOR_WHITE, 10)     # Background
#             curses.init_pair(2, 11, 10)                     # Border/header
#             curses.init_pair(3, curses.COLOR_WHITE, 12)     # Light square
#             curses.init_pair(4, curses.COLOR_WHITE, 13)     # Dark square
#             curses.init_pair(5, 14, 10)                     # Game messages
#             curses.init_pair(6, 15, 10)                     # Player 1
#             curses.init_pair(7, 16, 10)                     # Player 2
#             curses.init_pair(8, 17, 10)                     # Player 3
#             curses.init_pair(9, 18, 10)                     # Player 4
#             curses.init_pair(10, 19, 10)                    # Player 5
#         else:
#             # Fallback colors for terminals with limited color support
#             curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Background
#             curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Border/header
#             curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Light square
#             curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Dark square
#             curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Game messages
#             curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)      # Player 1
#             curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Player 2
#             curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)       # Player 3
#             curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Player 4
#             curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Player 5
    
#     def _center_text(self, window, text, y_offset=0):
#         """Center text in a window, handling multiline strings"""
#         height, width = window.getmaxyx()
#         lines = text.split('\n')
        
#         for i, line in enumerate(lines):
#             if i + y_offset < height - 1:  # Avoid writing at bottom-right corner
#                 x = max(0, (width - len(line)) // 2)
#                 try:
#                     window.addstr(i + y_offset, x, line)
#                 except curses.error:
#                     # Catch errors when trying to write at bottom-right corner
#                     pass
    
#     def draw_game_board(self, win):
#         """Draw the game board in its window"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game Board "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Check if env can provide a colored board
#         has_colored_board = hasattr(self.env, "create_colored_board") and callable(self.env.create_colored_board)
        
#         if has_colored_board:
#             # Get colored board representation
#             try:
#                 board_grid = self.env.create_colored_board()
#                 self._draw_colored_board(win, board_grid)
#             except Exception as e:
#                 # Fallback to string representation if colored board fails
#                 board_str = f"Error drawing colored board:\n{str(e)}"
#                 self._center_text(win, board_str, y_offset=2)
#         elif self.has_custom_board:
#             # Get string representation
#             board_str = self.env.create_board_str()
#             self._center_text(win, board_str, y_offset=2)
#         else:
#             board_str = "Board visualization\nnot available"
#             self._center_text(win, board_str, y_offset=2)
        
#         win.refresh()
    
#     def _draw_colored_board(self, win, board_grid):
#         """Draw a colored chess board using cell information"""
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Calculate starting position to center the board
#         # Each chess square is 2 characters wide (piece + space)
#         board_width = 16  # 8 squares × 2 chars
#         board_height = 8  # 8 rows
        
#         start_x = max((width - board_width) // 2, 2)
#         start_y = max((height - board_height) // 2, 2)
        
#         # Draw board coordinates
#         coord_color = curses.color_pair(2)  # Border color
        
#         # Draw column labels (a-h)
#         if start_y > 3:  # Only if there's room
#             col_y = start_y - 1
#             for col in range(8):
#                 col_label = chr(ord('a') + col)
#                 x_pos = start_x + col * 2 + 1
#                 try:
#                     win.addstr(col_y, x_pos, col_label, coord_color)
#                 except curses.error:
#                     pass
                    
#             # Draw row labels (1-8)
#             if start_x > 3:  # Only if there's room
#                 for row in range(8):
#                     row_label = str(8 - row)
#                     y_pos = start_y + row
#                     try:
#                         win.addstr(y_pos, start_x - 2, row_label, coord_color)
#                         win.addstr(y_pos, start_x + board_width + 1, row_label, coord_color)
#                     except curses.error:
#                         pass
                        
#             # Draw column labels at bottom
#             col_y = start_y + board_height
#             if col_y < height - 1:
#                 for col in range(8):
#                     col_label = chr(ord('a') + col)
#                     x_pos = start_x + col * 2 + 1
#                     try:
#                         win.addstr(col_y, x_pos, col_label, coord_color)
#                     except curses.error:
#                         pass
        
#         # Draw the board squares and pieces
#         for row in range(8):
#             for col in range(8):
#                 # Calculate position
#                 pos_x = start_x + col * 2
#                 pos_y = start_y + row
                
#                 if pos_y >= height - 1 or pos_x >= width - 2:
#                     continue  # Skip if out of bounds
                
#                 # Get cell information
#                 cell = board_grid[row][col]
                
#                 # Determine color pair to use
#                 color_pair = curses.color_pair(cell.bg_color)
                
#                 # Add attributes (like bold)
#                 attrs = cell.attrs
                
#                 # Draw the piece with its background
#                 try:
#                     win.addstr(pos_y, pos_x, cell.symbol + " ", color_pair | attrs)
#                 except curses.error:
#                     # Handle potential curses errors at screen edges
#                     pass
                    
#         # Draw frame around the board
#         if start_y > 1 and start_x > 1:
#             # Top border
#             try:
#                 win.addstr(start_y - 1, start_x - 1, '┌' + '─' * board_width + '┐', coord_color)
#             except curses.error:
#                 pass
                
#             # Side borders
#             for i in range(board_height):
#                 if start_y + i < height - 1:
#                     try:
#                         win.addstr(start_y + i, start_x - 1, '│', coord_color)
#                         win.addstr(start_y + i, start_x + board_width, '│', coord_color)
#                     except curses.error:
#                         pass
                        
#             # Bottom border
#             if start_y + board_height < height - 1:
#                 try:
#                     win.addstr(start_y + board_height, start_x - 1, '└' + '─' * board_width + '┘', coord_color)
#                 except curses.error:
#                     pass
    
#     def draw_game_state(self, win):
#         """Draw game state information"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game State "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get state information
#         game_state = self.env.state.game_state
        
#         # Determine which keys to render
#         render_keys = []
#         if self.has_render_keys:
#             render_keys = self.env.render_keys()
#         else:
#             # Use some basic keys by default
#             render_keys = ["turn", "max_turns", "current_player", "status"]
        
#         # Display the state information
#         y = 2
#         for key in render_keys:
#             if key in game_state and y < height - 1:
#                 value = str(game_state[key])
#                 display_str = f"{key}: {value}"
#                 if len(display_str) > width - 4:
#                     display_str = display_str[:width-7] + "..."
#                 win.addstr(y, 2, display_str, curses.color_pair(5))
#                 y += 1
        
#         # Always show turn information even if not in render_keys
#         if "turn" not in render_keys and y < height - 1:
#             turn_str = f"Turn: {self.env.state.turn}"
#             if hasattr(self.env.state, "max_turns") and self.env.state.max_turns:
#                 turn_str += f"/{self.env.state.max_turns}"
#             win.addstr(y, 2, turn_str, curses.color_pair(5) | curses.A_BOLD)
        
#         win.refresh()
    
#     def draw_player_stats(self, win):
#         """Draw player statistics"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Player Stats "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Find player-specific attributes
#         game_state = self.env.state.game_state
#         player_attributes = {}
        
#         # Look for dictionaries with integer keys (player IDs)
#         for key, value in game_state.items():
#             if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
#                 player_attributes[key] = value
        
#         # Display player information
#         y = 2
#         current_player = self.env.state.current_player_id if hasattr(self.env.state, "current_player_id") else None
        
#         # For each player
#         for player_id in range(self.env.state.num_players):
#             if y >= height - 1:
#                 break
                
#             # Highlight current player
#             color_pair = self.COLOR_PAIRS.get(f"player_{player_id+1}", 6)
#             attributes = curses.A_BOLD if player_id == current_player else 0
            
#             player_str = f"Player {player_id}"
#             if player_id == current_player:
#                 player_str = f"► {player_str}"
                
#             win.addstr(y, 2, player_str, curses.color_pair(color_pair) | attributes)
#             y += 1
            
#             # Display player attributes
#             for attr, values in player_attributes.items():
#                 if player_id in values and y < height - 1:
#                     attr_str = f"  {attr}: {values[player_id]}"
#                     if len(attr_str) > width - 4:
#                         attr_str = attr_str[:width-7] + "..."
#                     win.addstr(y, 2, attr_str)
#                     y += 1
                    
#             y += 1  # Add space between players
        
#         win.refresh()
    
#     def draw_game_log(self, win):
#         """Draw game log messages"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game Log "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get game logs
#         logs = self.env.state.logs if hasattr(self.env.state, "logs") else []
        
#         # Display logs (most recent first, up to window height)
#         max_logs = height - 3
#         recent_logs = logs[-max_logs:] if len(logs) > max_logs else logs
        
#         for i, (sender, message) in enumerate(recent_logs):
#             if i >= max_logs:
#                 break
                
#             y = max_logs - i + 1  # Display from bottom up
            
#             # Format by sender type
#             if sender == -1:  # Game message
#                 prefix = "GAME: "
#                 color = curses.color_pair(5)  # Game message color
#             else:
#                 prefix = f"P{sender}: "
#                 color_pair = self.COLOR_PAIRS.get(f"player_{sender+1}", 6)
#                 color = curses.color_pair(color_pair)
            
#             # Format and display message
#             log_str = f"{prefix}{message}"
#             if len(log_str) > width - 4:
#                 log_str = log_str[:width-7] + "..."
                
#             try:
#                 win.addstr(y, 2, log_str, color)
#             except curses.error:
#                 # Handle potential curses errors
#                 pass
        
#         win.refresh()
    
#     def _render_all(self, stdscr):
#         """Render the entire UI"""
#         # Get current screen size
#         height, width = stdscr.getmaxyx()
#         half_width = max(width // 2, 20)
#         half_height = max(height // 2, 10)
        
#         # Clear screen and reapply background
#         stdscr.erase()
#         stdscr.bkgd(' ', curses.color_pair(1))
        
#         # Fill screen with background color
#         for y in range(height):
#             try:
#                 stdscr.addstr(y, 0, " " * (width-1), curses.color_pair(1))
#             except curses.error:
#                 # Handle potential curses errors at screen edges
#                 pass
                
#         stdscr.refresh()
        
#         # Create windows for each section
#         if self.has_custom_board:
#             # Split left column for board and game state
#             game_board = curses.newwin(half_height, half_width, 0, 0)
#             game_state = curses.newwin(half_height, half_width, half_height, 0)
#             right_column_height = height
#         else:
#             # Use full left column for game state
#             game_board = None
#             game_state = curses.newwin(height, half_width, 0, 0)
#             right_column_height = height
        
#         # Create right column windows
#         player_stats = curses.newwin(half_height, half_width, 0, half_width)
#         game_log = curses.newwin(height - half_height, half_width, half_height, half_width)
        
#         # Set background for all windows
#         game_state.bkgd(' ', curses.color_pair(1))
#         player_stats.bkgd(' ', curses.color_pair(1))
#         game_log.bkgd(' ', curses.color_pair(1))
#         if game_board:
#             game_board.bkgd(' ', curses.color_pair(1))
        
#         # Draw content in each window
#         if game_board:
#             self.draw_game_board(game_board)
#         self.draw_game_state(game_state)
#         self.draw_player_stats(player_stats)
#         self.draw_game_log(game_log)
    
#     def render(self, stdscr):
#         """Main render function"""
#         self.stdscr = stdscr
        
#         # Initialize curses
#         curses.start_color()
#         curses.curs_set(0)  # Hide cursor
#         curses.noecho()
#         curses.cbreak()
#         stdscr.keypad(True)
        
#         # Setup colors
#         self._setup_colors()
        
#         # Set background
#         stdscr.bkgd(' ', curses.color_pair(1))
#         stdscr.refresh()
        
#         # Main rendering loop
#         while True:
#             # Render the UI
#             self._render_all(stdscr)
            
#             # Handle input
#             key = stdscr.getch()
#             if key == ord('q'):
#                 break
#             elif key == curses.KEY_RESIZE:
#                 # Handle terminal resize
#                 stdscr.erase()
#                 stdscr.refresh()



# class CursesTerminalRenderer:
#     """
#     Terminal renderer using curses for text-based game environments.
    
#     This renderer creates a responsive layout with sections for:
#     - Game board
#     - Game state information
#     - Player statistics
#     - Game logs
#     """
    
#     # Color definitions in RGB (0-255 range)
#     # These will be converted to curses color ranges (0-1000)
#     COLORS = {
#         "background": (3, 19, 23),      # Dark teal
#         "border": (13, 114, 105),       # Teal accent
#         "light_square": (19, 59, 47),   # Light teal
#         "dark_square": (3, 14, 10),     # Dark teal
#         "game_message": (167, 66, 230), # Purple
#         "player_1": (38, 115, 230),     # Blue
#         "player_2": (230, 134, 24),     # Orange
#         "player_3": (230, 77, 51),      # Red
#         "player_4": (94, 230, 60),      # Green
#         "player_5": (230, 196, 24),     # Yellow
#     }
    
#     # Color pair assignments
#     COLOR_PAIRS = {
#         "background": 1,    # Background color
#         "border": 2,        # Border/header color
#         "light_square": 3,  # Light squares on chess board
#         "dark_square": 4,   # Dark squares on chess board
#         "game_message": 5,  # Game messages
#         "player_1": 6,      # Player 1 (usually current player)
#         "player_2": 7,      # Player 2
#         "player_3": 8,      # Player 3
#         "player_4": 9,      # Player 4
#         "player_5": 10,     # Player 5
#     }
    
#     def __init__(self, env):
#         """
#         Initialize the terminal renderer
        
#         Args:
#             env: The game environment to render
#         """
#         self.env = env
#         self.stdscr = None
#         self.has_custom_board = hasattr(env, "create_board_str") and callable(env.create_board_str)
#         self.has_render_keys = hasattr(env, "render_keys") and callable(env.render_keys)
        
#     def hex_to_rgb(self, hex_color):
#         """Convert a hex string like '#0B2D2E' to (r, g, b) in curses range (0-1000)."""
#         hex_color = hex_color.lstrip('#')
#         rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
#         return tuple(int(c * 1000 / 255) for c in rgb)
    
#     def _setup_colors(self):
#         """Initialize color pairs for curses"""
#         if curses.can_change_color():
#             # Convert RGB values to curses range (0-1000)
#             for idx, (name, rgb) in enumerate(self.COLORS.items(), start=10):
#                 r, g, b = rgb
#                 curses.init_color(idx, int(r * 1000 / 255), int(g * 1000 / 255), int(b * 1000 / 255))
            
#             # Define color pairs
#             curses.init_pair(1, curses.COLOR_WHITE, 10)     # Background
#             curses.init_pair(2, 11, 10)                     # Border/header
#             curses.init_pair(3, curses.COLOR_WHITE, 12)     # Light square
#             curses.init_pair(4, curses.COLOR_WHITE, 13)     # Dark square
#             curses.init_pair(5, 14, 10)                     # Game messages
#             curses.init_pair(6, 15, 10)                     # Player 1
#             curses.init_pair(7, 16, 10)                     # Player 2
#             curses.init_pair(8, 17, 10)                     # Player 3
#             curses.init_pair(9, 18, 10)                     # Player 4
#             curses.init_pair(10, 19, 10)                    # Player 5
#         else:
#             # Fallback colors for terminals with limited color support
#             curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Background
#             curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Border/header
#             curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Light square
#             curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Dark square
#             curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Game messages
#             curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)      # Player 1
#             curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Player 2
#             curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)       # Player 3
#             curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Player 4
#             curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Player 5
    
#     def _center_text(self, window, text, y_offset=0):
#         """Center text in a window, handling multiline strings"""
#         height, width = window.getmaxyx()
#         lines = text.split('\n')
        
#         for i, line in enumerate(lines):
#             if i + y_offset < height - 1:  # Avoid writing at bottom-right corner
#                 x = max(0, (width - len(line)) // 2)
#                 try:
#                     window.addstr(i + y_offset, x, line)
#                 except curses.error:
#                     # Catch errors when trying to write at bottom-right corner
#                     pass
    
#     def draw_game_board(self, win):
#         """Draw the game board in its window"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game Board "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Check if env can provide a colored board
#         has_colored_board = hasattr(self.env, "create_colored_board") and callable(self.env.create_colored_board)
        
#         if has_colored_board:
#             # Get colored board representation
#             try:
#                 board_grid = self.env.create_colored_board()
#                 self._draw_colored_board(win, board_grid)
#             except Exception as e:
#                 # Fallback to string representation if colored board fails
#                 board_str = f"Error drawing colored board:\n{str(e)}"
#                 self._center_text(win, board_str, y_offset=2)
#         elif self.has_custom_board:
#             # Get string representation
#             board_str = self.env.create_board_str()
#             self._center_text(win, board_str, y_offset=2)
#         else:
#             board_str = "Board visualization\nnot available"
#             self._center_text(win, board_str, y_offset=2)
        
#         win.refresh()
    
#     def _draw_colored_board(self, win, board_grid):
#         """Draw a colored chess board using cell information"""
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Calculate starting position to center the board
#         # Each chess square is 2 characters wide (piece + space)
#         board_width = 16  # 8 squares × 2 chars
#         board_height = 8  # 8 rows
        
#         start_x = max((width - board_width) // 2, 2)
#         start_y = max((height - board_height) // 2, 2)
        
#         # Draw board coordinates
#         coord_color = curses.color_pair(2)  # Border color
        
#         # Draw column labels (a-h)
#         if start_y > 3:  # Only if there's room
#             col_y = start_y - 1
#             for col in range(8):
#                 col_label = chr(ord('a') + col)
#                 x_pos = start_x + col * 2 + 1
#                 try:
#                     win.addstr(col_y, x_pos, col_label, coord_color)
#                 except curses.error:
#                     pass
                    
#             # Draw row labels (1-8)
#             if start_x > 3:  # Only if there's room
#                 for row in range(8):
#                     row_label = str(8 - row)
#                     y_pos = start_y + row
#                     try:
#                         win.addstr(y_pos, start_x - 2, row_label, coord_color)
#                         win.addstr(y_pos, start_x + board_width + 1, row_label, coord_color)
#                     except curses.error:
#                         pass
                        
#             # Draw column labels at bottom
#             col_y = start_y + board_height
#             if col_y < height - 1:
#                 for col in range(8):
#                     col_label = chr(ord('a') + col)
#                     x_pos = start_x + col * 2 + 1
#                     try:
#                         win.addstr(col_y, x_pos, col_label, coord_color)
#                     except curses.error:
#                         pass
        
#         # Draw the board squares and pieces
#         for row in range(8):
#             for col in range(8):
#                 # Calculate position
#                 pos_x = start_x + col * 2
#                 pos_y = start_y + row
                
#                 if pos_y >= height - 1 or pos_x >= width - 2:
#                     continue  # Skip if out of bounds
                
#                 # Get cell information
#                 cell = board_grid[row][col]
                
#                 # Determine color pair to use
#                 color_pair = curses.color_pair(cell.bg_color)
                
#                 # Add attributes (like bold)
#                 attrs = cell.attrs
                
#                 # Draw the piece with its background
#                 try:
#                     win.addstr(pos_y, pos_x, cell.symbol + " ", color_pair | attrs)
#                 except curses.error:
#                     # Handle potential curses errors at screen edges
#                     pass
                    
#         # Draw frame around the board
#         if start_y > 1 and start_x > 1:
#             # Top border
#             try:
#                 win.addstr(start_y - 1, start_x - 1, '┌' + '─' * board_width + '┐', coord_color)
#             except curses.error:
#                 pass
                
#             # Side borders
#             for i in range(board_height):
#                 if start_y + i < height - 1:
#                     try:
#                         win.addstr(start_y + i, start_x - 1, '│', coord_color)
#                         win.addstr(start_y + i, start_x + board_width, '│', coord_color)
#                     except curses.error:
#                         pass
                        
#             # Bottom border
#             if start_y + board_height < height - 1:
#                 try:
#                     win.addstr(start_y + board_height, start_x - 1, '└' + '─' * board_width + '┘', coord_color)
#                 except curses.error:
#                     pass
    
#     def draw_game_state(self, win):
#         """Draw game state information"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game State "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get state information
#         game_state = self.env.state.game_state
        
#         # Determine which keys to render
#         render_keys = []
#         if self.has_render_keys:
#             render_keys = self.env.render_keys()
#         else:
#             # Use some basic keys by default
#             render_keys = ["turn", "max_turns", "current_player", "status"]
        
#         # Display the state information
#         y = 2
#         for key in render_keys:
#             if key in game_state and y < height - 1:
#                 value = str(game_state[key])
#                 display_str = f"{key}: {value}"
#                 if len(display_str) > width - 4:
#                     display_str = display_str[:width-7] + "..."
#                 win.addstr(y, 2, display_str, curses.color_pair(5))
#                 y += 1
        
#         # Always show turn information even if not in render_keys
#         if "turn" not in render_keys and y < height - 1:
#             turn_str = f"Turn: {self.env.state.turn}"
#             if hasattr(self.env.state, "max_turns") and self.env.state.max_turns:
#                 turn_str += f"/{self.env.state.max_turns}"
#             win.addstr(y, 2, turn_str, curses.color_pair(5) | curses.A_BOLD)
        
#         win.refresh()
    
#     def draw_player_stats(self, win):
#         """Draw player statistics"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Player Stats "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Find player-specific attributes
#         game_state = self.env.state.game_state
#         player_attributes = {}
        
#         # Look for dictionaries with integer keys (player IDs)
#         for key, value in game_state.items():
#             if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
#                 player_attributes[key] = value
        
#         # Display player information
#         y = 2
#         current_player = self.env.state.current_player_id if hasattr(self.env.state, "current_player_id") else None
        
#         # For each player
#         for player_id in range(self.env.state.num_players):
#             if y >= height - 1:
#                 break
                
#             # Highlight current player
#             color_pair = self.COLOR_PAIRS.get(f"player_{player_id+1}", 6)
#             attributes = curses.A_BOLD if player_id == current_player else 0
            
#             player_str = f"Player {player_id}"
#             if player_id == current_player:
#                 player_str = f"► {player_str}"
                
#             win.addstr(y, 2, player_str, curses.color_pair(color_pair) | attributes)
#             y += 1
            
#             # Display player attributes
#             for attr, values in player_attributes.items():
#                 if player_id in values and y < height - 1:
#                     attr_str = f"  {attr}: {values[player_id]}"
#                     if len(attr_str) > width - 4:
#                         attr_str = attr_str[:width-7] + "..."
#                     win.addstr(y, 2, attr_str)
#                     y += 1
                    
#             y += 1  # Add space between players
        
#         win.refresh()
    
#     def draw_game_log(self, win):
#         """Draw game log messages"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game Log "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get game logs
#         logs = self.env.state.logs if hasattr(self.env.state, "logs") else []
        
#         # Display logs (most recent first, up to window height)
#         max_logs = height - 3
#         recent_logs = logs[-max_logs:] if len(logs) > max_logs else logs
        
#         for i, (sender, message) in enumerate(recent_logs):
#             if i >= max_logs:
#                 break
                
#             y = max_logs - i + 1  # Display from bottom up
            
#             # Format by sender type
#             if sender == -1:  # Game message
#                 prefix = "GAME: "
#                 color = curses.color_pair(5)  # Game message color
#             else:
#                 prefix = f"P{sender}: "
#                 color_pair = self.COLOR_PAIRS.get(f"player_{sender+1}", 6)
#                 color = curses.color_pair(color_pair)
            
#             # Format and display message
#             log_str = f"{prefix}{message}"
#             if len(log_str) > width - 4:
#                 log_str = log_str[:width-7] + "..."
                
#             try:
#                 win.addstr(y, 2, log_str, color)
#             except curses.error:
#                 # Handle potential curses errors
#                 pass
        
#         win.refresh()
    
#     def _render_all(self, stdscr):
#         """Render the entire UI"""
#         # Get current screen size
#         height, width = stdscr.getmaxyx()
#         half_width = max(width // 2, 20)
#         half_height = max(height // 2, 10)
        
#         # Clear screen and reapply background
#         stdscr.erase()
#         stdscr.bkgd(' ', curses.color_pair(1))
        
#         # Fill screen with background color
#         for y in range(height):
#             try:
#                 stdscr.addstr(y, 0, " " * (width-1), curses.color_pair(1))
#             except curses.error:
#                 # Handle potential curses errors at screen edges
#                 pass
                
#         stdscr.refresh()
        
#         # Create windows for each section
#         if self.has_custom_board:
#             # Split left column for board and game state
#             game_board = curses.newwin(half_height, half_width, 0, 0)
#             game_state = curses.newwin(half_height, half_width, half_height, 0)
#             right_column_height = height
#         else:
#             # Use full left column for game state
#             game_board = None
#             game_state = curses.newwin(height, half_width, 0, 0)
#             right_column_height = height
        
#         # Create right column windows
#         player_stats = curses.newwin(half_height, half_width, 0, half_width)
#         game_log = curses.newwin(height - half_height, half_width, half_height, half_width)
        
#         # Set background for all windows
#         game_state.bkgd(' ', curses.color_pair(1))
#         player_stats.bkgd(' ', curses.color_pair(1))
#         game_log.bkgd(' ', curses.color_pair(1))
#         if game_board:
#             game_board.bkgd(' ', curses.color_pair(1))
        
#         # Draw content in each window
#         if game_board:
#             self.draw_game_board(game_board)
#         self.draw_game_state(game_state)
#         self.draw_player_stats(player_stats)
#         self.draw_game_log(game_log)
    
#     def render(self, stdscr):
#         """Main render function"""
#         self.stdscr = stdscr
        
#         # Initialize curses
#         curses.start_color()
#         curses.curs_set(0)  # Hide cursor
#         curses.noecho()
#         curses.cbreak()
#         stdscr.keypad(True)
        
#         # Setup colors
#         self._setup_colors()
        
#         # Set background
#         stdscr.bkgd(' ', curses.color_pair(1))
#         stdscr.refresh()
        
#         # Main rendering loop
#         while True:
#             # Render the UI
#             self._render_all(stdscr)
            
#             # Handle input
#             key = stdscr.getch()
#             if key == ord('q'):
#                 break
#             elif key == curses.KEY_RESIZE:
#                 # Handle terminal resize
#                 stdscr.erase()
#                 stdscr.refresh()
# def main():
#     """Test the renderer with dummy environment"""
#     env = DummyEnv()
#     renderer = CursesTerminalRenderer(env)
#     curses.wrapper(renderer.render)


# import curses
# import os
# import time
# from typing import Dict, Optional, Tuple, List, Any, Union, Set
# import threading

# from textarena.core import Env, RenderWrapper, Rewards, Info

# class CursesTerminalRenderer(RenderWrapper):
#     """
#     Curses-based terminal renderer for text-based game environments.
    
#     This renderer is a drop-in replacement for TerminalRenderWrapper,
#     using curses to render the game state in the terminal.
#     """
    
#     # Color pair assignments
#     COLOR_PAIRS = {
#         "background": 1,    # Background color
#         "border": 2,        # Border/header color
#         "light_square": 3,  # Light squares on chess board
#         "dark_square": 4,   # Dark squares on chess board
#         "game_message": 5,  # Game messages
#         "player_1": 6,      # Player 1 (current player)
#         "player_2": 7,      # Player 2
#         "player_3": 8,      # Player 3
#         "player_4": 9,      # Player 4
#         "player_5": 10,     # Player 5
#     }
    
#     def __init__(
#         self,
#         env: Env,
#         player_names: Optional[Dict[int, str]] = None,
#         **kwargs
#     ):
#         """
#         Initialize the curses terminal renderer
        
#         Args:
#             env: The environment to wrap
#             player_names: Mapping from player IDs to display names
#         """
#         super().__init__(env)
#         self.player_names = player_names or {}
#         self.stdscr = None
#         self.has_custom_board = hasattr(env, "create_board_str") and callable(env.create_board_str)
#         self.has_render_keys = hasattr(env, "terminal_render_keys")
#         self.curses_initialized = False
#         self._render_thread = None
#         self._stop_render = threading.Event()
        
#     def reset_render(self):
#         """Reset the renderer state"""
#         # Initialize curses if not already done
#         if not self.curses_initialized:
#             self._init_curses()
    
#     def _init_curses(self):
#         """Initialize curses environment"""
#         # Start curses in a separate thread
#         if self._render_thread is None:
#             self._stop_render.clear()
#             self._render_thread = threading.Thread(target=self._run_curses_ui)
#             self._render_thread.daemon = True
#             self._render_thread.start()
#             self.curses_initialized = True
    
#     def _run_curses_ui(self):
#         """Run the curses UI in a separate thread"""
#         try:
#             curses.wrapper(self._curses_main_loop)
#         except Exception as e:
#             print(f"Error in curses UI thread: {e}")
    
#     def _curses_main_loop(self, stdscr):
#         """Main curses loop"""
#         self.stdscr = stdscr
        
#         # Initialize curses
#         curses.start_color()
#         curses.curs_set(0)  # Hide cursor
#         curses.noecho()
#         curses.cbreak()
#         stdscr.keypad(True)
        
#         # Setup colors
#         self._setup_colors()
        
#         # Set background
#         stdscr.bkgd(' ', curses.color_pair(1))
        
#         # Main loop
#         while not self._stop_render.is_set():
#             try:
#                 # Render the UI
#                 self._render_all(stdscr)
                
#                 # Check for 'q' key to exit
#                 stdscr.nodelay(True)
#                 key = stdscr.getch()
#                 if key == ord('q'):
#                     break
#                 stdscr.nodelay(False)
                
#                 # Sleep to avoid high CPU usage
#                 time.sleep(0.1)
                
#             except Exception as e:
#                 # Just log the error and continue
#                 try:
#                     height, width = stdscr.getmaxyx()
#                     error_msg = f"Render error: {str(e)[:width-20]}"
#                     stdscr.addstr(height-1, 0, error_msg, curses.color_pair(7) | curses.A_BOLD)
#                     stdscr.refresh()
#                     time.sleep(1)
#                 except:
#                     pass
    
#     def _setup_colors(self):
#         """Initialize color pairs for curses"""
#         if curses.can_change_color():
#             # Background - dark teal
#             curses.init_color(10, 12, 74, 90)  # ~rgb(3, 19, 23)
            
#             # Border - teal accent
#             curses.init_color(11, 51, 443, 412)  # ~rgb(13, 114, 105)
            
#             # Light square - light teal
#             curses.init_color(12, 74, 231, 184)  # ~rgb(19, 59, 47)
            
#             # Dark square - deep teal
#             curses.init_color(13, 12, 55, 39)  # ~rgb(3, 14, 10)
            
#             # Game message - purple
#             curses.init_color(14, 655, 258, 902)  # ~rgb(167, 66, 230)
            
#             # Player colors
#             curses.init_color(15, 149, 451, 902)  # Player 1 - blue
#             curses.init_color(16, 902, 525, 94)   # Player 2 - orange
#             curses.init_color(17, 902, 301, 200)  # Player 3 - red
#             curses.init_color(18, 369, 902, 235)  # Player 4 - green
#             curses.init_color(19, 902, 769, 94)   # Player 5 - yellow
            
#             # Define color pairs
#             curses.init_pair(1, curses.COLOR_WHITE, 10)     # Background
#             curses.init_pair(2, 11, 10)                     # Border/header
#             curses.init_pair(3, curses.COLOR_WHITE, 12)     # Light square
#             curses.init_pair(4, curses.COLOR_WHITE, 13)     # Dark square
#             curses.init_pair(5, 14, 10)                     # Game messages
#             curses.init_pair(6, 15, 10)                     # Player 1
#             curses.init_pair(7, 16, 10)                     # Player 2
#             curses.init_pair(8, 17, 10)                     # Player 3
#             curses.init_pair(9, 18, 10)                     # Player 4
#             curses.init_pair(10, 19, 10)                    # Player 5
#         else:
#             # Fallback colors for terminals with limited color support
#             curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Background
#             curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Border/header
#             curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Light square
#             curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Dark square
#             curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Game messages
#             curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)      # Player 1
#             curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Player 2
#             curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)       # Player 3
#             curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Player 4
#             curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Player 5
    
#     def _center_text(self, window, text, y_offset=0):
#         """Center text in a window, handling multiline strings"""
#         height, width = window.getmaxyx()
#         lines = text.split('\n')
        
#         for i, line in enumerate(lines):
#             if i + y_offset < height - 1:  # Avoid writing at bottom-right corner
#                 x = max(0, (width - len(line)) // 2)
#                 try:
#                     window.addstr(i + y_offset, x, line)
#                 except curses.error:
#                     # Catch errors when trying to write at bottom-right corner
#                     pass
    
#     def draw_game_board(self, win):
#         """Draw the game board in its window"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game Board "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get board string from environment
#         if self.has_custom_board:
#             board_str = self.env.create_board_str()
#         else:
#             # Try to get board from game state
#             board_str = None
#             game_state = self.env.state.game_state
#             if isinstance(game_state, dict):
#                 for key in ['board', 'board_state', 'rendered_board', 'current_board']:
#                     if key in game_state and isinstance(game_state[key], str):
#                         board_str = game_state[key]
#                         break
            
#             if board_str is None:
#                 board_str = "Board visualization\nnot available"
        
#         # Center the board in the window
#         self._center_text(win, board_str, y_offset=2)
        
#         win.refresh()
    
#     def draw_game_state(self, win):
#         """Draw game state information"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game State "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get state information
#         game_state = self.env.state.game_state
        
#         # Determine which keys to render
#         render_keys = []
#         if self.has_render_keys:
#             render_keys = self.env.terminal_render_keys
#         else:
#             # Use some basic keys by default
#             render_keys = ["turn", "max_turns"]
#             # Add any other keys that might be useful
#             for key in ["status", "check", "current_player"]:
#                 if key in game_state:
#                     render_keys.append(key)
        
#         # Display the state information
#         y = 2
#         for key in render_keys:
#             if key in game_state and y < height - 1:
#                 value = str(game_state[key])
#                 # For valid_moves, just show the count
#                 if key == "valid_moves" and isinstance(game_state[key], list):
#                     value = f"{len(game_state[key])} moves"
                
#                 display_str = f"{key}: {value}"
#                 if len(display_str) > width - 4:
#                     display_str = display_str[:width-7] + "..."
#                 win.addstr(y, 2, display_str, curses.color_pair(5))
#                 y += 1
        
#         # Always show turn information even if not in render_keys
#         if "turn" not in render_keys and y < height - 1:
#             turn_str = f"Turn: {self.env.state.turn}"
#             if hasattr(self.env.state, "max_turns") and self.env.state.max_turns:
#                 turn_str += f"/{self.env.state.max_turns}"
#             win.addstr(y, 2, turn_str, curses.color_pair(5) | curses.A_BOLD)
#             y += 1
            
#         # Show current player
#         if y < height - 1 and hasattr(self.env.state, "current_player_id"):
#             current_player = self.env.state.current_player_id
#             player_name = self.player_names.get(current_player, f"Player {current_player}")
            
#             # Use role mapping if available
#             if hasattr(self.env.state, "role_mapping") and current_player in self.env.state.role_mapping:
#                 player_name = self.env.state.role_mapping[current_player]
                
#             color_pair = self.COLOR_PAIRS.get(f"player_{current_player+1}", 6)
#             win.addstr(y, 2, f"Current player: {player_name}", curses.color_pair(color_pair) | curses.A_BOLD)
        
#         win.refresh()
    
#     def draw_player_stats(self, win):
#         """Draw player statistics"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Player Stats "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Find player-specific attributes
#         game_state = self.env.state.game_state
#         player_attributes = {}
        
#         # Look for dictionaries with integer keys (player IDs)
#         if isinstance(game_state, dict):
#             for key, value in game_state.items():
#                 if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
#                     player_attributes[key] = value
        
#         # Display player information
#         y = 2
#         current_player = self.env.state.current_player_id if hasattr(self.env.state, "current_player_id") else None
        
#         # For each player
#         for player_id in range(self.env.state.num_players):
#             if y >= height - 1:
#                 break
                
#             # Highlight current player
#             color_pair = self.COLOR_PAIRS.get(f"player_{player_id+1}", 6)
#             attributes = curses.A_BOLD if player_id == current_player else 0
            
#             # Get player name
#             player_name = self.player_names.get(player_id, f"Player {player_id}")
#             if hasattr(self.env.state, "role_mapping") and player_id in self.env.state.role_mapping:
#                 player_name = self.env.state.role_mapping[player_id]
                
#             if player_id == current_player:
#                 player_str = f"► {player_name}"
#             else:
#                 player_str = f"  {player_name}"
                
#             win.addstr(y, 2, player_str, curses.color_pair(color_pair) | attributes)
#             y += 1
            
#             # Display player attributes
#             for attr, values in player_attributes.items():
#                 if player_id in values and y < height - 1:
#                     attr_str = f"  {attr}: {values[player_id]}"
#                     if len(attr_str) > width - 4:
#                         attr_str = attr_str[:width-7] + "..."
#                     win.addstr(y, 2, attr_str)
#                     y += 1
                    
#             y += 1  # Add space between players
        
#         win.refresh()
    
#     def draw_game_log(self, win):
#         """Draw game log messages"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game Log "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get game logs
#         logs = self.env.state.logs if hasattr(self.env.state, "logs") else []
        
#         # Display logs (most recent first, up to window height)
#         max_logs = height - 3
#         recent_logs = logs[-max_logs:] if len(logs) > max_logs else logs
        
#         for i, (sender, message) in enumerate(recent_logs):
#             if i >= max_logs:
#                 break
                
#             y = max_logs - i + 1  # Display from bottom up
            
#             # Format by sender type
#             if sender == -1:  # Game message
#                 prefix = "GAME: "
#                 color = curses.color_pair(5)  # Game message color
#             else:
#                 # Use role mapping or player names if available
#                 player_name = f"P{sender}"
#                 if sender in self.player_names:
#                     player_name = self.player_names[sender]
#                 elif hasattr(self.env.state, "role_mapping") and sender in self.env.state.role_mapping:
#                     player_name = self.env.state.role_mapping[sender]
                    
#                 prefix = f"{player_name}: "
#                 color_pair = self.COLOR_PAIRS.get(f"player_{sender+1}", 6)
#                 color = curses.color_pair(color_pair)
            
#             # Format and display message
#             log_str = f"{prefix}{message}"
#             if len(log_str) > width - 4:
#                 log_str = log_str[:width-7] + "..."
                
#             try:
#                 win.addstr(y, 2, log_str, color)
#             except curses.error:
#                 # Handle potential curses errors
#                 pass
        
#         win.refresh()
    
#     def _render_all(self, stdscr):
#         """Render the entire UI"""
#         # Get current screen size
#         height, width = stdscr.getmaxyx()
#         half_width = max(width // 2, 20)
#         half_height = max(height // 2, 10)
        
#         # Clear screen and reapply background
#         stdscr.erase()
#         stdscr.bkgd(' ', curses.color_pair(1))
        
#         # Fill screen with background color
#         for y in range(height):
#             try:
#                 stdscr.addstr(y, 0, " " * (width-1), curses.color_pair(1))
#             except curses.error:
#                 # Handle potential curses errors at screen edges
#                 pass
                
#         stdscr.refresh()
        
#         # Create windows for each section
#         if self.has_custom_board:
#             # Split left column for board and game state
#             game_board = curses.newwin(half_height, half_width, 0, 0)
#             game_state = curses.newwin(half_height, half_width, half_height, 0)
#         else:
#             # Use full left column for game state
#             game_board = None
#             game_state = curses.newwin(height, half_width, 0, 0)
        
#         # Create right column windows
#         player_stats = curses.newwin(half_height, half_width, 0, half_width)
#         game_log = curses.newwin(height - half_height, half_width, half_height, half_width)
        
#         # Set background for all windows
#         game_state.bkgd(' ', curses.color_pair(1))
#         player_stats.bkgd(' ', curses.color_pair(1))
#         game_log.bkgd(' ', curses.color_pair(1))
#         if game_board:
#             game_board.bkgd(' ', curses.color_pair(1))
        
#         # Draw content in each window
#         if game_board:
#             self.draw_game_board(game_board)
#         self.draw_game_state(game_state)
#         self.draw_player_stats(player_stats)
#         self.draw_game_log(game_log)
    
#     def get_observation(self):
#         """Get observation for the current player"""
#         if not self.curses_initialized:
#             self.reset_render()
            
#         if hasattr(self.env, 'get_observation'):
#             return self.env.get_observation()
        
#         # Simple fallback implementation if needed
#         player_id = self.env.state.current_player_id
#         if hasattr(self.env, '_generate_player_prompt'):
#             observation = self.env._generate_player_prompt(player_id, self.env.state.game_state)
#         else:
#             observation = f"Player {player_id}'s turn"
            
#         return player_id, observation
    
#     def step(self, action) -> Tuple[Rewards, bool, bool, Info]:
#         """Process a step in the environment and update the rendering"""
#         if not self.curses_initialized:
#             self.reset_render()
            
#         # Call the wrapped environment's step method
#         return self.env.step(action=action)
        
#     def reset(self, *args, **kwargs):
#         """Reset the environment and renderer"""
#         # Reset the wrapped environment
#         result = self.env.reset(*args, **kwargs)
        
#         # Initialize rendering if needed
#         self.reset_render()
        
#         return result
    
#     def close(self):
#         """Close the environment and clean up resources"""
#         # Stop the rendering thread
#         if self._render_thread is not None:
#             self._stop_render.set()
#             self._render_thread.join(timeout=1)
#             self._render_thread = None
#             self.curses_initialized = False
        
#         # Close the wrapped environment
#         if hasattr(self.env, 'close'):
#             return self.env.close()
#         return {}




# import curses
# import os
# import time
# from typing import Dict, Optional, Tuple, List, Any, Union, Set
# import threading

# from textarena.core import Env, RenderWrapper, Rewards, Info

# class CursesTerminalRenderer(RenderWrapper):
#     """
#     Curses-based terminal renderer for text-based game environments.
    
#     This renderer is a drop-in replacement for TerminalRenderWrapper,
#     using curses to render the game state in the terminal.
#     """
    
#     # Color pair assignments
#     COLOR_PAIRS = {
#         "background": 1,    # Background color - dark teal/black
#         "border": 2,        # Border/header color - teal accent
#         "light_square": 3,  # Light squares on chess board - light blue-green
#         "dark_square": 4,   # Dark squares on chess board - dark blue-green
#         "game_message": 5,  # Game messages - purple/magenta
#         "player_1": 6,      # Player 1 (White) - blue
#         "player_2": 7,      # Player 2 (Black) - orange/yellow
#         "player_3": 8,      # Player 3 - red
#         "player_4": 9,      # Player 4 - green
#         "player_5": 10,     # Player 5 - yellow
#     }
    
#     def __init__(
#         self,
#         env: Env,
#         player_names: Optional[Dict[int, str]] = None,
#         **kwargs
#     ):
#         """
#         Initialize the curses terminal renderer
        
#         Args:
#             env: The environment to wrap
#             player_names: Mapping from player IDs to display names
#         """
#         super().__init__(env)
#         self.player_names = player_names or {}
#         self.stdscr = None
#         self.has_custom_board = hasattr(env, "create_board_str") and callable(env.create_board_str)
#         self.has_render_keys = hasattr(env, "terminal_render_keys")
#         self.curses_initialized = False
#         self._render_thread = None
#         self._stop_render = threading.Event()
        
#     def reset_render(self):
#         """Reset the renderer state"""
#         # Initialize curses if not already done
#         if not self.curses_initialized:
#             self._init_curses()
    
#     def _init_curses(self):
#         """Initialize curses environment"""
#         # Start curses in a separate thread
#         if self._render_thread is None:
#             self._stop_render.clear()
#             self._render_thread = threading.Thread(target=self._run_curses_ui)
#             self._render_thread.daemon = True
#             self._render_thread.start()
#             self.curses_initialized = True
    
#     def _run_curses_ui(self):
#         """Run the curses UI in a separate thread"""
#         try:
#             curses.wrapper(self._curses_main_loop)
#         except Exception as e:
#             print(f"Error in curses UI thread: {e}")
    
#     def _curses_main_loop(self, stdscr):
#         """Main curses loop"""
#         self.stdscr = stdscr
        
#         # Initialize curses
#         curses.start_color()
#         curses.curs_set(0)  # Hide cursor
#         curses.noecho()
#         curses.cbreak()
#         stdscr.keypad(True)
        
#         # Setup colors
#         self._setup_colors()
        
#         # Set background
#         stdscr.bkgd(' ', curses.color_pair(1))
        
#         # Main loop
#         while not self._stop_render.is_set():
#             try:
#                 # Render the UI
#                 self._render_all(stdscr)
                
#                 # Check for 'q' key to exit
#                 stdscr.nodelay(True)
#                 key = stdscr.getch()
#                 if key == ord('q'):
#                     break
#                 stdscr.nodelay(False)
                
#                 # Sleep to avoid high CPU usage
#                 time.sleep(0.1)
                
#             except Exception as e:
#                 # Just log the error and continue
#                 try:
#                     height, width = stdscr.getmaxyx()
#                     error_msg = f"Render error: {str(e)[:width-20]}"
#                     stdscr.addstr(height-1, 0, error_msg, curses.color_pair(7) | curses.A_BOLD)
#                     stdscr.refresh()
#                     time.sleep(1)
#                 except:
#                     pass
    
#     def _setup_colors(self):
#         """Initialize color pairs for curses"""
#         if curses.can_change_color():
#             # Background - very dark teal/black
#             curses.init_color(10, 0, 39, 47)  # ~rgb(0, 10, 12)
            
#             # Border - teal accent
#             curses.init_color(11, 51, 443, 412)  # ~rgb(13, 114, 105)
            
#             # Light square - light blue-green
#             curses.init_color(12, 70, 231, 184)  # ~rgb(18, 59, 47)
            
#             # Dark square - dark blue-green 
#             curses.init_color(13, 12, 55, 39)  # ~rgb(3, 14, 10)
            
#             # Game message - purple
#             curses.init_color(14, 655, 258, 902)  # ~rgb(167, 66, 230)
            
#             # Player colors
#             curses.init_color(15, 149, 451, 902)  # Player 1 (White) - blue
#             curses.init_color(16, 902, 525, 94)   # Player 2 (Black) - orange
#             curses.init_color(17, 902, 301, 200)  # Player 3 - red
#             curses.init_color(18, 369, 902, 235)  # Player 4 - green
#             curses.init_color(19, 902, 769, 94)   # Player 5 - yellow
            
#             # Define color pairs
#             curses.init_pair(1, curses.COLOR_WHITE, 10)     # Background
#             curses.init_pair(2, 11, 10)                     # Border/header
#             curses.init_pair(3, curses.COLOR_WHITE, 12)     # Light square
#             curses.init_pair(4, curses.COLOR_WHITE, 13)     # Dark square
#             curses.init_pair(5, 14, 10)                     # Game messages
#             curses.init_pair(6, 15, 10)                     # Player 1 (White)
#             curses.init_pair(7, 16, 10)                     # Player 2 (Black)
#             curses.init_pair(8, 17, 10)                     # Player 3
#             curses.init_pair(9, 18, 10)                     # Player 4
#             curses.init_pair(10, 19, 10)                    # Player 5
#         else:
#             # Fallback colors for terminals with limited color support
#             curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Background
#             curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Border/header
#             curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)      # Light square
#             curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Dark square
#             curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Game messages
#             curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)      # Player 1 (White)
#             curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Player 2 (Black)
#             curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)       # Player 3
#             curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Player 4
#             curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Player 5
    
#     def _center_text(self, window, text, y_offset=0):
#         """Center text in a window, handling multiline strings"""
#         height, width = window.getmaxyx()
#         lines = text.split('\n')
        
#         for i, line in enumerate(lines):
#             if i + y_offset < height - 1:  # Avoid writing at bottom-right corner
#                 x = max(0, (width - len(line)) // 2)
#                 try:
#                     window.addstr(i + y_offset, x, line)
#                 except curses.error:
#                     # Catch errors when trying to write at bottom-right corner
#                     pass
    
#     def draw_chess_board(self, win, board_str):
#         """Draw a chess board with proper checkered background"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game Board "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Parse board string to extract pieces
#         lines = board_str.split('\n')
#         board_lines = []
#         board_start = False
        
#         # Extract just the board part (ignore coordinates/border)
#         for line in lines:
#             if '┌' in line:
#                 board_start = True
#                 continue
#             if '└' in line:
#                 break
#             if board_start and '│' in line:
#                 # Extract just the board content between the pipes
#                 parts = line.split('│')
#                 if len(parts) > 2:
#                     board_lines.append(parts[1].strip())
        
#         # If we couldn't parse the board properly, just center the text
#         if not board_lines:
#             self._center_text(win, board_str, y_offset=2)
#             win.refresh()
#             return
            
#         # Calculate board position to center it
#         board_height = len(board_lines)
#         board_width = max(len(line) for line in board_lines)
        
#         start_y = max(2, (height - board_height - 4) // 2)
#         start_x = max(4, (width - board_width - 4) // 2)
        
#         # Draw column labels (a-h) at top
#         col_y = start_y - 1
#         for i, label in enumerate('abcdefgh'):
#             if 0 <= col_y < height-1 and start_x + i*2 < width-1:
#                 try:
#                     win.addstr(col_y, start_x + i*2, label, curses.color_pair(2))
#                 except curses.error:
#                     pass
        
#         # Draw column labels (a-h) at bottom
#         col_y = start_y + board_height
#         for i, label in enumerate('abcdefgh'):
#             if 0 <= col_y < height-1 and start_x + i*2 < width-1:
#                 try:
#                     win.addstr(col_y, start_x + i*2, label, curses.color_pair(2))
#                 except curses.error:
#                     pass
        
#         # Draw row labels (8-1) and checkered board with pieces
#         for row_idx, line in enumerate(board_lines):
#             row_num = 8 - row_idx
#             # Draw row number on left
#             if 0 <= start_y + row_idx < height-1 and start_x - 2 >= 0:
#                 try:
#                     win.addstr(start_y + row_idx, start_x - 2, str(row_num), curses.color_pair(2))
#                 except curses.error:
#                     pass
                
#             # Draw row number on right
#             if 0 <= start_y + row_idx < height-1 and start_x + board_width + 1 < width:
#                 try:
#                     win.addstr(start_y + row_idx, start_x + board_width + 1, str(row_num), curses.color_pair(2))
#                 except curses.error:
#                     pass
            
#             # Draw checkered board with pieces
#             for col_idx, char in enumerate(line):
#                 if col_idx >= board_width or start_y + row_idx >= height-1 or start_x + col_idx >= width-1:
#                     continue
                    
#                 # Determine square color (checkerboard pattern)
#                 is_light_square = (row_idx + col_idx//2) % 2 == 0  # Division by 2 for wide chars
#                 square_color = curses.color_pair(3) if is_light_square else curses.color_pair(4)
                
#                 # Determine piece color (white or black)
#                 attrs = 0
#                 if char in '♙♖♘♗♕♔':  # White pieces (outlined)
#                     color = square_color
#                 elif char in '♟♜♞♝♛♚':  # Black pieces (filled)
#                     color = square_color | curses.A_BOLD
#                     attrs = curses.A_BOLD
#                 else:
#                     color = square_color
                
#                 # Draw the square with piece
#                 try:
#                     win.addstr(start_y + row_idx, start_x + col_idx, char, color | attrs)
#                 except curses.error:
#                     pass
        
#         # Draw frame around the board
#         start_y -= 1
#         start_x -= 1
#         end_y = start_y + board_height + 1
#         end_x = start_x + board_width + 1
        
#         # Draw top and bottom borders
#         for x in range(start_x, end_x+1):
#             if 0 <= start_y < height and 0 <= x < width:
#                 try:
#                     win.addstr(start_y, x, "─", curses.color_pair(2))
#                 except curses.error:
#                     pass
#             if 0 <= end_y < height and 0 <= x < width:
#                 try:
#                     win.addstr(end_y, x, "─", curses.color_pair(2))
#                 except curses.error:
#                     pass
        
#         # Draw left and right borders
#         for y in range(start_y, end_y+1):
#             if 0 <= y < height and 0 <= start_x < width:
#                 try:
#                     win.addstr(y, start_x, "│", curses.color_pair(2))
#                 except curses.error:
#                     pass
#             if 0 <= y < height and 0 <= end_x < width:
#                 try:
#                     win.addstr(y, end_x, "│", curses.color_pair(2))
#                 except curses.error:
#                     pass
        
#         # Draw corners
#         if 0 <= start_y < height and 0 <= start_x < width:
#             try:
#                 win.addstr(start_y, start_x, "┌", curses.color_pair(2))
#             except curses.error:
#                 pass
#         if 0 <= start_y < height and 0 <= end_x < width:
#             try:
#                 win.addstr(start_y, end_x, "┐", curses.color_pair(2))
#             except curses.error:
#                 pass
#         if 0 <= end_y < height and 0 <= start_x < width:
#             try:
#                 win.addstr(end_y, start_x, "└", curses.color_pair(2))
#             except curses.error:
#                 pass
#         if 0 <= end_y < height and 0 <= end_x < width:
#             try:
#                 win.addstr(end_y, end_x, "┘", curses.color_pair(2))
#             except curses.error:
#                 pass
                
#         win.refresh()
    
#     def draw_game_board(self, win):
#         """Draw the game board with proper checkered background"""
#         # Get board string from environment
#         if self.has_custom_board:
#             board_str = self.env.create_board_str()
#         else:
#             # Try to get board from game state
#             board_str = None
#             game_state = self.env.state.game_state
#             if isinstance(game_state, dict):
#                 for key in ['board', 'board_state', 'rendered_board', 'current_board']:
#                     if key in game_state and isinstance(game_state[key], str):
#                         board_str = game_state[key]
#                         break
            
#             if board_str is None:
#                 board_str = "Board visualization\nnot available"
                
#         # Draw the chess board with checkered background
#         self.draw_chess_board(win, board_str)
    
#     def draw_game_state(self, win):
#         """Draw game state information"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game State "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get state information
#         game_state = self.env.state.game_state
        
#         # Determine which keys to render
#         render_keys = []
#         if self.has_render_keys:
#             render_keys = self.env.terminal_render_keys
#         else:
#             # Use some basic keys by default
#             render_keys = ["turn", "max_turns"]
#             # Add any other keys that might be useful
#             for key in ["status", "check", "current_player"]:
#                 if key in game_state:
#                     render_keys.append(key)
        
#         # Display turn information at bottom of window
#         turn_y = height - 3
#         if turn_y > 1:
#             turn_str = f"Turn: {self.env.state.turn}"
#             if hasattr(self.env.state, "max_turns") and self.env.state.max_turns:
#                 turn_str += f"/{self.env.state.max_turns}"
#             try:
#                 win.addstr(turn_y, 2, turn_str, curses.color_pair(5) | curses.A_BOLD)
#             except curses.error:
#                 pass
            
#         # Show current player at bottom of window
#         player_y = height - 2
#         if player_y > 1 and hasattr(self.env.state, "current_player_id"):
#             current_player = self.env.state.current_player_id
#             player_name = self.player_names.get(current_player, f"Player {current_player}")
            
#             # Use role mapping if available
#             if hasattr(self.env.state, "role_mapping") and current_player in self.env.state.role_mapping:
#                 player_name = self.env.state.role_mapping[current_player]
                
#             color_pair = self.COLOR_PAIRS.get(f"player_{current_player+1}", 6)
#             try:
#                 win.addstr(player_y, 2, f"Current player: {player_name}", curses.color_pair(color_pair) | curses.A_BOLD)
#             except curses.error:
#                 pass
        
#         # Display other state information at top
#         y = 2
#         for key in render_keys:
#             # Skip turn and player info as we show those separately
#             if key in ['turn', 'max_turns', 'current_player']:
#                 continue
                
#             if key in game_state and y < height - 4:  # Leave space for turn/player info
#                 value = str(game_state[key])
#                 # For valid_moves, just show the count
#                 if key == "valid_moves" and isinstance(game_state[key], list):
#                     value = f"{len(game_state[key])} moves"
                
#                 display_str = f"{key}: {value}"
#                 if len(display_str) > width - 4:
#                     display_str = display_str[:width-7] + "..."
                
#                 try:
#                     win.addstr(y, 2, display_str, curses.color_pair(5))
#                 except curses.error:
#                     pass
#                 y += 1
        
#         win.refresh()
    
#     def draw_player_stats(self, win):
#         """Draw player statistics"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Player Stats "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Find player-specific attributes
#         game_state = self.env.state.game_state
#         player_attributes = {}
        
#         # Look for dictionaries with integer keys (player IDs)
#         if isinstance(game_state, dict):
#             for key, value in game_state.items():
#                 if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
#                     player_attributes[key] = value
        
#         # Display player information
#         y = 2
#         current_player = self.env.state.current_player_id if hasattr(self.env.state, "current_player_id") else None
        
#         # For each player
#         for player_id in range(self.env.state.num_players):
#             if y >= height - 1:
#                 break
                
#             # Highlight current player
#             color_pair = self.COLOR_PAIRS.get(f"player_{player_id+1}", 6)
#             attributes = curses.A_BOLD if player_id == current_player else 0
            
#             # Get player name
#             player_name = self.player_names.get(player_id, f"Player {player_id}")
#             if hasattr(self.env.state, "role_mapping") and player_id in self.env.state.role_mapping:
#                 player_name = self.env.state.role_mapping[player_id]
                
#             if player_id == current_player:
#                 player_str = f"► {player_name}"
#             else:
#                 player_str = f"  {player_name}"
                
#             try:
#                 win.addstr(y, 2, player_str, curses.color_pair(color_pair) | attributes)
#             except curses.error:
#                 pass
#             y += 1
            
#             # Display player attributes
#             for attr, values in player_attributes.items():
#                 if player_id in values and y < height - 1:
#                     attr_str = f"  {attr}: {values[player_id]}"
#                     if len(attr_str) > width - 4:
#                         attr_str = attr_str[:width-7] + "..."
#                     try:
#                         win.addstr(y, 2, attr_str)
#                     except curses.error:
#                         pass
#                     y += 1
                    
#             y += 1  # Add space between players
        
#         win.refresh()
    
#     def draw_game_log(self, win):
#         """Draw game log messages"""
#         # Clear window and draw border
#         win.clear()
#         win.box()
        
#         # Get window dimensions
#         height, width = win.getmaxyx()
        
#         # Fill window with background color
#         for y in range(1, height-1):
#             win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
#         # Add title
#         title = " Game Log "
#         win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
#         # Get game logs
#         logs = self.env.state.logs if hasattr(self.env.state, "logs") else []
        
#         # Display logs (most recent first, up to window height)
#         max_logs = height - 3
#         recent_logs = logs[-max_logs:] if len(logs) > max_logs else logs
        
#         # Display from bottom up
#         y_positions = list(range(2, 2 + len(recent_logs)))
        
#         for i, (sender, message) in enumerate(recent_logs):
#             y = y_positions[i]
#             if y >= height - 1:
#                 break
                
#             # Format by sender type
#             if sender == -1:  # Game message
#                 prefix = "GAME: "
#                 color = curses.color_pair(5)  # Game message color
#             else:
#                 # Use role mapping or player names if available
#                 player_name = f"P{sender}"
#                 if sender in self.player_names:
#                     player_name = self.player_names[sender]
#                 elif hasattr(self.env.state, "role_mapping") and sender in self.env.state.role_mapping:
#                     player_name = self.env.state.role_mapping[sender]
                    
#                 prefix = f"{player_name}: "
#                 color_pair = self.COLOR_PAIRS.get(f"player_{sender+1}", 6)
#                 color = curses.color_pair(color_pair)
            
#             # Format and display message
#             log_str = f"{prefix}{message}"
#             if len(log_str) > width - 4:
#                 log_str = log_str[:width-7] + "..."
                
#             try:
#                 win.addstr(y, 2, log_str, color)
#             except curses.error:
#                 # Handle potential curses errors
#                 pass
        
#         win.refresh()
    
#     def _render_all(self, stdscr):
#         """Render the entire UI"""
#         # Get current screen size
#         height, width = stdscr.getmaxyx()
#         half_width = max(width // 2, 20)
#         half_height = max(height // 2, 10)
        
#         # Clear screen and reapply background
#         stdscr.erase()
#         stdscr.bkgd(' ', curses.color_pair(1))
        
#         # Fill screen with background color
#         for y in range(height):
#             try:
#                 stdscr.addstr(y, 0, " " * (width-1), curses.color_pair(1))
#             except curses.error:
#                 # Handle potential curses errors at screen edges
#                 pass
                
#         stdscr.refresh()
        
#         # Create windows for each section
#         if self.has_custom_board:
#             # Split left column for board and game state
#             game_board = curses.newwin(half_height, half_width, 0, 0)
#             game_state = curses.newwin(half_height, half_width, half_height, 0)
#         else:
#             # Use full left column for game state
#             game_board = None
#             game_state = curses.newwin(height, half_width, 0, 0)
        
#         # Create right column windows
#         player_stats = curses.newwin(half_height, half_width, 0, half_width)
#         game_log = curses.newwin(height - half_height, half_width, half_height, half_width)
        
#         # Set background for all windows
#         game_state.bkgd(' ', curses.color_pair(1))
#         player_stats.bkgd(' ', curses.color_pair(1))
#         game_log.bkgd(' ', curses.color_pair(1))
#         if game_board:
#             game_board.bkgd(' ', curses.color_pair(1))
        
#         # Draw content in each window
#         if game_board:
#             self.draw_game_board(game_board)
#         self.draw_game_state(game_state)
#         self.draw_player_stats(player_stats)
#         self.draw_game_log(game_log)
    
#     def get_observation(self):
#         """Get observation for the current player"""
#         if not self.curses_initialized:
#             self.reset_render()
            
#         return self.env.get_observation()
    
#     def step(self, action) -> Tuple[Rewards, bool, bool, Info]:
#         """Process a step in the environment and update the rendering"""
#         if not self.curses_initialized:
#             self.reset_render()
            
#         # Call the wrapped environment's step method
#         return self.env.step(action=action)
    
#     def reset(self, *args, **kwargs):
#         """Reset the environment and renderer"""
#         # Reset the wrapped environment
#         result = self.env.reset(*args, **kwargs)
        
#         # Initialize rendering if needed
#         self.reset_render()
        
#         return result
    
#     def close(self):
#         """Close the environment and clean up resources"""
#         # Stop the rendering thread
#         if self._render_thread is not None:
#             self._stop_render.set()
#             self._render_thread.join(timeout=1)
#             self._render_thread = None
#             self.curses_initialized = False
        
#         # Close the wrapped environment
#         if hasattr(self.env, 'close'):
#             return self.env.close()
#         return {}


import curses
import os
import time
from typing import Dict, Optional, Tuple, List, Any, Union, Set
import threading

from textarena.core import Env, RenderWrapper, Rewards, Info

class CursesTerminalRenderer(RenderWrapper):
    """
    Curses-based terminal renderer for text-based game environments.
    
    This renderer is a drop-in replacement for TerminalRenderWrapper,
    using curses to render the game state in the terminal.
    """
    
    # Color pair assignments
    COLOR_PAIRS = {
        "background": 1,    # Background color - dark teal/black
        "border": 2,        # Border/header color - teal accent
        "light_square": 3,  # Light squares on chess board - light blue-green
        "dark_square": 4,   # Dark squares on chess board - dark blue-green
        "game_message": 5,  # Game messages - purple/magenta
        "player_1": 6,      # Player 1 (White) - blue
        "player_2": 7,      # Player 2 (Black) - orange/yellow
        "player_3": 8,      # Player 3 - red
        "player_4": 9,      # Player 4 - green
        "player_5": 10,     # Player 5 - yellow
    }
    
    def __init__(
        self,
        env: Env,
        player_names: Optional[Dict[int, str]] = None,
        **kwargs
    ):
        """
        Initialize the curses terminal renderer
        
        Args:
            env: The environment to wrap
            player_names: Mapping from player IDs to display names
        """
        super().__init__(env)
        self.player_names = player_names or {}
        self.stdscr = None
        self.has_custom_board = hasattr(env, "create_board_str") and callable(env.create_board_str)
        self.has_render_keys = hasattr(env, "terminal_render_keys")
        self.curses_initialized = False
        self._render_thread = None
        self._stop_render = threading.Event()
        
    def reset_render(self):
        """Reset the renderer state"""
        # Initialize curses if not already done
        if not self.curses_initialized:
            self._init_curses()
    
    def _init_curses(self):
        """Initialize curses environment"""
        # Start curses in a separate thread
        if self._render_thread is None:
            self._stop_render.clear()
            self._render_thread = threading.Thread(target=self._run_curses_ui)
            self._render_thread.daemon = True
            self._render_thread.start()
            self.curses_initialized = True
    
    def _run_curses_ui(self):
        """Run the curses UI in a separate thread"""
        try:
            curses.wrapper(self._curses_main_loop)
        except Exception as e:
            print(f"Error in curses UI thread: {e}")
    
    def _curses_main_loop(self, stdscr):
        """Main curses loop"""
        self.stdscr = stdscr
        
        # Initialize curses
        curses.start_color()
        curses.curs_set(0)  # Hide cursor
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        
        # Setup colors
        self._setup_colors()
        
        # Set background
        stdscr.bkgd(' ', curses.color_pair(1))
        
        # Main loop
        while not self._stop_render.is_set():
            try:
                # Render the UI
                self._render_all(stdscr)
                
                # Check for 'q' key to exit
                stdscr.nodelay(True)
                key = stdscr.getch()
                if key == ord('q'):
                    break
                stdscr.nodelay(False)
                
                # Sleep to avoid high CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                # Just log the error and continue
                try:
                    height, width = stdscr.getmaxyx()
                    error_msg = f"Render error: {str(e)[:width-20]}"
                    stdscr.addstr(height-1, 0, error_msg, curses.color_pair(7) | curses.A_BOLD)
                    stdscr.refresh()
                    time.sleep(1)
                except:
                    pass
    
    def _setup_colors(self):
        """Initialize color pairs for curses"""
        if curses.can_change_color():
            # Background - very dark teal/black (original color)
            curses.init_color(10, 12, 74, 90)  # ~rgb(3, 19, 23)
            
            # Border - teal accent
            curses.init_color(11, 51, 443, 412)  # ~rgb(13, 114, 105)
            
            # Light square - light teal 
            curses.init_color(12, 74, 231, 184)  # ~rgb(19, 59, 47)
            
            # Dark square - dark teal
            curses.init_color(13, 12, 55, 39)  # ~rgb(3, 14, 10)
            
            # Game message - purple
            curses.init_color(14, 655, 258, 902)  # ~rgb(167, 66, 230)
            
            # Player colors
            curses.init_color(15, 149, 451, 902)  # Player 1 (White) - blue
            curses.init_color(16, 902, 525, 94)   # Player 2 (Black) - yellow/orange
            curses.init_color(17, 902, 301, 200)  # Player 3 - red
            curses.init_color(18, 369, 902, 235)  # Player 4 - green
            curses.init_color(19, 902, 769, 94)   # Player 5 - yellow
            
            # Define color pairs
            curses.init_pair(1, curses.COLOR_WHITE, 10)     # Background
            curses.init_pair(2, 11, 10)                     # Border/header
            curses.init_pair(3, curses.COLOR_WHITE, 12)     # Light square
            curses.init_pair(4, curses.COLOR_WHITE, 13)     # Dark square
            curses.init_pair(5, 14, 10)                     # Game messages
            curses.init_pair(6, 15, 10)                     # Player 1 (White)
            curses.init_pair(7, 16, 10)                     # Player 2 (Black)
            curses.init_pair(8, 17, 10)                     # Player 3
            curses.init_pair(9, 18, 10)                     # Player 4
            curses.init_pair(10, 19, 10)                    # Player 5
        else:
            # Fallback colors for terminals with limited color support
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Background
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Border/header
            curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)      # Light square
            curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Dark square
            curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Game messages
            curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)      # Player 1 (White)
            curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Player 2 (Black)
            curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)       # Player 3
            curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Player 4
            curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Player 5
    
    def _center_text(self, window, text, y_offset=0):
        """Center text in a window, handling multiline strings"""
        height, width = window.getmaxyx()
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if i + y_offset < height - 1:  # Avoid writing at bottom-right corner
                x = max(0, (width - len(line)) // 2)
                try:
                    window.addstr(i + y_offset, x, line)
                except curses.error:
                    # Catch errors when trying to write at bottom-right corner
                    pass
    
    def draw_chess_board(self, win, board_str):
        """Draw a chess board with proper checkered background"""
        # Clear window and draw border
        win.clear()
        win.box()
        
        # Get window dimensions
        height, width = win.getmaxyx()
        
        # Fill window with background color
        for y in range(1, height-1):
            win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
        # Add title
        title = " Game Board "
        win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
        # Parse board string to extract pieces
        lines = board_str.split('\n')
        board_lines = []
        board_start = False
        
        # Extract just the board part (ignore coordinates/border)
        for line in lines:
            if '┌' in line:
                board_start = True
                continue
            if '└' in line:
                break
            if board_start and '│' in line:
                # Extract just the board content between the pipes
                parts = line.split('│')
                if len(parts) > 2:
                    board_lines.append(parts[1].strip())
        
        # If we couldn't parse the board properly, just center the text
        if not board_lines:
            self._center_text(win, board_str, y_offset=2)
            win.refresh()
            return
            
        # Calculate board position to center it
        board_height = len(board_lines)
        board_width = max(len(line) for line in board_lines)
        
        start_y = max(2, (height - board_height - 4) // 2)
        start_x = max(4, (width - board_width - 4) // 2)
        
        # Draw column labels (a-h) at top
        col_y = start_y - 1
        for i, label in enumerate('abcdefgh'):
            if 0 <= col_y < height-1 and start_x + i*2 < width-1:
                try:
                    win.addstr(col_y, start_x + i*2, label, curses.color_pair(2))
                except curses.error:
                    pass
        
        # Draw column labels (a-h) at bottom
        col_y = start_y + board_height
        for i, label in enumerate('abcdefgh'):
            if 0 <= col_y < height-1 and start_x + i*2 < width-1:
                try:
                    win.addstr(col_y, start_x + i*2, label, curses.color_pair(2))
                except curses.error:
                    pass
        
        # Draw row labels (8-1) and checkered board with pieces
        for row_idx, line in enumerate(board_lines):
            row_num = 8 - row_idx
            # Draw row number on left
            if 0 <= start_y + row_idx < height-1 and start_x - 2 >= 0:
                try:
                    win.addstr(start_y + row_idx, start_x - 2, str(row_num), curses.color_pair(2))
                except curses.error:
                    pass
                
            # Draw row number on right
            if 0 <= start_y + row_idx < height-1 and start_x + board_width + 1 < width:
                try:
                    win.addstr(start_y + row_idx, start_x + board_width + 1, str(row_num), curses.color_pair(2))
                except curses.error:
                    pass
            
            # Draw checkered board with pieces
            for col_idx, char in enumerate(line):
                if col_idx >= board_width or start_y + row_idx >= height-1 or start_x + col_idx >= width-1:
                    continue
                    
                # Determine square color (checkerboard pattern)
                is_light_square = (row_idx + col_idx//2) % 2 == 0  # Division by 2 for wide chars
                square_color = curses.color_pair(3) if is_light_square else curses.color_pair(4)
                
                # Determine piece color (white or black)
                attrs = 0
                if char in '♙♖♘♗♕♔':  # White pieces (outlined)
                    color = square_color
                elif char in '♟♜♞♝♛♚':  # Black pieces (filled)
                    color = square_color | curses.A_BOLD
                    attrs = curses.A_BOLD
                else:
                    color = square_color
                
                # Draw the square with piece
                try:
                    win.addstr(start_y + row_idx, start_x + col_idx, char, color | attrs)
                except curses.error:
                    pass
        
        # Draw frame around the board
        start_y -= 1
        start_x -= 1
        end_y = start_y + board_height + 1
        end_x = start_x + board_width + 1
        
        # Draw top and bottom borders
        for x in range(start_x, end_x+1):
            if 0 <= start_y < height and 0 <= x < width:
                try:
                    win.addstr(start_y, x, "─", curses.color_pair(2))
                except curses.error:
                    pass
            if 0 <= end_y < height and 0 <= x < width:
                try:
                    win.addstr(end_y, x, "─", curses.color_pair(2))
                except curses.error:
                    pass
        
        # Draw left and right borders
        for y in range(start_y, end_y+1):
            if 0 <= y < height and 0 <= start_x < width:
                try:
                    win.addstr(y, start_x, "│", curses.color_pair(2))
                except curses.error:
                    pass
            if 0 <= y < height and 0 <= end_x < width:
                try:
                    win.addstr(y, end_x, "│", curses.color_pair(2))
                except curses.error:
                    pass
        
        # Draw corners
        if 0 <= start_y < height and 0 <= start_x < width:
            try:
                win.addstr(start_y, start_x, "┌", curses.color_pair(2))
            except curses.error:
                pass
        if 0 <= start_y < height and 0 <= end_x < width:
            try:
                win.addstr(start_y, end_x, "┐", curses.color_pair(2))
            except curses.error:
                pass
        if 0 <= end_y < height and 0 <= start_x < width:
            try:
                win.addstr(end_y, start_x, "└", curses.color_pair(2))
            except curses.error:
                pass
        if 0 <= end_y < height and 0 <= end_x < width:
            try:
                win.addstr(end_y, end_x, "┘", curses.color_pair(2))
            except curses.error:
                pass
                
        win.refresh()
    
    def draw_game_board(self, win):
        """Draw the game board with proper checkered background"""
        # Get board string from environment
        if self.has_custom_board:
            board_str = self.env.create_board_str()
        else:
            # Try to get board from game state
            board_str = None
            game_state = self.env.state.game_state
            if isinstance(game_state, dict):
                for key in ['board', 'board_state', 'rendered_board', 'current_board']:
                    if key in game_state and isinstance(game_state[key], str):
                        board_str = game_state[key]
                        break
            
            if board_str is None:
                board_str = "Board visualization\nnot available"
                
        # Draw the chess board with checkered background
        self.draw_chess_board(win, board_str)
    
    def draw_game_state(self, win):
        """Draw game state information"""
        # Clear window and draw border
        win.clear()
        win.box()
        
        # Get window dimensions
        height, width = win.getmaxyx()
        
        # Fill window with background color
        for y in range(1, height-1):
            win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
        # Add title
        title = " Game State "
        win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
        # Get state information
        game_state = self.env.state.game_state
        
        # Determine which keys to render
        render_keys = []
        if self.has_render_keys:
            render_keys = self.env.terminal_render_keys
        else:
            # Use some basic keys by default
            render_keys = ["turn", "max_turns", "status", "check"]
        
        # Display general state information (not turn/player)
        y = 2
        for key in render_keys:
            # Skip turn since we show it separately at bottom
            if key in ['turn', 'max_turns']:
                continue
                
            if key in game_state and y < height - 4:  # Leave space for turn/player info
                value = str(game_state[key])
                # For valid_moves, just show the count
                if key == "valid_moves" and isinstance(game_state[key], list):
                    value = f"{len(game_state[key])} moves"
                
                display_str = f"{key}: {value}"
                if len(display_str) > width - 4:
                    display_str = display_str[:width-7] + "..."
                
                try:
                    win.addstr(y, 2, display_str, curses.color_pair(5))
                except curses.error:
                    pass
                y += 1
        
        # Display turn information at bottom of window
        turn_y = height - 3
        if turn_y > 1:
            # Format as Turn: X/Y
            turn_str = f"Turn: {self.env.state.turn}"
            if hasattr(self.env.state, "max_turns") and self.env.state.max_turns:
                turn_str += f"/{self.env.state.max_turns}"
            try:
                win.addstr(turn_y, 2, turn_str, curses.color_pair(5) | curses.A_BOLD)
            except curses.error:
                pass
            
        # Show current player at bottom of window
        player_y = height - 2
        if player_y > 1 and hasattr(self.env.state, "current_player_id"):
            current_player = self.env.state.current_player_id
            player_name = self.player_names.get(current_player, f"Player {current_player}")
            
            # Use role mapping if available
            if hasattr(self.env.state, "role_mapping") and current_player in self.env.state.role_mapping:
                player_name = self.env.state.role_mapping[current_player]
                
            color_pair = self.COLOR_PAIRS.get(f"player_{current_player+1}", 6)
            try:
                win.addstr(player_y, 2, f"Current player: {player_name}", curses.color_pair(color_pair) | curses.A_BOLD)
            except curses.error:
                pass
        
        win.refresh()
    
    # def draw_game_log(self, win):
    #     """Draw game log messages"""
    #     # Clear window and draw border
    #     win.clear()
    #     win.box()
        
    #     # Get window dimensions
    #     height, width = win.getmaxyx()
        
    #     # Fill window with background color
    #     for y in range(1, height-1):
    #         win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
    #     # Add title
    #     title = " Game Log "
    #     win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
    #     # Get game logs
    #     logs = self.env.state.logs if hasattr(self.env.state, "logs") else []
        
    #     # Format logs with wrapping
    #     formatted_logs = []
    #     for sender, message in logs:
    #         # Format by sender type
    #         if sender == -1:  # Game message
    #             prefix = "GAME: "
    #             color = curses.color_pair(5)  # Game message color
    #         else:
    #             # Use role mapping or player names if available
    #             player_name = f"P{sender}"
    #             if sender in self.player_names:
    #                 player_name = self.player_names[sender]
    #             elif hasattr(self.env.state, "role_mapping") and sender in self.env.state.role_mapping:
    #                 player_name = self.env.state.role_mapping[sender]
                    
    #             prefix = f"{player_name}: "
    #             color_pair = self.COLOR_PAIRS.get(f"player_{sender+1}", 6)
    #             color = curses.color_pair(color_pair)
            
    #         # Wrap long messages
    #         log_str = f"{prefix}{message}"
            
    #         # Split into lines that fit within the window width
    #         remaining = log_str
    #         while remaining:
    #             # How much can fit on this line
    #             line_width = width - 4  # Account for border and padding
    #             if len(remaining) <= line_width:
    #                 formatted_logs.append((remaining, color))
    #                 break
    #             else:
    #                 # Find a good breaking point
    #                 cutoff = line_width
    #                 while cutoff > 0 and remaining[cutoff] != ' ':
    #                     cutoff -= 1
    #                 if cutoff == 0:  # No space found, just cut at max width
    #                     cutoff = line_width
                    
    #                 formatted_logs.append((remaining[:cutoff], color))
    #                 remaining = remaining[cutoff:].lstrip()
        
    #     # Display logs, showing as many as will fit (most recent at bottom)
    #     display_lines = height - 3  # Account for border and title
    #     start_idx = max(0, len(formatted_logs) - display_lines)
        
    #     for i, (line, color) in enumerate(formatted_logs[start_idx:]):
    #         if i < display_lines:
    #             y = 2 + i
    #             try:
    #                 win.addstr(y, 2, line, color)
    #             except curses.error:
    #                 # Handle potential curses errors
    #                 pass
        
    #     win.refresh()
    # def draw_game_log(self, win):
    #     """Draw game log messages with proper wrapping and indentation"""
    #     # Clear window and draw border
    #     win.clear()
    #     win.box()
        
    #     # Get window dimensions
    #     height, width = win.getmaxyx()
        
    #     # Fill window with background color
    #     for y in range(1, height-1):
    #         win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
    #     # Add title
    #     title = " Game Log "
    #     win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
    #     # Get game logs
    #     logs = self.env.state.logs if hasattr(self.env.state, "logs") else []
        
    #     # Calculate available width for text
    #     available_width = width - 6  # Account for borders and padding
        
    #     # Format logs with wrapping
    #     formatted_logs = []
    #     for sender, message in logs:
    #         # Format by sender type
    #         if sender == -1:  # Game message
    #             prefix = "GAME: "
    #             color = curses.color_pair(5)  # Game message color
    #         else:
    #             # Use role mapping or player names if available
    #             player_name = f"P{sender}"
    #             if sender in self.player_names:
    #                 player_name = self.player_names[sender]
    #             elif hasattr(self.env.state, "role_mapping") and sender in self.env.state.role_mapping:
    #                 player_name = self.env.state.role_mapping[sender]
                    
    #             prefix = f"{player_name}: "
    #             color_pair = self.COLOR_PAIRS.get(f"player_{sender+1}", 6)
    #             color = curses.color_pair(color_pair)
            
    #         # Format the full message
    #         log_str = f"{prefix}{message}"
            
    #         # Split into lines with proper wrapping
    #         if len(log_str) <= available_width:
    #             # Message fits on one line
    #             formatted_logs.append((log_str, color, False))  # False = not indented
    #         else:
    #             # First line with prefix
    #             formatted_logs.append((log_str[:available_width], color, False))
                
    #             # Remaining text with indentation
    #             remaining = log_str[available_width:]
    #             indent_width = 4  # Indentation width for wrapped lines
    #             indent = " " * indent_width
    #             wrapped_width = available_width - indent_width
                
    #             while remaining:
    #                 # Find a good breaking point
    #                 if len(remaining) <= wrapped_width:
    #                     # Last line of this message
    #                     formatted_logs.append((indent + remaining, color, True))
    #                     break
    #                 else:
    #                     # Find a good breaking point (space)
    #                     cutoff = wrapped_width
    #                     while cutoff > 0 and remaining[cutoff] != ' ':
    #                         cutoff -= 1
                        
    #                     if cutoff == 0:  # No space found, just cut at max width
    #                         cutoff = wrapped_width
                        
    #                     line = indent + remaining[:cutoff]
    #                     formatted_logs.append((line, color, True))
    #                     remaining = remaining[cutoff:].lstrip()
        
    #     # Display logs, showing as many as will fit (most recent at bottom)
    #     display_lines = height - 3  # Account for border and title
    #     start_idx = max(0, len(formatted_logs) - display_lines)
        
    #     for i, (line, color, is_wrapped) in enumerate(formatted_logs[start_idx:]):
    #         if i < display_lines:
    #             y = 2 + i
    #             try:
    #                 # Make sure line doesn't exceed window width
    #                 if len(line) > width - 4:
    #                     line = line[:width-7] + "..."
                    
    #                 win.addstr(y, 2, line, color)
    #             except curses.error:
    #                 pass
        
    #     win.refresh()
    def draw_game_log(self, win):
        """Draw game log messages with proper wrapping and filtered newlines"""
        # Clear window and draw border
        win.clear()
        win.box()
        
        # Get window dimensions
        height, width = win.getmaxyx()
        
        # Fill window with background color
        for y in range(1, height-1):
            win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
        
        # Add title
        title = " Game Log "
        win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
        
        # Get game logs
        logs = self.env.state.logs if hasattr(self.env.state, "logs") else []
        
        # Calculate available width for text
        available_width = width - 6  # Account for borders and padding
        
        # Format logs with wrapping
        formatted_logs = []
        for sender, message in logs:
            # Filter out any newline characters or replace with spaces
            message = message.replace('\n', ' ').replace('\r', '')
            
            # Format by sender type
            if sender == -1:  # Game message
                prefix = "GAME: "
                color = curses.color_pair(5)  # Game message color
            else:
                # Use role mapping or player names if available
                player_name = f"P{sender}"
                if sender in self.player_names:
                    player_name = self.player_names[sender]
                elif hasattr(self.env.state, "role_mapping") and sender in self.env.state.role_mapping:
                    player_name = self.env.state.role_mapping[sender]
                    
                prefix = f"{player_name}: "
                color_pair = self.COLOR_PAIRS.get(f"player_{sender+1}", 6)
                color = curses.color_pair(color_pair)
            
            # Format the full message
            log_str = f"{prefix}{message}"
            
            # Split into lines with proper wrapping and indentation
            if len(log_str) <= available_width:
                # Message fits on one line
                formatted_logs.append((log_str, color))
            else:
                # First line with prefix (no indent)
                formatted_logs.append((log_str[:available_width], color))
                
                # Remaining text with indentation
                remaining = log_str[available_width:]
                indent_width = 4  # Indentation width for wrapped lines
                wrap_width = available_width - indent_width  # Adjusted width for wrapped lines
                
                while remaining:
                    # Find a good breaking point (space)
                    if len(remaining) <= wrap_width:
                        # Last line of this message
                        formatted_logs.append((" " * indent_width + remaining, color))
                        break
                    else:
                        # Find the last space before the wrap width
                        cutoff = wrap_width
                        while cutoff > 0 and remaining[cutoff] != ' ':
                            cutoff -= 1
                        
                        if cutoff == 0:  # No space found
                            # Just cut at the wrap width
                            cutoff = wrap_width
                        
                        formatted_logs.append((" " * indent_width + remaining[:cutoff], color))
                        remaining = remaining[cutoff:].lstrip()
        
        # Display logs (most recent at bottom)
        display_lines = height - 3  # Account for border and title
        start_idx = max(0, len(formatted_logs) - display_lines)
        
        for i, (line, color) in enumerate(formatted_logs[start_idx:]):
            if i < display_lines:
                y = 2 + i
                try:
                    # Make sure line doesn't exceed window width
                    if len(line) > width - 4:
                        line = line[:width-7] + "..."
                    win.addstr(y, 2, line, color)
                except curses.error:
                    pass
        
        win.refresh()
    
    def _render_all(self, stdscr):
        """Render the entire UI"""
        # Get current screen size
        height, width = stdscr.getmaxyx()
        half_width = max(width // 2, 20)
        half_height = max(height // 2, 10)
        
        # Clear screen and reapply background
        stdscr.erase()
        stdscr.bkgd(' ', curses.color_pair(1))
        
        # Fill screen with background color
        for y in range(height):
            try:
                stdscr.addstr(y, 0, " " * (width-1), curses.color_pair(1))
            except curses.error:
                # Handle potential curses errors at screen edges
                pass
                
        stdscr.refresh()
        
        # Create windows for each section - game log takes full right side
        if self.has_custom_board:
            # Split left column for board and game state
            game_board = curses.newwin(half_height, half_width, 0, 0)
            game_state = curses.newwin(half_height, half_width, half_height, 0)
        else:
            # Use full left column for game state
            game_board = None
            game_state = curses.newwin(height, half_width, 0, 0)
        
        # Game log takes full right side
        game_log = curses.newwin(height, half_width, 0, half_width)
        
        # Set background for all windows
        game_state.bkgd(' ', curses.color_pair(1))
        game_log.bkgd(' ', curses.color_pair(1))
        if game_board:
            game_board.bkgd(' ', curses.color_pair(1))
        
        # Draw content in each window
        if game_board:
            self.draw_game_board(game_board)
        self.draw_game_state(game_state)
        self.draw_game_log(game_log)
    
    def get_observation(self):
        """Get observation for the current player"""
        if not self.curses_initialized:
            self.reset_render()
            
        return self.env.get_observation()
    
    def step(self, action) -> Tuple[Rewards, bool, bool, Info]:
        """Process a step in the environment and update the rendering"""
        if not self.curses_initialized:
            self.reset_render()
            
        # Call the wrapped environment's step method
        return self.env.step(action=action)
        
    def reset(self, *args, **kwargs):
        """Reset the environment and renderer"""
        # Reset the wrapped environment
        result = self.env.reset(*args, **kwargs)
        
        # Initialize rendering if needed
        self.reset_render()
        
        return result
    
    def close(self):
        """Close the environment and clean up resources"""
        # Stop the rendering thread
        if self._render_thread is not None:
            self._stop_render.set()
            self._render_thread.join(timeout=1)
            self._render_thread = None
            self.curses_initialized = False
        
        # Close the wrapped environment
        if hasattr(self.env, 'close'):
            return self.env.close()
        return {}


def main():
    # Initialize agents
    agents = {
        0: ta.agents.OpenRouterAgent(model_name="GPT-4o-mini"),
        1: ta.agents.OpenRouterAgent(model_name="anthropic/claude-3.5-haiku"),
    }
    # Initialize environment from subset and wrap it
    env = ta.make(env_id="Chess-v0") # don't worry about this line of the next, just the rendering
    env = ta.wrappers.LLMObservationWrapper(env=env)
    env = CursesTerminalRenderer(
        env=env,
        # player_names={0: "GPT-4o-mini", 1: "claude-3.5-haiku"},
    )

    env.reset(num_players=2)
    # env.render()
    done = False
    while not done:
        print('loop 1')
        player_id, observation = env.get_observation()
        action = agents[player_id](observation)
        done, info = env.step(action=action)
        # env.render()
    rewards = env.close()

if __name__ == "__main__":
    main()