import unittest
from parameterized import parameterized
import warnings
from typing import Dict, List, Optional

from textarena.envs.two_player.LiarsDice.env import LiarsDiceEnv

# Suppress warnings for cleaner test output
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

class TestLiarsDiceEnv(unittest.TestCase):
    """
    Unit test suite for the 'LiarsDiceEnv' environment. This class tests various scenarios
    to ensure the environment behaves as expected under different conditions.
    """

    # Define test cases as class attributes
    test_cases = {
        "Valid Bids and Successful Bluff Call": {
            "env_id": "LiarsDice-v0",
            "actions": [
                "[Bid: 2, 3]", "[Bid: 3, 4]", "[Call]"
            ],
            "dice_rolls": {0: [2, 3, 5, 1, 4], 1: [4, 2, 6, 5, 1]},
            "expected_rewards": {0: 1, 1: -1},  # Player 0 wins by calling a successful bluff
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Valid Bids and Unsuccessful Bluff Call": {
            "env_id": "LiarsDice-v0",
            "actions": [
                "[Bid: 2, 3]", "[Bid: 3, 4]", "[Call]"
            ],
            "dice_rolls": {0: [4, 4, 5, 1, 4], 1: [4, 2, 6, 4, 1]},
            "expected_rewards": {0: -1, 1: 1},  # Player 0 loses by calling an unsuccessful bluff
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Invalid Bid Format": {
            "env_id": "LiarsDice-v0",
            "actions": ["Invalid action"],
            "dice_rolls": {0: [2, 3, 5, 1, 4], 1: [4, 2, 6, 5, 1]},
            "expected_rewards": {0: -1, 1: 0},  # Player 0 penalized for invalid action
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Invalid Bluff Call without Prior Bid": {
            "env_id": "LiarsDice-v0",
            "actions": ["[Call]"],
            "dice_rolls": {0: [2, 3, 5, 1, 4], 1: [4, 2, 6, 5, 1]},
            "expected_rewards": {0: -1, 1: 0},  # Invalid call penalizes Player 0
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Bids Increasing Correctly and Valid Final Call": {
            "env_id": "LiarsDice-v0",
            "actions": [
                "[Bid: 2, 2]", "[Bid: 2, 3]", "[Bid: 3, 3]", "[Call]"
            ],
            "dice_rolls": {0: [2, 3, 2, 1, 5], 1: [3, 2, 3, 4, 3]},
            "expected_rewards": {0: 1, 1: -1},  
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Incorrect Bid increase": {
            "env_id": "LiarsDice-v0",
            "actions": [
                "[Bid: 2, 2]", "[Bid: 3, 1]"
            ],
            "dice_rolls": {0: [2, 3, 2, 1, 5], 1: [3, 2, 3, 4, 3]},
            "expected_rewards": {0: 0, 1: -1},  
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Incorrect Bid increase 2": {
            "env_id": "LiarsDice-v0",
            "actions": [
                "[Bid: 2, 2]", "[Bid: 1, 3]"
            ],
            "dice_rolls": {0: [2, 3, 2, 1, 5], 1: [3, 2, 3, 4, 3]},
            "expected_rewards": {0: 0, 1: -1},  
            "expected_truncated": False,
            "expected_terminated": True,
        },
    }

    @parameterized.expand([
        (
            name,
            details["env_id"],
            details["actions"],
            details["dice_rolls"],
            details["expected_rewards"],
            details["expected_truncated"],
            details["expected_terminated"]
        )
        for name, details in test_cases.items()
    ])
    def test_liars_dice_env_outcomes(
        self,
        name: str,
        env_id: str,
        actions: List[str],
        dice_rolls: Dict[int, List[int]],
        expected_rewards: Optional[Dict[int, int]],
        expected_truncated: bool,
        expected_terminated: bool
    ):
        """
        Parameterized test method that verifies the outcomes of different game scenarios
        in the 'LiarsDiceEnv' environment.

        Args:
            name (str): The name of the test case.
            env_id (str): The identifier for the environment variant to be tested.
            actions (List[str]): A list of actions to be executed in sequence.
            dice_rolls (Dict[int, List[int]]): Predefined dice rolls for each player.
            expected_rewards (Optional[Dict[int, int]]): The expected rewards for each player at the end
                of the game.
            expected_truncated (bool): Whether the game is expected to be truncated.
            expected_terminated (bool): Whether the game is expected to be terminated.
        """
        with self.subTest(test_case=name):
            try:
                # Initialize the environment
                env = LiarsDiceEnv()
            except Exception as e:
                self.fail(f"Failed to initialize environment '{env_id}': {e}")

            try:
                # Reset the environment with a fixed seed for reproducibility
                env.reset(seed=42)
                # Set the dice rolls manually
                env.state.game_state["dice_rolls"] = dice_rolls
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
