import random
import re
from typing import Any, Dict, Optional, Tuple

import chess

import textarena as ta


class ChessEnv(ta.Env):
    """Environment for playing the game of Chess."""

    def __init__(
        self,
        is_open: bool = True,
        max_turns: int = 30,
        show_valid: bool = True,
    ):
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
            render_keys=["current_board"],
            role_mapping={0: "White", 1: "Black"}
        )

        # Regex patterns
        self.move_pattern = re.compile(r"\[[a-h][1-8][a-h][1-8][qrbn]?\]", re.IGNORECASE)

    def reset(
        self, seed: Optional[int] = None
    ) -> Optional[ta.Observations]:
        """
        Reset the game to its initial state.
        Args:
            seed (Optional[int]): Seed for random number generator to ensure reproducibility.
        Returns:
            Optional[ta.Observations]: Initial prompts for both players and additional info.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        # Initialize the chess board
        self.board = chess.Board()

        return self.state.reset(
            game_state={"current_board": str(self.board)},
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
            "You can also include additional text in your messages.\n"
        )
        if self.is_open:
            prompt += f"Current board state:\n{self.board}\n"

        # prompt += "It's your turn. What is your move?"

        if player_id == 0:
            prompt += "Please make the first move."

        return prompt

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
        Process the player's move.
        Args:
            player_id (int): The player's ID (0 for White, 1 for Black).
            action (str): The move in UCI notation enclosed in square brackets (e.g., [Move] e2e4).
        Returns:
            tuple: (observations, reward, truncated, terminated, info)
        """
        # check the player_id and action fromat
        self.state.check_action_format(
            action=action,
            player_id=player_id
        )

        # update the log
        self.state.add_observation(
            from_id=player_id,
            to_id=-1, # Broadcast
            message=action,
            for_logging=True
        )


        # execute move
        self._execute_player_move(player_id=player_id, action=action)


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
        if not match:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[f"Player {player_id} did not provide a move."]
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
                    player_ids=[player_id],
                    reasons=[f"Player {player_id} tried making an illegal move."]
                )


    def _check_gameover(self):
        """Check if the game has ended and set the appropriate state."""
        print(self.board.is_stalemate())
        print(self.board)
        if self.board.is_game_over():
            
            # get winner
            outcome = self.board.outcome().result() #.result()
            print(outcome)
            print(self.board.check_stalemate())
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




    # def render(self):
    #     """
    #     Render the current game state.
    #     This method can be called externally to display the game state.
    #     """
    #     print(f"Turn {self.game_state['turn']}/{self.game_state['max_turns']}")
    #     print("Current Board State:")
    #     print(self.board)
    #     print("\nAction Logs:")
    #     for sender_id, message in self.game_state["logs"]:
    #         if sender_id == -1:
    #             print(f"[GAME]: {message}")
    #         else:
    #             print(f"Player {sender_id}: {message}")
    #     print("\n")
    def render(self):
        """
        Render the current game state.
        This method can be called externally to display the game state.
        """
        current_turn = self.state.game_state.get("turn", 0)
        max_turns = self.state.game_state.get("max_turns", 30)
        print(f"Turn {current_turn}/{max_turns}")
        print("Current Board State:")
        print(self.board)
        print("\nAction Logs:")
        for sender_id, message in self.state.game_state["logs"]:
            if sender_id == -1:
                print(f"[GAME]: {message}")
            else:
                print(f"Player {sender_id}: {message}")
        print("\n")
