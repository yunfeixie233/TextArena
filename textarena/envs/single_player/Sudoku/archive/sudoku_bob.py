from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, List
import time
import copy
import random
import textarena as ta

class SudokuEnv(ta.Env):
    """
    Sudoku game environment for TextArena.
    """

    environment_name = "Sudoku"

    def __init__(self, difficulty: str = "Easy", max_incorrect: int = 5, time_limit: Optional[int] = None):
        """
        Initialize the Sudoku environment.

        Args:
            difficulty (str): Difficulty level of the puzzle ("Easy", "Medium", "Hard").
            max_incorrect (int): Maximum number of incorrect attempts allowed.
            time_limit (Optional[int]): Time limit in seconds. None means no time limit.
        """
        self.ENVIRONMENT_NAME = f"Sudoku ({difficulty})"
        self.difficulty = difficulty
        self.max_incorrect = max_incorrect
        self.time_limit = time_limit  # in seconds

        # Initialize game state
        self.game_state = ta.State({
            "grid": [],
            "incorrect_attempts": 0,
            "start_time": None,
            "time_elapsed": 0,
            "completed": False,
            "logs": []
        }
        )

    def _load_puzzle(self, difficulty: str) -> List[List[int]]:
        """
        Generate a Sudoku puzzle based on the difficulty level.

        Args:
            difficulty (str): Difficulty level ("Easy", "Medium", "Hard").

        Returns:
            List[List[int]]: 9x9 Sudoku grid with zeros representing empty cells.
        """
        # Define number of clues based on difficulty
        difficulty_levels = {
            "Easy": 28,     # 53 clues (28 cells removed)
            "Medium": 32,  # 49 clues (32 cells removed)
            "Hard": 36,    # 45 clues (36 cells removed)
        }
        clues = difficulty_levels.get(difficulty, 28)  # Default to Easy if undefined

        # Generate a full grid
        full_grid = self._generate_full_grid()

        # Remove cells to create puzzle
        puzzle_grid = self._remove_cells(full_grid, clues)

        return puzzle_grid

    def _generate_full_grid(self) -> List[List[int]]:
        """
        Generates a fully solved Sudoku grid using backtracking.

        Returns:
            List[List[int]]: A fully solved 9x9 Sudoku grid.
        """
        grid = [[0 for _ in range(9)] for _ in range(9)]
        self._fill_grid(grid)
        return grid

    def _fill_grid(self, grid: List[List[int]]) -> bool:
        """
        Recursively fills the Sudoku grid using backtracking.

        Args:
            grid (List[List[int]]): The Sudoku grid to fill.

        Returns:
            bool: True if the grid is successfully filled, False otherwise.
        """
        empty = self._find_empty(grid)
        if not empty:
            return True  # Grid is complete
        row, col = empty

        numbers = list(range(1, 10))
        random.shuffle(numbers)
        for num in numbers:
            if self.is_safe(grid, row, col, num):
                grid[row][col] = num
                if self._fill_grid(grid):
                    return True
                grid[row][col] = 0
        return False

    def _find_empty(self, grid: List[List[int]]) -> Optional[Tuple[int, int]]:
        """
        Finds an empty cell in the grid.

        Args:
            grid (List[List[int]]): The Sudoku grid.

        Returns:
            Optional[Tuple[int, int]]: The row and column of an empty cell, or None if full.
        """
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    return (i, j)
        return None

    def is_safe(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """
        Checks if it's safe to place a number in a given cell.

        Args:
            grid (List[List[int]]): The Sudoku grid.
            row (int): Row index.
            col (int): Column index.
            num (int): Number to place.

        Returns:
            bool: True if safe, False otherwise.
        """
        # Check row
        if num in grid[row]:
            return False
        # Check column
        if num in [grid[i][col] for i in range(9)]:
            return False
        # Check subgrid
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if grid[i][j] == num:
                    return False
        return True

    def _remove_cells(self, grid: List[List[int]], clues: int) -> List[List[int]]:
        """
        Removes cells from the full grid to create a puzzle, ensuring a unique solution.

        Args:
            grid (List[List[int]]): A fully solved Sudoku grid.
            clues (int): Number of clues (filled cells) to retain.

        Returns:
            List[List[int]]: The resulting Sudoku puzzle grid.
        """
        puzzle = copy.deepcopy(grid)
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)

        while len(cells) > (81 - clues):
            row, col = cells.pop()
            removed = puzzle[row][col]
            puzzle[row][col] = 0

            # Make a copy to check for uniqueness
            grid_copy = copy.deepcopy(puzzle)
            solutions = []
            self._count_solutions(grid_copy, solutions)
            if len(solutions) != 1:
                # Not unique, revert the removal
                puzzle[row][col] = removed

        return puzzle

    def _solve_sudoku(self, grid: List[List[int]]) -> bool:
        """
        Solves the Sudoku puzzle using backtracking. Modifies the grid in-place.

        Args:
            grid (List[List[int]]): The Sudoku grid to solve.

        Returns:
            bool: True if solvable, False otherwise.
        """
        empty = self._find_empty(grid)
        if not empty:
            return True  # Solved
        row, col = empty

        for num in range(1, 10):
            if self.is_safe(grid, row, col, num):
                grid[row][col] = num
                if self._solve_sudoku(grid):
                    return True
                grid[row][col] = 0
        return False

    def _count_solutions(self, grid: List[List[int]], solutions: List[List[List[int]]], limit: int = 2) -> int:
        """
        Counts the number of solutions for a given Sudoku puzzle.

        Args:
            grid (List[List[int]]): The Sudoku grid.
            solutions (List[List[List[int]]]): A list to store found solutions.
            limit (int): The maximum number of solutions to find.

        Returns:
            int: The number of solutions found.
        """
        if len(solutions) >= limit:
            return len(solutions)

        empty = self._find_empty(grid)
        if not empty:
            solutions.append(copy.deepcopy(grid))
            return len(solutions)
        row, col = empty

        for num in range(1, 10):
            if self.is_safe(grid, row, col, num):
                grid[row][col] = num
                self._count_solutions(grid, solutions, limit)
                grid[row][col] = 0
        return len(solutions)

    def reset(
        self,
        seed: Optional[int] = None
    ) -> Tuple[Optional[Dict[int, str]], Dict[str, Any]]:
        """
        Reset the Sudoku environment to the initial state.

        Args:
            seed (Optional[int]): Seed for random number generator (not used here).

        Returns:
            Tuple containing:
                - observations (Optional[Dict[int, str]]): Initial observations for the player.
                - info (Dict[str, Any]): Additional information.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        self.state = ""

        # Load predefined puzzles
        self.initial_grid = self._load_puzzle(self.difficulty)

        self.game_state["grid"] = copy.deepcopy(self.initial_grid)
        self.game_state["incorrect_attempts"] = 0
        self.game_state["completed"] = False
        self.game_state["logs"] = ["[GAME] New Sudoku game started!"]
        self.game_state["start_time"] = time.time()
        self.game_state["time_elapsed"] = 0
        self.game_state["render"] = ["grid", "incorrect_attempts", "time_elapsed"]

        observations = {
            0: self._generate_player_prompt(0)
        }
        info = {
            "difficulty": self.difficulty,
            "max_incorrect": self.max_incorrect,
            "time_limit": self.time_limit
        }
        
        return observations, info

    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the initial prompt for the player, providing them with the Sudoku grid and instructions.

        Returns:
            str: Initial prompt for the player.
        """
        prompt = (
            f"You are Player {player_id}. You are playing Sudoku ({self.difficulty}).\n"
            "Here is the current state of the Sudoku grid. Each row is numbered from 1 to 9, and each column is also numbered from 1 to 9.\n"
            "Empty cells are represented by '.', and pre-filled cells contain digits from 1 to 9.\n\n"
            "Current Sudoku Grid:\n"
        )
        
        # Include the grid with row and column indices for clarity
        grid_str = self._get_grid_string_with_indices()
        prompt += f"{grid_str}\n\n"
        
        prompt += (
            "Your objective is to fill the empty cells in the 9x9 grid with digits from 1 to 9 such that:\n"
            "1. Each row contains all digits from 1 to 9 without repetition.\n"
            "2. Each column contains all digits from 1 to 9 without repetition.\n"
            "3. Each of the nine 3x3 subgrids contains all digits from 1 to 9 without repetition.\n\n"
            "Rules and Instructions:\n"
            "1. **Do not overwrite** the initial numbers provided in the grid.\n"
            "2. **Only fill** empty cells represented by '.'.\n"
            "3. **Respond only** with a single move at a time in the following format: 'row column number'.\n"
            "   - Example: To place the number 7 in row 5, column 3, respond with '5 3 7'.\n"
            "4. **Ensure** that your move does not violate Sudoku rules. Invalid moves will result in penalties.\n"
            "5. **Do not** include any additional text or explanations in your response.\n\n"
            "Examples:\n"
            "- **Valid Move**:\n"
            "  - Grid Snippet Before Move:\n"
            "  \n"
            "  - Move: `5 3 7`\n"
            "  - Explanation: Placing 7 at row 5, column 3 does not violate any Sudoku rules.\n\n"
            "- **Invalid Move** (Overwriting a pre-filled cell):\n"
            "  - Grid Snippet Before Move:\n"
            "  \n"
            "  - Move: `1 1 9`\n"
            "  - Explanation: Cell (1,1) is already filled with 5. You cannot overwrite it.\n\n"
            "- **Invalid Move** (Violating Sudoku rules):\n"
            "  - Grid Snippet Before Move:\n"
            "  \n"
            "  - Move: `1 3 5`\n"
            "  - Explanation: Placing 5 in row 1, column 3 violates the rule since 5 already exists in row 1.\n\n"
            "Good luck!\n\n"
        )
        
        if self.time_limit:
            prompt += f"You have {self.time_limit} seconds to complete the puzzle.\n"
        
        return prompt

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[Dict[int, str]],  # observations
        Optional[Dict[int, int]],  # rewards
        bool,  # truncated
        bool,  # terminated
        Dict[str, Any],  # info
    ]:
        """
        Performs a single step in the Sudoku environment.

        Args:
            player_id (int): The ID of the player (0 in single-player).
            action (str): The action to be taken in the format "row column number".

        Returns:
            Tuple containing:
                - observations (Optional[Dict[int, str]]): Updated grid.
                - rewards (Optional[Dict[int, int]]): Reward for the player.
                - truncated (bool): If the game was truncated due to time limit.
                - terminated (bool): If the game has been won or lost.
                - info (Dict[str, Any]): Additional information.
        """
        # if self.game_state["completed"]:
        #     return self.get_observations(), {"score": 0}, False, True, {"message": "Game already completed."}

        self.state += f"Player {player_id}: {action}\n"
        observation = f"Player {player_id} made a move: {action}"

        observations = {
            0: observation
        }

        # Check for time limit
        elapsed_time = time.time() - self.game_state["start_time"]
        if self.time_limit and elapsed_time > self.time_limit:
            self.game_state["completed"] = True
            self.game_state["time_elapsed"] = round(elapsed_time, 1)
            self.game_state["logs"].append("[GAME] Time limit exceeded.")
            info = {"reason": "Time limit exceeded."}
            return observations, {"score": -100}, True, True, info

        # Parse and validate action
        try:
            row, col, num = map(int, action.strip().split())
            if not (1 <= row <= 9 and 1 <= col <= 9 and 1 <= num <= 9):
                raise ValueError
        except ValueError:
            # Invalid action format
            self.game_state["time_elapsed"] = round(elapsed_time, 1)
            self.game_state["incorrect_attempts"] += 1
            reward = -10
            info = {"message": "Invalid action format. Use 'row column number' with values between 1 and 9."}
            self.game_state["logs"].append(f"[INVALID ACTION] {action}")
            return observations, {"score": reward}, self._check_truncated(), self._check_terminated(), info

        row_idx, col_idx = row - 1, col - 1

        # Check if the cell is already filled in the initial grid
        if self.initial_grid[row_idx][col_idx] != 0:
            self.game_state["time_elapsed"] = round(elapsed_time, 1)
            self.game_state["incorrect_attempts"] += 1
            reward = -10
            info = {"message": f"Cell ({row}, {col}) is already filled with {self.initial_grid[row_idx][col_idx]}."}
            self.game_state["logs"].append(f"[INVALID MOVE] Attempt to overwrite initial cell ({row}, {col}).")
            return observations, {"score": reward}, self._check_truncated(), self._check_terminated(), info

        # Check if the move is correct
        if self._is_move_correct(row_idx, col_idx, num):
            self.game_state["time_elapsed"] = round(elapsed_time, 1)
            self.game_state["grid"][row_idx][col_idx] = num
            reward = 1
            info = {"message": f"Placed {num} at ({row}, {col}). Correct move."}
            self.game_state["logs"].append(f"[CORRECT MOVE] Placed {num} at ({row}, {col}).")
        else:
            self.game_state["time_elapsed"] = round(elapsed_time, 1)
            self.game_state["incorrect_attempts"] += 1
            reward = -10
            info = {"message": f"Incorrect move: Cannot place {num} at ({row}, {col})."}
            self.game_state["logs"].append(f"[INCORRECT MOVE] Attempted to place {num} at ({row}, {col}).")

        # Check if the puzzle is completed
        if self._is_puzzle_complete():
            self.game_state["time_elapsed"] = round(elapsed_time, 1)
            self.game_state["completed"] = True
            reward += 10  # Bonus for completing the puzzle
            info["message"] = "Puzzle completed successfully!"
            self.game_state["logs"].append("[GAME] Puzzle completed successfully!")

        return observations, reward, self._check_truncated(), self._check_terminated(), info

    def render(self):
        """
        Renders the current state of the Sudoku grid.
        """
        grid_str = self._get_grid_string_with_indices()
        print(grid_str)
        print(f"Incorrect Attempts: {self.game_state['incorrect_attempts']}/{self.max_incorrect}")
        if self.time_limit:
            elapsed_time = int(time.time() - self.game_state["start_time"])
            print(f"Time Elapsed: {elapsed_time} seconds / {self.time_limit} seconds")

    def _get_grid_string_with_indices(self) -> str:
        """
        Converts the current grid to a formatted string with row and column indices.

        Returns:
            str: Formatted grid string with indices.
        """
        header = "   " + " ".join([f"C{j+1}" for j in range(9)])  # Column headers
        lines = [header]
        for i, row in enumerate(self.game_state["grid"]):
            row_str = f"R{i+1} "  # Row header
            for j, num in enumerate(row):
                cell = str(num) if num != 0 else "."
                row_str += f"{cell} "
                if (j + 1) % 3 == 0 and j < 8:
                    row_str += "| "
            lines.append(row_str.strip())
            if (i + 1) % 3 == 0 and i < 8:
                lines.append("   " + "- " * 11)
        return "\n".join(lines)


    def _is_move_correct(self, row: int, col: int, num: int) -> bool:
        """
        Checks if placing a number at the given position is correct.

        Args:
            row (int): Row index (0-based).
            col (int): Column index (0-based).
            num (int): Number to place.

        Returns:
            bool: True if the move is correct, False otherwise.
        """
        # Check row
        if num in self.game_state["grid"][row]:
            return False
        # Check column
        if num in [self.game_state["grid"][i][col] for i in range(9)]:
            return False
        # Check 3x3 subgrid
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if self.game_state["grid"][i][j] == num:
                    return False
        return True

    def _is_puzzle_complete(self) -> bool:
        """
        Checks if the puzzle is completely and correctly filled.

        Returns:
            bool: True if complete, False otherwise.
        """
        for i in range(9):
            for j in range(9):
                num = self.game_state["grid"][i][j]
                if num == 0 or not self._is_move_correct_complete(i, j, num):
                    return False
        return True

    def _is_move_correct_complete(self, row: int, col: int, num: int) -> bool:
        """
        Checks if the current move is still valid in the completed puzzle.

        Args:
            row (int): Row index (0-based).
            col (int): Column index (0-based).
            num (int): Number to place.

        Returns:
            bool: True if the move is correct, False otherwise.
        """
        # Temporarily remove the number to check for duplicates
        self.game_state["grid"][row][col] = 0
        correct = self._is_move_correct(row, col, num)
        self.game_state["grid"][row][col] = num
        return correct

    def _check_truncated(self) -> bool:
        """
        Determines if the episode should be truncated based on the time limit.

        Returns:
            bool: True if truncated, False otherwise.
        """
        if self.time_limit:
            elapsed_time = time.time() - self.game_state["start_time"]
            return elapsed_time > self.time_limit
        return False

    def _check_terminated(self) -> bool:
        """
        Determines if the episode should be terminated based on game completion or incorrect attempts.

        Returns:
            bool: True if terminated, False otherwise.
        """
        if self.game_state["completed"]:
            return True
        if self.game_state["incorrect_attempts"] >= self.max_incorrect:
            self.game_state["completed"] = True
            self.game_state["logs"].append("[GAME] Maximum number of incorrect attempts reached.")
            return True
        return False
