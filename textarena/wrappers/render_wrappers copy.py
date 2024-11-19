from textarena.core import Env, Message, RenderWrapper, State

import os 
import tkinter as tk 
from tkinter import ttk, scrolledtext 
from PIL import Image, ImageTk

from typing import Any, Dict, Optional, List, Callable


__all__ = [
    "PrettyRenderWrapper"
    "TkinterRenderWrapper"
]

BG_COLOR = "#2B2B2B"

class ChatWindow(ttk.Frame):
    def __init__(self, master, player_names: Dict[int, str], player_colors: Dict[int, str]):
        super().__init__(master)
        self.master = master 
        self.player_names = player_names 
        self.player_colors = player_colors 

        self.master.title("TextArena")
        self.master.geometry("600x400")
        self.master.minsize(400, 300)
        self.master.configure(bg=BG_COLOR)

        # Create a frame to contain the ScolledText
        self.container_frame = ttk.Frame(self.master)
        self.container_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create text widget
        self.text_area = scrolledtext.ScrolledText(
            self.container_frame,
            wrap=tk.WORD, 
            height=15,
            bg=BG_COLOR, 
            fg='white', 
            font=('Helvetica', 12),
            insertbackground='white',
            selectbackground='#404040',
            selectforeground='white',
        )
        self.text_area.pack(fill='both', expand=True)


        # Try to set icon if available
        icon_path = os.path.join("textarena", "assets", "textarena-icon.png")
        if os.path.exists(icon_path):
            try:
                self.master.iconphoto(False, tk.PhotoImage(file=icon_path))
            except Exception as e:
                print(f"Could not set window icon: {e}")

        # Enable mouse wheel scrolling for both the text area and its parent
        self.text_area.bind('<MouseWheel>', self._on_mousewheel)
        self.text_area.bind('<Button-4>', self._on_mousewheel)
        self.text_area.bind('<Button-5>', self._on_mousewheel)
        self.master.bind('<MouseWheel>', self._on_mousewheel)
        self.master.bind('<Button-4>', self._on_mousewheel)
        self.master.bind('<Button-5>', self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        if event.num == 4:  # Linux scroll up
            self.text_area.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.text_area.yview_scroll(1, "units")
        else:  # Windows
            self.text_area.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"  # Prevents event propagation

    def add_message(self, player_id: int, message: str):
        """Add a new message to the chat window with player-specific formatting."""
        self.text_area.configure(state='normal')
        player_name = self.player_names.get(player_id, f"Player {player_id}")
        color = self.player_colors.get(player_id, 'white')
        self.text_area.insert('end', f"{player_name}: ", f"player_{player_id}")
        self.text_area.insert('end', f"{message}\n\n")
        self.text_area.tag_config(f"player_{player_id}", foreground=color)
        self.text_area.see('end')
        self.text_area.configure(state='disabled')


class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        
        # Set window properties
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.transient(parent)

        # Create custom styles for the dialog
        style = ttk.Style()
        style.configure('Custom.TLabel',
            background=BG_COLOR,
            foreground='white',
            font=('Helvetica', 12)
        )
        style.configure('Custom.TButton',
            background='#3C3F41',
            foreground='white',
            padding=5
        )

        # Create and pack the image label if the icon exists
        icon_path = os.path.join("textarena", "assets", "textarena-icon.png")
        if os.path.exists(icon_path):
            try:
                # Open and resize the image
                original_image = Image.open(icon_path)
                new_size = (int(original_image.width * 0.3), int(original_image.height * 0.3))  # Scale by 30%
                resized_image = original_image.resize(new_size, Image.ANTIALIAS)
                
                # Convert the image to a format Tkinter can use
                self.photo = ImageTk.PhotoImage(resized_image)
                img_label = tk.Label(self, image=self.photo, bg=BG_COLOR)
                img_label.pack(pady=(10, 10))  # Add vertical padding as needed
            except Exception as e:
                print(f"Could not load image: {e}")
        else:
            print(f"Icon path does not exist: {icon_path}")

        # Create and pack the message label
        label = ttk.Label(
            self,
            text=message,
            style='Custom.TLabel',
            wraplength=300
        )
        label.pack(padx=20, pady=(0, 10))
        
        # Create and pack the OK button
        button = ttk.Button(
            self,
            text="OK",
            style='Custom.TButton',
            command=self.destroy
        )
        button.pack(pady=(0, 20))
        
        # Update idle tasks to ensure geometry info is accurate
        self.update_idletasks()
        
        # Center the dialog on the parent window
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        center_x = parent_x + (parent_width // 2) - (dialog_width // 2)
        center_y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f"+{center_x}+{center_y}")
        
        # Make the dialog modal
        self.grab_set()
        self.focus_set()
        self.wait_window()



# class TkinterRenderWrapper:
#     def __init__(self, env: Any, player_names: Optional[Dict[int, str]] = None):
#         self.env = env
#         self.player_names = player_names or {0: "Player 0", 1: "Player 1"}

#         self.root = tk.Tk()
#         self.game_render = env.board_state_render(self.root, env, player_names)
#         self.chat_window = tk.Toplevel(self.root)
#         self.chat = ChatWindow(
#             self.chat_window,
#             player_names=self.player_names,
#             player_colors=self.game_render.player_colors
#         )

#         self._create_styles()
#         self.game_render.draw_board()


#     def _create_styles(self):
#         style = ttk.Style()
#         style.theme_use('clam')
#         style.configure('TFrame', background=BG_COLOR)
#         style.configure('TLabel', background=BG_COLOR, foreground='#FFFFFF', font=('Helvetica', 12))
#         style.configure('TButton', background='#3C3F41', foreground='#FFFFFF', font=('Helvetica', 12))
#         style.map('TButton', background=[('active', '#5C5C5C')])


#     def step(self, player_id: int, action: str):
#         """Step the environment and update the display."""
#         # Add message to chat window before stepping
#         self.chat.add_message(player_id, action)
        
#         # Step the environment
#         result = self.env.step(player_id, action)
#         observations, rewards, truncated, terminated, info = result
        
#         # Update the display
#         self.game_render.draw_board()
#         self.root.update_idletasks()
#         self.root.update()
        
#         # Show game over message if applicable
#         if terminated or truncated:
#             reason = info.get("reason", "Game Over")
#             # check if player_name in reason
#             for player_id in self.player_names.keys():
#                 if f"Player {player_id}" in reason:
#                     reason = reason.replace(f"Player {player_id}", self.player_names[player_id])
#             CustomDialog(self.root, "Game Over", reason)
        
#         return result

#     def reset(self, seed: Optional[int] = None):
#         """Reset the environment and update the display."""
#         result = self.env.reset(seed)
#         self.game_render.draw_board()
#         self.root.update_idletasks()
#         self.root.update()
#         return result

#     def close(self):
#         self.chat_window.destroy()
#         self.root.destroy()
#         self.running = False

#     def get_current_player_id(self):
#         """Get the current player ID from the wrapped environment."""
#         return self.env.get_current_player_id()

#     def __getattr__(self, name):
#         """Delegate unknown attributes to wrapped env."""
#         return getattr(self.env, name)



class TkinterRenderWrapper:
    def __init__(self, env: Any, player_names: Optional[Dict[int, str]] = None):
        self.env = env
        self.player_names = player_names or {0: "Player 0", 1: "Player 1"}

        self.root = tk.Tk()
        self.game_render = env.board_state_render(self.root, env, player_names)
        self.chat_window = tk.Toplevel(self.root)
        self.chat = ChatWindow(
            self.chat_window,
            player_names=self.player_names,
            player_colors=self.game_render.player_colors
        )

        # Create a container for the end game button
        self.button_frame = ttk.Frame(self.root)
        self.end_game_button = ttk.Button(
            self.button_frame, 
            text="End Game", 
            command=self._handle_game_end,
            state='disabled'
        )
        self.button_frame.pack(side='bottom', fill='x', padx=10, pady=5)
        self.end_game_button.pack(side='right')

        self._create_styles()
        self.game_render.draw_board()
        
        # Store end game info
        self.pending_end_info = None

    def _create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', background=BG_COLOR, foreground='#FFFFFF', font=('Helvetica', 12))
        style.configure('TButton', background='#3C3F41', foreground='#FFFFFF', font=('Helvetica', 12))
        style.map('TButton', background=[('active', '#5C5C5C')])

    def _handle_game_end(self):
        """Handle the user clicking the end game button"""
        if self.pending_end_info:
            reason = self.pending_end_info.get("reason", "Game Over")
            for player_id in self.player_names.keys():
                if f"Player {player_id}" in reason:
                    reason = reason.replace(f"Player {player_id}", self.player_names[player_id])
            CustomDialog(self.root, "Game Over", reason)
            self.end_game_button.configure(state='disabled')
            self.pending_end_info = None

    def step(self, player_id: int, action: str):
        """Step the environment and update the display."""
        # Add message to chat window before stepping
        self.chat.add_message(player_id, action)
        
        # Step the environment
        result = self.env.step(player_id, action)
        observations, rewards, truncated, terminated, info = result
        
        # Update the display
        self.game_render.draw_board()
        self.root.update_idletasks()
        self.root.update()
        
        if terminated or truncated:
            # Store the end game info and enable the button
            self.pending_end_info = info
            self.end_game_button.configure(state='normal')
        
        return result

    def reset(self, seed: Optional[int] = None):
        """Reset the environment and update the display."""
        self.pending_end_info = None
        self.end_game_button.configure(state='disabled')
        result = self.env.reset(seed)
        self.game_render.draw_board()
        self.root.update_idletasks()
        self.root.update()
        return result

    def close(self):
        self.chat_window.destroy()
        self.root.destroy()
        self.running = False

    def get_current_player_id(self):
        """Get the current player ID from the wrapped environment."""
        return self.env.get_current_player_id()

    def __getattr__(self, name):
        """Delegate unknown attributes to wrapped env."""
        return getattr(self.env, name)