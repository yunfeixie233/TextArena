import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional
from PIL import Image, ImageTk
import os

class GameStateRender(ttk.Frame):
    CARD_HEIGHT = 100
    CARD_WIDTH = 75
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 800
    TABLE_HEIGHT = 300
    TABLE_PADDING = 30
    CARD_SPACING = 15
    
    def __init__(self, master, env, player_names: Optional[Dict[int, str]] = None):
        super().__init__(master)
        self.master = master
        self.env = env
        self.player_names = player_names or {0: "Player 0", 1: "Player 1"}
        
        # Color scheme
        self.player_colors = {
            0: '#4A90E2',  # Blue
            1: '#E24A4A'   # Red
        }
        self.bg_color = '#2B2B2B'
        self.felt_color = '#1B5E20'  # Darker poker table green
        
        # Configure main window
        self.master.title("Texas Hold'em Poker")
        self.master.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.master.resizable(False, False)
        self.master.configure(bg=self.bg_color)
        
        # Load card images
        self.card_images = {}
        self.load_card_images()
        
        self.create_widgets()


    def _get_card_filename(self, rank: str, suit: str) -> str:
        """Convert rank and suit to filename format."""
        rank_map = {
            "J": "jack",
            "Q": "queen",
            "K": "king",
            "A": "ace"
        }
        rank_str = rank_map.get(rank, str(rank))
        
        suit_map = {
            "♠": "spades",
            "♥": "hearts",
            "♦": "diamonds",
            "♣": "clubs"
        }
        suit_str = suit_map[suit]
        
        return f"{rank_str}_of_{suit_str}.png"

    def load_card_images(self):
        """Load card images from assets folder."""
        assets_path = os.path.join("textarena", "envs", "two_player", "Poker", "render_assets")
        
        suits = ["♠", "♥", "♦", "♣"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        
        for suit in suits:
            for rank in ranks:
                try:
                    filename = self._get_card_filename(rank, suit)
                    filepath = os.path.join(assets_path, filename)
                    image = Image.open(filepath)
                    image = image.resize((self.CARD_WIDTH, self.CARD_HEIGHT), Image.Resampling.LANCZOS)
                    self.card_images[f"{rank}{suit}"] = ImageTk.PhotoImage(image)
                except Exception as e:
                    print(f"Could not load image for {rank}{suit}: {e}")
        
        try:
            back_path = os.path.join(assets_path, "back.png")
            back = Image.open(back_path)
            back = back.resize((self.CARD_WIDTH, self.CARD_HEIGHT), Image.Resampling.LANCZOS)
            self.card_images["BACK"] = ImageTk.PhotoImage(back)
        except Exception as e:
            print(f"Could not load card back image: {e}")
            self._create_fallback_card_back()

    def _create_fallback_card_back(self):
        """Create a simple card back if image loading fails."""
        image = Image.new('RGB', (self.CARD_WIDTH, self.CARD_HEIGHT), '#AA0000')
        self.card_images["BACK"] = ImageTk.PhotoImage(image)

    def draw_card(self, canvas, card, x, y, face_up=True):
        """Draw a card at the specified position."""
        if face_up:
            card_key = f"{card['rank']}{card['suit']}"
            image = self.card_images.get(card_key)
        else:
            image = self.card_images["BACK"]
            
        if image:
            canvas.create_image(x, y, image=image)

    def create_widgets(self):
        """Create the poker table interface."""
        # Main container
        self.container = ttk.Frame(self.master)
        self.container.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Player 1 (top) area
        self.player_frames = {}
        self.player_frames[1] = self.create_player_frame(1, 'top')
        
        # Table frame
        self.table_frame = ttk.Frame(self.container)
        self.table_frame.pack(fill='both', expand=True, pady=5)
        
        # Calculate canvas position
        canvas_width = self.WINDOW_WIDTH - 70
        canvas_x = (self.WINDOW_WIDTH - canvas_width) // 2 #- 10  # Adjust for container padding
        
        self.table_canvas = tk.Canvas(
            self.table_frame,
            height=self.TABLE_HEIGHT,
            width=canvas_width,
            bg=self.felt_color,
            highlightthickness=0
        )
        self.table_canvas.place(relx=0.5, rely=0.5, anchor='center')
        
        # Player 0 (bottom) area
        self.player_frames[0] = self.create_player_frame(0, 'bottom')


    def create_player_frame(self, player_id, position):
        """Create a frame for displaying player's cards and chips."""
        frame = ttk.Frame(self.container)
        frame.pack(fill='x', pady=5)
        
        # Header frame for player info
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill='x', pady=2)
        
        name_label = ttk.Label(
            header_frame,
            text=f"{self.player_names[player_id]}",
            font=('Arial', 14, 'bold'),
            background=self.bg_color,
            foreground=self.player_colors[player_id]
        )
        name_label.pack(side='left', padx=(0, 10))
        
        chips_label = ttk.Label(
            header_frame,
            text="Chips: 1000",
            font=('Arial', 12),
            background=self.bg_color,
            foreground='white'
        )
        chips_label.pack(side='left')
        
        frame.chips_label = chips_label
        
        # Canvas for cards
        canvas = tk.Canvas(
            frame,
            height=self.CARD_HEIGHT + 10,
            width=self.WINDOW_WIDTH - 40,
            bg=self.bg_color,
            highlightthickness=0
        )
        canvas.pack(fill='x')
        
        return frame

    def draw_board(self):
        """Update the display with current game state."""
        if not hasattr(self.env.state, "game_state"):
            return
            
        game_state = self.env.state.game_state
        
        # Clear and redraw table
        self.table_canvas.delete('all')
        
        # Draw rounded table
        table_width = self.WINDOW_WIDTH - 80
        table_height = self.TABLE_HEIGHT - 20
        x1, y1 = 10, 10
        x2, y2 = table_width, table_height
        radius = 40
        
        self.table_canvas.create_polygon(
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
            fill='#2E7D32',
            smooth=True
        )
        
        # Draw pot at the top
        self.table_canvas.create_text(
            self.WINDOW_WIDTH // 2 - self.TABLE_PADDING,
            30,
            text=f"Pot: ${game_state['pot']}",
            fill='white',
            font=('Arial', 16, 'bold')
        )
        
        # Draw community cards centered
        visible_cards = game_state["visible_community_cards"]
        all_cards = game_state["community_cards"]
        
        total_width = (5 * self.CARD_WIDTH) + (4 * self.CARD_SPACING)
        start_x = ((self.WINDOW_WIDTH - 60) - total_width) // 2
        
        for i in range(5):
            x = start_x + (i * (self.CARD_WIDTH + self.CARD_SPACING)) + self.CARD_WIDTH // 2
            y = self.TABLE_HEIGHT // 2
            
            if i < len(visible_cards):
                self.draw_card(self.table_canvas, all_cards[i], x, y, face_up=True)
            else:
                self.draw_card(self.table_canvas, {'rank': 'BACK', 'suit': 'BACK'}, x, y, face_up=False)
        
        # Draw round information
        betting_round_names = ["Pre-flop", "Flop", "Turn", "River"]
        current_betting_round = betting_round_names[game_state["betting_round"]]
        current_round = game_state.get("round", 1)
        total_rounds = self.env.state.max_turns #game_state.get("total_rounds", 1)

        round_text = f"Round {current_round}/{total_rounds} - ({current_betting_round})"
        
        self.table_canvas.create_text(
            self.WINDOW_WIDTH // 2 - self.TABLE_PADDING,
            self.TABLE_HEIGHT - 40,
            text=round_text,
            fill='white',
            font=('Arial', 14, 'bold')
        )
        
        # Update player hands
        for player_id in [0, 1]:
            frame = self.player_frames[player_id]
            chips = game_state["player_chips"][player_id]
            current_bet = game_state["player_bets"][player_id]
            frame.chips_label.configure(
                text=f"Chips: {chips} (Bet: {current_bet})"
            )
            
            # Clear and redraw player cards
            canvas = [w for w in frame.winfo_children() if isinstance(w, tk.Canvas)][0]
            canvas.delete('all')
            
            # Draw player's hole cards centered
            cards = game_state["player_hands"][player_id]
            if cards:
                total_width = (2 * self.CARD_WIDTH) + self.CARD_SPACING
                start_x = (self.WINDOW_WIDTH - total_width) // 2 - 20
                y = self.CARD_HEIGHT // 2 + 10
                
                self.draw_card(canvas, cards[0], start_x + self.CARD_WIDTH // 2, y, face_up=True)
                self.draw_card(canvas, cards[1], start_x + self.CARD_WIDTH + self.CARD_SPACING + self.CARD_WIDTH // 2, y, face_up=True)