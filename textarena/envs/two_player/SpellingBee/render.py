import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional
import math
import re


class GameStateRender(ttk.Frame):
    """
    Visual renderer for the Spelling Bee game state using tkinter.
    Displays the allowed letters in a hexagonal pattern with player words and scores.
    """
    
    # Visual configuration
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 800
    LETTER_CELL_SIZE = 40
    LETTER_FONT_SIZE = 18
    
    def __init__(self, master, env, player_names: Optional[Dict[int, str]] = None):
        """
        Initialize the game renderer.
        
        Args:
            master: The tkinter root window
            env: The SpellingBee game environment
            player_names: Optional dictionary mapping player IDs to display names
        """
        super().__init__(master)
        self.master = master
        self.env = env
        self.player_names = player_names or {0: "Player 0", 1: "Player 1"}
        self.player_colors = {
            0: '#4A90E2',  # Blue
            1: '#E24A4A'   # Red
        }
        
        # Color scheme
        self.bg_color = '#2B2B2B'  # Dark background
        self.letter_colors = {
            'bg': '#FFD700',  # Gold background for letters
            'fg': '#000000',  # Black text for letters
        }
        
        # Configure main window
        self.master.title("Spelling Bee Game")
        self.master.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.master.resizable(False, False)
        self.master.configure(bg=self.bg_color)
        
        # Initialize canvas_center coordinates
        self.canvas_center_x = self.WINDOW_WIDTH // 2
        self.canvas_center_y = self.WINDOW_HEIGHT // 4
        
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange the UI components."""
        # Main container with padding
        self.container = ttk.Frame(self.master)
        self.container.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Title area
        self.title_label = ttk.Label(
            self.container,
            text="Spelling Bee",
            font=('Arial', 20, 'bold'),
            foreground='white',
            background=self.bg_color
        )
        self.title_label.pack(pady=(0, 10))
        
        # Letters display canvas
        canvas_size = max(self.WINDOW_WIDTH - 40, self.WINDOW_HEIGHT // 2)
        self.letters_canvas = tk.Canvas(
            self.container,
            height=canvas_size,
            width=canvas_size,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.letters_canvas.pack(pady=10)
        
        # Bind the configure event to update canvas center coordinates
        self.letters_canvas.bind('<Configure>', self._update_canvas_center)
        
        # Player information area
        self.player_frame = ttk.Frame(self.container)
        self.player_frame.pack(fill='x', pady=10)
        
        # Create frames for each player
        self.player_info_frames = {}
        for player_id in [0, 1]:
            frame = ttk.Frame(self.player_frame)
            frame.pack(side='left', expand=True, padx=10)
            
            # Simple label for player word display
            label = tk.Label(
                frame,
                font=('Arial', 12),
                fg='white',
                bg=self.bg_color
            )
            label.pack(pady=5)
            
            self.player_info_frames[player_id] = {
                'frame': frame,
                'label': label
            }

    def _update_canvas_center(self, event=None):
        """Update the canvas center coordinates when the canvas is configured."""
        self.canvas_center_x = self.letters_canvas.winfo_width() // 2
        self.canvas_center_y = self.letters_canvas.winfo_height() // 2
        self.draw_board()

    def _calculate_hexagon_points(self, center_x: float, center_y: float, size: float) -> list:
        """Calculate the points for drawing a hexagon."""
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            x = center_x + size * math.cos(angle_rad)
            y = center_y + size * math.sin(angle_rad)
            points.extend([x, y])
        return points

    def _draw_letter_cell(self, x: float, y: float, letter: str, is_center: bool = False):
        """Draw a hexagonal cell with a letter inside."""
        points = self._calculate_hexagon_points(x, y, self.LETTER_CELL_SIZE)
        
        self.letters_canvas.create_polygon(
            points,
            fill=self.letter_colors['bg'],
            outline='black',
            width=2
        )
        
        self.letters_canvas.create_text(
            x, y,
            text=letter.upper(),
            font=('Arial', self.LETTER_FONT_SIZE, 'bold' if is_center else 'normal'),
            fill=self.letter_colors['fg']
        )

    def draw_board(self):
        """Update the display with current game state."""
        if not hasattr(self.env.state, "game_state"):
            return
            
        game_state = self.env.state.game_state
        
        # Clear existing canvas
        self.letters_canvas.delete('all')
        
        # Get allowed letters
        letters = sorted(list(game_state["allowed_letters"]))
        if not letters:
            return
            
        # Calculate positions for any number of letters
        num_letters = len(letters)
        if num_letters <= 6:
            # Original positions for 6 or fewer letters
            positions = [
                (0, -2),      # Top
                (1.75, -1),   # Top right
                (1.75, 1),    # Bottom right
                (0, 2),       # Bottom
                (-1.75, 1),   # Bottom left
                (-1.75, -1),  # Top left
            ]
        else:
            # Create positions for all letters in a circular pattern
            positions = []
            radius = 2  # Adjust this value to control the circle size
            for i in range(num_letters):
                angle = 2 * math.pi * i / num_letters - math.pi/2  # Start from top
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                positions.append((x * 1.75, y))  # Adjust multiplier to control spacing
        
        # Draw hexagons in pattern
        spacing = self.LETTER_CELL_SIZE * 1.2
        for i, letter in enumerate(letters):
            if i < len(positions):
                dx, dy = positions[i]
                x = self.canvas_center_x + dx * spacing
                y = self.canvas_center_y + dy * spacing
                self._draw_letter_cell(x, y, letter)
        
        # Update player information - simple text display
        for player_id in [0, 1]:
            word = game_state["player_words"].get(player_id)
            label = self.player_info_frames[player_id]['label']
            
            if not word:
                label.config(text=f"{self.player_names[player_id]}: ---")
            else:
                label.config(text=f"{self.player_names[player_id]}: {word}")
        
        # Update the display
        self.update()