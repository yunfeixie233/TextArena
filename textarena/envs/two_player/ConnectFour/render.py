import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Any, Dict, Optional, Tuple, List, Callable


import os 
import textarena as ta


class GameStateRender(ttk.Frame):
    DISC_SIZE = 40
    MIN_WINDOW_WIDTH = 400
    MIN_WINDOW_HEIGHT = 300
    
    def __init__(self, master, env, player_names: Optional[Dict[int, str]] = None):
        super().__init__(master)
        self.master = master 
        self.env = env
        self.player_names = player_names or {0: "Player 0", 1: "Player 1"}
        self.player_names[ta.GAME_ID] = "GAME"

        self.player_colors = {0: '#4A90E2', 1: '#E24A4A'}  # Blue and Red

        # Configure the main window 
        self.master.title("Connect Four")
        initial_height = env.num_rows * self.DISC_SIZE + 120
        initial_width = max(env.num_cols * self.DISC_SIZE + 80, self.MIN_WINDOW_WIDTH)
        self.master.geometry(f"{initial_width}x{initial_height}")
        self.master.minsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        self.master.configure(bg='#2B2B2B')

        # Try to set icon if available
        icon_path = os.path.join("textarena", "assets", "textarena-icon.png")
        if os.path.exists(icon_path):
            try:
                self.master.iconphoto(False, tk.PhotoImage(file=icon_path))
            except Exception as e:
                print(f"Could not set window icon: {e}")
        

        self.create_widgets()
        
        # Bind resize event
        self.master.bind('<Configure>', self.on_window_resize)

    def create_widgets(self):
        # Main container frame
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill='both', expand=True)
        
        # Board frame
        self.board_frame = ttk.Frame(self.main_frame)
        self.board_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Canvas for the game board
        self.board_canvas = tk.Canvas(
            self.board_frame,
            bg='#2B2B2B',
            highlightthickness=0
        )
        self.board_canvas.pack(fill='both', expand=True)
        
        # Center-aligned player info frame
        self.player_frame = ttk.Frame(self.main_frame)
        self.player_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Center container for player indicators
        self.center_container = ttk.Frame(self.player_frame)
        self.center_container.pack(expand=True)
        
        # Create player indicators in the center container
        for player_id in [0, 1]:
            frame = ttk.Frame(self.center_container)
            frame.pack(side='left', padx=20)
            
            # Create small canvas for player disc
            disc_canvas = tk.Canvas(
                frame,
                width=20,
                height=20,
                bg='#2B2B2B',
                highlightthickness=0
            )
            disc_canvas.pack(side='left', padx=5)
            disc_canvas.create_oval(2, 2, 18, 18, fill=self.player_colors[player_id], outline=self.player_colors[player_id])
            
            # Player name label
            ttk.Label(
                frame,
                text=self.player_names[player_id],
                foreground='white',
                background='#2B2B2B'
            ).pack(side='left')

    def on_window_resize(self, event):
        """Handle window resize events."""
        if event.widget == self.master:
            # Ensure minimum size
            width = max(event.width, self.MIN_WINDOW_WIDTH)
            height = max(event.height, self.MIN_WINDOW_HEIGHT)
            
            # Calculate new disc size based on window size and board dimensions
            width_disc_size = (width - 80) / self.env.num_cols
            height_disc_size = (height - 120) / self.env.num_rows  # Account for player info space
            self.DISC_SIZE = min(width_disc_size, height_disc_size)
            
            # Redraw the board with new size
            self.draw_board()

    def draw_board(self):
        """Draw the game board based on the current state."""
        # Calculate board dimensions
        board_width = self.env.num_cols * self.DISC_SIZE
        board_height = self.env.num_rows * self.DISC_SIZE
        
        # Configure canvas size
        self.board_canvas.configure(width=board_width, height=board_height)
        
        # Clear previous drawings
        self.board_canvas.delete('all')
        
        # Draw the grid and discs
        for col in range(self.env.num_cols):
            for row in range(self.env.num_rows):
                x1 = col * self.DISC_SIZE
                y1 = row * self.DISC_SIZE
                x2 = x1 + self.DISC_SIZE
                y2 = y1 + self.DISC_SIZE
                
                # Draw cell background
                self.board_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill='#3C3F41',
                    outline='#2B2B2B'
                )
                
                # Draw disc
                padding = self.DISC_SIZE * 0.2  # Dynamic padding
                disc = self.env.state.game_state["board"][row][col]
                color = '#2B2B2B'  # Empty slot
                if disc == "X":
                    color = self.player_colors[0]
                elif disc == "O":
                    color = self.player_colors[1]
                
                self.board_canvas.create_oval(
                    x1 + padding,
                    y1 + padding,
                    x2 - padding,
                    y2 - padding,
                    fill=color,
                    outline=color
                )
        
        # Center the board canvas
        self.board_canvas.place(relx=0.5, rely=0.5, anchor='center')

