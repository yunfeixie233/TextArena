import re, random
from collections import deque
from typing import Optional, Tuple, List, Dict, Any

import textarena as ta
from textarena.envs.games.Minesweeper.renderer import create_board_str

class MinesweeperEnv(ta.Env):
    def __init__(self, rows: int=8, cols: int=8, num_mines: int=10, max_turns: int=100):
        """
        Args:
            rows (int): the number of rows
            cols (int): the number of columns
            num_mines (int): the number of mines
        """
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.max_turns = max_turns

    def get_board_str(self):
        return create_board_str(self.grid, self.revealed, self.state.game_state["flags"])
    
    def reset(self, num_players: int, seed: Optional[int]=None):
        self.state = ta.SinglePlayerState(num_players=num_players, seed=seed)

        ## initialize the game state
        grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        flags = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        first_move = True # Track if it's the first move to ensure playability

        ## reset the game state
        game_state = {"grid": grid, "revealed": revealed, "flags": flags, "first_move": first_move, "rendered_board": self._render_board()}
        self.state.reset(game_state=game_state, player_prompt_function=self._generate_player_prompt)
    
    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        prompt = (
            f"You are playing the Minesweeper game.\nThe objective of the game is to reveal all cells that do not contain mines.\n"
            "To make a move, you can either reveal a cell or place a flag on a suspected mine location using one of the following commands:\n"
            "- '[reveal]': Reveal the contents of a specific cell.\n"
            "- '[flag]': Place or remove a flag on a specific cell to mark it as a potential mine.\n"
            "For example:\n"
            "- `[reveal 3 2]` to reveal the cell in Row 3, Column 2.\n"
            "- `[flag 5 6]` to place or remove a flag on the cell in Row 5, Column 6.\n"
            "On your first move, you will reveal an area around the cell you choose to ensure a safe start.\n"
            "The current board layout is shown below. Cells that are unrevealed are represented by a dot ('.'), revealed numbers show the count of adjacent mines, and flagged cells are marked with an 'F'.\n"
            "Be mindful not to choose revealed or flagged cells.\n"
            "Here is the current board layout:\n"
        ) + game_state["rendered_board"]
        return prompt
    
    def _render_board(self) -> str:
        """ Render the game board """
        board_str = "   " + " ".join([str(c).rjust(2) for c in range(self.cols)]) + "\n"
        for r in range(self.rows):
            row_str = f"{r:2} "
            for c in range(self.cols):
                if self.revealed[r][c]:
                    if self.grid[r][c] == -1:
                        row_str += " * "
                    else:
                        row_str += f" {self.grid[r][c]} "
                elif self.state.game_state["flags"][r][c]:
                    row_str += " F "
                else:
                    row_str += " . "
            board_str += row_str + "\n"
        return board_str
        
    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(from_id=self.state.current_player_id, message=action) ## Update the observation
        match = re.compile(r"\[([a-zA-Z]+)\s(\d+)\s(\d+)\]").search(action) # e.g. [reveal 3 2]
        if match is None:
            self.state.set_invalid_move(reason="You not respond with a valid action and coordinates in square brackets.")
        else:
            action, row, col = match.group(1).lower(), int(match.group(2)), int(match.group(3))
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                self.state.set_invalid_move(reason="The specified row and column coordinates are out of bounds.")
            else:
                if action == "reveal":
                    if self.revealed[row][col] or self.state.game_state["flags"][row][col]:
                        self.state.set_invalid_move(reason="The cell at ({row}, {col}) has already been revealed or flagged.")
                    if self.first_move: ## Handle the first move
                        self.clear_all_flags()
                        self.setup_mines(row, col)
                        self.first_move = False
                    
                    queue = deque([(row, col)])  # Start with the initial cell in the queue
                    self.revealed[row][col] = True  # Mark the initial cell as revealed immediately
                    while queue:
                        current_row, current_col = queue.popleft()
                        # Check if it's a mine
                        if self.grid[current_row][current_col] == -1:
                            pct_complete = self._get_percentage_completion()
                            self.state.set_singleplayer_game_outcome(reward=pct_complete, reason=f"Game over! Player {player_id} hit a mine at ({current_row}, {current_col}). You successfully uncovered {round(pct_complete * 100)}% of the safe cells.")

                        # If the cell has no adjacent mines, add its neighbors to the queue
                        if self.grid[current_row][current_col] == 0:
                            for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                                neighbor_row, neighbor_col = current_row + dr, current_col + dc
                                # Only add to the queue if within bounds and not revealed or flagged
                                if 0 <= neighbor_row < self.rows and 0 <= neighbor_col < self.cols:
                                    if not self.revealed[neighbor_row][neighbor_col] and not self.state.game_state["flags"][neighbor_row][neighbor_col]:
                                        self.revealed[neighbor_row][neighbor_col] = True  # Mark as revealed when adding to queue
                                        queue.append((neighbor_row, neighbor_col))

                    self.state.add_observation(message=f"Game Board:\n{self._render_board()}")
                    
                elif action == "flag":
                    if not self.revealed[row][col]:
                        self.state.game_state["flags"][row][col] = not self.state.game_state["flags"][row][col]
                    self.state.add_observation(message=f"Game Board:\n{self._render_board()}")

                else:
                    self.state.set_invalid_move(reason="You did not respond with a valid action in square brackets.")
       
        self.state.game_state["rendered_board"] = self._render_board()  ## Update the rendered board

        ## Check if the game is terminated
        if self._is_solved():
            self.state.set_singleplayer_game_outcome(reward=1, reason=f"Congratulations! You have successfully cleared the Minesweeper board.")
        elif self.state.check_turn_limit():
            pct_complete = self._get_percentage_completion()
            self.state.set_singleplayer_game_outcome(reward=pct_complete, reason=f"The turn limit has been reached. You successfully uncovered {round(pct_complete * 100)}% of the safe cells.")
            
        return self.state.step()

    def _get_percentage_completion(self) -> float:
        """ Return the percentage of safe (non-mine) cells that have been revealed """
        safe_total = sum(1 for r in range(self.rows) for c in range(self.cols) if self.grid[r][c] != -1)
        revealed_safe = sum(1 for r in range(self.rows) for c in range(self.cols) if self.grid[r][c] != -1 and self.revealed[r][c])
        return revealed_safe/safe_total if safe_total > 0 else 0.0

    
    def setup_mines(self, safe_row: int, safe_col: int):
        mines = set()
        while len(mines) < self.num_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            # Avoid placing mines in the safe zone
            if (r, c) not in mines and (r < safe_row - 1 or r > safe_row + 1 or c < safe_col - 1 or c > safe_col + 1):
                mines.add((r, c))
                self.grid[r][c] = -1  # -1 represents a mine
        self.calculate_adjacent_numbers()

    def calculate_adjacent_numbers(self):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    continue
                mine_count = sum((0 <= r + dr < self.rows and 0 <= c + dc < self.cols and self.grid[r + dr][c + dc] == -1) for dr, dc in directions)
                self.grid[r][c] = mine_count

    def clear_all_flags(self):
        self.state.game_state["flags"] = [[False for _ in range(self.cols)] for _ in range(self.rows)]

    def _is_solved(self) -> bool:
        return all((self.grid[r][c] == -1 and self.state.game_state["flags"][r][c]) or (self.grid[r][c] != -1 and self.revealed[r][c]) for r in range(self.rows) for c in range(self.cols))
    