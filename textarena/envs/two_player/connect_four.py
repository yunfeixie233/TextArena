"""
Connect Four Game

In this game, two players take turns dropping discs into a vertical grid, trying to connect four of their own discs in a row either vertically, horizontally, or diagonally before the other player does.

**Gameplay:**

- The game is played on a grid of customizable size (`num_rows` x `num_cols`).
- Players take turns dropping their discs into one of the columns.
- A disc falls to the lowest available space within the column.
- The first player to connect four of their own discs vertically, horizontally, or diagonally wins.
- If the board fills up before either player connects four, the game is a draw.

**Key Rules:**

- Players must enter a valid column number (0 to `num_cols` - 1) on their turn.
- If a player provides an invalid column number or a column that is full, they lose.
- The game can be played in open or closed mode:
  - **Open Mode**: The game state (board) is visible to both players.
  - **Closed Mode**: The game state is not visible to the players.

**Parameters:**

- `is_open`: If `True`, the game state is visible to the players.
- `num_rows`: Number of rows in the game board.
- `num_cols`: Number of columns in the game board.

**Game Outcomes:**

- A player wins by connecting four of their own discs.
- A player loses if they make an invalid move.
- The game is a draw if the board is full without any player winning.
"""

from typing import Any, Dict, Optional, Tuple, List
import random, re
import textarena as ta


class ConnectFourEnv(ta.Env):
    """
    Environment for Connect Four Game.
    """

    def __init__(
        self,
        is_open: Optional[bool] = True,
        num_rows: Optional[int] = 6,
        num_cols: Optional[int] = 7,
    ):
        """
        Initialize the Connect Four game environment.

        Args:
            is_open (bool): If True, the game state is visible to the players.
            num_rows (int): Number of rows in the game board.
            num_cols (int): Number of columns in the game board.
        """
        self.environment_name = "Connect Four"
        self.is_open = is_open
        self.num_rows = num_rows
        self.num_cols = num_cols

        # Initialize game state variables
        self.state = ta.State(
            num_players=2,
            max_turns=None,
            render_keys=["rendered_board"]
        )


    def reset(
        self, seed: Optional[int] = None
    ) -> Tuple[Optional[ta.Observation], ta.Reward]:
        """
        Reset the game to its initial state.

        Args:
            seed (Optional[int]): Seed for random number generator to ensure reproducibility.

        Returns:
            Tuple[Dict[int, str], Dict[int, Any]]: Initial prompts for both players and additional info.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        # create the game board
        game_board = self._create_game_board()

        self.state.reset(
            game_state={
                "board":game_board,
                "rendered_board": self._render_board(game_board)
            },
        )

        # add the observations 
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=0,
            message=self._generate_player_prompt(player_id=0),
            for_logging=False
        )
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=1,
            message=self._generate_player_prompt(player_id=1),
            for_logging=False
        )

        return self.state.get_observations()


    def _create_game_board(self):
        """ TODO """
        return [["." for _ in range(self.num_cols)] for _ in range(self.num_rows)]

    def _generate_player_prompt(self, player_id: int) -> ta.Message:
        """
        Generate the initial prompt for a player.

        Args:
            player_id (int): The player's ID.

        Returns:
            str: The initial prompt for the player.
        """
        prompt = (
            f"You are Player {player_id} in Connect Four.\n"
            f"Your disc symbol: {'X' if player_id == 0 else 'O'}.\n"
            f"The game board has {self.num_rows} rows and {self.num_cols} columns.\n"
            f"Players take turns dropping their disc into one of the columns (0 to {self.num_cols - 1}).\n"
            "First to connect four discs vertically, horizontally, or diagonally wins.\n"
            "On your turn, enter the column number in squared brackets to make your move.\n"
            "For example: '[col 4]' or '[col 1]'.\n"
        )
        if self.is_open:
            prompt += (
                "The game board is visible to both players.\n"
                f"Current Board: {self._render_board()}"
            )
        else:
            prompt += "The game board is not visible to players.\n"
        return prompt

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[ta.Observation],  # observations
        Optional[ta.Reward],  # reward
        bool,  # truncated
        bool,  # terminated
        ta.Info,  # info
    ]:
        """
        Process the player's action.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The player's move (column number).

        Returns:
            tuple: (observations, reward, truncated, terminated, info)
        """

        # update the observations
        self.state.add_observation(
            from_id=player_id,
            to_id=-1, # all 
            message=action,
            for_logging=True
        )


        # Validate the action
        action_search_pattern = re.compile(r"\[col [0-9]*\]", re.IGNORECASE)
        match = action_search_pattern.search(action)

        if not match:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reason=f"Invalid action. Player {player_id} did not not provide a valid column number."
            )

        else:
            # extract the number 
            col = int(match.group(0).lower().replace("[col ", "").replace("]", ""))

            # check if valid number
            if not (0 <= col < self.num_cols) or self.state.game_state["board"][0][col] != ".":
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reason=f"Invalid action. Player {player_id} tried playing in column {col}.",
                )

            else:
                # Place the disc
                row = self._get_available_row(col)
                self.state.game_state["board"][row][col] = "X" if player_id == 0 else "O"

                # check for win
                if self._check_win(row, col):
                    self.state.set_winners(
                        player_ids=[player_id],
                        reason=f"Player {player_id} wins by connecting four!"
                    )

                # check for draw
                elif all(self.state.game_state["board"][0][c] != "." for c in range(self.num_cols)):
                    self.state.set_draw(
                        reason=f"The game is a draw."
                    )

                else:
                    # update observation
                    board_str = self._render_board()
                    if self.is_open:
                        self.state.add_observation(
                            from_id=ta.GAME_ID,
                            to_id=-1, # all 
                            message=f"Board state: {board_str}",
                            for_logging=False
                        )
                    self.state.game_state["rendered_board"] = board_str

        # step the state
        return self.state.step()

    def _get_available_row(self, col: int) -> int:
        """
        Get the next available row in the specified column.

        Args:
            col (int): The column number.

        Returns:
            int: The row index.
        """
        for r in range(self.num_rows - 1, -1, -1):
            if self.state.game_state["board"][r][col] == ".":
                return r
        return -1  # Should not happen if move is valid

    def _check_win(self, row: int, col: int) -> bool:
        """
        Check if placing a disc at (row, col) results in a win.

        Args:
            row (int): The row index.
            col (int): The column index.

        Returns:
            bool: True if the move results in a win, False otherwise.
        """
        board = self.state.game_state["board"]
        disc = board[row][col]
        directions = [
            [(0, 1), (0, -1)],  # Horizontal
            [(1, 0), (-1, 0)],  # Vertical
            [(-1, -1), (1, 1)],  # Diagonal /
            [(-1, 1), (1, -1)],  # Diagonal \
        ]
        for direction in directions:
            count = 1
            for dr, dc in direction:
                r, c = row, col
                while True:
                    r += dr
                    c += dc
                    if (
                        0 <= r < self.num_rows
                        and 0 <= c < self.num_cols
                        and board[r][c] == disc
                    ):
                        count += 1
                    else:
                        break
            if count >= 4:
                return True
        return False

    def _render_board(self, game_board: Optional[List[int]] = None) -> str:
        """
        Return a string representation of the board with column numbers.

        Returns:
            str: The board as a string.
        """
        if game_board is None:
            game_board = self.state.game_state["board"]

        column_numbers = " ".join([str(c) for c in range(self.num_cols)])
        board_rows = "\n".join([" ".join(row) for row in game_board])
        board_str = f"{column_numbers}\n{board_rows}"
        return board_str

    def render(self):
        """
        Render the current game state.
        """
        print(f"Turn: {self.state.turn}")
        print("Game Board:")
        print(self.state.game_state["rendered_board"])
        print("\nGame Logs:")
        for i, log in self.state.logs[-5:]:
            if i == -1:
                print(f"[GAME] {log}")
            else:
                print(f"[Player {i}] {log}")
        print("\n")
