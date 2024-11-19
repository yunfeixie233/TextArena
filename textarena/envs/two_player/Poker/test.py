from textarena.envs.two_player.Poker.env import PokerEnv

import warnings
import unittest
from parameterized import parameterized
from typing import Dict, List, Optional, Any
from collections import Counter


# Suppress specific warnings to keep test output clean
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


class TestPokerEnv(unittest.TestCase):
    """
    Unit test suite for the 'PokerEnv' environment. Tests various poker scenarios
    to ensure the environment behaves correctly under different conditions.
    """

    # Rest of the test cases remain the same until the hand evaluation test
    test_cases = {
        "Simple Check-Check Sequence": {
            "config": {"num_rounds": 1, "starting_chips": 1000},
            "actions": ["[Call]", "[Check]"],
            "expected_state": {
                "betting_round": 1,  # Should advance to flop
                "pot": 40,  # Just blinds + call
                "current_bet": 0,
            },
            "expected_terminated": False,
        },
        "Basic Betting Sequence": {
            "config": {"num_rounds": 1, "starting_chips": 1000},
            "actions": ["[Bet 50]", "[Call]"],
            "expected_state": {
                "betting_round": 1,
                "pot": 100,  # [10, 20] -> [50, 20] -> [50, 50] 
                "current_bet": 0,  # Reset after betting round
            },
            "expected_terminated": False,
        },
        "Fold Sequence": {
            "config": {"num_rounds": 1, "starting_chips": 1000},
            "actions": ["[Bet 100]", "[Fold]"],
            "expected_state": {
                "pot": 0,  # Pot should be awarded to non-folding player
                "current_bet": 0,
            },
            "expected_terminated": True,
        },
        "Invalid Bet Amount": {
            "config": {"num_rounds": 1, "starting_chips": 100},
            "actions": ["[Bet 200]"],  # Trying to bet more than available chips
            "expected_state": None,
            "expected_terminated": True,
        }
    }

    @parameterized.expand([
        (
            name,
            details["config"],
            details["actions"],
            details["expected_state"],
            details["expected_terminated"],
        )
        for name, details in test_cases.items()
    ])
    def test_poker_scenarios(
        self,
        name: str,
        config: Dict[str, int],
        actions: List[str],
        expected_state: Optional[Dict[str, Any]],
        expected_terminated: bool,
    ):
        """
        Test various poker game scenarios.

        Args:
            name (str): Name of the test case
            config (Dict[str, int]): Configuration parameters for the environment
            actions (List[str]): Sequence of actions to execute
            expected_state (Optional[Dict[str, Any]]): Expected final state
            expected_terminated (bool): Whether the game should be terminated
        """
        with self.subTest(test_case=name):
            # Initialize environment with configuration
            env = PokerEnv(**config)

            try:
                # Reset environment with fixed seed for reproducibility
                observations = env.reset(seed=42)
            except Exception as e:
                self.fail(f"Failed to reset the environment: {e}")

            # Track game state
            terminated = False
            truncated = False

            # Execute action sequence
            for i, action in enumerate(actions):
                if terminated or truncated:
                    break

                player_id = env.get_current_player_id()
                try:
                    # Execute the action in the environment
                    step_result = env.step(player_id, action)
                    if len(step_result) != 5:
                        self.fail(f"env.step() returned {len(step_result)} elements, expected 5")
                    observations, rewards, truncated, terminated, info = step_result
                except Exception as e:
                    self.fail(f"env.step() failed for player {player_id}: {e}")

            # Verify final state matches expectations
            if expected_state is not None:
                game_state = env.state.game_state
                for key, expected_value in expected_state.items():
                    self.assertEqual(
                        game_state[key],
                        expected_value,
                        f"State mismatch for {key}. Expected {expected_value}, got {game_state[key]}"
                    )

            # Verify termination state
            self.assertEqual(
                terminated,
                expected_terminated,
                f"Termination state mismatch. Expected {expected_terminated}, got {terminated}"
            )

    def test_betting_validation(self):
        """Test validation of betting actions."""
        env = PokerEnv(starting_chips=100)
        env.reset(seed=42)

        # Test invalid bet amount
        with self.subTest(case="Oversized bet"):
            _, _, _, terminated, _ = env.step(1, "[Bet 200]")
            self.assertTrue(terminated, "Game should terminate on invalid bet")

        # Reset and test invalid raise
        env.reset(seed=42)
        env.step(1, "[Bet 20]")
        with self.subTest(case="Invalid raise"):
            _, _, _, terminated, _ = env.step(0, "[Raise 500]")
            self.assertTrue(terminated, "Game should terminate on invalid raise")

    def test_blinds_posting(self):
        """Test correct posting of blinds."""
        env = PokerEnv(small_blind=10, big_blind=20)
        env.reset(seed=42)

        game_state = env.state.game_state
        self.assertEqual(game_state["pot"], 30, "Incorrect blind total")
        self.assertEqual(game_state["current_bet"], 20, "Incorrect current bet")

    def test_basic_hand_comparison(self):
        """Test basic hand comparison logic without recursion."""
        env = PokerEnv()
        
        # Test pair vs high card
        pair_hand = [
            {"rank": "A", "suit": "♠"},
            {"rank": "A", "suit": "♣"},
            {"rank": "K", "suit": "♥"},
            {"rank": "Q", "suit": "♦"},
            {"rank": "J", "suit": "♠"},
        ]
        
        high_card_hand = [
            {"rank": "A", "suit": "♠"},
            {"rank": "K", "suit": "♣"},
            {"rank": "Q", "suit": "♥"},
            {"rank": "J", "suit": "♦"},
            {"rank": "9", "suit": "♠"},
        ]

        pair_rank = env._evaluate_single_hand(pair_hand)[0]
        high_card_rank = env._evaluate_single_hand(high_card_hand)[0]
        
        self.assertGreater(pair_rank, high_card_rank, "Pair should rank higher than high card")

        # Test three of a kind vs pair
        three_kind_hand = [
            {"rank": "A", "suit": "♠"},
            {"rank": "A", "suit": "♣"},
            {"rank": "A", "suit": "♥"},
            {"rank": "K", "suit": "♦"},
            {"rank": "Q", "suit": "♠"},
        ]
        
        three_kind_rank = env._evaluate_single_hand(three_kind_hand)[0]
        self.assertGreater(three_kind_rank, pair_rank, "Three of a kind should rank higher than pair")


if __name__ == '__main__':
    unittest.main()