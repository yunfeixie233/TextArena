import unittest
from parameterized import parameterized
from textarena.envs.two_player.Debate.env import DebateEnv
from unittest.mock import patch

# Helper Functions
def generate_debate_sequence(arguments_player_0, arguments_player_1):
    """
    Generates a sequence of arguments from both players.

    Args:
        arguments_player_0 (List[str]): List of arguments from Player 0.
        arguments_player_1 (List[str]): List of arguments from Player 1.

    Returns:
        List[Tuple[int, str]]: List of (player_id, action) tuples.
    """
    actions = []
    for arg0, arg1 in zip(arguments_player_0, arguments_player_1):
        actions.append((0, arg0))
        actions.append((1, arg1))
    return actions

class TestDebateEnv(unittest.TestCase):

    # Define test cases as class attributes
    test_cases = {
        "affirmative_wins": {
            "max_turns": 4,
            "num_judges": 11,
            "pre_debate_votes": {"Affirmative": 5, "Negative": 6},
            "post_debate_votes": {"Affirmative": 7, "Negative": 4},
            "expected_winner": "Affirmative",
            "arguments_player_0": ["Affirmative argument 1", "Affirmative argument 2"],
            "arguments_player_1": ["Negative argument 1", "Negative argument 2"],
        },
        "negative_wins": {
            "max_turns": 4,
            "num_judges": 11,
            "pre_debate_votes": {"Affirmative": 6, "Negative": 5},
            "post_debate_votes": {"Affirmative": 5, "Negative": 6},
            "expected_winner": "Negative",
            "arguments_player_0": ["Affirmative argument 1", "Affirmative argument 2"],
            "arguments_player_1": ["Negative argument 1", "Negative argument 2"],
        },
        "draw": {
            "max_turns": 4,
            "num_judges": 11,
            "pre_debate_votes": {"Affirmative": 5, "Negative": 6},
            "post_debate_votes": {"Affirmative": 5, "Negative": 6},
            "expected_winner": None,
            "arguments_player_0": ["Affirmative argument 1", "Affirmative argument 2"],
            "arguments_player_1": ["Negative argument 1", "Negative argument 2"],
        },
        # Add more test cases as needed
    }

    @parameterized.expand([
        (name, details)
        for name, details in test_cases.items()
    ])
    @patch('textarena.game_makers.GPTJudgeVote.evaluate')
    def test_debate_outcomes(self, name, details, mock_evaluate):
        """
        Test various Debate outcomes using predefined action sequences and mocked judge evaluations.

        Args:
            name (str): Test case name.
            details (dict): Test case details.
            mock_evaluate (Mock): Mocked judge evaluate function.
        """
        # Set up the mocked evaluate function
        def side_effect(context):
            if "No debate has occurred yet" in context:
                return details["pre_debate_votes"]
            else:
                return details["post_debate_votes"]
        mock_evaluate.side_effect = side_effect

        # Initialize the environment
        env = DebateEnv(
            max_turns=details["max_turns"],
            num_judges=details["num_judges"],
            topics_path=None,  # Assuming topics are not essential for this test
        )
        observations = env.reset(seed=42)

        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}

        # Determine which player is Affirmative and Negative
        sides = env.state.game_state["sides"]
        affirmative_player_id = next(pid for pid, side in sides.items() if side == "Affirmative")
        negative_player_id = 1 - affirmative_player_id

        # Generate action sequence
        actions = generate_debate_sequence(
            details["arguments_player_0"], details["arguments_player_1"]
        )

        for player_id, action in actions:
            if terminated or truncated:
                break
            # Execute the action
            observations, reward, truncated, terminated, info = env.step(player_id, action)

            # Update rewards
            if reward:
                rewards.update(reward)

        # Check the expected outcome
        if details["expected_winner"] == "Affirmative":
            winning_player_id = affirmative_player_id
            losing_player_id = negative_player_id
            self.assertEqual(rewards[winning_player_id], 1, f"Player {winning_player_id} should have received +1 for winning.")
            self.assertEqual(rewards[losing_player_id], -1, f"Player {losing_player_id} should have received -1 for losing.")
        elif details["expected_winner"] == "Negative":
            winning_player_id = negative_player_id
            losing_player_id = affirmative_player_id
            self.assertEqual(rewards[winning_player_id], 1, f"Player {winning_player_id} should have received +1 for winning.")
            self.assertEqual(rewards[losing_player_id], -1, f"Player {losing_player_id} should have received -1 for losing.")
        else:
            # It's a draw
            self.assertEqual(rewards[0], 0, "Player 0 should have received 0 reward for a draw.")
            self.assertEqual(rewards[1], 0, "Player 1 should have received 0 reward for a draw.")

def run_unit_test():
    print("Running ConnectFourEnv tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
