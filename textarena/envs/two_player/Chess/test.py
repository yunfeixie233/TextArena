import unittest
from parameterized import parameterized
import warnings
from typing import List, Dict, Optional

from textarena.envs.two_player.Chess.env import ChessEnv

# Suppress warnings for cleaner test output
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

class TestChessEnv(unittest.TestCase):
    """
    Unit test suite for the 'ChessEnv' environment. This class tests various scenarios
    to ensure the environment behaves as expected under different conditions.
    """

    # Define test cases as class attributes
    test_cases = {
        # "Valid Moves and Checkmate": {
        #     "env_id": "Chess-v0",
        #     "actions": ["[e2e4]", "[e7e5]", "[d1h5]", "[b8c6]", "[f1c4]", "[g8f6]", "[h5f7]"],  # Fool's mate
        #     "expected_rewards": {0: 1, 1: -1},  # White wins by checkmate
        #     "expected_truncated": False,
        #     "expected_terminated": True,
        # },
        # "Draw by Stalemate": {
        #     "env_id": "Chess-v0",
        #     "actions": ["[e3e5]", "[Ke2Ke7]", "[Kd3Ke6]", "[Kc4Kf5]", "[Kb4Ke4]", "[Ka5Kd5]", "[Kb5]"],  # White achieves stalemate
        #     "expected_rewards": {0: 0, 1: 0},  # Draw
        #     "expected_truncated": False,
        #     "expected_terminated": True,
        # },
        "Stalemate Example": {
    "env_id": "Chess-v0",
    "actions": [
        "[e2e3]",   # 1. e3
        "[a7a5]",   # 1... a5
        "[d1g4]",   # 2. Qg4
        "[a5a4]",   # 2... a4
        "[g4xd7+]", # 3. Qxd7+ (Check)
        "[e8xd7]",  # 3... Kxd7
        "[e1e2]",   # 4. Ke2
        "[d7d6]",   # 4... Kd6
        "[e2e3]",   # 5. Ke3
        "[d6d5]",   # 5... Kd5
        "[e3f4]",   # 6. Kf4
        "[d5c5]",   # 6... Kc5
        "[f4g5]",   # 7. Kg5
        "[c5b4]",   # 7... Kb4
        "[g5h6]",   # 8. Kh6
        "[b4a3]",   # 8... Ka3
        "[h6g7]",   # 9. Kg7
        "[a3a2]",   # 9... a2
        "[g7f8]",   # 10. Kf8
        "[a2a1=Q]", # 10... a1=Q (Promote to queen)
        "[f8g8]",   # 11. Kg8
        "[h7h6]"    # 11... h6 (Any move; White is stalemated)
    ],
    "expected_rewards": {0: 0, 1: 0},  # Adjust according to your environment
    "expected_truncated": False,
    "expected_terminated": True,
}







        # "Invalid Move Attempt": {
        #     "env_id": "Chess-v0",
        #     "actions": ["[e2e5]"],  # Invalid opening move by White
        #     "expected_rewards": {0: -1, 1: 0},  # White penalized for invalid move
        #     "expected_truncated": False,
        #     "expected_terminated": True,
        # },
        # "Invalid Move Attempt 2": {
        #     "env_id": "Chess-v0",
        #     "actions": ["No move at all"],  # no move provided
        #     "expected_rewards": {0: -1, 1: 0},  # White penalized for invalid move
        #     "expected_truncated": False,
        #     "expected_terminated": True,
        # },
        # "Exceeding Max Turns": {
        #     "env_id": "Chess-v0",
        #     "actions": ["[e2e4]", "[e7e5]", "[d2d4]", "[d7d5]", "[e4d5]", "[d8d5]"] * 5,  # 30 moves without checkmate or draw
        #     "expected_rewards": {0: 0, 1: 0},  # Draw by max turns
        #     "expected_truncated": True,
        #     "expected_terminated": False,
        # },
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
    def test_chess_env_outcomes(
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
        in the 'ChessEnv' environment.

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
                env = ChessEnv()
            except Exception as e:
                self.fail(f"Failed to initialize environment '{env_id}': {e}")

            try:
                # Reset the environment with a fixed seed for reproducibility
                env.reset(seed=42)
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
