""" Scenario Planning Game Environment """

import json
import os
import random
from typing import Any, Dict, Optional, Tuple

import textarena as ta
from textarena import utils


class ScenarioPlanningEnv(ta.Env):
    """
    Environment for the Scenario Planning Game.
    """

    def __init__(
        self,
        num_judges: Optional[int] = 11,
        judge_class: ta.JudgeVote = ta.game_makers.GPTJudgeVote,
        scenarios_path: Optional[str] = None,
    ):
        """
        Initialize the Scenario Planning game environment.

        Args:
            num_judges (int): Number of judges evaluating the strategies.
            judge_class (ta.JudgeVote): The judge evaluation class.
            scenarios_path (str): Path to the JSON file containing scenarios.
        """
        self.environment_name = "Scenario Planning"

        # Load scenarios
        self._load_scenarios(scenarios_path)

        # Initialize judges
        self.judge = judge_class(
            num_judges=num_judges,
            options=["Player 0", "Player 1"]
        )

        # Initialize game state variables
        self.state = ta.State(
            num_players=2,
            max_turns=None,
            render_keys=["scenario"]
        )

    def _load_scenarios(self, scenarios_path: Optional[str]):
        """
        Load scenarios from the JSON file.

        Args:
            scenarios_path (str): Path to the JSON file containing scenarios.
        """
        if scenarios_path is None:
            scenarios_path = os.path.join(
                "textarena",
                "envs",
                "two_player",
                "ScenarioPlanning",
                "scenarios.json",
            )

        if not os.path.exists(scenarios_path):
            raise FileNotFoundError(f"Scenarios file not found at {scenarios_path}")

        with open(scenarios_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "scenarios" not in data or not isinstance(data["scenarios"], list):
            raise ValueError(
                "Invalid format for scenarios JSON. Expected a key 'scenarios' with a list of scenarios."
            )

        self.scenarios = data["scenarios"]
        if not self.scenarios:
            raise ValueError("Scenarios list is empty.")

    def reset(
        self, seed: Optional[int] = None
    ) -> Tuple[Optional[Dict[int, str]], Dict[int, Any]]:
        """
        Reset the Scenario Planning game to its initial state.

        Args:
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.

        Returns:
            Tuple[Dict[int, str], Dict[int, Any]]: Initial prompts for both players and additional info.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        # Select a random scenario
        self.selected_scenario = random.choice(self.scenarios)



        # reset game state 
        return self.state.reset(
            game_state={
                "strategies": {0: None, 1: None},
                "scenario": self.selected_scenario
            },
            player_prompt_function=self._generate_player_prompt
        )

    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the initial prompt for a player based on the scenario.

        Args:
            player_id (int): The player's ID (0 or 1).
            scenario (str): The survival scenario.

        Returns:
            ta.Message: The initial prompt for the player.
        """
        prompt = (
            f"You are Player {player_id} in the Scenario Planning game.\n"
            f"Scenario: {self.selected_scenario}\n"
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
        Optional[ta.Observations], # Observations: Dict[int, Tuple[int, str]]
        Optional[ta.Rewards], # Rewards: Dict[int, int]
        bool, # Truncated
        bool, # Terminated
        ta.Info, # Info: Optional[Dict[str, Any]]
    ]:
        """
        Process the player's strategy.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The strategy proposed by the player.

        Returns:
            tuple: (observations, rewards, truncated, terminated, info)
        """
        # check the player_id and action fromat
        self.state.check_action_format(
            action=action,
            player_id=player_id
        )

        # update the log
        self.state.add_log(
            from_id=player_id,
            message=action
        )
        
        
        # Store the strategy
        self.state.game_state["strategies"][player_id] = action


        # check if both players have submitted their strategies
        if all(
            strategy is not None for strategy in self.state.game_state["strategies"].values()
        ):
            # Conduct judging
            votes = self._evaluate_strategies()

            # check for draw firs
            if votes["Player 0"] == votes["Player 1"]:
                self.state.set_draw(reson="An equal number of judges voted for each option.")
            else:
                # get winner id
                winner_id = 0 if votes["Player 0"] > votes["Player 1"] else 1
                self.state.set_winners(
                    player_ids=[winner_id],
                    reason=f"Player {winner_id} wins by convincing the judges."
                )
            
        return self.state.step()


    def _evaluate_strategies(self) -> Dict[str, int]:
        """
        Conduct evaluation by judges based on the submitted strategies.

        Returns:
            Dict[str, int]: A dictionary with 'Player 0' and 'Player 1' as keys and their corresponding vote counts.
        """
        prompt = (
            f"Scenario: {self.state.game_state['scenario']}\n\n"
            f"Player 0's Strategy:\n{self.state.game_state['strategies'][0]}\n\n"
            f"Player 1's Strategy:\n{self.state.game_state['strategies'][1]}\n\n"
            f"Based on the above strategies, which player's strategy is more effective and feasible for survival?\n"
            f"Vote for 'Player 0' or 'Player 1'. Provide only the player you vote for."
        )

        votes = self.judge.evaluate(
            context=prompt
        )
        return votes

    def render(self):
        """
        Render the current game state.
        """
        print(f"Scenario: {self.state.game_state['scenario']}")
        print("Game Logs:")
        for sender_id, message in self.state.logs:
            if sender_id == ta.GAME_ID:
                print(f"[GAME]: {message}")
            else:
                print(f"[Player {sender_id}]: {message}")
        print("\n")
