import unittest
from parameterized import parameterized
from unittest.mock import patch
from textarena.envs.two_player.ScenarioPlanning.env import ScenarioPlanningEnv


# Helper Functions
def generate_strategy_sequence(strategy_player_0, strategy_player_1):
    """
    Generates a sequence of (player_id, strategy) tuples representing the debate turns.

    Args:
        strategy_player_0 (List[str]): List of strategies from Player 0.
        strategy_player_1 (List[str]): List of strategies from Player 1.

    Returns:
        List[Tuple[int, str]]: List of (player_id, strategy) tuples.
    """
    actions = []
    for strat0, strat1 in zip(strategy_player_0, strategy_player_1):
        actions.append((0, strat0))
        actions.append((1, strat1))
    return actions


class TestScenarioPlanningEnv(unittest.TestCase):

    # Define test cases as class attributes
    test_cases = {
        "player0_wins": {
            "num_judges": 11,
            "pre_evaluation_votes": {"Player 0": 5, "Player 1": 6},
            "post_evaluation_votes": {"Player 0": 7, "Player 1": 4},
            "expected_winner": "Player 0",
            "strategies_player_0": ["Strategy A1", "Strategy A2"],
            "strategies_player_1": ["Strategy B1", "Strategy B2"],
        },
        "player1_wins": {
            "num_judges": 11,
            "pre_evaluation_votes": {"Player 0": 6, "Player 1": 5},
            "post_evaluation_votes": {"Player 0": 5, "Player 1": 6},
            "expected_winner": "Player 1",
            "strategies_player_0": ["Strategy A1", "Strategy A2"],
            "strategies_player_1": ["Strategy B1", "Strategy B2"],
        },
        "tie_game": {
            "num_judges": 11,
            "pre_evaluation_votes": {"Player 0": 5, "Player 1": 6},
            "post_evaluation_votes": {"Player 0": 5, "Player 1": 6},
            "expected_winner": None,
            "strategies_player_0": ["Strategy A1", "Strategy A2"],
            "strategies_player_1": ["Strategy B1", "Strategy B2"],
        },
        # Add more test cases as needed
    }

    @parameterized.expand([
        (name, details)
        for name, details in test_cases.items()
    ])
    @patch('textarena.game_makers.GPTJudgeVote.evaluate')
    def test_scenario_planning_outcomes(self, name, details, mock_evaluate):
        """
        Test various Scenario Planning outcomes using predefined strategy sequences and mocked judge evaluations.

        Args:
            name (str): Test case name.
            details (dict): Test case details.
            mock_evaluate (Mock): Mocked judge evaluate function.
        """
        # Set up the mocked evaluate function
        def side_effect(context):
            if "Player 0's Strategy" in context and "Player 1's Strategy" in context:
                # Post-debate evaluation
                return details["post_evaluation_votes"]
            else:
                # Pre-debate evaluation (if applicable)
                return details["pre_evaluation_votes"]

        mock_evaluate.side_effect = side_effect

        # Initialize the environment
        env = ScenarioPlanningEnv(
            num_judges=details["num_judges"],
            scenarios_path=None,  # Assuming default scenarios are loaded
        )
        observations, info = env.reset(seed=42)

        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}

        # Generate action sequence
        actions = generate_strategy_sequence(
            details["strategies_player_0"],
            details["strategies_player_1"]
        )

        for player_id, strategy in actions:
            if terminated or truncated:
                break
            # Execute the strategy
            observations, reward, truncated, terminated, info = env.step(player_id, strategy)

            # Update rewards
            if reward:
                rewards.update(reward)

        # Determine the expected outcome
        if details["expected_winner"]:
            winner_player_num = 0 if details["expected_winner"] == "Player 0" else 1
            self.assertTrue(terminated, "Game should have terminated after both strategies were submitted.")
            self.assertEqual(rewards[winner_player_num], 1, f"Player {winner_player_num} should have received +1 for winning.")
            loser_player_num = 1 - winner_player_num
            self.assertEqual(rewards[loser_player_num], -1, f"Player {loser_player_num} should have received -1 for losing.")
        else:
            # It's a tie
            self.assertTrue(terminated, "Game should have terminated after both strategies were submitted.")
            self.assertEqual(rewards[0], 0, "Player 0 should have received 0 reward for a tie.")
            self.assertEqual(rewards[1], 0, "Player 1 should have received 0 reward for a tie.")


def run_unit_test():
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
