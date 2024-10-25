import unittest
from parameterized import parameterized
from textarena.envs.single_player.WordSearch.env import WordSearchEnv

## helper functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a Hangman game.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[8 2 8 12] [3 9 8 9]", "[3 9 8 9]"]  # Words are 'observation' and 'profit'

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["[start_row 8 start_col 2 end_row 8 end_col 12]"]  # Invalid format

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with out-of-bounds coordinates.
    """
    return ["[8 2 200 12]"]  # Out of bounds

class TestWordSearchEnv(unittest.TestCase):

    # Define environment variants as class attributes
    env_variants = [
        {"hardcore": False},
        {"hardcore": True},
    ]
    
    # Define test cases as class attributes
    test_cases = {
        "correct_move_basic": {
            "hardcore": False,
            "actions": generate_correct_move_sequence()
        },
        "invalid_format_basic": {
            "hardcore": False,
            "actions": generate_invalid_format_sequence()
        },
        "out_of_bounds_basic": {
            "hardcore": False,
            "actions": generate_out_of_bounds_sequence()
        },
    }

    @parameterized.expand([
        (name, details["hardcore"], details["actions"]) 
        for name, details in test_cases.items()
    ])
    def test_single_player_word_search(self, name, hardcore, action_sequence):
        """
        Test the WordSearch environment with a specific test case.
        """
        # Initialize the environment
        env_config = next((env for env in self.env_variants if env["hardcore"] == hardcore), None)
        self.assertIsNotNone(env_config, f"Environment configuration not found for hardcore={hardcore}")

        env = WordSearchEnv(hardcore=env_config["hardcore"])

        observations = env.reset(seed=490)

        terminated = False
        truncated = False

        for i, action in enumerate(action_sequence):
            if terminated or truncated:
                break
            player_id = 0
            
            observations, reward, truncated, terminated, info = env.step(player_id, action)

            if "correct_move" in name:
                self.assertFalse(truncated, "Game should not truncate for correct moves.")
                self.assertFalse(terminated, "Game should not terminate until the puzzle is complete.")
            elif "invalid_format" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(reward[0], -1, "Player should receive -1 reward for an invalid move format.")
            elif "out_of_bounds" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an out-of-bounds move.")
                self.assertEqual(reward[0], -1, "Player should receive -1 for out-of-bounds move.")
            else:
                self.fail(f"Unknown test case name: {name}")

def run_unit_test():
    print("Running WordSearch tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)