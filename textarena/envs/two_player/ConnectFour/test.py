import unittest
from parameterized import parameterized
from textarena.envs.two_player.ConnectFour.env import ConnectFourEnv
import json

# Helper Functions
def generate_horizontal_win_sequence(winner=0, num_cols=7):
    """
    Generates an action sequence leading to a horizontal win for the specified player.
    """
    actions = []
    for col in range(3):
        actions.append(f"[col {col}]")  # Player 0
        actions.append(f"[col {col}]")  # Player 1
    actions.append(f"[col 3]")  # Player 0 wins
    return actions

def generate_vertical_win_sequence(winner=1, col=0, num_rows=6):
    """
    Generates an action sequence leading to a vertical win for the specified player.
    """
    actions = []
    for _ in range(3):
        actions.append(f"[col {col}]")  # Player 0
        actions.append(f"[col {col}]")  # Player 1
    actions.append(f"[col {col}]")  # Player 1 wins
    return actions

def generate_diagonal_win_asc_sequence(winner=0):
    """
    Generates an action sequence leading to an ascending diagonal win for the specified player.
    """
    actions = [
        "[col 0]", "[col 1]",
        "[col 1]", "[col 2]",
        "[col 2]", "[col 3]",
        "[col 2]", "[col 3]",
        "[col 3]", "[col 4]",
        "[col 3]"  # Player 0 wins
    ]
    return actions

def generate_diagonal_win_desc_sequence(winner=1):
    """
    Generates an action sequence leading to a descending diagonal win for the specified player.
    """
    actions = [
        "[col 3]", "[col 2]",
        "[col 2]", "[col 1]",
        "[col 1]", "[col 0]",
        "[col 1]", "[col 0]",
        "[col 0]", "[col 0]",
        "[col 0]"  # Player 1 wins
    ]
    return actions

def generate_draw_sequence(num_rows=6, num_cols=7):
    """
    Generates an action sequence leading to a draw.
    """
    actions = []
    for row in range(num_rows):
        for col in range(num_cols):
            actions.append(f"[col {col}]")
    return actions

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move format.
    """
    return ["col3"]  # Invalid format

def generate_out_of_bounds_sequence(num_cols=7):
    """
    Generates an action sequence with an out-of-bounds column number.
    """
    return [f"[col {num_cols}]"]  # Out-of-bounds column

def generate_full_column_sequence(winner=0, col=0, num_rows=6):
    """
    Generates an action sequence leading to an attempt to place in a full column.
    """
    actions = []
    for _ in range(num_rows):
        actions.append(f"[col {col}]")  # Player 0
        actions.append(f"[col {col}]")  # Player 1
    actions.append(f"[col {col}]")  # Player 0 attempts to place in full column
    return actions

class TestConnectFourEnv(unittest.TestCase):
    
    # Define environment variants as class attributes
    env_variants = [
        {"env_id": "ConnectFour-v0", "is_open": True, "num_rows": 6, "num_cols": 7},
        {"env_id": "ConnectFour-v0-large", "is_open": True, "num_rows": 12, "num_cols": 15},
        {"env_id": "ConnectFour-v0-blind", "is_open": False, "num_rows": 6, "num_cols": 7},
    ]
    
    # Define test cases as class attributes
    test_cases = {
        "horizontal_win_v0": {
            "env_id": "ConnectFour-v0",
            "actions": generate_horizontal_win_sequence(winner=0, num_cols=7)
        },
        "horizontal_win_large": {
            "env_id": "ConnectFour-v0-large",
            "actions": generate_horizontal_win_sequence(winner=0, num_cols=15)
        },
        "vertical_win_v0": {
            "env_id": "ConnectFour-v0",
            "actions": generate_vertical_win_sequence(winner=1, col=0, num_rows=6)
        },
        "vertical_win_large": {
            "env_id": "ConnectFour-v0-large",
            "actions": generate_vertical_win_sequence(winner=1, col=14, num_rows=12)
        },
        "diagonal_win_asc_v0": {
            "env_id": "ConnectFour-v0",
            "actions": generate_diagonal_win_asc_sequence(winner=0)
        },
        "diagonal_win_desc_v0": {
            "env_id": "ConnectFour-v0",
            "actions": generate_diagonal_win_desc_sequence(winner=1)
        },
        "draw_v0": {
            "env_id": "ConnectFour-v0",
            "actions": generate_draw_sequence(num_rows=6, num_cols=7)
        },
        "invalid_format_v0": {
            "env_id": "ConnectFour-v0",
            "actions": generate_invalid_format_sequence()
        },
        "out_of_bounds_v0": {
            "env_id": "ConnectFour-v0",
            "actions": generate_out_of_bounds_sequence(num_cols=7)
        },
        "full_column_v0": {
            "env_id": "ConnectFour-v0",
            "actions": generate_full_column_sequence(winner=0, col=0, num_rows=6)
        },
        # Add more test cases as needed
    }
    
    @parameterized.expand([
        (name, details["env_id"], details["actions"])
        for name, details in test_cases.items()
    ])
    def test_connect_four_outcomes(self, name, env_id, action_sequence):
        """
        Test various Connect Four outcomes using predefined action sequences across different environment versions.
        
        Args:
            name (str): Test case name.
            env_id (str): Environment ID to test.
            action_sequence (List[str]): List of action strings to execute.
        """
        # Initialize the environment based on env_id
        env_config = next((env for env in self.env_variants if env["env_id"] == env_id), None)
        self.assertIsNotNone(env_config, f"Environment config for {env_id} not found.")
        
        env = ConnectFourEnv(
            is_open=env_config["is_open"],
            num_rows=env_config["num_rows"],
            num_cols=env_config["num_cols"]
        )
        observations = env.reset()
        
        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}
        
        for i, action in enumerate(action_sequence):
            if terminated or truncated:
                break
            player_id = i % 2  # Player 0 and Player 1 alternate
            obs = observations[player_id]
            env_action = action
            
            # Execute the action
            observations, reward, truncated, terminated, info = env.step(player_id, env_action)
            
            # Update rewards
            if isinstance(reward, dict):
                rewards[0] += reward.get(0, 0)
                rewards[1] += reward.get(1, 0)
            else:
                # Handle if reward is not a dict
                rewards[player_id] += reward
        
        # Determine the expected outcome based on the test case name
        if "win" in name:
            if "horizontal" in name or "vertical" in name or "diagonal_win_asc" in name or "diagonal_win_desc" in name:
                # Determine which player should have won
                if "desc" in name:
                    winner = 1
                else:
                    winner = 0
                self.assertTrue(terminated or truncated, "Game should have terminated due to a win.")
                self.assertEqual(rewards[winner], 1, f"Player {winner} should have received +1 reward for winning.")
                loser = 1 - winner
                self.assertEqual(rewards[loser], -1, f"Player {loser} should have received -1 reward for losing.")
        elif "draw" in name:
            self.assertTrue(terminated or truncated, "Game should have terminated due to a draw.")
            self.assertEqual(rewards[0], 0, "Player 0 should have received 0 reward for a draw.")
            self.assertEqual(rewards[1], 0, "Player 1 should have received 0 reward for a draw.")
        elif "invalid_format" in name:
            self.assertTrue(terminated or truncated, "Game should have terminated due to an invalid move.")
            # The player making the invalid move should have -1, the other 0
            invalid_player = 0  # Assuming the invalid move is made by Player 0
            self.assertEqual(rewards[invalid_player], -1, f"Player {invalid_player} should have received -1 for invalid move.")
        elif "out_of_bounds" in name:
            self.assertTrue(terminated or truncated, "Game should have terminated due to an out-of-bounds move.")
            invalid_player = 0  # Assuming the invalid move is made by Player 0
            self.assertEqual(rewards[invalid_player], -1, f"Player {invalid_player} should have received -1 for out-of-bounds move.")
        elif "full_column" in name:
            self.assertTrue(terminated or truncated, "Game should have terminated due to attempting to place in a full column.")
            invalid_player = 1  # Assuming Player 1 made the invalid move
            self.assertEqual(rewards[invalid_player], -1, f"Player {invalid_player} should have received -1 for placing in a full column.")
        else:
            self.fail(f"Unknown test case name: {name}")

def run_unit_test():
    print("Running ConnectFourEnv tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
