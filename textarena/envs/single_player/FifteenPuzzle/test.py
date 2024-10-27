import unittest
from parameterized import parameterized
from textarena.envs.single_player.FifteenPuzzle.env import FifteenPuzzleEnv

## Helper functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a FifteenPuzzle puzzle.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[down]", "[right]"]  # Example sequence

def generate_invalid_move_sequence():
    """
    Generates an action sequence with an invalid move.
    """
    return ["[up]"]  # Invalid move

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["(down)", "down"]  # Invalid format

class TestFifteenPuzzleEnv(unittest.TestCase):

    test_cases = {
        "correct_move": {
            "actions": generate_correct_move_sequence()
        },
        "invalid_move": {
            "actions": generate_invalid_move_sequence()
        },
        "invalid_format": {
            "actions": generate_invalid_format_sequence()
        }
    }

    @parameterized.expand([
        (name, details["actions"])
        for name, details in test_cases.items()
    ])
    def test_fifteenpuzzle_outcomes(self, name, action_sequence):
        """
        Test the outcomes of a FifteenPuzzle environment with different action sequences.
        """
        ## Initialize the environment
        env = FifteenPuzzleEnv()

        _ = env.reset(seed=490)

        terminated = False
        truncated = False

        for i, action in enumerate(action_sequence):
            if terminated or truncated:
                break
            player_id = 0

            ## execute the action sequence
            observations, reward, truncated, terminated, info = env.step(player_id, action)

            ## test different outcomes based on the test case name
            if "correct_move" in name:
                self.assertFalse(terminated, f"Test case {name}: The game terminated unexpectedly.")
                self.assertFalse(truncated, f"Test case {name}: The game was truncated unexpectedly.")
            elif "invalid_move" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(reward[0], -1, "Player should receive -1 reward for an invalid move format.")
            elif "invalid_format" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(reward[0], -1, "Player should receive -1 reward for an invalid move format.")
            else:
                self.fail(f"Unknown test case name: {name}")

def run_unit_test():
    print("Running SudokuEnv tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)