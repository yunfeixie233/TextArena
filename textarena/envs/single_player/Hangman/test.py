import unittest
from parameterized import parameterized
from textarena.envs.single_player.Hangman.env import HangmanEnv

## helper functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a Hangman game.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[t]", "[h]", "[o]"]  # Example sequence

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["[1]", "[2]", "[L L]", "[LL]"]  # Invalid format

class TestHangmanEnv(unittest.TestCase):

    ## define environment variants as class attributes
    env_variants = [
        {"hardcore": False},
        {"hardcore": True}
    ]

    ## define test cases as class attributes
    test_cases = {
        "correct_moves": {
            "hardcore": False,
            "actions": generate_correct_move_sequence()
        },
        "invalid_format": {
            "hardcore": False,
            "actions": generate_invalid_format_sequence()
        }
    }

    @parameterized.expand([
        (name, details['hardcore'], details['actions'])
        for name, details in test_cases.items()
    ])
    def test_hangman_outcomes(self, name, hardcore, actions):
        ## initialize the environment based on the hardcore level
        env_config = next((env for env in self.env_variants if env['hardcore'] == hardcore), None)
        self.assertIsNotNone(env_config, f"Invalid hardcore level: {hardcore}")

        env = HangmanEnv(hardcore=env_config["hardcore"])

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
            if "correct_moves" in name:
                self.assertFalse(truncated, "Game should not truncate for correct moves.")
                self.assertFalse(terminated, "Game should not terminate for correct moves.")
            elif "invalid_format" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(reward[0], -1, "Player should receive -1 for out-of-bounds move.")
            else:
                self.fail(f"Invalid test case name: {name}")

    def run_unit_test():
        print("Running unit tests for HangmanEnv...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)