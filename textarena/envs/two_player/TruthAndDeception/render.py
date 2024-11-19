import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

class GameStateRender(ttk.Frame):
    """Renderer for the Truth and Deception game state."""
    
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    PADDING = 20
    
    def __init__(self, master, env, player_names: Optional[Dict[int, str]] = None):
        super().__init__(master)
        self.master = master
        self.env = env
        self.player_names = player_names or {0: "Player 0", 1: "Player 1"}
        self.player_colors = {
            0: '#4A90E2',  # Blue
            1: '#E24A4A'   # Red
        }
        
        # Color scheme
        self.bg_color = '#2B2B2B'
        self.text_color = '#FFFFFF'
        self.deceiver_color = '#E24A4A'  # Red for deceiver
        self.guesser_color = '#4A90E2'   # Blue for guesser
        self.fact_bg_color = '#1E1E1E'
        self.correct_fact_color = '#2E7D32'  # Green for correct fact
        self.wrong_fact_color = '#424242'  # Darker gray for wrong fact
        
        # Configure main window
        self.master.title("Truth and Deception Game")
        self.master.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.master.configure(bg=self.bg_color)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create the main UI components."""
        # Main container with padding
        self.container = ttk.Frame(self.master)
        self.container.pack(expand=True, fill='both', padx=self.PADDING, pady=self.PADDING)
        
        # Game info section (includes turn counter and player roles)
        self.info_frame = tk.Frame(self.container, bg=self.bg_color)
        self.info_frame.pack(fill='x', pady=(0, self.PADDING))
        
        # Turn counter
        self.turn_label = tk.Label(
            self.info_frame,
            text="Turn: 0/0",
            font=('Arial', 14, 'bold'),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.turn_label.pack(side='left')
        
        # Spacer
        tk.Label(
            self.info_frame,
            text="  |  ",
            font=('Arial', 14, 'bold'),
            bg=self.bg_color,
            fg='#404040'  # Darker separator color
        ).pack(side='left')
        
        # Player roles
        # Deceiver (Player 0)
        tk.Label(
            self.info_frame,
            text=f"{self.player_names[0]} (Deceiver)",
            font=('Arial', 14, 'bold'),
            bg=self.bg_color,
            fg=self.deceiver_color
        ).pack(side='left')
        
        # Small spacer
        tk.Label(
            self.info_frame,
            text="  •  ",
            font=('Arial', 14),
            bg=self.bg_color,
            fg='#404040'  # Darker separator color
        ).pack(side='left')
        
        # Guesser (Player 1)
        tk.Label(
            self.info_frame,
            text=f"{self.player_names[1]} (Guesser)",
            font=('Arial', 14, 'bold'),
            bg=self.bg_color,
            fg=self.guesser_color
        ).pack(side='left')
        
        # Facts section
        self.facts_frame = ttk.Frame(self.container)
        self.facts_frame.pack(fill='x', pady=(0, self.PADDING))
        
        # Facts header
        facts_header = tk.Label(
            self.facts_frame,
            text="Facts in Discussion:",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color,
            fg=self.text_color
        )
        facts_header.pack(fill='x', pady=(0, 10))
        
        # Create fact displays
        self.create_fact_display("Fact 1:", 0)
        self.create_fact_display("Fact 2:", 1)
        
        # Conversation history
        self.create_conversation_view()
        
    def create_fact_display(self, label: str, index: int):
        """Create a clean display for a fact without borders."""
        frame = tk.Frame(self.facts_frame, bg=self.bg_color)
        frame.pack(fill='x', pady=(0, 10))
        
        # Fact label
        label_widget = tk.Label(
            frame,
            text=label,
            font=('Arial', 11, 'bold'),
            bg=self.bg_color,
            fg=self.text_color,
            anchor='w'
        )
        label_widget.pack(side='left', padx=(0, 10))
        
        # Fact text
        fact_label = tk.Label(
            frame,
            text="",
            font=('Arial', 11),
            bg=self.bg_color,
            fg=self.text_color,
            justify='left',
            anchor='w',
            wraplength=600  # Allow text wrapping
        )
        fact_label.pack(side='left', fill='x', expand=True)
        
        # Store references
        setattr(self, f'fact_{index}_label', label_widget)
        setattr(self, f'fact_{index}_text', fact_label)
        
    def create_conversation_view(self):
        """Create the conversation history view."""
        frame = ttk.Frame(self.container)
        frame.pack(fill='both', expand=True)
        
        # Header
        header = tk.Label(
            frame,
            text="Conversation History",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color,
            fg=self.text_color
        )
        header.pack(fill='x', pady=(0, 5))
        
        # Conversation text area
        self.conversation_text = tk.Text(
            frame,
            font=('Arial', 11),
            wrap='word',
            bg=self.fact_bg_color,
            fg=self.text_color,
            relief='flat',
            state='disabled'
        )
        self.conversation_text.pack(fill='both', expand=True)
        
        # Configure tags for different message types
        self.conversation_text.tag_configure(
            'deceiver',
            foreground=self.deceiver_color,
            font=('Arial', 11, 'bold')
        )
        self.conversation_text.tag_configure(
            'guesser',
            foreground=self.guesser_color,
            font=('Arial', 11, 'bold')
        )
        self.conversation_text.tag_configure(
            'game',
            foreground='#A0A0A0',
            font=('Arial', 11, 'italic')
        )
        
    def update_fact_display(self, index: int, text: str, is_correct: bool):
        """Update the text and styling of a fact display."""
        text_widget = getattr(self, f'fact_{index}_text')
        label_widget = getattr(self, f'fact_{index}_label')
        
        # Update text
        text_widget.configure(text=text)
        
        # Update colors based on correctness
        if is_correct:
            text_widget.configure(fg=self.correct_fact_color)
            label_widget.configure(fg=self.correct_fact_color)
        else:
            text_widget.configure(fg=self.text_color)
            label_widget.configure(fg=self.text_color)
        
    def add_conversation_message(self, sender_id: int, message: str):
        """Add a message to the conversation history."""
        self.conversation_text.configure(state='normal')
        
        # Add newline if not empty
        if self.conversation_text.get('1.0', 'end').strip():
            self.conversation_text.insert('end', '\n')
        
        # Format message based on sender
        if sender_id == -1:  # Game message
            self.conversation_text.insert('end', '[GAME] ', 'game')
            self.conversation_text.insert('end', f"{message}")
        else:  # Player message
            role = 'deceiver' if sender_id == 0 else 'guesser'
            self.conversation_text.insert('end', f"[{self.player_names[sender_id]}] ", role)
            self.conversation_text.insert('end', f"{message}")
        
        # Auto-scroll to bottom
        self.conversation_text.see('end')
        self.conversation_text.configure(state='disabled')
        
    def draw_board(self):
        """Update the display with current game state."""
        if not hasattr(self.env.state, "game_state"):
            return
            
        game_state = self.env.state.game_state
        
        # Update turn counter
        self.turn_label.configure(
            text=f"Turn: {self.env.state.turn}/{self.env.state.max_turns}"
        )
        
        # Update facts
        self.update_fact_display(
            0, 
            game_state['fact1']['fact'],
            game_state['fact1']['is_correct']
        )
        self.update_fact_display(
            1, 
            game_state['fact2']['fact'],
            game_state['fact2']['is_correct']
        )
        
        # Clear and redraw conversation history
        self.conversation_text.configure(state='normal')
        self.conversation_text.delete('1.0', 'end')
        
        # Add all messages from logs
        for sender_id, message in self.env.state.logs:
            self.add_conversation_message(sender_id, message)
            
        self.conversation_text.configure(state='disabled')