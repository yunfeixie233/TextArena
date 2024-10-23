import unittest
from parameterized import parameterized
from textarena.envs.single_player.sudoku.env import SudokuEnv  # Make sure the SudokuEnv class is imported correctly

# Helper Functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a Sudoku puzzle.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[6 4 4]", "[7 3 3]"]  # Example sequence

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["row 3 col 2 4"]  # Invalid format

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with out-of-bounds row or column numbers.
    """
    return ["[10 3 5]"]  # Row number out of bounds

def generate_overwrite_pre_filled_sequence():
    """
    Generates an action sequence where a player attempts to overwrite a pre-filled cell.
    """
    return ["[2 1 7]"]  # Assuming (1, 1) was pre-filled

def generate_invalid_move_sequence():
    """
    Generates an action sequence where the move violates Sudoku rules (duplicate in row/column/subgrid).
    """
    return ["[7 3 9]", "[1 2 5]"]  # Duplicate number in the same row

class TestSudokuEnv(unittest.TestCase):

    # Define environment variants as class attributes
    env_variants = [
        {"difficulty": "easy", "max_turns": 5},
        {"difficulty": "medium", "max_turns": 10},
        {"difficulty": "hard", "max_turns": 15},
    ]
    
    # Define test cases as class attributes
    test_cases = {
        "correct_move_easy": {
            "difficulty": "easy",
            "actions": generate_correct_move_sequence()
        },
        "invalid_format_easy": {
            "difficulty": "easy",
            "actions": generate_invalid_format_sequence()
        },
        "out_of_bounds_easy": {
            "difficulty": "easy",
            "actions": generate_out_of_bounds_sequence()
        },
        "overwrite_pre_filled_easy": {
            "difficulty": "easy",
            "actions": generate_overwrite_pre_filled_sequence()
        },
        "invalid_move_easy": {
            "difficulty": "easy",
            "actions": generate_invalid_move_sequence()
        },
    }
    
    @parameterized.expand([
        (name, details["difficulty"], details["actions"])
        for name, details in test_cases.items()
    ])
    def test_sudoku_outcomes(self, name, difficulty, action_sequence):
        """
        Test various Sudoku outcomes using predefined action sequences across different difficulty levels.
        
        Args:
            name (str): Test case name.
            difficulty (str): Difficulty level of the Sudoku environment.
            action_sequence (List[str]): List of action strings to execute.
        """
        # Initialize the environment based on the difficulty level
        env_config = next((env for env in self.env_variants if env["difficulty"] == difficulty), None)
        self.assertIsNotNone(env_config, f"Environment config for {difficulty} not found.")
        
        env = SudokuEnv(difficulty=env_config["difficulty"], max_turns=env_config["max_turns"])

        observations = env.reset(seed=490)
        
        terminated = False
        truncated = False

        for i, action in enumerate(action_sequence):
            if terminated or truncated:
                break
            player_id = 0  # Single-player game, player ID is always 0
            obs = observations
            
            # Execute the action
            observations, reward, truncated, terminated, info = env.step(player_id, action)
            
            # Test different outcomes based on the test case name
            if "correct_move" in name:
                self.assertFalse(truncated, "Game should not truncate for correct moves.")
                self.assertFalse(terminated, "Game should not terminate until the puzzle is complete.")
            elif "invalid_format" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(reward[0], -1, "Player should receive -1 reward for an invalid move format.")
            elif "out_of_bounds" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an out-of-bounds move.")
                self.assertEqual(reward[0], -1, "Player should receive -1 for out-of-bounds move.")
            elif "overwrite_pre_filled" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to overwriting a pre-filled cell.")
                self.assertEqual(reward[0], -1, "Player should receive -1 for overwriting a pre-filled cell.")
            elif "invalid_move" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move.")
                self.assertEqual(reward[0], -1, "Player should receive -1 for violating Sudoku rules.")
            else:
                self.fail(f"Unknown test case name: {name}")

def run_unit_test():
    print("Running SudokuEnv tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
