import re
from typing import Optional, Dict, Tuple, List, Any

import textarena as ta
from textarena.envs.games.SimpleTak.renderer import create_board_str

class SimpleTakEnv(ta.Env):
    def __init__(self, board_size: int = 5):
        """
        Args:
            board_size (int): The size of the NxN board (default 5).
        """
        super().__init__()
        self.board_size = board_size
        self.cell_mapping = {i: (i // board_size, i % board_size) for i in range(board_size * board_size)}

    def get_board_str(self):
        return create_board_str(board=self.state.game_state["board"], board_size=self.board_size)

    def reset(self, num_players: int = 2, seed: Optional[int] = None):
        self.state = ta.TwoPlayerState(num_players=num_players, seed=seed)
        self.state.reset(game_state={"board": [['' for _ in range(self.board_size)] for _ in range(self.board_size)]}, player_prompt_function=self._prompt)
        self._observe_current_state()

    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"You are Player {player_id} in SimpleTak.\n"
            f"On the board, your stones appear as '{'O' if player_id == 0 else 'X'}' and "
            f"your opponent's stones appear as '{'O' if player_id == 1 else 'X'}'.\n\n"
            "On your turn, choose one empty cell (by its numbered index) and place your stone there.\n"
            "For example, '[12]' places your stone in cell 12.\n\n"
            "Your objective is to form a continuous path of your stones that connects two opposite edges of the board "
            "(top-to-bottom or left-to-right). If you do this, you win immediately.\n"
        )

    def _observe_current_state(self) -> None:
        # Gather all empty cells as possible moves
        available_moves = []
        for i in range(self.board_size * self.board_size):
            r, c = self.cell_mapping[i]
            if self.state.game_state["board"][r][c] == '': 
                available_moves.append(f"[{i}]")
        self.state.add_observation(message=f"Current Board:\n\n{self._render_board()}\nAvailable Moves: " + ", ".join(available_moves))

    def _render_board(self) -> str:
        # Determine cell width based on the largest cell number
        # e.g., for board_size=4, largest cell_num=15 => 2 digits
        max_cell_num = self.board_size * self.board_size - 1
        digit_count = len(str(max_cell_num))
        cell_width = max(digit_count, 2)  # at least 2 for occupant symbols

        # Helper: content for cell (row,col) either occupant 'X'/'O' or the cell number
        def cell_str(r: int, c: int) -> str:
            if self.state.game_state["board"][r][c] == '': return str(r * self.board_size + c) # If empty, show cell number
            else: return self.state.game_state["board"][r][c] # Occupied by 'O' or 'X'

        # Build a horizontal separator line that frames each row
        # We want something like: +----+----+ for each column
        def build_hline() -> str:
            line_parts = []
            for _ in range(self.board_size):
                line_parts.append("-" * (cell_width + 2))  # +2 for spacing around content
            # Join them with '+' and add a leading+trailing '+'
            return "+" + "+".join(line_parts) + "+"

        lines = []
        # Add top framing line first
        lines.append(build_hline())

        for r in range(self.board_size):
            # For each row, build the row of cells
            row_cells = []
            for c in range(self.board_size):
                text = cell_str(r, c)
                # Center the text in cell_width
                text_centered = f" {text:^{cell_width}} "
                row_cells.append(text_centered)
            # Join with '|'
            row_line = "|" + "|".join(row_cells) + "|"
            lines.append(row_line)
            lines.append(build_hline())

        return "\n".join(lines)

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        symbol = 'O' if self.state.current_player_id == 0 else 'X'
        self.state.add_observation(from_id=self.state.current_player_id, message=action)
        match = re.compile(r"\[\s*(\d+)\s*\]").search(action) # Regex to parse moves like [12]
        if match is None:
            self.state.set_invalid_move(reason="Invalid move format")
        else:
            cell_num = int(match.group(1))
            if cell_num not in self.cell_mapping: # Check if cell_num in valid range
                self.state.set_invalid_move(reason=f"Invalid cell number {cell_num}. Must be between 0 and {self.board_size**2 - 1}.")
            else:
                row, col = self.cell_mapping[cell_num]
                board = self.state.game_state["board"]
                if board[row][col] == '':
                    board[row][col] = symbol # Place the stone
                    if self._check_win(symbol): # Check for a winning path
                        self.state.set_winner(player_id=self.state.current_player_id, reason=f"Player {self.state.current_player_id} ('{symbol}') connected two opposite edges!")
                    else:
                        if all(board[r][c] != '' for r in range(self.board_size) for c in range(self.board_size)): # If board is fully occupied and no winner => draw
                            self.state.set_draw(reason="The board is full. It's a draw!")
                else:
                    self.state.set_invalid_move(reason=f"Cell {cell_num} is already occupied. Choose an empty cell.")
        self._observe_current_state()
        return self.state.step()

    def _check_win(self, symbol: str) -> bool:
        visited = set()
        directions = [(0,1), (1,0), (0,-1), (-1,0)]
        n = self.board_size

        def valid(r, c):
            return 0 <= r < n and 0 <= c < n and self.state.game_state["board"][r][c] == symbol

        def dfs(r, c, edges):
            if (r, c) in visited:
                return False
            visited.add((r, c))

            # Check which edges we're on
            if r == 0: edges.add("top")
            if r == n - 1: edges.add("bottom")
            if c == 0: edges.add("left")
            if c == n - 1: edges.add("right")

            # If we connect top↔bottom or left↔right, it's a win
            if ("top" in edges and "bottom" in edges) or ("left" in edges and "right" in edges): return True

            # Continue DFS
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if valid(nr, nc):
                    if dfs(nr, nc, edges.copy()):
                        return True
            return False

        # Start DFS from every cell that has the player's symbol
        for row in range(n):
            for col in range(n):
                if self.state.game_state["board"][row][col] == symbol:
                    if dfs(row, col, set()):
                        return True
        return False