from textarena.envs.two_player.SpellingBee.env import SpellingBeeEnv

import warnings
import unittest
from parameterized import parameterized
from typing import Dict, List, Optional, Any


# Suppress specific warnings to keep test output clean
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


class TestSpellingBeeEnv(unittest.TestCase):
    """
    Unit test suite for the SpellingBee environment. Tests various game scenarios
    to ensure the environment behaves correctly under different conditions.
    """

    test_cases = {
        "Valid Words Same Length": {
            "config": {"num_letters": 5},
            "allowed_letters": {"a", "b", "c", "d", "e"},
            "actions": ["[bed]", "[ace]"],
            "expected_state": {
                "player_words": {0: "[bed]", 1: "[ace]"},
            },
            "expected_rewards": {0: 0, 1: 0},  # Draw results in 0 rewards
            "expected_terminated": True,
        },
        "Valid Words Different Length": {
            "config": {"num_letters": 5},
            "allowed_letters": {"a", "b", "c", "d", "e"},
            "actions": ["[bead]", "[ace]"],
            "expected_state": {
                "player_words": {0: "[bead]", 1: "[ace]"},
            },
            "expected_rewards": {0: 1, 1: -1},  # Player 0 wins with longer word
            "expected_terminated": True,
        },
        "Invalid Word Format": {
            "config": {"num_letters": 5},
            "allowed_letters": {"a", "b", "c", "d", "e"},
            "actions": ["bead", "[ace]"],  # First word missing brackets
            "expected_state": {
                "player_words": {0: "bead", 1: "[ace]"},
            },
            "expected_rewards": {0: -1, 1: 0},  # Player 0's invalid move
            "expected_terminated": True,
        },
        "Invalid Letters Used": {
            "config": {"num_letters": 5},
            "allowed_letters": {"a", "b", "c", "d", "e"},
            "actions": ["[zebra]", "[ace]"],  # First word uses 'z'
            "expected_state": {
                "player_words": {0: "[zebra]", 1: "[ace]"},
            },
            "expected_rewards": {0: -1, 1: 0},  # Player 0's invalid move
            "expected_terminated": True,
        },
        "Non-English Word": {
            "config": {"num_letters": 5},
            "allowed_letters": {"a", "b", "c", "d", "e"},
            "actions": ["[aaaa]", "[ace]"],  # First word not in dictionary
            "expected_state": {
                "player_words": {0: "[aaaa]", 1: "[ace]"},
            },
            "expected_rewards": {0: -1, 1: 0},  # Player 0's invalid move
            "expected_terminated": True,
        },
        "Both Players Invalid": {
            "config": {"num_letters": 5},
            "allowed_letters": {"a", "b", "c", "d", "e"},
            "actions": ["[zzz]", "[yyy]"],  # Both use invalid letters
            "expected_state": {
                "player_words": {0: "[zzz]", 1: "[yyy]"},
            },
            "expected_rewards": {0: -1, 1: -1},  # Both players invalid
            "expected_terminated": True,
        }
    }

    def setUp(self):
        """Set up test cases."""
        self.env = SpellingBeeEnv(num_letters=5)

    @parameterized.expand([
        (
            name,
            details["config"],
            details["allowed_letters"],
            details["actions"],
            details["expected_state"],
            details["expected_rewards"],
            details["expected_terminated"],
        )
        for name, details in test_cases.items()
    ])
    def test_spelling_bee_scenarios(
        self,
        name: str,
        config: Dict[str, int],
        allowed_letters: set,
        actions: List[str],
        expected_state: Dict[str, Any],
        expected_rewards: Dict[int, int],
        expected_terminated: bool,
    ):
        """
        Test various SpellingBee game scenarios.

        Args:
            name (str): Name of the test case
            config (Dict[str, int]): Configuration parameters
            allowed_letters (set): Set of allowed letters
            actions (List[str]): Sequence of player actions
            expected_state (Dict[str, Any]): Expected final state
            expected_rewards (Dict[int, int]): Expected rewards for each player
            expected_terminated (bool): Whether the game should be terminated
        """
        with self.subTest(test_case=name):
            # Initialize environment with configuration
            env = SpellingBeeEnv(**config)

            try:
                # Reset environment with fixed seed
                observations = env.reset(seed=42)
                # Override allowed letters for consistent testing
                env.state.game_state["allowed_letters"] = allowed_letters
            except Exception as e:
                self.fail(f"Failed to reset environment: {e}")

            # Track game state
            terminated = False
            truncated = False
            final_rewards = None

            # Execute action sequence
            for i, action in enumerate(actions):
                if terminated or truncated:
                    break

                player_id = env.get_current_player_id()
                try:
                    observations, rewards, truncated, terminated, info = env.step(
                        player_id, action
                    )
                    final_rewards = rewards  # Keep track of final rewards
                except Exception as e:
                    self.fail(f"env.step() failed for player {player_id}: {e}")

            # Verify final state
            game_state = env.state.game_state
            for key, expected_value in expected_state.items():
                self.assertEqual(
                    game_state[key],
                    expected_value,
                    f"State mismatch for {key}. Expected {expected_value}, got {game_state[key]}"
                )

            # Verify rewards
            self.assertIsNotNone(final_rewards, "Final rewards should not be None")
            for player_id, expected_reward in expected_rewards.items():
                self.assertEqual(
                    final_rewards[player_id],
                    expected_reward,
                    f"Reward mismatch for Player {player_id}. Expected {expected_reward}, got {final_rewards[player_id]}"
                )

            # Verify termination state
            self.assertEqual(
                terminated,
                expected_terminated,
                f"Termination state mismatch. Expected {expected_terminated}, got {terminated}"
            )

    def test_letter_generation(self):
        """Test the generation of allowed letters."""
        env = SpellingBeeEnv(num_letters=5)
        env.reset(seed=42)
        
        # Check number of letters
        self.assertEqual(
            len(env.state.game_state["allowed_letters"]),
            5,
            "Incorrect number of allowed letters"
        )
        
        # Check letters are lowercase
        self.assertTrue(
            all(l.islower() for l in env.state.game_state["allowed_letters"]),
            "All letters should be lowercase"
        )
        
        # Check letters are unique
        self.assertEqual(
            len(env.state.game_state["allowed_letters"]),
            len(set(env.state.game_state["allowed_letters"])),
            "Letters should be unique"
        )


    def test_word_validation(self):
        """Test word validation logic."""
        env = SpellingBeeEnv(num_letters=5)
        env.state.game_state = {"allowed_letters": {"a", "b", "c", "d", "e"}}
        
        # Test valid word
        is_valid, reason, length = env._check_word_validity("[bed]", 0)
        self.assertTrue(is_valid, "Should accept valid word")
        self.assertEqual(length, 3, "Incorrect word length")
        
        # Test word with invalid letters
        is_valid, reason, length = env._check_word_validity("[zebra]", 0)
        self.assertFalse(is_valid, "Should reject word with invalid letters")
        
        # Test non-English word
        is_valid, reason, length = env._check_word_validity("[aaaa]", 0)
        self.assertFalse(is_valid, "Should reject non-English word")
        
        # Test missing brackets
        is_valid, reason, length = env._check_word_validity("bed", 0)
        self.assertFalse(is_valid, "Should reject word without brackets")


if __name__ == '__main__':
    unittest.main()