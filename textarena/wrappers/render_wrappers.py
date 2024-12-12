from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import cv2
import numpy as np
from PIL import Image
import io
import time
import os
import webbrowser
from typing import Dict, Optional, Any

class BrowserRenderWrapper:
    def __init__(self, env: Any, player_names: Optional[Dict[int, str]] = None, port: int = 8000, 
                 record_video: bool = False, video_path: str = "game_recording.mp4"):
        self.env = env
        self.port = port
        self.chat_history = []
        self.record_video = record_video
        self.video_path = video_path
        self.frames = []
        
        if not hasattr(self.env, 'offline_renderer'):
            raise AttributeError("Environment must have 'offline_renderer' attribute")
            
        # Initialize renderer
        self.renderer = self.env.offline_renderer(env=self.env, player_names=player_names, port=port)
        
        # Setup video recording if enabled
        if self.record_video:
            self._setup_recorder()
        
        # Open browser for user
        webbrowser.open(f"http://localhost:{self.port}")
        print(f"Game server started at http://localhost:{self.port}")

    def _setup_recorder(self):
        """Initialize the headless browser for recording entire window"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # Set a large fixed window size that will contain everything
        chrome_options.add_argument("--window-size=1920,2160")  # Full 4K height
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--hide-scrollbars")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(f"http://localhost:{self.port}")
        
        # Wait for the game to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "game-container"))
        )
        
        # Apply CSS to ensure proper spacing
        self.driver.execute_script("""
            document.body.style.padding = '50px';
            document.body.style.overflow = 'hidden';
        """)
        
        time.sleep(1)  # Allow time for any adjustments

    def _capture_frame(self):
        """Capture the entire browser window"""
        if not self.record_video:
            return
            
        try:
            time.sleep(0.5)  # Wait for any updates
            screenshot = self.driver.get_screenshot_as_png()
            image = Image.open(io.BytesIO(screenshot))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            self.frames.append(frame)
        except Exception as e:
            print(f"Error capturing frame: {e}")

    def step(self, action: str):
        """Take a step and update the display with proper timing"""
        current_player = self.env.state.current_player_id
        self.chat_history.append({
            "player_id": current_player,
            "message": action,
            "timestamp": time.time()
        })
        
        reward, truncated, terminated, info = self.env.step(action)
        self.renderer.chat_history = self.chat_history
        self.renderer.draw()
        
        if self.record_video:
            time.sleep(1)  # Wait 1 second per turn
            self._capture_frame()
            
            # If game is over, add end game frame
            if terminated or truncated:
                self._add_end_game_frame(reward, info)
        
        return reward, truncated, terminated, info

    def _add_end_game_frame(self, rewards, info):
        """Add an end game frame with result information"""
        
        # Determine winner from rewards
        winner_text = ""
        if rewards:
            max_reward = max(rewards.values())
            winners = [pid for pid, r in rewards.items() if r == max_reward]
            if len(winners) > 1:
                winner_text = "Game ended in a draw"
            else:
                winner = winners[0]
                winner_text = f"Winner: {self.renderer.player_names[winner]}"
        
        # Get reason from info
        reason = info.get('reason', 'Game Over')
        
        # Add end game overlay through JavaScript
        self.driver.execute_script("""
            // Create end game overlay if it doesn't exist
            let overlay = document.getElementById('end-game-overlay');
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.id = 'end-game-overlay';
                overlay.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.8);
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    color: white;
                    font-size: 24px;
                    text-align: center;
                    padding: 20px;
                    z-index: 1000;
                `;
                document.body.appendChild(overlay);
            }
            
            overlay.innerHTML = `
                <h1 style="font-size: 36px; margin-bottom: 20px;">Game Over</h1>
                <p style="font-size: 28px; margin-bottom: 15px;">${arguments[0]}</p>
                <p style="font-size: 24px;">${arguments[1]}</p>
            `;
        """, winner_text, reason)
        
        # Wait to show the end game screen
        time.sleep(3)  # Show end game screen for 3 seconds
        self._capture_frame()

    def _save_video(self):
        """Save the recorded frames as a video with adjusted fps"""
        if not self.frames:
            return
            
        try:
            height, width = self.frames[0].shape[:2]
            
            # Initialize video writer with slower fps
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                self.video_path,
                fourcc,
                1.0,  # 1 FPS for slower playback
                (width, height),
                True
            )
            
            # Write frames
            for frame in self.frames:
                out.write(frame)
            
            out.release()
            
            # Re-encode with ffmpeg if available
            try:
                import subprocess
                temp_path = self.video_path + ".temp.mp4"
                os.rename(self.video_path, temp_path)
                subprocess.run([
                    'ffmpeg', '-i', temp_path,
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '18',
                    '-y',
                    self.video_path
                ])
                os.remove(temp_path)
            except:
                if os.path.exists(temp_path):
                    os.rename(temp_path, self.video_path)
            
            print(f"Video saved to {self.video_path}")
            
        except Exception as e:
            print(f"Error saving video: {e}")

    def reset(self, seed: Optional[int] = None):
        obs = self.env.reset(seed)
        self.chat_history = []
        self.renderer.chat_history = []
        self.renderer.draw()
        
        if self.record_video:
            time.sleep(1)
            self._capture_frame()
            
        return obs

    def close(self):
        if self.record_video:
            try:
                self._save_video()
                self.driver.quit()
            except Exception as e:
                print(f"Error during cleanup: {e}")

    def __getattr__(self, name):
        return getattr(self.env, name)