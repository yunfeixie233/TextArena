import unittest
from parameterized import parameterized
from textarena.envs.single_player.TowerOfHanoi.env import TowerOfHanoiEnv

# Helper Functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a Tower of Hanoi puzzle.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[A B]", "[A C]"] # Example sequence

def generate_invalid_move_sequence():
    """
    Generates an action sequence where a player attempts to place a larger disk on top of a smaller disk.
    """
    return ["[B A]", "[C A]", "[A A]", "[B C]"] # Invalid move

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with out-of-bounds rod indices.
    """
    return ["[A D]"] # Rod index out of bounds

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["A B", "(A C)", "[A, C]"] # Invalid format

class TestTowerOfHanoiEnv(unittest.TestCase):

    # define environment variants as class attributes
    env_variants = [
        {"difficulty": "easy"},
        {"difficulty": "medium"},
        {"difficulty": "hard"}
    ]

    # define test cases as class attributes
    test_cases = {
        "correct_move_easy": {
            "difficulty": "easy",
            "actions": generate_correct_move_sequence()
        },
        "invalid_move_easy": {
            "difficulty": "easy",
            "actions": generate_invalid_move_sequence()
        },
        "out_of_bounds_easy": {
            "difficulty": "easy",
            "actions": generate_out_of_bounds_sequence()
        },
        "invalid_format_easy": {
            "difficulty": "easy",
            "actions": generate_invalid_format_sequence()
        }
    }

    @parameterized.expand([
        (name, details['difficulty'], details['actions'])
        for name, details in test_cases.items()
    ])
    def test_towerofhanoi_outcomes(self, name, difficulty, actions):
        # initialize the environment
        env_config = next((env for env in self.env_variants if env['difficulty'] == difficulty), None)
        self.assertIsNotNone(env_config, f"Invalid difficulty level: {difficulty}")

        env = TowerOfHanoiEnv(difficulty=env_config['difficulty'])

        observations = env.reset(seed=490)

        terminated = False
        truncated = False

        for i, action in enumerate(actions):
            if terminated or truncated:
                break
            player_id = 0
            obs = observations

            ## execute the actions
            observations, rewards, truncated, terminated, info = env.step(player_id, action)

            if "correct_move" in name:
                self.assertFalse(truncated, "Game should not truncate for correct moves.")
                self.assertFalse(terminated, "Game should not terminate until the puzzle is complete.")
            elif "invalid_move" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(rewards[0], -1, "Player should receive -1 reward for an invalid move format.")
            elif "out_of_bounds" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an out-of-bounds move.")
                self.assertEqual(rewards[0], -1, "Player should receive -1 for out-of-bounds move.")
            elif "invalid_format" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move.")
                self.assertEqual(rewards[0], -1, "Player should receive -1 for violating Sudoku rules.")
            else:
                self.fail(f"Unknown test case name: {name}")

    def run_unit_test():
        print("Running CrosswordsEnv tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)

