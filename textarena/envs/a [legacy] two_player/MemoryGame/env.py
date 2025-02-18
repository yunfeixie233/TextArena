from typing import Any, Dict, Optional, Tuple, List
import random
import textarena as ta
import re

class MemoryGameEnv(ta.Env):
    """
    Environment for Memory Game.
    """
    def __init__(
        self,
        difficulty: Optional[str] = "easy",
    ):
        """
        Initialize the Memory Game environment.
        
        Args:
            difficulty (str): Difficulty level of the game. Possible values are "easy", "medium", and "hard".
        """
        self.environment_name = "MemoryGame"
        self.difficulty = difficulty

        # Initialize the grid size based on the difficulty level
        if self.difficulty == "easy":
            self.grid_size = 4
        elif self.difficulty == "medium":
            self.grid_size = 6
        elif self.difficulty == "hard":
            self.grid_size = 8
        else:
            raise ValueError("Invalid difficulty level. Please choose from 'easy', 'medium', or 'hard'.")
        
        # Initialize the game state
        self.state = ta.State(
            num_players=2,
            max_turns=None,
        )

    @property
    def terminal_render_keys(self):
        return ["rendered_board", "scores"]

    def reset(self, num_players: int = 2, seed: Optional[int] = None):
        """
        Reset the environment to start a new game.
        
        Args:
            seed (int): Seed for the random number generator.
        """
        ## set the random seed
        if seed is not None:
            random.seed(seed)
        assert num_players==2, f"The number of players has to be 2 for MemoryGame. You provided {num_players}"

        ## Initialize the board
        self.board = self._generate_board()
        self.matched_positions = set()
        self.score = {0: 0, 1: 0}

        ## Initialize the game state
        return self.state.reset(
            game_state={
                "board": self.board,
                "rendered_board": self._render_board(self.board),
                "scores": {
                    0: {"Score": 0},
                    1: {"Score": 0}
                }
            },
            player_prompt_function=self._generate_player_prompt
        )
    
    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """
        Generate the player prompt.
        
        Args:
            player_id (int): ID of the player.
        
        Returns:
            str: Player prompt.
        """
        prompt = (
            f"You are Player {player_id}. You are playing the Memory Game ({self.difficulty} level).\n"
            "Your goal is to match more pairs of cards on the board, than your opponent.\n"
            "On your turn, select two cards to flip by entering the row and column numbers of the first and second card respectively like [0 1 1 0], where the first card is in row 0 and column 1, and the second card is in row 1 and column 0.\n"
            "If the two cards match, you get a point and the cards remain face up. If they do not match, the cards are flipped back face down, e.g. '.'.\n"
            "The game ends when all pairs have been matched.\n"
            "Here is the initial board with all cards faced down:\n"
        )

        prompt += self._render_board(self.board)

        return prompt
    
    def _generate_board(self) -> List[List[str]]:
        """
        Generate the initial board with shuffled pairs of cards.
        
        Returns:
            List[List[str]]: Initial board configuration.
        """
        ## Generate pairs of cards
        num_pairs = (self.grid_size ** 2) // 2
        symbols = [chr(65 + i) for i in range(num_pairs)] * 2
        random.shuffle(symbols)

        board = [symbols[i * self.grid_size:(i + 1) * self.grid_size] for i in range(self.grid_size)]

        return board
    
    def _render_board(self, board: List[List[str]]) -> str:
        """
        Render the board state.
        
        Args:
            board (List[List[str]]): Current board configuration.
        
        Returns:
            str: Rendered board state.
        """
        rendered_board = "  " + " ".join(str(c) for c in range(self.grid_size)) + "\n"
        for r in range(self.grid_size):
            row = f"{r} "
            for c in range(self.grid_size):
                if (r, c) in self.matched_positions:
                    row += f"{board[r][c]} "
                else:
                    row += ". "
            rendered_board += row.strip() + "\n"
        
        return rendered_board
    
    def step(self, action: List[int]) -> Tuple[bool, ta.Info]:
        """
        Process the player's action.

        Args:
            player_id (int): The ID of the player making the move.
            action (List[int]): The action taken by the player.

        Returns:
            bool: Whether the game is terminated.
            Info: Additional information about the game state
        """

        player_id = self.state.current_player_id

        ## update the observation
        self.state.add_observation(
            from_id=player_id,
            to_id=-1, # this means broadcast to all
            message=action,
            for_logging=True
        )

        ## action search pattern
        action_search_pattern = re.compile(r"\[([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+)\]") # e.g. [0 1 1 0]
        match = action_search_pattern.search(action)

        if match is None:
            self.state.set_invalid_move(
                player_id=player_id,
                reason=f"Invalid move format. Player {player_id} did not respond with a valid direction in square brackets."
            )
        else:
            r1, c1, r2, c2 = map(int, match.groups())
            if r1 < 0 or r1 >= self.grid_size or c1 < 0 or c1 >= self.grid_size or r2 < 0 or r2 >= self.grid_size or c2 < 0 or c2 >= self.grid_size:
                self.state.set_invalid_move(
                    player_id=player_id,
                    reason=f"Invalid move. Player {player_id} selected an out-of-bounds position."
                )
            elif (r1, c1) == (r2, c2):
                self.state.set_invalid_move(
                    player_id=player_id,
                    reason=f"Invalid move. Player {player_id} selected the same card twice."
                )
            elif (r1, c1) in self.matched_positions or (r2, c2) in self.matched_positions:
                self.state.set_invalid_move(
                    player_id=player_id,
                    reason=f"Invalid move. Player {player_id} selected one or both cards that have already been matched."
                )
            else:
                if self.board[r1][c1] == self.board[r2][c2]:
                    ## update the score
                    self.score[player_id] += 1

                    ## update the matched positions
                    self.matched_positions.update([(r1, c1), (r2, c2)])

                    ## check if the game is over
                    if len(self.matched_positions) == self.grid_size ** 2:
                        ## check if there is a tie
                        if self.score[0] == self.score[1]:
                            self.state.set_draw(
                                reason="Both players matched the same number of pairs of cards."
                            )
                        else:
                            ## set the winner
                            winner_id = max(self.score, key=self.score.get)
                            self.state.set_winners(
                                player_ids=[winner_id],
                                reason=f"Player {winner_id} matched more pairs of cards."
                            )

                    ## log the action
                    self.state.add_observation(
                        from_id=ta.GAME_ID,
                        to_id=-1,
                        message=f"Cards at positions [{r1} {c1}] and [{r2} {c2}] match!\nUpdated board:\n" + self._render_board(self.board),
                        for_logging=False
                    )

                else:
                    ## log the action
                    pos1 = self.board[r1][c1]
                    pos2 = self.board[r2][c2]
                    self.state.add_observation(
                        from_id=ta.GAME_ID,
                        to_id=-1,
                        message=f"The cards do not match. Cards at positions [{r1} {c1}] and [{r2} {c2}] are {pos1} and {pos2} respectively.",
                        for_logging=False
                    )

        ## update the scores
        self.state.game_state["scores"] = {
            0: {"Score": self.score[0]},
            1: {"Score": self.score[1]}
        }

        ## update the rendered board
        self.state.game_state["rendered_board"] = self._render_board(self.board)


        ## return the updated game state
        return self.state.step()
            
    def render(self):
        """
        Render the current game state.
        """
        print(self.state.game_state["rendered_board"])

    