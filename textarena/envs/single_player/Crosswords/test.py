import unittest
from parameterized import parameterized
from textarena.envs.single_player.Crosswords.env import CrosswordsEnv

# Helper Functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a Crosswords puzzle.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[7 2 C]"]  # Example sequence

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["row 2 col 8 D"]  # Invalid format

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with out-of-bounds row or column numbers.
    """
    return ["[130 3 R], [6 111 J]"]  # Row number out of bounds

def generate_invalid_move_sequence():
    """
    Generates an action sequence where a player attempts to overwrite a pre-filled cell.
    """
    return ["[2 2 R]"]  # (2 2) is not a valid "_" cell, it's "." cell

class TestCrosswordsEnv(unittest.TestCase):

    # define environment variants as class attributes
    env_variants = [
        {"hardcore": False, "max_turns": 10, "num_words": 5},
        {"hardcore": True, "max_turns": 10, "num_words": 5}
    ]

    # define test cases as class attributes
    test_cases = {
        "correct_move_easy": {
            "hardcore": False,
            "actions": generate_correct_move_sequence()
        },
        "invalid_format_easy": {
            "hardcore": False,
            "actions": generate_invalid_format_sequence()
        },
        "out_of_bounds_easy": {
            "hardcore": False,
            "actions": generate_out_of_bounds_sequence()
        },
        "invalid_move_easy": {
            "hardcore": False,
            "actions": generate_invalid_move_sequence()
        }
    }

    @parameterized.expand([
        (name, details['hardcore'], details['actions'])
        for name, details in test_cases.items()
    ])
    def test_crosswords_outcomes(self, name, hardcore, actions):
        # Initialize the environment based on the hardcore level
        env_config = next((env for env in self.env_variants if env['hardcore'] == hardcore), None)
        self.assertIsNotNone(env_config, f"Invalid hardcore level: {hardcore}")

        env = CrosswordsEnv(hardcore=env_config['hardcore'], max_turns=env_config['max_turns'], num_words=env_config['num_words'])

        observations = env.reset(seed=490)

        terminated = False
        truncated = False
        
        for i, action in enumerate(actions):
            if terminated or truncated:
                break
            player_id = 0
            obs = observations

            ## execute the actions
            observations, reward, truncated, terminated, info = env.step(player_id, action)

            ## test different outcomes based on the test case name
            if "correct_move" in name:
                self.assertFalse(truncated, "Game should not truncate for correct moves.")
                self.assertFalse(terminated, "Game should not terminate until the puzzle is complete.")
            elif "invalid_format" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(reward[0], -1, "Player should receive -1 reward for an invalid move format.")
            elif "out_of_bounds" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an out-of-bounds move.")
                self.assertEqual(reward[0], -1, "Player should receive -1 for out-of-bounds move.")
            elif "invalid_move" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move.")
                self.assertEqual(reward[0], -1, "Player should receive -1 for violating Sudoku rules.")
            else:
                self.fail(f"Unknown test case name: {name}")

    def run_unit_test():
        print("Running CrosswordsEnv tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)