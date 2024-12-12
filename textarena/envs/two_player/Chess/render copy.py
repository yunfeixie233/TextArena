import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional
from PIL import Image, ImageTk
import os
import chess

class GameStateRender(ttk.Frame):
    """Render wrapper for the Chess environment."""
    
    SQUARE_SIZE = 64  # Size of each chess square in pixels
    LABEL_SPACE = 20  # Space for coordinate labels
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 610
    
    def __init__(self, master, env, player_names: Optional[Dict[int, str]] = None):
        super().__init__(master)
        self.master = master
        self.env = env
        self.player_names = player_names or {0: "White", 1: "Black"}
        
        # Color scheme
        self.light_square_color = '#EEEED2'  # Light square color
        self.dark_square_color = '#769656'   # Dark square color
        self.bg_color = '#2B2B2B'           # Background color
        self.text_color = '#FFFFFF'          # Text color
        self.player_colors = {
            0: '#FFFFFF',
            1: '#000000'
        }
        
        # Configure main window
        self.master.title("Chess Game")
        self.master.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.master.configure(bg=self.bg_color)
        
        # Load piece images
        self.piece_images = {}
        self.load_piece_images()
        
        # Try to set icon if available
        icon_path = os.path.join("textarena", "assets", "textarena-icon.png")
        if os.path.exists(icon_path):
            try:
                self.master.iconphoto(False, tk.PhotoImage(file=icon_path))
            except Exception as e:
                print(f"Could not set window icon: {e}")
        
        self.create_widgets()
        
    def load_piece_images(self):
        """Load and resize chess piece images."""
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
        for piece in pieces:
            try:
                image = Image.open(
                    os.path.join(
                        "textarena", "envs", "two_player",
                        "Chess", "render_assets",
                        f"{piece}.png"
                    )
                )
                image = image.resize((self.SQUARE_SIZE, self.SQUARE_SIZE), Image.Resampling.LANCZOS)
                self.piece_images[piece] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Could not load image for {piece}: {e}")
                self.create_fallback_piece(piece)
    
    def create_fallback_piece(self, piece: str):
        """Create a fallback text-based piece image if PNG loading fails."""
        img = Image.new('RGBA', (self.SQUARE_SIZE, self.SQUARE_SIZE), (0, 0, 0, 0))
        self.piece_images[piece] = ImageTk.PhotoImage(img)
    
    def create_widgets(self):
        """Create all widgets for the chess interface."""
        # Main container
        self.container = ttk.Frame(self.master)
        self.container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Game info frame (top)
        self.info_frame = ttk.Frame(self.container)
        self.info_frame.pack(fill='x', pady=(0, 10))
        
        # Turn indicator
        self.turn_label = ttk.Label(
            self.info_frame,
            text="White to move",
            font=('Arial', 14, 'bold'),
            background=self.bg_color,
            foreground=self.text_color
        )
        self.turn_label.pack(side='left')
        
        # Move history frame (right)
        self.history_frame = ttk.Frame(self.container)
        self.history_frame.pack(side='right', fill='y', padx=(10, 0))
        
        history_label = ttk.Label(
            self.history_frame,
            text="Move History",
            font=('Arial', 12, 'bold'),
            background=self.bg_color,
            foreground=self.text_color
        )
        history_label.pack(pady=(0, 5))
        
        # Move history text widget
        self.history_text = tk.Text(
            self.history_frame,
            width=20,
            height=20,
            bg=self.bg_color,
            fg=self.text_color,
            font=('Arial', 10)
        )
        self.history_text.pack(fill='both', expand=True)
        
        # Chess board frame
        self.board_frame = ttk.Frame(self.container)
        self.board_frame.pack(side='left', padx=(0, 10))
        
        # Create chess board canvas with extra space for labels
        board_size = self.SQUARE_SIZE * 8
        canvas_size = board_size + self.LABEL_SPACE
        self.board_canvas = tk.Canvas(
            self.board_frame,
            width=canvas_size,
            height=canvas_size,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.board_canvas.pack()
        
        # Game status label (bottom)
        self.status_label = ttk.Label(
            self.container,
            text="",
            font=('Arial', 12),
            background=self.bg_color,
            foreground=self.text_color
        )
        self.status_label.pack(fill='x', pady=(10, 0))
    
    def draw_board(self):
        """Update the display with current game state."""
        if not hasattr(self.env.state, "game_state"):
            return
            
        board = self.env.board #chess.Board(self.env.state.game_state["current_board"])
        
        # Clear canvas
        self.board_canvas.delete('all')
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * self.SQUARE_SIZE + self.LABEL_SPACE  # Offset for rank labels
                y1 = (7 - row) * self.SQUARE_SIZE
                x2 = x1 + self.SQUARE_SIZE
                y2 = y1 + self.SQUARE_SIZE
                
                # Determine square color
                color = self.light_square_color if (row + col) % 2 == 0 else self.dark_square_color
                
                # Draw square
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
                
                # Draw piece if present
                square = chess.square(col, row)
                piece = board.piece_at(square)
                if piece:
                    piece_symbol = piece.symbol()
                    if piece_symbol in self.piece_images:
                        self.board_canvas.create_image(
                            x1 + self.SQUARE_SIZE/2,
                            y1 + self.SQUARE_SIZE/2,
                            image=self.piece_images[piece_symbol]
                        )
        
        # Draw coordinates
        for i in range(8):
            # Draw rank labels (1-8) on the left
            self.board_canvas.create_text(
                self.LABEL_SPACE/2,
                i * self.SQUARE_SIZE + self.SQUARE_SIZE/2,
                text=str(8 - i),
                fill=self.text_color,
                font=('Arial', 10)
            )
            # Draw file labels (a-h) below
            self.board_canvas.create_text(
                i * self.SQUARE_SIZE + self.SQUARE_SIZE/2 + self.LABEL_SPACE,
                8 * self.SQUARE_SIZE + self.LABEL_SPACE/2,
                text=chr(97 + i),
                fill=self.text_color,
                font=('Arial', 10)
            )
        
        # Update turn indicator
        current_player = "White" if board.turn else "Black"
        self.turn_label.configure(text=f"{current_player} to move")
        
        # Update game status
        if board.is_checkmate():
            winner = "Black" if board.turn else "White"
            self.status_label.configure(text=f"Checkmate! {winner} wins!")
        elif board.is_stalemate():
            self.status_label.configure(text="Stalemate! Game is drawn.")
        elif board.is_insufficient_material():
            self.status_label.configure(text="Draw due to insufficient material.")
        elif board.is_check():
            self.status_label.configure(text=f"{current_player} is in check!")
        else:
            self.status_label.configure(text="")
        
        # Update move history
        self.update_move_history(board)
    
    def update_move_history(self, board: chess.Board):
        """Update the move history display."""
        self.history_text.delete('1.0', tk.END)
        moves = list(board.move_stack)
        for i in range(0, len(moves), 2):
            move_number = i // 2 + 1
            white_move = moves[i].uci()
            black_move = moves[i + 1].uci() if i + 1 < len(moves) else ""
            self.history_text.insert(tk.END, f"{move_number}. {white_move} {black_move}\n")