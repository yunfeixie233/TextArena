import unittest
from parameterized import parameterized
import warnings
from typing import Dict, List, Optional

from textarena.envs.two_player.ConnectFour.env import ConnectFourEnv

# Suppress warnings for cleaner test output
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

class TestConnectFourEnv(unittest.TestCase):
    """
    Unit test suite for the 'ConnectFourEnv' environment. This class tests various scenarios
    to ensure the environment behaves as expected under different conditions.
    """

    # Define test cases as class attributes
    test_cases = {
        "Winning Horizontal Connect": {
            "env_id": "ConnectFour-v0",
            "actions": [
                "[col 0]", "[col 0]", 
                "[col 1]", "[col 1]", 
                "[col 2]", "[col 2]", 
                "[col 3]"  # Player 0 wins horizontally
            ],
            "expected_rewards": {0: 1, 1: -1},
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Winning Vertical Connect": {
            "env_id": "ConnectFour-v0",
            "actions": [
                "[col 0]", "[col 1]", 
                "[col 0]", "[col 1]", 
                "[col 0]", "[col 1]", 
                "[col 0]"  # Player 0 wins vertically
            ],
            "expected_rewards": {0: 1, 1: -1},
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Winning Diagonal Connect": {
            "env_id": "ConnectFour-v0",
            "actions": [
                "[col 0]", "[col 1]",
                "[col 1]", "[col 2]",
                "[col 2]", "[col 3]",
                "[col 2]", "[col 3]",
                "[col 3]", "[col 2]",
                "[col 3]"  # Player 1 wins diagonally
            ],
            "expected_rewards": {0: 1, 1: -1},
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Invalid Move Format": {
            "env_id": "ConnectFour-v0",
            "actions": ["Invalid action"],
            "expected_rewards": {0: -1, 1: 0},  # Invalid action penalizes Player 0
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Column Full": {
            "env_id": "ConnectFour-v0",
            "actions": [
                "[col 0]", "[col 0]",
                "[col 0]", "[col 0]",
                "[col 0]", "[col 0]",
                "[col 0]"  # Column 0 is full after 6 moves
            ],
            "expected_rewards": {0: -1, 1: 0},  # Invalid move penalizes Player 0
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Game Draw": {
            "env_id": "ConnectFour-v0",
            "actions": [
                "[col 0]", "[col 1]", "[col 2]", "[col 3]", "[col 4]", "[col 5]", "[col 6]",
                "[col 0]", "[col 1]", "[col 2]", "[col 3]", "[col 4]", "[col 5]", "[col 6]",
                "[col 1]", "[col 2]", "[col 3]", "[col 4]", "[col 5]", "[col 6]", "[col 0]",
                "[col 0]", "[col 1]", "[col 2]", "[col 3]", "[col 4]", "[col 5]", "[col 6]",
                "[col 0]", "[col 1]", "[col 2]", "[col 3]", "[col 4]", "[col 5]", "[col 6]",
                "[col 1]", "[col 2]", "[col 3]", "[col 4]", "[col 5]", "[col 6]", "[col 0]",
                "[col 0]", "[col 1]", "[col 2]", "[col 3]", "[col 4]", "[col 5]", "[col 6]",
            ],
            "expected_rewards": {0: 0, 1: 0},  # Draw results in no reward
            "expected_truncated": False,
            "expected_terminated": True,
        },
    }

    @parameterized.expand([
        (
            name,
            details["env_id"],
            details["actions"],
            details["expected_rewards"],
            details["expected_truncated"],
            details["expected_terminated"]
        )
        for name, details in test_cases.items()
    ])
    def test_connect_four_env_outcomes(
        self,
        name: str,
        env_id: str,
        actions: List[str],
        expected_rewards: Optional[Dict[int, int]],
        expected_truncated: bool,
        expected_terminated: bool
    ):
        """
        Parameterized test method that verifies the outcomes of different game scenarios
        in the 'ConnectFourEnv' environment.

        Args:
            name (str): The name of the test case.
            env_id (str): The identifier for the environment variant to be tested.
            actions (List[str]): A list of actions to be executed in sequence.
            expected_rewards (Optional[Dict[int, int]]): The expected rewards for each player at the end
                of the game.
            expected_truncated (bool): Whether the game is expected to be truncated.
            expected_terminated (bool): Whether the game is expected to be terminated.
        """
        with self.subTest(test_case=name):
            try:
                # Initialize the environment
                env = ConnectFourEnv()
            except Exception as e:
                self.fail(f"Failed to initialize environment '{env_id}': {e}")

            try:
                # Reset the environment with a fixed seed for reproducibility
                observations = env.reset(seed=42)
            except Exception as e:
                self.fail(f"Failed to reset the environment '{env_id}': {e}")

            # Initialize game state flags
            terminated = False
            truncated = False

            for i, action in enumerate(actions):
                player_id = i % 2

                try:
                    # Execute the action in the environment
                    step_result = env.step(player_id, action)
                    if len(step_result) != 5:
                        self.fail(f"env.step() returned {len(step_result)} elements, expected 5.")
                    observations, rewards, truncated, terminated, info = step_result
                except Exception as e:
                    self.fail(f"env.step() raised an unexpected exception for player {player_id}: {e}")

                if terminated or truncated:
                    break

            # Check the expected outcome
            self.assertEqual(
                rewards,
                expected_rewards,
                f"The rewards did not match. Expected {expected_rewards}; received {rewards}"
            )

            self.assertEqual(
                terminated,
                expected_terminated,
                f"Terminated flag mismatch. Expected {expected_terminated}; received {terminated}"
            )

            self.assertEqual(
                truncated,
                expected_truncated,
                f"Truncated flag mismatch. Expected {expected_truncated}; received {truncated}"
            )


# Run the tests
if __name__ == '__main__':
    unittest.main()
