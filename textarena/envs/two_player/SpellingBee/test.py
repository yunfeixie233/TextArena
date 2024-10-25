import unittest
from parameterized import parameterized
from unittest.mock import patch
from textarena.envs.two_player.SpellingBee.env import SpellingBeeEnv


# Helper Functions
def generate_word_submission_sequence(word_player_0: str, word_player_1: str):
    """
    Generates a sequence of (player_id, word) tuples representing the word submissions.

    Args:
        word_player_0 (str): Word submitted by Player 0.
        word_player_1 (str): Word submitted by Player 1.

    Returns:
        List[Tuple[int, str]]: List of (player_id, word) tuples.
    """
    return [
        (0, word_player_0),
        (1, word_player_1),
    ]


class TestSpellingBeeEnv(unittest.TestCase):

    # Define test cases as class attributes
    test_cases = {
        "player0_wins": {
            "num_letters": 6,
            "allowed_letters": {'a', 'e', 'l', 'm', 'p', 's'},
            "word_player_0": "[examples]",
            "word_player_1": "[lamp]",
            "expected_winner": 0,
            "expected_rewards": {0: 1, 1: -1},
            "info_reason": "Player 0 wins by submitting a longer valid word."
        },
        "player1_wins": {
            "num_letters": 6,
            "allowed_letters": {'c', 'o', 'd', 'e', 's', 't'},
            "word_player_0": "[code]",
            "word_player_1": "[codes]",
            "expected_winner": 1,
            "expected_rewards": {0: -1, 1: 1},
            "info_reason": "Player 1 wins by submitting a longer valid word."
        },
        "tie_game": {
            "num_letters": 6,
            "allowed_letters": {'b', 'o', 't', 'h', 'e', 'n'},
            "word_player_0": "[both]",
            "word_player_1": "[bone]",
            "expected_winner": None,
            "expected_rewards": {0: 0, 1: 0},
            "info_reason": "The game is a tie. Both players submitted words of equal length."
        },
        "player0_invalid_word": {
            "num_letters": 6,
            "allowed_letters": {'x', 'y', 'z', 'q', 'v', 'b'},
            "word_player_0": "[xyz]",  # Invalid word
            "word_player_1": "[vex]",
            "expected_winner": 1,
            "expected_rewards": {0: -1, 1: 1},
            "info_reason": "Player 0 provided an invalid word."
        },
        "player1_invalid_word": {
            "num_letters": 6,
            "allowed_letters": {'d', 'r', 'a', 'g', 'o', 'n'},
            "word_player_0": "[dragon]",
            "word_player_1": "[goran]",  # Invalid word
            "expected_winner": 0,
            "expected_rewards": {0: 1, 1: -1},
            "info_reason": "Player 1 provided an invalid word."
        },
        "both_players_invalid_words": {
            "num_letters": 6,
            "allowed_letters": {'k', 'j', 'q', 'z', 'x', 'v'},
            "word_player_0": "[kjxz]",  # Invalid word
            "word_player_1": "[qvz]",   # Invalid word
            "expected_winner": None,
            "expected_rewards": {0: 0, 1: 0},
            "info_reason": "The game is a tie. Both players submitted words of equal length."
        },
        "word_not_wrapped_correctly": {
            "num_letters": 6,
            "allowed_letters": {'c', 'a', 't', 's', 'e', 'r'},
            "word_player_0": "cats",        # Not wrapped in brackets
            "word_player_1": "[cater]",
            "expected_winner": 1,
            "expected_rewards": {0: -1, 1: 1},
            "info_reason": "Player 0 did not submit a word in the correct format."
        },
        "word_contains_illegal_letters": {
            "num_letters": 6,
            "allowed_letters": {'m', 'a', 't', 'h', 'e', 's'},
            "word_player_0": "[mathes]",    # Valid word assuming 'mathes' is recognized
            "word_player_1": "[mathesy]",   # Contains 'y' which is not allowed
            "expected_winner": 0,
            "expected_rewards": {0: 1, 1: -1},
            "info_reason": "Player 1 provided an invalid word."
        },
        "num_letters_exceeds_alphabet": {
            "num_letters": 27,  # Invalid, exceeds 26
            "allowed_letters": None,  # Will not be used
            "word_player_0": "[example]",
            "word_player_1": "[lamp]",
            "expected_winner": None,
            "expected_rewards": None,
            "info_reason": "ValueError expected due to num_letters exceeding 26."
        },
        # Add more test cases as needed
    }

    @parameterized.expand([
        (name, details)
        for name, details in test_cases.items()
    ])
    @patch('textarena.envs.two_player.SpellingBee.env.enchant.Dict')
    def test_spelling_bee_outcomes(self, name, details, mock_enchant_dict):
        """
        Test various Spelling Bee outcomes using predefined word submissions and mocked word validations.

        Args:
            name (str): Test case name.
            details (dict): Test case details.
            mock_enchant_dict (Mock): Mocked Enchant Dict class.
        """
        if name == "num_letters_exceeds_alphabet":
            # Test for ValueError when num_letters exceeds 26
            with self.assertRaises(ValueError):
                SpellingBeeEnv(num_letters=details["num_letters"])
            return

        # Set up the mocked enchant dictionary's check method
        def mock_check(word):
            # Define a set of valid words for testing purposes
            valid_words = {
                "examples", "lamp", "code", "codes", "both", "bone", "dragon", "cater", "mathes"
            }
            return word in valid_words

        # Configure the mock to use the mock_check function
        mock_enchant_instance = mock_enchant_dict.return_value
        mock_enchant_instance.check.side_effect = mock_check

        # Initialize the environment with specified number of letters
        env = SpellingBeeEnv(num_letters=details["num_letters"])

        # Manually set allowed_letters for controlled testing
        if details["allowed_letters"]:
            env.allowed_letters = details["allowed_letters"]
            env.state.game_state["allowed_letters"] = env.allowed_letters

        # Reset the environment with the specified seed to ensure reproducibility
        observations, info = env.reset(seed=42)

        # Simulate the game turns
        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}

        # Generate action sequence
        actions = generate_word_submission_sequence(
            details["word_player_0"],
            details["word_player_1"]
        )

        for player_id, word in actions:
            if terminated or truncated:
                break
            try:
                # Execute the action
                observations, reward, truncated, terminated, info = env.step(player_id, word)

                # Update rewards
                if reward:
                    rewards.update(reward)
            except Exception as e:
                if name == "num_letters_exceeds_alphabet":
                    self.assertIsInstance(e, ValueError)
                else:
                    self.fail(f"Unexpected exception raised: {e}")

        # Determine the expected outcome
        if details["expected_winner"] is not None:
            if details["expected_rewards"]:
                # Check rewards and info_reason
                self.assertTrue(terminated, f"Game '{name}' should have terminated after both players submitted their words.")
                self.assertEqual(rewards, details["expected_rewards"], f"Rewards mismatch for test case '{name}'.")
                self.assertEqual(info["reason"], details["info_reason"], f"Info reason mismatch for test case '{name}'.")
        else:
            if details["expected_rewards"] is None:
                # Handled above
                pass
            else:
                # It's a tie or both players invalid
                self.assertTrue(terminated, f"Game '{name}' should have terminated after both players submitted their words.")
                self.assertEqual(rewards, details["expected_rewards"], f"Rewards mismatch for test case '{name}'.")
                self.assertEqual(info["reason"], details["info_reason"], f"Info reason mismatch for test case '{name}'.")


def run_unit_test():
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
