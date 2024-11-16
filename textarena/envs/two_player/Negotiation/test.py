from textarena.envs.two_player.Negotiation.env import NegotiationEnv

import warnings
import unittest
from parameterized import parameterized
from typing import Dict, List, Optional


# Suppress specific warnings to keep test output clean
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


class TestNegotiationEnv(unittest.TestCase):
    """
    Unit test suite for the 'NegotiationEnv' environment. This class tests various scenarios
    to ensure the environment behaves as expected under different conditions.
    """

    # Define environment variants as class attributes (if needed for future expansions)
    env_variants = [
        "Negotiation-v0",
        "Negotiation-v0-hardcore",
        "Negotiation-v0-unlimited"
    ]

    # Define test cases as class attributes
    test_cases = {
        "No Trades": {
            "env_id": "Negotiation-v0",
            "actions": [" "]*19,
            "expected_rewards": None,
            "expected_truncated": False,
            "expected_terminated": False,
        },
        "No Trades, Turn-Limit": {
            "env_id": "Negotiation-v0",
            "actions": [" "] * 20,
            "expected_rewards": {0: 0, 1: 0},  # Draw
            "expected_truncated": False,
            "expected_terminated": True,  # Game terminates after max turns
        },
        "Single Trade Offer Accepted with Valid Resources": {
            "env_id": "Negotiation-v0",
            "actions": [
                "[Offer: 1 Wheat -> 3 Wheat]", "[Accept]",
            ] + [" "]*18,
            "expected_rewards": {0: 1, 1: -1},  # Assuming gain in value
            "expected_truncated": False, 
            "expected_terminated": True,
        },
        "Multiple Trade Offers Accepted": {
            "env_id": "Negotiation-v0",
            "actions": [" "] * 2 + [
                "[Offer: 1 Wheat -> 5 Wood]", "[Accept]",
            ] + [" "] * 2 + [
                "[Offer: 2 Sheep -> 3 Ore]", "[Accept]",
            ] + [" "]* 12,
            "expected_rewards": {0: 1, 1: -1},  # Assuming gain in value
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Trade Offer with Insufficient Proposer Resources": {
            "env_id": "Negotiation-v0",
            "actions": [
                "[Offer: 999 Wheat -> 1 Wood]", "[Accept]",
            ],
            "expected_rewards": {0: -1, 1: 0},  # invalid move
            "expected_truncated": False,
            "expected_terminated": True,  # Game terminates early due to invalid move
        },
        "Trade Offer with Insufficient Acceptor Resources": {
            "env_id": "Negotiation-v0",
            "actions": [
                "[Offer: 1 Wheat -> 999 Wood]", "[Accept]",
            ],  
            "expected_rewards": {0: 0, 1: -1},  # Acceptor invalid move
            "expected_truncated": False,
            "expected_terminated": True,  # Game terminates early due to invalid move
        },
        "Trade Offer Denied by Acceptor": {
            "env_id": "Negotiation-v0",
            "actions": [
                "[Offer: 1 Wheat -> 2 Wheat]", "[Deny]",
            ]+[" "]*18,  # Player 0 offers, Player 1 denies, rest do nothing
            "expected_rewards": {0: 0, 1: 0},  # No change since offer was denied
            "expected_truncated": False,
            "expected_terminated": True,  # Game terminates after the trade cycle
        },
        "Multiple Trades with Mixed Outcomes": {
            "env_id": "Negotiation-v0",
            "actions": [
                "[Offer: 2 Wheat -> 1 Wheat]", "[Accept]",
                "[Offer: 3 Sheep -> 2 Ore]", "[Deny]",
                "[Offer: 2 Brick -> 1 Brick]", "[Accept]",
            ] + [" "]*14,
            "expected_rewards": {0: -1, 1: 1},  # Two successful trades
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Two trades with same outcome": {
            "env_id": "Negotiation-v0",
            "actions": [
                "[Offer: 2 Wheat -> 1 Ore]", "[Accept]",
                "Nice", "[Offer: 2 Wheat -> 1 Ore]",
                "[Accept]", "Nice"
            ] + [" "]*14,
            "expected_rewards": {0: 0, 1: 0},  # Draw no gain on either side
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Trade Offer with Invalid Format": {
            "env_id": "Negotiation-v0",
            "actions": [
                "[Offer: blabla -> Invalid Trade Format]", " ",
                " ", " ", " ", " ", " "  # Early termination expected
            ],  # Player 0 makes an invalid offer, Player 1 does nothing
            "expected_rewards": {0: -1, 1: 0},  # Proposer penalized for invalid format
            "expected_truncated": False,
            "expected_terminated": True,  # Game terminates early due to invalid move
        },
        "Trade Cycle Test": {
            "env_id": "Negotiation-v0",
            "actions": [
                "[Offer: 2 Wheat -> 1 Wood]", "[Accept]",
                "[Offer: 1 Wood -> 2 Sheep]", "[Accept]",
                "[Offer: 2 Sheep -> 2 Ore]", "[Accept]",
                "[Offer: 2 Ore -> 2 Wheat]", "[Accept]",
                " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "
            ],  # Player 0 initiates a cycle of trades, Player 1 accepts all
            "expected_rewards": {0: 0, 1: 0},  # no change in total value
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
    def test_negotiation_env_outcomes(
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
        in the 'NegotiationEnv' environment.

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
                env = NegotiationEnv(
                    max_turns=20
                )
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
