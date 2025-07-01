import re
from typing import Dict, Any
import numpy as np

import textarena as ta
from textarena.envs.IteratedPrisonersDilemma.env import IteratedPrisonersDilemmaEnv
from textarena.envs.IteratedStagHunt.renderer import create_board_str


class IteratedStagHuntEnv(IteratedPrisonersDilemmaEnv):
    """Environment for Iterated Stag Hunt"""

    def __init__(
            self,
            num_rounds: int = 5,
            communication_turns: int = 3,
            mutual_stag_reward: int = 10,
            single_hare_reward: int = 8,
            single_stag_reward: int = 1,
            mutual_hare_reward: int = 5,
            random_seed: int = None,
    ):
        """
        Initialize the Iterated Stag Hunt environment. Stag hunt is a game with two pure strategy Nash equilibria, the
        *risk dominant* version, hunting for stags, and the *payoff dominant* version, hunting for hares. The general
        payoff matrix in the game is as follows, where a > b ≥ d > c.

        +------+--------+--------+
        |      | Stag   | Hare   |
        +------+--------+--------+
        | Stag | (a, a) | (c, b) |
        +------+--------+--------+
        | Hare | (b, c) | (d, d) |
        +------+--------+--------+

        Args:
            num_rounds (int): Number of decision rounds.
            communication_turns (int): Number of communication turns between decisions.
            mutual_stag_reward (int): Reward for mutual cooperation when hunting stags (a).
            single_hare_reward (int): Reward for hunting hares when the other hunts for stags (b).
            single_stag_reward (int): Reward for hunting stags where the other hunts for hares (c).
            mutual_hare_reward (int): Reward for both hunting hares (d).
            random_seed (int): A random seed for generating the payoff matrices per round. If `None`, the game uses the
                same payoff matrix for each round, which is defined by the rewards above. If a random seed is provided,
                then the rewards are drawn from a uniform distribution, where the rewards provided by the user are
                considered the maximum.

        Notes:
            The Iterated Stag Hunt environment is based on ``TextArena`` s existing implementation of the Iterated
            Prisoner's Dilemma. The elements of the payoff matrix are assigned to their jail equivalent.

        """
        # Initialize the iterated Prisoner's Dilemma to build upon
        super().__init__()

        # Game parameters (update aliases)
        self.num_rounds = num_rounds
        self.communication_turns = communication_turns
        self.max_turns = num_rounds * (communication_turns + 2)

        # Payoff matrix parameters
        if random_seed is None:
            self.cooperate_reward = mutual_stag_reward * np.ones(self.num_rounds, dtype=int) # a
            self.defect_reward = single_hare_reward * np.ones(self.num_rounds, dtype=int)  # b
            self.sucker_reward = single_stag_reward * np.ones(self.num_rounds, dtype=int) # c
            self.mutual_defect_reward = mutual_hare_reward * np.ones(self.num_rounds, dtype=int) # d

        else:
            np.random.seed(random_seed)  # Reseed the random state on init
            a, b, c, d = self.get_payoff_matrix(mutual_stag_reward, single_hare_reward, single_stag_reward,
                                                mutual_hare_reward)
            self.cooperate_reward = a
            self.defect_reward = b
            self.sucker_reward = c
            self.mutual_defect_reward = d


        # Action patterns
        self.cooperate_pattern = re.compile(r"\[Stag\]", re.IGNORECASE)
        self.defect_pattern = re.compile(r"\[Hare\]", re.IGNORECASE)

    def get_payoff_matrix(self, a_max: int, b_max: int, c_max: int, d_max: int) -> tuple:
        """
        Generate a payoff matrix for each round of the game. The general payoff matrix in the game is as follows,
        where a > b ≥ d > c.

        +------+--------+--------+
        |      | Stag   | Hare   |
        +------+--------+--------+
        | Stag | (a, a) | (c, b) |
        +------+--------+--------+
        | Hare | (b, c) | (d, d) |
        +------+--------+--------+

        Args:
            a_max (int): the maximal value for reward a.
            b_max (int): the maximal value for reward b.
            c_max (int): the maximal value for reward c.
            d_max (int): the maximal value for reward d.

        Returns:
            tuple: a tuple containing the cooperate reward, defect reward, sucker reward and mutual defect reward.
        """
        c = np.ones(self.num_rounds, dtype=int) * c_max
        d = np.random.randint(c + 1, d_max + 1)
        b = np.random.randint(d, b_max + 1)
        a = np.random.randint(b + 1, a_max + 1)
        return a, b, c, d

    def get_board_str(self) -> str:
        """Get the string representing the Iterative Stag Hunt board."""
        return create_board_str(game_state=self.state.game_state)

    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """Generate the initial prompt for a player."""
        i = self.state.game_state['current_round'] - 1
        prompt = (
            f"You are Player {player_id} in an Iterated Stag Hunt game.\n\n"
            f"Game Structure:\n"
            f"- The game consists of {self.num_rounds} decision rounds\n"
            f"- Before each decision, you have {self.communication_turns} turns to communicate\n"
            f"- After communication, both players simultaneously choose to hunt a Stag or Hare\n\n"
            f"Rewards:\n"
            f"- The rewards associated with hunting stags and hares may differ between rounds\n"
            f"- The rewards are presented at the start of each round\n\n"
            f"How to Play:\n"
            f"- During communication: Simply type your message\n"
            f"- During decision phase: Use [Stag] or [Hare]\n"
            f"You can include additional text before or after these tokens.\n"
        )

        if game_state['current_round'] == 1:
            round_start = (
                f"\nStarting Round 1\n"
                f"Payoff Matrix:\n"
                f"- Both hunt a Stag: Both get {self.cooperate_reward[i]} points\n"
                f"- Both hunt a Hare: Both get {self.mutual_defect_reward[i]} points\n"
                f"- One hunts a Hare, One hunts a Stag: The hunter of the Hare gets {self.defect_reward[i]} points,"
                f" the hunter of the Stag gets {self.sucker_reward[i]} point\n"
            )
            prompt += round_start

        return prompt

    def _calculate_round_rewards(self):
        """Calculate and apply rewards based on player decisions."""
        p0_decision = self.state.game_state["round_decisions"][0]
        p1_decision = self.state.game_state["round_decisions"][1]
        current_round = self.state.game_state['current_round'] - 1

        # Calculate rewards
        if p0_decision == "cooperate" and p1_decision == "cooperate":
            p0_reward = p1_reward = self.cooperate_reward[current_round]
            outcome = "Both players hunted a stag"
        elif p0_decision == "defect" and p1_decision == "defect":
            p0_reward = p1_reward = self.mutual_defect_reward[current_round]
            outcome = "Both players hunted a hare"
        elif p0_decision == "cooperate" and p1_decision == "defect":
            p0_reward = self.sucker_reward[current_round]
            p1_reward = self.defect_reward[current_round]
            outcome = "Player 0 hunted a stag, Player 1 hunted a hare"
        else:  # p0 defects, p1 cooperates
            p0_reward = self.defect_reward[current_round]
            p1_reward = self.sucker_reward[current_round]
            outcome = "Player 0 hunted a hare, Player 1 hunted a stag"

        # Update scores
        self.state.game_state["scores"][0] += p0_reward
        self.state.game_state["scores"][1] += p1_reward

        # Reveal round results to all players
        message = (
            f"Round {self.state.game_state['current_round']} Results:\n"
            f"{outcome}\n"
            f"Player 0 scored {p0_reward}, total: {self.state.game_state['scores'][0]}\n"
            f"Player 1 scored {p1_reward}, total: {self.state.game_state['scores'][1]}\n\n"
        )
        self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message, observation_type=ta.ObservationType.GAME_MESSAGE)

    def _handle_decision_phase(self, player_id: int, action: str):
        # Parse decision
        decision = None
        if self.cooperate_pattern.search(action):
            decision = "cooperate"
        elif self.defect_pattern.search(action):
            decision = "defect"
        if decision is None: self.state.add_observation(from_id=self.state.current_player_id,
                                                        to_id=self.state.current_player_id,
                                                        message=f"Player {player_id} did not provide a valid decision.",
                                                        observation_type=ta.ObservationType.GAME_ADMIN); return
        self.state.game_state["round_decisions"][player_id] = decision  # Record decision

        # If both players have decided, calculate rewards and reveal decisions
        if all(d is not None for d in self.state.game_state["round_decisions"].values()):
            self._calculate_round_rewards()
            self.state.game_state["history"].append({"round": self.state.game_state["current_round"],
                                                     "decisions": self.state.game_state[
                                                         "round_decisions"].copy()})  # Record round history
            if self.state.game_state["current_round"] == self.num_rounds:
                self._determine_winner()  # Check if game is complete
            else:  # Reset for next round
                self.state.game_state["current_round"] += 1
                self.state.game_state["current_comm_turn"] = 0
                self.state.game_state["is_decision_phase"] = False
                self.state.game_state["round_decisions"] = {0: None, 1: None}
                i = self.state.game_state['current_round'] - 1

                message = (
                    f"Starting Round {self.state.game_state['current_round']}\n"
                    f"The payoff matrix for Round {self.state.game_state['current_round']} is:\n"
                    f"- Both hunt a Stag: Both get {self.cooperate_reward[i]} points\n"
                    f"- Both hunt a Hare: Both get {self.mutual_defect_reward[i]} points\n"
                    f"- One hunts a Hare, One hunts a Stag: The hunter of the Hare gets {self.defect_reward[i]} points,"
                    f" the hunter of the Stag gets {self.sucker_reward[i]} point\n\n"
                           )

                self.state.add_observation(message=message, observation_type=ta.ObservationType.GAME_MESSAGE)
