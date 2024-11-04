import random
from typing import Optional, Dict, Tuple, Any

import textarena as ta


def _num_rounds(max_rounds, mode="random"):
    if mode == "random":
        return max(int(random.betavariate(2, 5) * max_rounds), 1) * 2
    elif mode == "fixed":
        return max_rounds * 2
    else:
        raise ValueError(f"Invalid mode: {mode}, must be 'random' or 'fixed'.")


class PrisonersDilemmaEnv(ta.Env):
    """
    Environment for the Iterated Prisoner's Dilemma Game.
    """

    def __init__(self, max_rounds: int = 30, mode: str = "random"):
        """
        Initialize the Iterated Prisoner's Dilemma game environment.

        Args:
            rounds (int): Number of rounds for the game.
        """
        self.max_rounds = max_rounds
        self.payoff_matrix = {
            ("cooperate", "cooperate"): (3, 3),
            ("cooperate", "defect"): (0, 5),
            ("defect", "cooperate"): (5, 0),
            ("defect", "defect"): (1, 1),
        }
        self.mode = mode
        num_rounds = _num_rounds(max_rounds, mode)
        self.state = ta.State(
            num_players=2,
            max_turns=num_rounds,
            render_keys=[["player_actions", 0], ["player_actions", 1]],
        )

    def reset(self, seed: Optional[int] = None) -> Optional[ta.Observations]:
        """
        Reset the game state for a new game.

        Args:
            seed (Optional[int]): Random seed for reproducibility.

        Returns:
            Observations for each player.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        game_state = {
            "player_scores": {0: 0, 1: 0},
            "player_actions": {0: None, 1: None},
        }
        out = self.state.reset(
            game_state=game_state, player_prompt_function=self._generate_player_prompt
        )
        self.state.max_turns = _num_rounds(self.max_rounds, self.mode)
        return out

    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the prompt shown to a player at each turn.

        Args:
            player_id (int): The player's ID.

        Returns:
            str: The prompt for the player.
        """
        prompt = (
            f"You are Player {player_id} in Iterated Prisoner's Dilemma.\n"
            f"On each turn, you may either 'cooperate' or 'defect'.\n"
            "Payoff matrix:\n"
            "  - If both players cooperate, each gets 3 points.\n"
            "  - If you cooperate and the opponent defects, you get 0 points, and they get 5.\n"
            "  - If you defect and the opponent cooperates, you get 5 points, and they get 0.\n"
            "  - If both defect, each gets 1 point.\n"
            "Each turn you can send a one-line message to your opponent followed by either 'cooperate' or 'defect' on the subsequent line."
            "Your action won't be revealed until both players have acted, but your message will be\n"
        )
        return prompt

    def step(self, player_id: int, action: str) -> Tuple[
        Optional[Dict[int, str]],  # observations
        Optional[Dict[int, int]],  # rewards
        bool,  # truncated
        bool,  # terminated
        Dict[str, Any],  # info
    ]:
        """
        Process the action of a player.

        Args:
            player_id (int): The player's ID.
            action (str): The action chosen by the player ('cooperate' or 'defect').

        Returns:
            tuple: (observations, rewards, truncated, terminated, info)
        """
        # Validate action
        parsed_action = action.split("\n")
        if len(parsed_action) > 2:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[
                    f"Invalid action by Player {player_id}: Must include a message followed by 'cooperate' or 'defect'."
                ],
            )
            return self.state.step()
        elif len(parsed_action) == 2:
            message = parsed_action[0]
            action = parsed_action[1]
        else:
            message = None
            action = parsed_action[0]
        if message is not None:
            self.state.add_observation(
                from_id=player_id,
                to_id=1 - player_id,
                message=message,
                for_logging=True,
            )
        if action not in {"cooperate", "defect"}:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[
                    f"Invalid action by Player {player_id}: '{action}'. Must be 'cooperate' or 'defect'."
                ],
            )
            return self.state.step()

        # Record player's action, broadcast to self
        self.state.game_state["player_actions"][player_id] = action
        self.state.add_observation(
            from_id=player_id,
            to_id=player_id,
            message=f"Player {player_id} chose to {action}",
            for_logging=True,
        )

        # Process actions if both players have acted
        if None not in self.state.game_state["player_actions"].values():
            actions = tuple(self.state.game_state["player_actions"].values())
            # broadcast actions to both players...
            self.state.add_observation(
                from_id=-1,
                to_id=0,
                message=f"Player 1 chose to {actions[1]}",
                for_logging=True,
            )
            self.state.add_observation(
                from_id=-1,
                to_id=1,
                message=f"Player 0 chose to {actions[0]}",
                for_logging=True,
            )
            scores = self.payoff_matrix[actions]

            # Update scores and log outcome
            for i, score in enumerate(scores):
                self.state.game_state["player_scores"][i] += score
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1,  # Broadcast to all
                message=f"Round result: {actions}. Scores updated to {self.state.game_state['player_scores']}",
                for_logging=True,
            )
            # check if game is over
            if self.state.turn >= self.state.max_turns - 1:
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1,  # Broadcast to all
                    message="Game over!",
                )
                if (
                    self.state.game_state["player_scores"][0]
                    == self.state.game_state["player_scores"][1]
                ):
                    self.state.set_draw(reason="Players have equal scores, game ended")
                else:
                    winner = max(
                        self.state.game_state["player_scores"],
                        key=self.state.game_state["player_scores"].get,
                    )
                    self.state.set_winners(
                        player_ids=[winner],
                        reason=f"Player {winner} has the highest score, game ended",
                    )
            else:
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1,  # Broadcast to all
                    message="Next round starting... Send a one-line message followed by 'cooperate' or 'defect' on the next line.",
                )

                # Reset actions for next round
                self.state.game_state["player_actions"] = {0: None, 1: None}
        return self.state.step()

    def render(self):
        """
        Render the current game state to the console.
        """
        print(f"Round {self.state.turn} / {self.state.max_turns}")
        print(
            f"Scores: Player 0 = {self.state.game_state['player_scores'][0]}, Player 1 = {self.state.game_state['player_scores'][1]}"
        )
        print("Game Logs:")
        for sender_id, message in self.state.game_state["logs"]:
            if sender_id == "GAME":
                print(f"[GAME]: {message}")
            else:
                print(f"Player {sender_id}: {message}")
        print("\n")
