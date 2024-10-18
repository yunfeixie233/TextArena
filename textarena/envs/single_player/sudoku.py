"""Single Player Sudoku Game Environment."""

SUDOKU_SOURCE = "MathMindsAGI/sudoku_v1"

import random
from datasets import load_dataset
from typing import Optional
import textarena as ta
import random


class SudokuEnv(ta.Env):
    environment_name = "Sudoku"

    def __init__(self):
        self.board = self.generate_board()
        self.game_state = ta.State(
            render={"board": self.board}, logs=[], player_map={0: "Player"}
        )

    def generate_board(self):
        """Generates a simple 9x9 Sudoku board with some preset values."""
        # load board from huggingface dataset
        dataset = load_dataset(SUDOKU_SOURCE)
        return random.choice(dataset["train"])["grid"]  # TODO: handle train or test

    def reset(
        self, seed: Optional[int] = None
    ) -> tuple[Optional[ta.Observation], Optional[ta.Info]]:
        if seed is not None:
            random.seed(seed)
        self.board = self.generate_board()
        self.game_state.render = {"board": self.board}
        self.game_state.logs = [(ta.GAME_ID, "New Sudoku game started.")]
        return {0: [(ta.GAME_ID, "Sudoku board reset.")]}, {}

    def step(
        self, player_id: int, action: str
    ) -> tuple[ta.Observation, ta.Reward, bool, bool, ta.Info]:
        """
        Takes an action in the form of 'row,col,value' and updates the board.
        """
        message = (0, action)
        try:
            row, col, value = map(int, action.split(","))
            if self.board[row][col] != 0:
                return (
                    {0: [message, (ta.GAME_ID, "Cell is already filled.")]},
                    {0: -1},
                    True,
                    False,
                    {},
                )
            self.board[row][col] = value
            self.game_state.render["board"] = self.board
            self.game_state.logs.append(
                (player_id, f"Player placed {value} at ({row}, {col}).")
            )
            if self.check_valid() and self.check_complete():
                return (
                    {0: [message, (ta.GAME_ID, "You completed the Sudoku!")]},
                    {0: 100},
                    True,
                    False,
                    {},
                )
            return (
                {0: [message, (ta.GAME_ID, f"Placed {value} at ({row}, {col}).")]},
                {0: 0},
                False,
                False,
                {},
            )
        except Exception:
            return (
                {
                    0: [
                        message,
                        (ta.GAME_ID, "Invalid action. Use format 'row,col,value'."),
                    ]
                },
                {0: -1},
                True,
                False,
                {},
            )

    def render(self):
        board_str = "\n".join(
            [
                " ".join(str(cell) if cell != 0 else "." for cell in row)
                for row in self.board
            ]
        )
        print(board_str)

    def is_valid_group(self, group):
        """Check if a group (row, column, or subgrid) contains unique numbers from 1 to 9."""
        group = [num for num in group if num != 0]  # Exclude empty cells
        return len(group) == len(set(group)) and all(1 <= num <= 9 for num in group)

    def check_valid(self):
        """Check if the board is valid according to Sudoku rules."""

        # Check all rows
        for row in self.board:
            if not self.is_valid_group(row):
                return False

        # Check all columns
        for col_idx in range(9):
            col = [self.board[row_idx][col_idx] for row_idx in range(9)]
            if not self.is_valid_group(col):
                return False

        # Check all 3x3 subgrids
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                subgrid = [
                    self.board[r][c]
                    for r in range(box_row, box_row + 3)
                    for c in range(box_col, box_col + 3)
                ]
                if not self.is_valid_group(subgrid):
                    return False

        # If all checks passed, the board is valid
        return True

    def check_complete(self):
        """Check if the board is completely filled."""
        return all(all(cell != 0 for cell in row) for row in self.board)
