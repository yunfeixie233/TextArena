import unittest
from parameterized import parameterized
from textarena.envs.single_player.Minesweeper.env import MinesweeperEnv

## Helper Functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a Minesweeper puzzle.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[reveal 3 3]", "[flag 0 0]"]  # Example sequence

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with an invalid move.
    """
    return ["[reveal 100 100]"]  # Invalid move

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["(reveal 3 3)", "reveal 3 3"]  # Invalid format

class TestMinesweeperEnv(unittest.TestCase):
    """
    Test class for the Minesweeper environment.
    """
    env_variants = [
        {"difficulty": "easy"},
        {"difficulty": "medium"},
        {"difficulty": "hard"}
    ]

    test_cases = {
        "correct_move": {
            "difficulty": "easy",
            "actions": generate_correct_move_sequence()
        },
        "out_of_bounds": {
            "difficulty": "medium",
            "actions": generate_out_of_bounds_sequence()
        },
        "invalid_format": {
            "difficulty": "hard",
            "actions": generate_invalid_format_sequence()
        }
    }

    @parameterized.expand([
        (name, details['difficulty'], details['actions'])
        for name, details in test_cases.items()
    ])
    def test_minesweeper_env(self, name, difficulty, actions):
        """
        Test method for the Minesweeper environment.
        """
        env_config = next((env for env in self.env_variants if env["difficulty"] == difficulty), None)
        self.assertIsNotNone(env_config, f"Invalid difficulty level: {difficulty}")

        env = MinesweeperEnv(difficulty=env_config["difficulty"])

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

            ## test different outcomes
            if name == "correct_move":
                self.assertFalse(truncated, "Game should not be truncated")
                self.assertFalse(terminated, "Game should not be terminated")
            elif "out_of_bounds" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an out-of-bounds move.")
                self.assertEqual(rewards[0], -1, "Player should receive -1 for out-of-bounds move.")
            elif "invalid_format" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(rewards[0], -1, "Player should receive -1 reward for an invalid move format.")
            else:
                self.fail(f"Unknown test case name: {name}")
    
    def run_unit_test():
        print("Running CrosswordsEnv tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
