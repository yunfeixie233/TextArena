import re, random
from typing import Any, Dict, Optional, Tuple, List

import textarena as ta
from textarena.envs.games.PigDice.renderer import create_board_str

class PigDiceEnv(ta.Env):
    def __init__(self, winning_score: int = 100, max_turns: int = 500):
        """
        Args:
            winning_score (int): The score needed to win.
            max_turns (int): Maximum number of turns before the game ends.
        """
        super().__init__()
        self.winning_score = winning_score
        self.max_turns = max_turns
        self.roll_value = None

    def get_board_str(self):
        return create_board_str(
            scores=self.state.game_state["scores"], turn_total=self.state.game_state["turn_total"],
            current_player=self.state.current_player_id, current_roll=self.roll_value  # This is only available inside `_perform_roll`
        )

    def reset(self, num_players: int, seed: Optional[int] = None) -> None:
        self.state = ta.TwoPlayerState(num_players=num_players, max_turns=self.max_turns, seed=seed)
        self.state.reset(game_state={"scores": [0]*num_players, "turn_total": 0, "turn_count": 0}, player_prompt_function=self._prompt)

    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"[GAME] Welcome to Pig Dice Game!\n\n"
            f"You are Player {player_id}.\n\n"
            f"Rules:\n"
            f"- On your turn, you can either '[roll]' or '[hold]'\n"
            f"- Roll a 2-6: Add to your turn total\n"
            f"- Roll a 1: Lose turn total and end turn\n"
            f"- Hold: Add turn total to your score and end turn\n"
            f"- First to {self.winning_score} points wins\n\n"
            f"When it's your turn, you'll see the current scores and turn total.\n"
            f"Respond with '[roll]' to roll the die or '[hold]' to bank your points.\n"
        ) + f"\n\nCurrent turn total: {self.state.game_state['turn_total']}.\nAvailable actions: '[roll]', '[hold]'." if player_id==0 else ""

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(from_id=self.state.current_player_id, to_id=-1, message=action)
        match = re.compile(r"\[(roll|hold)\]", re.IGNORECASE).search(action.strip()) # Parse the action using regex
        if not match:
            self.state.set_invalid_move(reason=f"Invalid action format. Use '[roll]' or '[hold]'.")
            return self.state.step(rotate_player=False) 
            
        action = match.group(1).lower() # Extract the actual action
        # Execute the action
        if action == "roll": self._perform_roll(self.state.current_player_id)
        elif action == "hold": self._perform_hold(self.state.current_player_id)
        self.state.add_observation(to_id=self.state.current_player_id, message="Available actions: '[roll]' or '[hold]'")
        return self.state.step(rotate_player=False)
        
    def _determine_winner(self, scores):
        if scores[0] > scores[1]: return 0
        elif scores[0] < scores[1]: return 1
        return None

    def _rotate_to_next_player(self):
        scores = self.state.game_state['scores']
        # End game if the turn limit is reached
        if self.state.game_state["turn_count"] + 1 >= self.state.max_turns:
            winner_id = self._determine_winner(scores)
            if winner_id is None: self.state.set_draw(reason=f"The turn limit has been reached and all players have the same score: {scores}")
            else: self.state.set_winner(player_id=winner_id, reason=f"Player {winner_id} won by having a higher score at the turn limit ({scores})")
            return
        # End game if the winning score is reached
        if any(score >= self.winning_score for score in scores):
            winner_id = 0 if scores[0] > scores[1] else 1
            self.state.set_winner(player_id=winner_id, reason=f"Player {winner_id} won by reaching the target score of {self.winning_score}!")
            return
        # Otherwise, continue the game
        self.state.game_state["turn_count"] += 1
        self.state.game_state["turn_total"] = 0
        next_player_id = (self.state.current_player_id + 1) % self.state.num_players
        self.state.manually_set_current_player_id(new_player_id=next_player_id)
        scores_str = "\n".join(f"Player {i} score: {score}" for i, score in enumerate(scores))
        message = f"Player {next_player_id}'s turn\n\n{scores_str}\n\nCurrent turn total: {self.state.game_state['turn_total']}\n"
        self.state.add_observation(to_id=next_player_id, message=message)

    def _perform_roll(self, player_id: int) -> None:
        """ Perform the dice roll logic """
        roll_value = random.randint(1, 6)
        self.roll_value = roll_value
        self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=f"Player {player_id} rolls a {roll_value}.")
        if roll_value == 1: # Bust! Lose the turn total, end the turn
            self.state.add_observation(message=f"Player {player_id} busted! Lost all points for this turn.\n\n")
            self._rotate_to_next_player()
        else: # Accumulate turn total
            self.state.game_state["turn_total"] += roll_value
            self.state.add_observation(message=f"Turn total is now {self.state.game_state['turn_total']}.")

    def _perform_hold(self, player_id: int) -> None:
        """ The player holds, adding turn_total to their overall score and ending the turn """
        # Add turn total to player's score
        self.state.game_state['scores'][player_id] += self.state.game_state['turn_total']
        message = f"Player {player_id} holds and banks {self.state.game_state['turn_total']} points.\n\nTotal score: {self.state.game_state['scores'][player_id]}"
        self.state.add_observation(message=message)
        self._rotate_to_next_player()

