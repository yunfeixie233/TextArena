from textarena.core import Env, Message, RenderWrapper, State
import os 
import tkinter as tk 
from tkinter import ttk, scrolledtext 
from PIL import Image, ImageTk, ImageGrab 
import numpy as np
import cv2
import time
from typing import Any, Dict, Optional, List, Callable
from datetime import datetime

__all__ = [
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


class TkinterRenderWrapper:
    def __init__(
        self, 
        env: Any, 
        player_names: Optional[Dict[int, str]] = None,
        enable_recording: bool = False
    ):
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

        # Video recording setup
        self.enable_recording = enable_recording
        self.recording = False
        self.video_writer = None
        self.frame_rate = 0.5  # Half speed (0.5 frames per second)
        self.last_frame_time = 0
        self.recording_path = None

        self._create_styles()
        self.game_render.draw_board()

    def _create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', background=BG_COLOR, foreground='#FFFFFF', font=('Helvetica', 12))
        style.configure('TButton', background='#3C3F41', foreground='#FFFFFF', font=('Helvetica', 12))
        style.map('TButton', background=[('active', '#5C5C5C')])

    def start_recording(self):
        """Start recording the game board."""
        if not self.enable_recording:
            return
            
        if not self.recording:
            # Create recordings directory if it doesn't exist
            recordings_dir = os.path.join(os.getcwd(), 'recordings')
            os.makedirs(recordings_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.recording_path = os.path.join(recordings_dir, f'game_{timestamp}.mp4')
            
            # Initialize video writer with H.264 codec
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
            
            if not os.path.exists(self.recording_path):
                # Try alternative codec if avc1 is not available
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            self.video_writer = cv2.VideoWriter(
                self.recording_path,
                fourcc,
                self.frame_rate,
                (self.game_render.WINDOW_WIDTH, self.game_render.WINDOW_HEIGHT),
                isColor=True
            )
            
            if not self.video_writer.isOpened():
                print("Warning: Failed to initialize H.264 codec, falling back to MJPG/AVI")
                self.recording_path = self.recording_path.replace('.mp4', '.avi')
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                self.video_writer = cv2.VideoWriter(
                    self.recording_path,
                    fourcc,
                    self.frame_rate,
                    (self.game_render.WINDOW_WIDTH, self.game_render.WINDOW_HEIGHT),
                    isColor=True
                )
            
            self.recording = True
            self.last_frame_time = time.time()
            print(f"Started recording to {os.path.abspath(self.recording_path)}")

    def _capture_frame(self, force: bool = False):
        """
        Capture the current state of the game board as a frame.
        
        Args:
            force (bool): If True, captures frame regardless of frame rate timing
        """
        if not self.enable_recording or not self.recording:
            return
            
        if force or time.time() - self.last_frame_time >= 1/self.frame_rate:
            try:
                # Get window position and size
                x = self.game_render.winfo_rootx()
                y = self.game_render.winfo_rooty()
                width = self.game_render.WINDOW_WIDTH
                height = self.game_render.WINDOW_HEIGHT
                
                # Ensure UI is fully updated before capture
                self.root.update_idletasks()
                self.root.update()
                
                # Add small delay to ensure UI is completely rendered
                time.sleep(0.1)
                
                # Capture the window area
                screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
                
                # Convert PIL image to OpenCV format
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Write the frame
                self.video_writer.write(frame)
                
            except Exception as e:
                print(f"Error capturing frame: {e}")
                
            self.last_frame_time = time.time()

    def stop_recording(self):
        """Stop recording and save the video."""
        if self.recording:
            # Force capture of the final frame
            self._capture_frame(force=True)
            
            self.recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            print(f"Recording saved to {os.path.abspath(self.recording_path)}")

    def step(self, action: str):
        """Step the environment and update the display."""
        player_id = self.env.state.current_player_id
        # Add message to chat window before stepping
        self.chat.add_message(player_id, action)
        
        # Step the environment
        result = self.env.step(action)
        rewards, truncated, terminated, info = result
        
        # Update the display
        self.game_render.draw_board()
        self.root.update_idletasks()
        self.root.update()
        
        # Capture frame if recording
        if self.enable_recording:
            self._capture_frame()
        
        # Show game over message if applicable
        if terminated or truncated:
            reason = info.get("reason", "Game Over")
            # check if player_name in reason
            for player_id in self.player_names.keys():
                if f"Player {player_id}" in reason:
                    reason = reason.replace(f"Player {player_id}", self.player_names[player_id])
            
            # Make sure the final state is captured before stopping
            if self.recording:
                # Force capture final frame before dialog
                self._capture_frame(force=True)
                # Now show dialog and stop recording
                CustomDialog(self.root, "Game Over", reason)
                self.stop_recording()
        
        return result

    def reset(self, seed: Optional[int] = None):
        """Reset the environment and update the display."""
        # Start a new recording if previous one exists
        if self.recording:
            self.stop_recording()
        if self.enable_recording:
            self.start_recording()
        
        result = self.env.reset(seed)
        self.game_render.draw_board()
        self.root.update_idletasks()
        self.root.update()
        
        # Capture initial frame
        if self.enable_recording:
            self._capture_frame(force=True)
            
        return result

    def close(self):
        if self.recording:
            self.stop_recording()
        self.chat_window.destroy()
        self.root.destroy()
        self.running = False

    def get_current_player_id(self):
        """Get the current player ID from the wrapped environment."""
        return self.env.get_current_player_id()

    def __getattr__(self, name):
        """Delegate unknown attributes to wrapped env."""
        return getattr(self.env, name)