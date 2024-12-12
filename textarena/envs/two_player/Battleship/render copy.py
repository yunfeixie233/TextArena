import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional
from PIL import Image, ImageTk
import os

class GameStateRender(ttk.Frame):
    """Render wrapper for the Battleship environment."""
    
    CELL_SIZE = 40  # Size of each grid cell in pixels
    LABEL_SPACE = 30  # Space for coordinate labels
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 600
    
    def __init__(self, master, env, player_names: Optional[Dict[int, str]] = None):
        super().__init__(master)
        self.master = master
        self.env = env
        self.player_names = player_names or {0: "Player 0", 1: "Player 1"}
        
        # Color scheme
        self.water_color = '#1E90FF'      # Blue for water/empty cells
        self.ship_color = '#808080'       # Gray for ships
        self.hit_color = '#FF4444'        # Red for hits
        self.miss_color = '#FFFFFF'       # White for misses
        self.bg_color = '#2B2B2B'         # Dark background
        self.text_color = '#FFFFFF'       # White text
        self.grid_line_color = '#4A4A4A'  # Grid lines
        self.player_colors = {
            0: '#4A90E2',  # Blue
            1: '#E24A4A'   # Red
        }
        
        # Configure main window
        self.master.title("Battleship Game")
        self.master.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.master.configure(bg=self.bg_color)
        
        # Try to set icon if available
        icon_path = os.path.join("textarena", "assets", "textarena-icon.png")
        if os.path.exists(icon_path):
            try:
                self.master.iconphoto(False, tk.PhotoImage(file=icon_path))
            except Exception as e:
                print(f"Could not set window icon: {e}")
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create all widgets for the battleship interface."""
        # Main container
        self.container = ttk.Frame(self.master)
        self.container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Game info frame (top)
        self.info_frame = ttk.Frame(self.container)
        self.info_frame.pack(fill='x', pady=(0, 10))
        
        # Turn indicator
        self.turn_label = ttk.Label(
            self.info_frame,
            text="Player 0's Turn",
            font=('Arial', 14, 'bold'),
            background=self.bg_color,
            foreground=self.text_color
        )
        self.turn_label.pack(side='left')
        
        # Status message
        self.status_label = ttk.Label(
            self.info_frame,
            text="",
            font=('Arial', 12),
            background=self.bg_color,
            foreground=self.text_color
        )
        self.status_label.pack(side='right')
        
        # Grids container
        self.grids_container = ttk.Frame(self.container)
        self.grids_container.pack(expand=True, fill='both')
        
        # Create player board frames and canvases
        self.player_boards = {}
        for player_id in [0, 1]:
            # Board frame
            board_frame = ttk.Frame(self.grids_container)
            board_frame.pack(side='left', padx=20)
            
            # Board title
            title = ttk.Label(
                board_frame,
                text=f"{self.player_names[player_id]}'s Board",
                font=('Arial', 12, 'bold'),
                background=self.bg_color,
                foreground=self.text_color
            )
            title.pack(pady=(0, 10))
            
            # Grid size includes space for labels
            grid_size = self.env.grid_size * self.CELL_SIZE + self.LABEL_SPACE
            
            # Create canvas for the board
            canvas = tk.Canvas(
                board_frame,
                width=grid_size,
                height=grid_size,
                bg=self.bg_color,
                highlightthickness=0
            )
            canvas.pack()
            
            # Store references
            self.player_boards[player_id] = {
                'frame': board_frame,
                'canvas': canvas
            }
            
        # Ships status frame (bottom)
        self.ships_frame = ttk.Frame(self.container)
        self.ships_frame.pack(fill='x', pady=(20, 0))
        
        # Create ship status displays for both players
        self.ship_status = {}
        for player_id in [0, 1]:
            status_frame = ttk.Frame(self.ships_frame)
            status_frame.pack(side='left', padx=20)
            
            header = ttk.Label(
                status_frame,
                text=f"{self.player_names[player_id]}'s Ships",
                font=('Arial', 11, 'bold'),
                background=self.bg_color,
                foreground=self.text_color
            )
            header.pack(pady=(0, 5))
            
            self.ship_status[player_id] = {}
            for ship_name in self.env.ships.keys():
                label = ttk.Label(
                    status_frame,
                    text=f"{ship_name}: Active",
                    font=('Arial', 10),
                    background=self.bg_color,
                    foreground='#90EE90'  # Light green
                )
                label.pack()
                self.ship_status[player_id][ship_name] = label

    def draw_board(self):
        """Update the display with current game state."""
        if not hasattr(self.env.state, "game_state"):
            return
            
        # Update game status
        current_player = self.env.state.current_player_id
        self.turn_label.configure(text=f"{self.player_names[current_player]}'s Turn")
        
        # Draw both players' boards
        for player_id in [0, 1]:
            canvas = self.player_boards[player_id]['canvas']
            canvas.delete('all')
            
            # Draw grid and ships
            for row in range(self.env.grid_size):
                for col in range(self.env.grid_size):
                    x1 = col * self.CELL_SIZE + self.LABEL_SPACE
                    y1 = row * self.CELL_SIZE + self.LABEL_SPACE
                    x2 = x1 + self.CELL_SIZE
                    y2 = y1 + self.CELL_SIZE
                    
                    # Get cell content
                    cell = self.env.board[player_id][row][col]
                    
                    # Determine cell color
                    if cell == 'X':
                        color = self.hit_color
                    elif cell == 'O':
                        color = self.miss_color
                    elif cell == '~':
                        color = self.water_color
                    else:  # Ship
                        color = self.ship_color
                    
                    # Draw cell
                    canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=color,
                        outline=self.grid_line_color
                    )
                    
                    # Draw hit marker
                    if cell == 'X':
                        self.draw_hit_marker(canvas, x1, y1, x2, y2)
                    elif cell == 'O':
                        self.draw_miss_marker(canvas, x1, y1, x2, y2)
            
            # Draw row labels (A-J)
            for i in range(self.env.grid_size):
                canvas.create_text(
                    self.LABEL_SPACE/2,
                    i * self.CELL_SIZE + self.LABEL_SPACE + self.CELL_SIZE/2,
                    text=chr(ord('A') + i),
                    fill=self.text_color,
                    font=('Arial', 10)
                )
            
            # Draw column labels (0-9)
            for i in range(self.env.grid_size):
                canvas.create_text(
                    i * self.CELL_SIZE + self.LABEL_SPACE + self.CELL_SIZE/2,
                    self.LABEL_SPACE/2,
                    text=str(i),
                    fill=self.text_color,
                    font=('Arial', 10)
                )
        
        # Update ship status
        self.update_ship_status()
    
    def draw_hit_marker(self, canvas, x1, y1, x2, y2):
        """Draw an X marker for hits."""
        padding = 5
        canvas.create_line(
            x1 + padding, y1 + padding,
            x2 - padding, y2 - padding,
            fill='white',
            width=2
        )
        canvas.create_line(
            x2 - padding, y1 + padding,
            x1 + padding, y2 - padding,
            fill='white',
            width=2
        )
    
    def draw_miss_marker(self, canvas, x1, y1, x2, y2):
        """Draw a dot marker for misses."""
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        radius = 4
        canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=self.bg_color,
            outline=self.bg_color
        )
    
    def update_ship_status(self):
        """Update the ship status display."""
        for player_id in [0, 1]:
            board = self.env.board[player_id]
            for ship_name in self.env.ships.keys():
                ship_initial = ship_name[0]
                # Check if ship is still on the board
                ship_alive = any(ship_initial in row for row in board)
                label = self.ship_status[player_id][ship_name]
                if ship_alive:
                    label.configure(
                        text=f"{ship_name}: Active",
                        foreground='#90EE90'  # Light green
                    )
                else:
                    label.configure(
                        text=f"{ship_name}: Sunk",
                        foreground='#FF6B6B'  # Light red
                    )
