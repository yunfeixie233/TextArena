import unittest
from parameterized import parameterized
from textarena.envs.single_player.GuessTheNumber.env import GuessTheNumberEnv

## helper functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a GuessTheNumber game.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[5]"]  # Example sequence

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["[1, 2]", "[3]", "4"]  # Invalid format

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with out-of-bounds row or column numbers.
    """
    return ["[10000]"]  # Number out of bounds

class TestGuessTheNumberEnv(unittest.TestCase):

    ## define the environment variants as class attributes
    env_variants = [
        {"hardcore": False},
        {"hardcore": True}
    ]

    ## define the test cases as class attributes
    test_cases = {
        "correct_moves": {
            "hardcore": False,
            "actions": generate_correct_move_sequence()
        },
        "invalid_format": {
            "hardcore": False,
            "actions": generate_invalid_format_sequence()
        },
        "out_of_bounds": {
            "hardcore": False,
            "actions": generate_out_of_bounds_sequence()
        }
    }

    @parameterized.expand([
        (name, details['hardcore'], details['actions'])
        for name, details in test_cases.items()
    ])
    def test_guessthenumber_outcomes(self, name, difficulty, action_sequence):
        """
        Test various outcomes of the GuessTheNumber game.
        """
        # initializat the environment based on the difficulty level
        env_config = next((env for env in self.env_variants if env['hardcore'] == difficulty), None)
        self.assertIsNotNone(env_config, f"Invalid difficulty level: {difficulty}")

        env = GuessTheNumberEnv(hardcore=env_config["hardcore"])

        observations = env.reset(seed=490)

        terminated = False
        truncated = False

        for i, action in enumerate(action_sequence):
            if terminated or truncated:
                break
            player_id = 0
            obs = observations

            ## execute the actions
            observations, reward, truncated, terminated, info = env.step(player_id, action)

            ## test different outcomes based on the test case name
            if "correct_moves" in name:
                self.assertFalse(truncated, "Game should not truncate for correct moves.")
                self.assertFalse(terminated, "Game should not terminate for correct moves.")
            elif "invalid_format" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(reward[0], -1, "Player should receive -1 reward for an invalid move format.")
            elif "out_of_bounds" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an out-of-bounds number.")
                self.assertEqual(reward[0], -1, "Player should receive -1 reward for an invalid move format.")
            else:
                self.fail(f"Unknown test case name: {name}")

    def run_unit_test():
        print("Running SudokuEnv tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)    