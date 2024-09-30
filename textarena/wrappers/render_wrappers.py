from textarena.core import RenderWrapper, Env
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Union

# Set up rendering via Rich console and Layout
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

__all__ = [
    "PrettyRenderWrapper"
]


class PrettyRenderWrapper(RenderWrapper):
    """Render wrapper that provides a formatted and enhanced rendering of the environment.

    This wrapper uses the 'rich' library to render the game state and logs in a more readable and visually appealing way.
    """

    def __init__(self, env: Env, agent_identifiers: Optional[Dict[int, str]] = None):
        """
        Initialize the PrettyRenderWrapper.

        Args:
            env (Env): The environment to wrap.
            agent_identifiers (Optional[Dict[int, str]]): Mapping from player IDs to agent names.
        """
        super().__init__(env)
        # Default agent identifiers if none provided
        if agent_identifiers is None:
            agent_identifiers = {0: 'Player 0', 1: 'Player 1'}
        self.agent_identifiers = agent_identifiers

        self.console = Console()
        self.layout = Layout()

        # Initialize layout with two sections: game state and logs
        self.layout.split(
            Layout(name="upper", size=10),
            Layout(name="lower")
        )

    def _process_logs(self, logs: list) -> str:
        """
        Process logs by replacing 'Player 0' and 'Player 1' with agent names.

        Args:
            logs (list): List of log strings.

        Returns:
            str: Processed log string.
        """
        processed_logs = []
        for log in logs:
            for player_id, name in self.agent_identifiers.items():
                log = log.replace(f"Player {player_id}", name) + "\n"
            processed_logs.append(log)
        return "\n".join(processed_logs)

    def render(self):
        """
        Renders the current game state and logs using 'rich' library.

        This method displays the game state and logs in a formatted layout using the 'rich' library.
        """
        env = self.env  # The wrapped environment

        # Access game state
        if hasattr(env, 'game_state'):
            game_state = env.game_state
        else:
            # If the environment does not have game_state, use a minimal render
            self.console.print("[bold red]Environment does not have 'game_state'. Using minimal render.[/bold red]")
            env.render()
            return

        # Create the game state table
        table = Table(title="Game State", show_header=True, header_style="bold blue")
        table.add_column("Player", justify="center", style="cyan", no_wrap=True)
        table.add_column("Secret Word", justify="center", style="magenta")
        table.add_column("Turn", justify="center", style="green")
        if game_state["max_turns"]:
            table.add_column("Max Turns", justify="center", style="green")

        # Add rows for each player
        for player_id in [0, 1]:
            table.add_row(
                self.agent_identifiers.get(player_id, f"Player {player_id}"),
                game_state["target_words"][player_id],
                str(game_state["turn"]),
                str(game_state["max_turns"]) if game_state["max_turns"] else "-"
            )

        # Create the log panel with markup enabled
        processed_logs = self._process_logs(game_state["logs"])
        log_panel = Panel(
            Text.from_markup(processed_logs),  # Use Text.from_markup to parse Rich markup
            title="Game Log",
            border_style="green",
            padding=(1, 1)
        )

        # Update the layout sections
        self.layout["upper"].update(Panel(table, title="Game State", border_style="blue"))
        self.layout["lower"].update(log_panel)

        # Render the layout
        self.console.print(self.layout)