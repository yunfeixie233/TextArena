import re, chess 
from typing import Any, Dict, Optional, Tuple

import textarena as ta


class ChessEnv(ta.Env):
    """Environment for playing the game of Chess."""

    def __init__(self, is_open: bool=True, max_turns: int=30, show_valid: bool=True):
        """
        Initialize the Chess game environment.
        Args:
            is_open (bool): If True, both players can see the current board state.
                            If False, players receive minimal information.
            max_turns (int): Maximum number of turns before the game ends.
            show_valid (bool): If True, players can see a list of valid moves.
        """
        self.is_open = is_open 
        self.show_valid = show_valid 

        # Initialize game state variables
        self.state = ta.State(
            num_players=2,
            max_turns=max_turns,
            role_mapping={0: "White", 1: "Black"}
        )
        self.board = None

        # Regex patterns
        self.move_pattern = re.compile(r"\[[a-h][1-8][a-h][1-8][qrbn]?\]", re.IGNORECASE)


    @property
    def offline_renderer(self):
        from textarena.envs.two_player.Chess.render.renderer import ChessRenderer
        return ChessRenderer

    @property
    def terminal_render_keys(self):
        return ["current_board"]


    def reset(self, num_players: int=2, seed: Optional[int]=None):
        """
        Reset the game to its initial state.
        Args:
            seed (Optional[int]): Seed for random number generator to ensure reproducibility.
        """
        if seed is not None:
            random.seed(seed)

        assert num_players==2, f"The number of players has to be 2 for Chess. You provided {num_players}"


        # Initialize the chess board
        self.board = chess.Board()

        self.state.reset(
            game_state={
                "current_board": str(self.board),
                "valid_moves": ', '.join([f'[{move.uci()}]' for move in self.board.legal_moves])
            },
            player_prompt_function=self._generate_player_prompt
        )


    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        """
        Generate the initial prompt for a player.
        Args:
            player_id (int): ID of the player (0 for White, 1 for Black).
        Returns:
            str: The initial prompt for the player.
        """
        color = "White" if player_id == 0 else "Black"
        prompt = (
            f"You are playing {color} in a game of Chess.\n"
            "Make your move in UCI format enclosed in square brackets (e.g., [e2e4]).\n"
            "You can include additional text in your messages.\n"
        )
        if self.is_open:
            prompt += f"Current board state:\n{self.board}\n"

        if player_id == 0:
            prompt += "Please make the first move."

        if self.show_valid:
            prompt += f"Valid moves: {game_state['valid_moves']}"

        return prompt

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """
        Process the player's move.
        Args:
            action (str): The move in UCI notation enclosed in square brackets (e.g., [Move] e2e4).
        Returns:
            tuple: (done, info)
        """
        # update the log
        self.state.add_observation(
            from_id=self.state.current_player_id,
            to_id=-1, # Broadcast
            message=action,
            for_logging=True
        )


        # execute move
        self._execute_player_move(
            player_id=self.state.current_player_id, 
            action=action
        )


        # check from game over
        self._check_gameover()

        # add valid moves / board state to observations as necessary
        self._agument_observations()


        # update the board state string
        self.state.game_state["current_board"] = str(self.board)

        return self.state.step()




    def _execute_player_move(self, player_id: int, action: str):
        """Execute the player's move based on the action string."""
        match = self.move_pattern.search(action.strip())
        
        # check if a move was provided
        if match is None:
            self.state.set_invalid_move(
                player_id=player_id,
                reason=f"Player {player_id} did not provide a move."
            )

        else:
            # Extract the move from within the brackets
            move_uci = match.group(0).lower().replace("[", "").replace("]", "")

            # Attempt to make the move
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                # execute move
                self.board.push(move)
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1, # Broadcast to all
                    message=f"Player {player_id} made the following move: {move_uci}"
                )

            else:
                # illegal move
                self.state.set_invalid_move(
                    player_id=player_id,
                    reason=f"Player {player_id} tried making an illegal move."
                )


    def _check_gameover(self):
        """Check if the game has ended and set the appropriate state."""
        if self.board.is_game_over():
            
            # get winner
            outcome = self.board.outcome().result() #.result()

            # check for draw
            if outcome == "1/2-1/2":
                self.state.set_draw(
                    reason=f"Game ended in a draw."
                )
            else:
                winner_id = 0 if outcome == "1-0" else 1
                self.state.set_winners(
                    player_ids=[winner_id],
                    reason=f"Player {winner_id} wins the match."
                )


    def _agument_observations(self):
        """Augment observations with current board state and valid moves."""
        if self.is_open:
            # display the board state
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1, # Broadcast to all 
                message=str(self.board),
                for_logging=False # already displayed in Game State section
            )

        if self.show_valid:
            # show the valid moves
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1, # Broadcast to all 
                message=f"Valid moves: {', '.join([f'[{move.uci()}]' for move in self.board.legal_moves])}",
                for_logging=False # already displayed in Game State section
            )