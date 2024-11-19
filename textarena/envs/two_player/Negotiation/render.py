import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Any, Dict, Optional
from PIL import Image, ImageTk
import os 
import textarena as ta 
import time 

class GameStateRender(ttk.Frame):
    CARD_HEIGHT = 100
    CARD_WIDTH = 75
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 950
    
    def __init__(self, master, env, player_names: Optional[Dict[int, str]] = None):
        super().__init__(master)
        self.master = master 
        self.env = env 
        self.player_names = player_names or {0: "Player 0", 1: "Player 1"}
        self.player_names[ta.GAME_ID] = "GAME"
        
        # Animation state
        self.animation_id = None
        self.animation_items = []
        
        # Color scheme
        self.player_colors = {
            0: '#4A90E2',  # Blue
            1: '#E24A4A'   # Red
        }
        self.bg_color = '#2B2B2B'
        
        # Configure the main window with fixed size
        self.master.title("Resource Trading")
        self.master.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.master.resizable(False, False)
        self.master.configure(bg=self.bg_color)
        
        # Load and store resource card images
        self.resource_images = {}
        self.load_resource_images()
        
        # Try to set icon if available
        icon_path = os.path.join("textarena", "assets", "textarena-icon.png")
        if os.path.exists(icon_path):
            try:
                self.master.iconphoto(False, tk.PhotoImage(file=icon_path))
            except Exception as e:
                print(f"Could not set window icon: {e}")
        
        self.create_widgets()
        
        # Force an initial size update after widget creation
        self.update_idletasks()
    
    
    def load_resource_images(self):
        """Load and resize resource card images."""
        resources = ['brick', 'ore', 'sheep', 'wheat', 'wood']
        for resource in resources:
            try:
                image = Image.open(
                    os.path.join(
                        "textarena", "envs", "two_player",
                        "Negotiation", "render_assets",
                        f"{resource}.png"
                    )
                )
                image = image.resize((self.CARD_WIDTH, self.CARD_HEIGHT), Image.Resampling.LANCZOS)
                self.resource_images[resource] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Could not load image for {resource}: {e}")
                self.create_fallback_image(resource)

    def create_widgets(self):
        """Create all widgets for the game interface."""
        # Main container
        self.container = ttk.Frame(self.master)
        self.container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Player frames
        self.player_frames = {}
        self.player_frames[0] = self.create_player_frame(0)
        
        # Center container for trade display
        self.trade_container = ttk.Frame(self.container)
        self.trade_container.pack(fill='x', pady=20)
        
        # Trade content wrapper for centering
        self.trade_content = ttk.Frame(self.trade_container)
        self.trade_content.pack(expand=True, anchor='center')
        
        # Trade cards section
        self.trade_frame = ttk.Frame(self.trade_content)
        self.trade_frame.pack(side='left', padx=10)
        
        self.trade_header = ttk.Label(
            self.trade_frame,
            text="Current Trade Offer",
            font=('Arial', 14, 'bold'),
            background=self.bg_color,
            foreground='white'
        )
        self.trade_header.pack(pady=10)
        
        # Increase canvas height to accommodate all elements
        self.trade_canvas = tk.Canvas(
            self.trade_frame,
            height=self.CARD_HEIGHT * 4,  # Increased height
            width=self.WINDOW_WIDTH - 100,  # Adjust width to window size
            bg=self.bg_color,
            highlightthickness=0
        )
        self.trade_canvas.pack()
        
        self.player_frames[1] = self.create_player_frame(1)


    def create_player_frame(self, player_id):
        """Create a frame for displaying player's resources and values."""
        frame = ttk.Frame(self.container)
        frame.pack(fill='x', pady=10)
        
        # Create header frame to hold name and value change
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill='x', pady=5)
        
        # Player name
        name_label = ttk.Label(
            header_frame,
            text=f"{self.player_names[player_id]}",
            font=('Arial', 14, 'bold'),
            background=self.bg_color,
            foreground=self.player_colors[player_id]
        )
        name_label.pack(side='left', padx=(0, 10))
        
        # Value change label (store reference to update later)
        value_label = ttk.Label(
            header_frame,
            text="(Value Change: +0)",
            font=('Arial', 12),
            background=self.bg_color,
            foreground='white'
        )
        value_label.pack(side='left')
        
        # Store reference to value label
        frame.value_label = value_label
        
        # Create canvas with explicit width
        canvas = tk.Canvas(
            frame,
            height=self.CARD_HEIGHT + 40,
            width=self.WINDOW_WIDTH - 40,  # Account for padding
            bg=self.bg_color,
            highlightthickness=0
        )
        canvas.pack(fill='x')
        
        return frame

    def animate_trade_result(self, accepted: bool):
        """Animate trade acceptance or rejection."""
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
            for item in self.animation_items:
                try:
                    self.trade_canvas.delete(item)
                except:
                    pass
        
        result_text = "ACCEPTED" if accepted else "REJECTED"
        color = "green" if accepted else "red"
        
        # Calculate center position (where the arrow is)
        canvas_width = self.trade_canvas.winfo_width()
        canvas_height = self.trade_canvas.winfo_height()
        cx = canvas_width // 2
        cy = canvas_height // 2
        
        # Create semi-transparent overlay
        overlay = self.trade_canvas.create_rectangle(
            cx - 100, cy - 30,  # Smaller overlay around the arrow
            cx + 100, cy + 30,
            fill='black',
            stipple='gray50',
            tags='animation'
        )
        
        # Create text on top of the overlay
        text = self.trade_canvas.create_text(
            cx, cy,
            text=result_text,
            font=('Arial', 48, 'bold'),
            fill=color,
            tags='animation'
        )
        
        self.animation_items = [overlay, text]
        
        def clear_animation():
            for item in self.animation_items:
                self.trade_canvas.delete(item)
            self.animation_items = []
            self.animation_id = None
        
        # Update the animation timing
        self.animation_id = self.master.after(2000, clear_animation)  # Increased to 2 seconds
        self.master.update()  # Force update to show animation

    def calculate_card_positions(self, resources, canvas_width):
        """Calculate x positions for centering cards given canvas width."""
        num_cards = len(resources)
        total_cards_width = num_cards * self.CARD_WIDTH
        total_spacing = (num_cards - 1) * 20 if num_cards > 1 else 0
        total_width = total_cards_width + total_spacing
        
        start_x = (canvas_width - total_width) // 2 + self.CARD_WIDTH // 2
        
        return [start_x + i * (self.CARD_WIDTH + 20) for i in range(num_cards)]
    

    def draw_board(self):
        """Update the display with current game state."""
        if hasattr(self.env.state, "game_state"):
            game_state = self.env.state.game_state
            
            # Update value change labels
            for player_id in [0, 1]:
                frame = self.player_frames[player_id]
                value_change = game_state["inventory_value"][player_id]["change"]
                value_color = 'green' if value_change > 0 else 'red' if value_change < 0 else 'white'
                frame.value_label.configure(
                    text=f"(Value Change: {value_change:+d})",
                    foreground=value_color
                )
            
            # Update player resources
            for player_id in [0, 1]:
                frame = self.player_frames[player_id]
                canvas = [w for w in frame.winfo_children() if isinstance(w, tk.Canvas)][0]
                canvas.delete('all')
                
                resources = game_state["player_resources"][player_id]
                values = game_state["player_values"][player_id]
                
                # Calculate x positions for perfect centering
                x_positions = self.calculate_card_positions(resources, canvas.winfo_width())
                
                for (resource, quantity), x in zip(resources.items(), x_positions):
                    self.draw_resource_card(
                        canvas,
                        resource,
                        quantity,
                        values[resource],
                        x,
                        self.CARD_HEIGHT//2 + 20,
                        self.player_colors[player_id],
                        show_value=True
                    )
            
            # Update trade offer display
            current_offer = game_state.get("current_offer")
            if current_offer:
                self.update_trade_display(current_offer)
            else:
                self.trade_header.configure(text="No Current Trade Offers")
                self.trade_canvas.delete('all')
            

    def draw_resource_card(self, canvas, resource, quantity, value, x, y, highlight_color=None, show_value=True):
        """Draw a resource card with quantity and value information."""
        # Draw card frame
        padding = 4
        frame_color = highlight_color if highlight_color else self.bg_color
        canvas.create_rectangle(
            x - self.CARD_WIDTH//2 - padding,
            y - self.CARD_HEIGHT//2 - padding,
            x + self.CARD_WIDTH//2 + padding,
            y + self.CARD_HEIGHT//2 + padding,
            fill=frame_color,
            outline=frame_color
        )
        
        # Draw card image
        canvas.create_image(x, y, image=self.resource_images[resource.lower()])
        
        # Draw value below the card (if requested)
        if show_value:
            canvas.create_text(
                x,
                y + self.CARD_HEIGHT//2 + 15,
                text=f"Value: {value}",
                fill='white',
                font=('Arial', 10, 'bold')
            )
        
        # Draw quantity badge in bottom right
        badge_radius = 12
        badge_x = x + self.CARD_WIDTH//2 - badge_radius - 5
        badge_y = y + self.CARD_HEIGHT//2 - badge_radius - 5
        
        canvas.create_oval(
            badge_x - badge_radius,
            badge_y - badge_radius,
            badge_x + badge_radius,
            badge_y + badge_radius,
            fill='#2B2B2B',
            outline='white'
        )
        canvas.create_text(
            badge_x,
            badge_y,
            text=str(quantity),
            fill='white',
            font=('Arial', 10, 'bold')
        )

    def calculate_trade_value(self, offer, player_id):
        """Calculate the value change for a player if the trade is accepted."""
        if not offer:
            return 0
            
        game_state = self.env.state.game_state
        player_values = game_state["player_values"][player_id]
        
        # Calculate value of resources received
        value_received = 0
        if player_id == offer["to_player"]:
            for resource, qty in offer["offered_resources"].items():
                value_received += player_values[resource] * qty
        else:
            for resource, qty in offer["requested_resources"].items():
                value_received += player_values[resource] * qty
                
        # Calculate value of resources given
        value_given = 0
        if player_id == offer["to_player"]:
            for resource, qty in offer["requested_resources"].items():
                value_given += player_values[resource] * qty
        else:
            for resource, qty in offer["offered_resources"].items():
                value_given += player_values[resource] * qty
                
        return value_received - value_given


    def update_trade_display(self, offer):
        """Update the trade offer display with cards and value calculations."""
        self.trade_canvas.delete('all')
        
        from_player = offer["from_player"]
        to_player = offer["to_player"]
        
        self.trade_header.configure(
            text=f"Trade Offer from {self.player_names[from_player]} to {self.player_names[to_player]}"
        )
        
        canvas_width = self.trade_canvas.winfo_width()
        canvas_height = self.trade_canvas.winfo_height()
        
        # Player 0 is always on top, Player 1 on bottom
        # Position resources based on player positions, not offer direction
        if from_player == 0:
            # Player 0 (top) is offering to Player 1 (bottom)
            top_resources = offer["offered_resources"]
            bottom_resources = offer["requested_resources"]
            arrow_direction = 1  # Pointing down
        else:
            # Player 1 (bottom) is offering to Player 0 (top)
            top_resources = offer["requested_resources"]
            bottom_resources = offer["offered_resources"]
            arrow_direction = -1  # Pointing up
        
        # Calculate value changes
        value_change_top = self.calculate_trade_value(offer, 0)  # Player 0 (top)
        value_change_bottom = self.calculate_trade_value(offer, 1)  # Player 1 (bottom)
        
        # Calculate vertical positions
        value_text_top_y = canvas_height * 0.05
        cards_top_y = canvas_height * 0.3
        cards_bottom_y = canvas_height * 0.7
        value_text_bottom_y = canvas_height * 0.95
        
        # Display top player's value change
        color_top = 'green' if value_change_top > 0 else 'red' if value_change_top < 0 else 'white'
        self.trade_canvas.create_text(
            canvas_width // 2,
            value_text_top_y,
            text=f"{self.player_names[0]}'s value change: {value_change_top:+d}",
            fill=color_top,
            font=('Arial', 12, 'bold')
        )
        
        # Display bottom player's value change
        color_bottom = 'green' if value_change_bottom > 0 else 'red' if value_change_bottom < 0 else 'white'
        self.trade_canvas.create_text(
            canvas_width // 2,
            value_text_bottom_y,
            text=f"{self.player_names[1]}'s value change: {value_change_bottom:+d}",
            fill=color_bottom,
            font=('Arial', 12, 'bold')
        )
        
        # Calculate horizontal positions for cards
        x_start_top = (canvas_width - len(top_resources) * (self.CARD_WIDTH + 20)) // 2 + self.CARD_WIDTH//2
        x_start_bottom = (canvas_width - len(bottom_resources) * (self.CARD_WIDTH + 20)) // 2 + self.CARD_WIDTH//2
        
        # Draw arrow
        cx = canvas_width // 2
        arrow_y1 = cards_top_y + self.CARD_HEIGHT//2 + 10
        arrow_y2 = cards_bottom_y - self.CARD_HEIGHT//2 - 10
        
        if arrow_direction == 1:
            # Arrow pointing down (from top to bottom)
            start_y = arrow_y1
            end_y = arrow_y2
        else:
            # Arrow pointing up (from bottom to top)
            start_y = arrow_y2
            end_y = arrow_y1
        
        self.trade_canvas.create_line(
            cx, start_y,
            cx, end_y,
            arrow='last',
            fill='white',
            width=2
        )
        
        # Draw top resources
        for i, (resource, quantity) in enumerate(top_resources.items()):
            x = x_start_top + i * (self.CARD_WIDTH + 20)
            self.draw_resource_card(
                self.trade_canvas,
                resource,
                quantity,
                self.env.state.game_state["player_values"][0][resource],  # Always Player 0's values for top
                x,
                cards_top_y,
                self.player_colors[0],  # Always Player 0's color for top
                show_value=False
            )
        
        # Draw bottom resources
        for i, (resource, quantity) in enumerate(bottom_resources.items()):
            x = x_start_bottom + i * (self.CARD_WIDTH + 20)
            self.draw_resource_card(
                self.trade_canvas,
                resource,
                quantity,
                self.env.state.game_state["player_values"][1][resource],  # Always Player 1's values for bottom
                x,
                cards_bottom_y,
                self.player_colors[1],  # Always Player 1's color for bottom
                show_value=False
            )

    def on_window_resize(self, event):
        """Handle window resize events - removed since window is now fixed size."""
        pass
