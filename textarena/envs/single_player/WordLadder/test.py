import unittest
from parameterized import parameterized
from textarena.envs.single_player.WordLadder.env import WordLadderEnv

## Helper Functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a WordLadder puzzle.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[tain]", "[main]"]  # Example sequence

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["(sain)", "[sage]"]  # Invalid format

def generate_incorrect_move_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["[sang]", "[join]"]  # Invalid format


class TestWordLadderEnv(unittest.TestCase):

    ## Define environment variants as class attributes
    env_variants = [
        {"Hardcore": True, "word_len": 4},
    ]

    ## Define test cases as clas attributes
    test_cases = {
        "correct_move_hardcore": {
            "Hardcore": True,
            "actions": generate_correct_move_sequence()
        },
        "invalid_format_hardcore": {
            "Hardcore": True,
            "actions": generate_invalid_format_sequence()
        },
        "incorrect_move_hardcore": {
            "Hardcore": True,
            "actions": generate_incorrect_move_sequence()
        }
    }

    @parameterized.expand([
        (name, details["Hardcore"], details["actions"])
        for name, details in test_cases.items()
    ])
    def test_wordladder_outcomes(self, name, hardcore, action_sequence):
        """
        Test the outcomes of a WordLadder environment with different action sequences.
        """
        ## Initialize the environment
        env_config = next((env for env in self.env_variants if env["Hardcore"] == hardcore), None)
        self.assertIsNotNone(env_config, f"Environment configuration for {hardcore} not found.")

        env = WordLadderEnv(hardcore=env_config["Hardcore"], word_len=env_config["word_len"])

        observations = env.reset(seed=490)

        terminated = False
        truncated = False

        for i, action in enumerate(action_sequence):
            if terminated or truncated:
                break
            player_id = 0

            # execute the action sequence
            observations, reward, terminated, truncated, info = env.step(player_id, action)

            # test different outcomes based on the test case name
            if "correct_move" in name:
                self.assertFalse(truncated, "Game should not truncate for correct moves.")
                self.assertFalse(terminated, "Game should not terminate until the puzzle is complete.")
            elif "invalid_format" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(reward[0], -1, "Player should receive -1 reward for an invalid move format.")
            elif "incorrect_move" in name:
                self.assertFalse(truncated, "Game should not truncate for correct moves.")
                self.assertFalse(terminated, "Game should not terminate until the puzzle is complete.")
            else:
                self.fail(f"Unknown test case name: {name}")

def run_unit_test():
    print("Running SudokuEnv tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)