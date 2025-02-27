import os
import time
from typing import Dict, Optional, Tuple, List, Callable, Any, Union, Set
from io import StringIO
import cv2
import numpy as np

from rich import box
from rich.columns import Columns
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table
from rich.text import Text

from textarena.core import Env, Message, Info, Rewards, RenderWrapper, State


class SimpleRenderWrapper(RenderWrapper):
    """
    Enhanced terminal render wrapper for text-based game environments.

    Supports:
    - Single player, two-player, and multiplayer games
    - Flexible layout (full-screen or half-screen modes)
    - Custom ASCII board rendering
    - Automatic player color assignment
    - Configurable rendering of generic and player-specific game states
    - Video recording capabilities

    Usage:
        env = YourGameEnvironment(...)
        wrapped_env = SimpleRenderWrapper(
            env,
            player_names={0: "Alice", 1: "Bob"},
            full_screen=True,
            record_video=False
        )
    """

    PLAYER_COLORS = [
        "red",
        "green", 
        "blue",
        "magenta",
        "yellow",
        "cyan",
        "bright_red",
        "bright_green",
        "bright_blue",
        "bright_magenta", 
        "bright_yellow",
        "bright_cyan",
    ]

    GAME_MESSAGE_COLOR = "yellow"
    GAME_KEYWORD_COLOR = "cyan"
    INFO_COLOR = "bright_white"
    WARNING_COLOR = "bright_yellow"
    ERROR_COLOR = "bright_red"

    def __init__(
        self,
        env: Env,
        player_names: Optional[Dict[int, str]] = None,
        full_screen: bool = True,
        record_video: bool = False,
        video_path: str = "game_recording.mp4",
        video_fps: int = 1,
        max_log_lines: int = 20,
    ):
        super().__init__(env)
        self.full_screen = full_screen
        self.record_video = record_video
        self.video_path = video_path
        self.video_fps = video_fps
        self.max_log_lines = max_log_lines
        self.player_names = player_names
        
        self.console: Optional[Console] = None
        self.layout: Optional[Layout] = None
        self.player_color_map: Dict[int, str] = {}
        self.frames: List[np.ndarray] = []
        self.last_render_time = 0
        self._layout_sections: Set[str] = set()

    def reset(self, *args, **kwargs) -> Tuple[Optional[Rewards], bool, bool, Optional[Info]]:
        result = self.env.reset(*args, **kwargs)
        self.state = self.env.state
        self.reset_render()
        self._render()
        return result

    def reset_render(self):
        if not hasattr(self, 'state') or self.state is None:
            self._setup_placeholder_layout()
            return

        if self.player_names is None:
            self.player_names = {}
            for player_id in range(self.state.num_players):
                self.player_names[player_id] = f"Player {player_id}"
            if hasattr(self.state, 'role_mapping') and self.state.role_mapping:
                if isinstance(self.state.role_mapping, dict):
                    self.player_names.update(self.state.role_mapping)

        self.console = Console(highlight=False)
        self.player_color_map = self._assign_player_colors()
        self._setup_layout()
        if self.record_video:
            self.frames = []
            self._capture_and_store_frame()
        self.last_render_time = time.time()

    def step(self, action: str) -> Tuple[Optional[Rewards], bool, bool, Optional[Info]]:
        step_results = self.env.step(action=action)
        self._render()
        return step_results

    def close(self):
        if self.record_video and self.frames:
            self._save_video()
        return self.env.close()

    def _setup_layout(self):
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="header", size=1),
            Layout(name="main", ratio=20)
        )

        # Determine if we have any player-specific state to display
        has_player_state = False
        if hasattr(self, 'state') and hasattr(self.state, 'game_state'):
            game_state = self.state.game_state
            if isinstance(game_state, dict):
                for key, value in game_state.items():
                    if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
                        has_player_state = True
                        break

        if self.full_screen:
            self.layout["main"].split_row(
                Layout(name="left_column", ratio=1),
                Layout(name="right_column", ratio=1)
            )
            self.layout["left_column"].split_column(
                Layout(name="board", ratio=2),
                Layout(name="game_state", ratio=1)
            )
            if has_player_state:
                self.layout["right_column"].split_column(
                    Layout(name="player_state", ratio=1),
                    Layout(name="game_log", ratio=2)
                )
            else:
                # Instead of update(), use split_column to create a child layout for game_log.
                self.layout["right_column"].split_column(
                    Layout(name="game_log", ratio=1)
                )
        else:
            self.layout["main"].split_column(
                Layout(name="upper", ratio=1),
                Layout(name="lower", ratio=1)
            )
            self.layout["upper"].split_row(
                Layout(name="board", ratio=1),
                Layout(name="game_state", ratio=1)
            )
            if has_player_state:
                self.layout["lower"].split_row(
                    Layout(name="player_state", ratio=1),
                    Layout(name="game_log", ratio=1)
                )
            else:
                # Again, use split_row to create a game_log layout.
                self.layout["lower"].split_row(
                    Layout(name="game_log", ratio=1)
                )

        self._layout_sections = set(self._collect_layout_names(self.layout))
        required_sections = ["board", "game_state", "game_log"]
        missing_sections = [section for section in required_sections if section not in self._layout_sections]
        if missing_sections:
            print(f"Warning: Layout is missing required sections: {missing_sections}")

    def _setup_placeholder_layout(self):
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="header", size=1),
            Layout(name="main", ratio=20),
        )
        self.layout["main"].split_row(
            Layout(name="left_column", ratio=1),
            Layout(name="right_column", ratio=1)
        )
        self.layout["left_column"].split_column(
            Layout(name="board", ratio=2),
            Layout(name="game_state", ratio=1)
        )
        # Create both player_state and game_log layouts for consistency.
        self.layout["right_column"].split_column(
            Layout(name="player_state", ratio=1),
            Layout(name="game_log", ratio=2)
        )
        self._layout_sections = set(self._collect_layout_names(self.layout))
        if self.console is None:
            self.console = Console(highlight=False)

    def _collect_layout_names(self, layout: Layout) -> List[str]:
        names = [layout.name] if layout.name else []
        for child in getattr(layout, 'children', []):
            names.extend(self._collect_layout_names(child))
        return names

    def _assign_player_colors(self) -> Dict[int, str]:
        color_map = {}
        if not self.player_names:
            return color_map
        player_ids = list(self.player_names.keys())
        player_ids.sort()
        num_colors = len(self.PLAYER_COLORS)
        for idx, player_id in enumerate(player_ids):
            color_map[player_id] = self.PLAYER_COLORS[idx % num_colors]
        return color_map

    def _render(self):
        if not self.console or not self.layout:
            self.reset_render()
        if not hasattr(self, 'state') or self.state is None:
            if self.console:
                self.console.clear()
                self.console.print("Waiting for game state to initialize...")
            return

        has_player_state = False
        if hasattr(self.state, 'game_state') and isinstance(self.state.game_state, dict):
            for key, value in self.state.game_state.items():
                if isinstance(value, dict) and all(isinstance(k, int) for k in value.keys()):
                    has_player_state = True
                    break
        currently_has_player_state = ("player_state" in self._layout_sections)
        if has_player_state != currently_has_player_state:
            self._setup_layout()

        try:
            self.layout["header"].update(self._render_header())
            if "board" in self._layout_sections:
                self.layout["board"].update(self._render_ascii_board())
            if "game_state" in self._layout_sections:
                self.layout["game_state"].update(self._render_generic_game_state())
            if "player_state" in self._layout_sections:
                self.layout["player_state"].update(self._render_player_state())
            
            logs = getattr(self.state, "logs", []) or []
            log_panel = Panel(
                self._process_logs(logs),
                title="Game Log",
                border_style="yellow", 
                padding=(1, 1)
            )
            if "game_log" in self._layout_sections:
                self.layout["game_log"].update(log_panel)
            else:
                print("Warning: No 'game_log' layout section found.")

            self.console.clear()
            self.console.print(self.layout)
            if self.record_video:
                current_time = time.time()
                if current_time - self.last_render_time >= 1.0 / self.video_fps:
                    self._capture_and_store_frame()
                    self.last_render_time = current_time

        except Exception as e:
            self.console.clear()
            self.console.print(f"Error rendering game state: {e}")
            self._setup_placeholder_layout()

    def _render_header(self) -> RenderableType:
        env_name = self.env.__class__.__name__
        turn_info = ""
        player_info = ""
        if hasattr(self, 'state') and self.state:
            if hasattr(self.state, 'turn'):
                turn_info = f"Turn {self.state.turn}"
                if hasattr(self.state, 'max_turns') and self.state.max_turns:
                    turn_info += f"/{self.state.max_turns}"
            if hasattr(self.state, 'current_player_id'):
                current_player = self.state.current_player_id
                player_name = self.player_names.get(current_player, f"Player {current_player}")
                color = self.player_color_map.get(current_player, "white")
                player_info = f" | Current Player: [{color}]{player_name}[/{color}]"
        header_text = f"Game: [bold]{env_name}[/bold]"
        if turn_info:
            header_text += f" | {turn_info}"
        if player_info:
            header_text += player_info
        return Text.from_markup(header_text)

    def _render_ascii_board(self) -> RenderableType:
        board_str = None
        if hasattr(self.env, "render_board") and callable(self.env.render_board):
            board_str = self.env.render_board()
        if board_str is None and hasattr(self.state, 'game_state'):
            gs = self.state.game_state
            if isinstance(gs, dict):
                for candidate in ['board', 'board_state', 'rendered_board', 'current_board', 'rendered_piles']:
                    val = gs.get(candidate)
                    if isinstance(val, str):
                        board_str = val
                        break
        if not board_str:
            return Panel(
                "Board visualization not available",
                title="Game Board",
                border_style="bright_blue",
                padding=(1, 1)
            )
        lines = board_str.splitlines()
        centered_lines = []
        if self.console:
            console_width = self.console.width
            if "left_column" in self._layout_sections:
                estimated_panel_width = console_width // 2 - 4
            else:
                estimated_panel_width = console_width - 4
        else:
            estimated_panel_width = 80
        if lines:
            for ln in lines:
                if len(ln) < estimated_panel_width:
                    pad = (estimated_panel_width - len(ln)) // 2
                    centered_lines.append(" " * pad + ln)
                else:
                    centered_lines.append(ln)
        centered_board = "\n".join(centered_lines)
        return Panel(
            centered_board,
            title="Game Board",
            border_style="bright_blue",
            padding=(1, 1)
        )

    def _render_generic_game_state(self) -> RenderableType:
        if not hasattr(self, 'state') or not hasattr(self.state, 'game_state'):
            return Panel(
                "Game state not available",
                title="Game State",
                border_style="blue"
            )
        gs = self.state.game_state
        if not isinstance(gs, dict):
            return Panel("Game state is not a dictionary", title="Game State", border_style="blue")
        render_keys = getattr(self.env, "terminal_render_keys", [])
        if not render_keys:
            to_skip = {'board', 'board_state', 'rendered_board', 'current_board', 'rendered_piles'}
            for k, v in gs.items():
                if isinstance(v, dict) and all(isinstance(x, int) for x in v.keys()):
                    to_skip.add(k)
            render_keys = [k for k in gs.keys() if k not in to_skip]
        game_info = []
        if hasattr(self.state, 'turn'):
            turn_str = str(self.state.turn)
            if hasattr(self.state, 'max_turns') and self.state.max_turns:
                turn_str += f"/{self.state.max_turns}"
            game_info.append(("Turn", turn_str))
        game_info.append(("Players", str(self.state.num_players)))
        if hasattr(self.state, 'current_player_id'):
            cp = self.state.current_player_id
            color = self.player_color_map.get(cp, "white")
            pname = self.player_names.get(cp, f"Player {cp}")
            game_info.append(("Current Player", f"[{color}]{pname}[/{color}]"))
        for k in render_keys:
            if k in gs:
                val = gs[k]
                if isinstance(val, dict) and all(isinstance(x, int) for x in val.keys()):
                    continue
                if isinstance(val, (dict, list)):
                    val_str = "\n" + Pretty(val).__str__()
                else:
                    val_str = str(val)
                game_info.append((k, val_str))
        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        for name, value in game_info:
            table.add_row(name, value)
        return Panel(
            table,
            title="Game Information",
            border_style="blue",
            padding=(1, 1)
        )

    def _render_player_state(self) -> RenderableType:
        if not hasattr(self, 'state') or not hasattr(self.state, 'game_state'):
            return Panel(
                "Player state not available",
                title="Player State",
                border_style="green"
            )
        gs = self.state.game_state
        if not isinstance(gs, dict):
            return Panel("Player state not in dict form", title="Player State", border_style="green")
        player_attributes = {}
        for k, v in gs.items():
            if isinstance(v, dict) and all(isinstance(x, int) for x in v.keys()):
                player_attributes[k] = v
        if not player_attributes:
            return Panel(
                "No player-specific attributes found",
                title="Player State",
                border_style="green"
            )
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAD)
        table.add_column("Player", style="cyan", no_wrap=True)
        attribute_keys = list(player_attributes.keys())
        for attr_key in attribute_keys:
            table.add_column(attr_key, style="green")
        all_pids = set()
        for attr_dict in player_attributes.values():
            all_pids.update(attr_dict.keys())
        sorted_pids = sorted(all_pids)
        for pid in sorted_pids:
            color = self.player_color_map.get(pid, "white")
            pname = self.player_names.get(pid, f"Player {pid}")
            if hasattr(self.state, 'current_player_id') and pid == self.state.current_player_id:
                row_player = f"[{color}]➤ {pname}[/{color}]"
            else:
                row_player = f"[{color}]{pname}[/{color}]"
            row_values = [row_player]
            for attr in attribute_keys:
                val = player_attributes[attr].get(pid, "")
                row_values.append(str(val))
            table.add_row(*row_values)
        return Panel(
            table,
            title="Player State",
            border_style="green",
            padding=(1, 1)
        )

    def _process_logs(self, logs: List[Message]) -> Text:
        if not logs:
            return Text("No log messages yet.", style="dim")
        processed_lines: List[Text] = []
        for role, message in logs:
            msg_str = str(message)
            if role != -1:
                player_name = self.player_names.get(role, f"Player {role}")
                color = self.player_color_map.get(role, "white")
                prefix = f"[{color}]{player_name}[/{color}]"
                log_str = f"{prefix}: {msg_str}"
            else:
                log_str = f"[{self.GAME_MESSAGE_COLOR}][GAME]: {msg_str}[/{self.GAME_MESSAGE_COLOR}]"
            log_text = Text.from_markup(log_str)
            if self.console:
                wrapped = log_text.wrap(self.console, width=self.console.width)
                processed_lines.extend(wrapped)
            else:
                processed_lines.append(log_text)
        if self.max_log_lines is not None and len(processed_lines) > self.max_log_lines:
            processed_lines = processed_lines[-self.max_log_lines:]
        return Text('\n').join(processed_lines)

    def _capture_frame(self) -> Optional[np.ndarray]:
        try:
            width, height = os.get_terminal_size()
        except OSError:
            width, height = 80, 24
        string_io = StringIO()
        temp_console = Console(file=string_io, width=width, height=height, record=True)
        temp_console.print(self.layout)
        text_content = string_io.getvalue()
        lines = text_content.split('\n')
        img = np.ones((height * 20, width * 10, 3), dtype=np.uint8) * 255
        y_pos = 20
        for i, line in enumerate(lines[:height]):
            cv2.putText(
                img,
                line,
                (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA
            )
            y_pos += 20
        return img

    def _capture_and_store_frame(self):
        if not self.record_video:
            return
        frame = self._capture_frame()
        if frame is not None:
            self.frames.append(frame)

    def _save_video(self):
        if not self.frames:
            return
        try:
            height, width = self.frames[0].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(self.video_path, fourcc, self.video_fps, (width, height))
            for frame in self.frames:
                out.write(frame)
            out.release()
            print(f"\nVideo saved to {self.video_path}")
        except Exception as e:
            print(f"Error saving video: {e}")
