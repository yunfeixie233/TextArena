"""
Scenario Planning Game

In this game, two players are presented with a survival scenario and must each propose a strategy for survival.

**Gameplay:**

- Both players receive the same scenario.
- Each player independently proposes a strategy for survival in that scenario.
- After both strategies are submitted, a panel of judges evaluates the strategies.
- The player with the most effective and feasible strategy, as determined by the judges, wins.

**Key Rules:**

- Players must submit their own unique strategies.
- Strategies are evaluated based on effectiveness and feasibility.
- The game ends after both players have submitted their strategies and the judges have made their decision.

**Parameters:**

- `num_judges`: Number of simulated judges evaluating the strategies.
- `scenarios_path`: Path to the JSON file containing survival scenarios.

**Game Outcomes:**

- **Win**: The player whose strategy is deemed more effective by the judges wins.
- **Tie**: If both strategies are equally effective, the game is a tie.
"""

from typing import Any, Dict, Optional, Tuple
import os
import json
import random
import textarena as ta

class ScenarioPlanningEnv(ta.Env):
    def __init__(
        self,
        num_judges: Optional[int] = 11,
        scenarios_path: Optional[str] = None,
    ):
        """
        Initialize the Scenario Planning game.

        Args:
            num_judges (int): Number of judges evaluating the strategies.
            scenarios_path (str): Path to the JSON file containing scenarios.
        """
        self.ENVIRONMENT_NAME = "Scenario Planning"

        self.num_judges = num_judges

        # Load scenarios
        self._load_scenarios(scenarios_path)

        # Initialize game state
        self.game_state = {
            "strategies": {0: None, 1: None},
            "scenario": None,
            "logs": [],
            "render": ["scenario"],
        }

    def _load_scenarios(self, scenarios_path: Optional[str]):
        """
        Load scenarios from the JSON file.

        Args:
            scenarios_path (str): Path to the JSON file containing scenarios.
        """
        if scenarios_path is None:
            scenarios_path = os.path.join(
                "textarena", "envs",
                "two_player", "data",
                "scenario_planning_scenarios.json"
            )

        if not os.path.exists(scenarios_path):
            raise FileNotFoundError(f"Scenarios file not found at {scenarios_path}")

        with open(scenarios_path, 'r') as f:
            data = json.load(f)

        if "scenarios" not in data or not isinstance(data["scenarios"], list):
            raise ValueError("Invalid format for scenarios JSON. Expected a key 'scenarios' with a list of scenarios.")

        self.scenarios = data["scenarios"]
        if not self.scenarios:
            raise ValueError("Scenarios list is empty.")

    def reset(
        self,
        seed: Optional[int] = None
    ) -> Tuple[Optional[Dict[int, str]], Dict[int, Any]]:
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

        self.game_state["strategies"] = {0: None, 1: None}
        self.game_state["logs"] = []

        # Select a random scenario
        self.game_state["scenario"] = random.choice(self.scenarios)
        self.game_state["logs"].append(f"[GAME] Scenario: {self.game_state['scenario']}")

        # Generate initial prompts for both players
        observations = {
            0: self._generate_player_prompt(player_id=0),
            1: self._generate_player_prompt(player_id=1),
        }

        info = {
            "scenario": self.game_state["scenario"],
        }

        self.game_state["logs"].append("[GAME] New game started.")

        return observations, info

    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the initial prompt for a player based on the scenario.

        Args:
            player_id (int): The player's ID (0 or 1).

        Returns:
            str: The initial prompt for the player.
        """
        prompt = (
            f"You are Player {player_id} in the Scenario Planning game.\n"
            f"Scenario: {self.game_state['scenario']}\n"
            "Your goal is to propose a strategy for survival in this scenario.\n"
            "After both players submit their strategies, a panel of judges will evaluate them.\n"
            "On your turn, simply type your strategy."
        )
        return prompt

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[Dict[int, str]],  # observations
        Optional[Dict[int, int]],  # reward
        bool,  # truncated
        bool,  # terminated
        Dict[str, Any],  # info
    ]:
        """
        Process the player's strategy.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The strategy proposed by the player.

        Returns:
            tuple: (observations, reward, truncated, terminated, info)
        """
        terminated = False
        truncated = False
        reward = None
        info = {}
        other_player_id = 1 - player_id

        # Store the strategy
        if self.game_state["strategies"][player_id] is not None:
            # Player has already submitted a strategy
            info["reason"] = f"Player {player_id} has already submitted a strategy."
            return None, reward, truncated, terminated, info

        self.game_state["strategies"][player_id] = action
        self.game_state["logs"].append(f"[Player {player_id}] Strategy: {action}")

        observations = {player_id: action, other_player_id: action}

        # Check if both players have submitted their strategies
        if all(strategy is not None for strategy in self.game_state["strategies"].values()):
            # Conduct judging
            votes = self._evaluate_strategies()

            # Determine winner
            if votes["Player 0"] > votes["Player 1"]:
                winner_id = 0
                reward = {0: 1, 1: -1}
                info["reason"] = f"Player {winner_id} wins with a more effective strategy."
                self.game_state["logs"].append(f"[GAME] {info['reason']}")
            elif votes["Player 1"] > votes["Player 0"]:
                winner_id = 1
                reward = {0: -1, 1: 1}
                info["reason"] = f"Player {winner_id} wins with a more effective strategy."
                self.game_state["logs"].append(f"[GAME] {info['reason']}")
            else:
                # It's a tie
                reward = {0: 0, 1: 0}
                info["reason"] = "The game is a tie."
                self.game_state["logs"].append(f"[GAME] {info['reason']}")

            terminated = True

        return observations, reward, truncated, terminated, info

    def _evaluate_strategies(self) -> Dict[str, int]:
        """
        Conduct evaluation by judges based on the submitted strategies.

        Returns:
            Dict[str, int]: A dictionary with 'Player 0' and 'Player 1' as keys and their corresponding vote counts.
        """
        votes = {"Player 0": 0, "Player 1": 0}

        strategy_player0 = self.game_state["strategies"][0]
        strategy_player1 = self.game_state["strategies"][1]

        if not strategy_player0 or not strategy_player1:
            raise ValueError("Both players must submit their strategies before evaluation.")

        # Simulate judge evaluations (placeholder logic)
        for _ in range(self.num_judges):
            # Placeholder for actual evaluation logic
            # Replace the following with actual judge evaluation code or API calls
            judge_decision = random.choice(["Player 0", "Player 1"])
            votes[judge_decision] += 1

        self.game_state["logs"].append(f"[GAME] Judge Votes: {votes}")
        return votes

    def render(self):
        """
        Render the current game state.
        """
        print(f"Scenario: {self.game_state['scenario']}")
        print("Game Logs:")
        for log in self.game_state["logs"]:
            print(log)
        print("\n")
