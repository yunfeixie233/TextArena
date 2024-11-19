""" Connect Four Environment """

import textarena as ta

import random, re
from typing import Any, Dict, Optional, Tuple, List, Callable


class ConnectFourEnv(ta.Env):
    """ Environment for Connect Four Game. """
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
        self.is_open = is_open
        self.num_rows = num_rows
        self.num_cols = num_cols

        # Initialize game state variables
        self.state = ta.State(
            num_players=2,
            max_turns=None,
            render_keys=["rendered_board"]
        )

        self.observers: List[Callable[[Dict[str, Any]], None]] = []

        # load the game-board render object
        self.board_state_render = ta.envs.two_player.ConnectFour.render.GameStateRender

    def reset(
        self, seed: Optional[int] = None
    ) -> Optional[ta.Observations]:
        """
        Reset the Connect Four game to its initial state.

        Args:
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.

        Returns:
            Optional[ta.Observation]: Initial observations for both players as a dictionary.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        # create the game board
        game_board = self._create_game_board()


        # reset the state
        return self.state.reset(
            game_state={
                "board":game_board,
                "rendered_board": self._render_board(game_board)
            },
            player_prompt_function=self._generate_player_prompt
        )

    def _create_game_board(self) -> List[List[str]]:
        """
        Create an empty game board.

        Returns:
            List[List[str]]: A 2D list representing the game board initialized with '.' in all positions.
        """
        return [["." for _ in range(self.num_cols)] for _ in range(self.num_rows)]


    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
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

    def get_current_player_id(self):
        return self.state.current_player 

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[ta.Observations], # Observations: Dict[int, Tuple[int, str]]
        Optional[ta.Rewards], # Rewards: Dict[int, int]
        bool, # Truncated
        bool, # Terminated
        ta.Info, # Info: Optional[Dict[str, Any]]
    ]:
        """
        Process the player's action.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The player's move (column number).

        Returns:
            tuple: (observations, rewards, truncated, terminated, info)
        """
        # check the player_id and action fromat
        self.state.check_action_format(
            action=action,
            player_id=player_id
        )

        # update the observations and log the action
        self.state.add_observation(
            from_id=player_id,
            to_id=-1, # Broadcast to all
            message=action,
            for_logging=True
        )


        # Validate and parse the action
        is_valid, col_or_reason = self._validate_action(
            player_id=player_id,
            action=action
        )
        if not is_valid:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[col_or_reason]
            )
            return self.state.step()

        col = col_or_reason 

        # Place the disc
        row = self._get_available_row(col)
        self.state.game_state["board"][row][col] = "X" if player_id == 0 else "O"


        # Check for a win
        if self._check_win(row, col):
            self.state.set_winners(
                player_ids=[player_id],
                reason=f"Player {player_id} wins by connecting four!"
            )

        # Check for a draw
        elif self._is_draw():
            self.state.set_draw("The game is a draw.")
        
        else:
            # Update board state
            board_str = self._render_board()
            if self.is_open:
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1, # Broadcast to all 
                    message=f"Board state:\n{board_str}",
                    for_logging=False,
                )
            self.state.game_state["rendered_board"] = board_str

        return self.state.step()

    def _validate_action(self, player_id: int, action: str) -> Tuple[bool, Any]:
        """
        Validate the player's action.

        Args:
            action (str): The action string provided by the player.

        Returns:
            Tuple[bool, Any]: (is_valid, column number or reason for invalidity)
        """
        action_pattern = re.compile(r"\[col (\d+)\]", re.IGNORECASE)
        match = action_pattern.search(action.strip())
        if not match:
            return False, f"Player {player_id}, Invalid action format. Expected format: '[col x]'."

        col = int(match.group(1))
        if not (0 <= col < self.num_cols):
            return False, f"Player {player_id}, Invalid action. Column {col} is out of bounds."

        if self.state.game_state["board"][0][col] != ".":
            return False, f"Player {player_id}, Invalid action. Column {col} is full."

        return True, col

    def _is_draw(self) -> bool:
        """
        Check if the game has resulted in a draw.

        Returns:
            bool: True if the game is a draw, False otherwise.
        """
        return all(self.state.game_state["board"][0][c] != "." for c in range(self.num_cols))

    def _get_available_row(self, col: int) -> int:
        """
        Get the next available row in the specified column.

        Args:
            col (int): The column number.

        Returns:
            int: The row index where the disc can be placed.
        """
        for r in range(self.num_rows - 1, -1, -1):
            if self.state.game_state["board"][r][col] == ".":
                return r
        raise Exception("The column should be validated before calling the _get_available_row function.")

    def _check_direction(self, board, row, col, delta_row, delta_col, disc) -> int:
        """
        Check the number of consecutive discs in a specific direction.

        Args:
            board (List[List[str]]): The game board.
            row (int): Starting row index.
            col (int): Starting column index.
            delta_row (int): Row increment.
            delta_col (int): Column increment.
            disc (str): Disc symbol ('X' or 'O').

        Returns:
            int: Number of consecutive discs in the specified direction.
        """
        count = 0
        r, c = row + delta_row, col + delta_col
        while 0 <= r < self.num_rows and 0 <= c < self.num_cols and board[r][c] == disc:
            count += 1
            r += delta_row
            c += delta_col
        return count

    def _check_win(self, row: int, col: int) -> bool:
        """
        Check if the latest move at (row, col) wins the game.

        Args:
            row (int): The row index of the latest disc.
            col (int): The column index of the latest disc.

        Returns:
            bool: True if the move results in a win, False otherwise.
        """
        board = self.state.game_state["board"]
        disc = board[row][col]
        directions = [
            ((0, 1), (0, -1)),    # Horizontal
            ((1, 0), (-1, 0)),    # Vertical
            ((1, 1), (-1, -1)),   # Diagonal /
            ((1, -1), (-1, 1)),   # Diagonal \
        ]

        for direction in directions:
            total = 1  # Count the disc just placed
            for delta_row, delta_col in direction:
                total += self._check_direction(board, row, col, delta_row, delta_col, disc)
            if total >= 4:
                return True
        return False


    def _render_board(self, game_board: Optional[List[List[str]]] = None) -> str:
        """
        Return a string representation of the board with column numbers.

        Args:
            game_board (Optional[List[List[str]]]): The game board to render. 
                If None, uses the current game state.

        Returns:
            str: The board as a formatted string.
        """
        if game_board is None:
            game_board = self.state.game_state["board"]

        column_numbers = " ".join([str(c) for c in range(self.num_cols)])
        separator = "-" * (self.num_cols * 2 - 1)
        board_rows = "\n".join([" ".join(row) for row in game_board])
        board_str = f"{column_numbers}\n{separator}\n{board_rows}"
        return board_str


    def render(self):
        """
        Render the current game state to the console.
        """
        raise NotImplementedError("Please use a render wrapper.")
        # print(f"Turn: {self.state.turn}")
        # print("Game Board:")
        # print(self.state.game_state["rendered_board"])
        # print("\nRecent Game Logs:")
        # recent_logs = self.state.logs[-5:]  # Display the last 5 logs
        # for sender_id, log in recent_logs:
        #     if sender_id == ta.GAME_ID:
        #         print(f"[GAME] {log}")
        #     else:
        #         print(f"[Player {sender_id}] {log}")


    def register_observer(self, observer: Callable[[Dict[str, Any]], None]):
        """ Register an observer callback. """
        if observer not in self.observers:
            self.observers.append(observer)