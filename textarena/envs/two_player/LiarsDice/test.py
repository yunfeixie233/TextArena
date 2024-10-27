""" Test Script for Liar's Dice Game Environment """

import unittest
from parameterized import parameterized
from textarena.envs.two_player.LiarsDice.env import LiarsDiceEnv
import json

# Helper Functions
def generate_normal_game_sequence(player_messages):
    """
    Generates a sequence of valid player messages and bids without triggering any win or loss conditions.
    
    Args:
        player_messages (List[str]): List of messages from players alternating.
    
    Returns:
        List[str]: Action sequence of player messages and bids.
    """
    actions = []
    for msg in player_messages:
        actions.append(msg)
    return actions

def generate_valid_bid_sequence(player_id, quantity, face_value):
    """
    Generates an action sequence where a player makes a valid bid.
    
    Args:
        player_id (int): ID of the player making the bid.
        quantity (int): Quantity in the bid.
        face_value (int): Face value in the bid.
    
    Returns:
        List[str]: Action sequence leading to a valid bid.
    """
    actions = []
    bid_str = f"[Bid] {quantity} {face_value}"
    actions.append(bid_str)
    return actions

def generate_bluff_call_sequence(player_id):
    """
    Generates an action sequence where a player calls a bluff.
    
    Args:
        player_id (int): ID of the player calling the bluff.
    
    Returns:
        List[str]: Action sequence leading to a bluff call.
    """
    actions = []
    call_str = "[Call]"
    actions.append(call_str)
    return actions

def generate_invalid_bid_sequence(player_id, quantity, face_value):
    """
    Generates an action sequence where a player makes an invalid bid.
    
    Args:
        player_id (int): ID of the player making the invalid bid.
        quantity (int): Quantity in the bid.
        face_value (int): Face value in the bid.
    
    Returns:
        List[str]: Action sequence leading to an invalid bid.
    """
    actions = []
    # Intentionally making an invalid bid (e.g., decreasing quantity)
    bid_str = f"[Bid] {quantity} {face_value}"
    actions.append(bid_str)
    return actions

def generate_invalid_action_sequence(player_id, action):
    """
    Generates an action sequence with an invalid action format.
    
    Args:
        player_id (int): ID of the player making the invalid action.
        action (str): The invalid action string.
    
    Returns:
        List[str]: Action sequence leading to an invalid action.
    """
    actions = []
    actions.append(action)
    return actions

class TestLiarsDiceEnv(unittest.TestCase):
    
    # Define environment variants as class attributes
    env_variants = [
        {"env_id": "LiarsDice-v0", "num_dice": 5},
        {"env_id": "LiarsDice-v0-extended", "num_dice": 6},
        {"env_id": "LiarsDice-v0-short", "num_dice": 3},
    ]
    
    # Define test cases as class attributes
    test_cases = {
        "normal_game_v0": {
            "env_id": "LiarsDice-v0",
            "actions": generate_normal_game_sequence([
                "[Bid] 2 3",
                "[Bid] 3 3",
                "[Bid] 3 4",
                "[Bid] 4 4",
            ])
        },
        "bluff_call_win_v0": {
            "env_id": "LiarsDice-v0",
            "actions": generate_bluff_call_sequence(player_id=1)
        },
        "bluff_call_lose_v0": {
            "env_id": "LiarsDice-v0",
            "actions": generate_bluff_call_sequence(player_id=1)
        },
        "invalid_bid_v0": {
            "env_id": "LiarsDice-v0",
            "actions": generate_invalid_bid_sequence(player_id=0, quantity=1, face_value=2)
        },
        "invalid_action_v0": {
            "env_id": "LiarsDice-v0",
            "actions": generate_invalid_action_sequence(player_id=0, action="Hello there!")
        },
        "normal_game_extended": {
            "env_id": "LiarsDice-v0-extended",
            "actions": generate_normal_game_sequence([
                "[Bid] 1 2",
                "[Bid] 1 3",
                "[Bid] 2 3",
                "[Bid] 2 4",
            ])
        },
        "bluff_call_win_extended": {
            "env_id": "LiarsDice-v0-extended",
            "actions": generate_bluff_call_sequence(player_id=1)
        },
        "invalid_bid_extended": {
            "env_id": "LiarsDice-v0-extended",
            "actions": generate_invalid_bid_sequence(player_id=1, quantity=1, face_value=1)
        },
        # Add more test cases as needed
    }
    
    @parameterized.expand([
        (name, details["env_id"], details["actions"])
        for name, details in test_cases.items()
    ])
    def test_liars_dice_outcomes(self, name, env_id, action_sequence):
        """
        Test various Liar's Dice outcomes using predefined action sequences across different environment variants.
        
        Args:
            name (str): Test case name.
            env_id (str): Environment ID to test.
            action_sequence (List[str]): List of action strings to execute.
        """
        # Initialize the environment based on env_id
        env_config = next((env for env in self.env_variants if env["env_id"] == env_id), None)
        self.assertIsNotNone(env_config, f"Environment config for {env_id} not found.")
        
        env = LiarsDiceEnv(
            num_dice=env_config["num_dice"]
        )
        observations, info = env.reset(seed=42)
        
        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}
        
        for i, action in enumerate(action_sequence):
            if terminated or truncated:
                break
            player_id = i % 2  # Player 0 and Player 1 alternate
            env_action = action
            
            # Execute the action
            observations, reward, truncated, terminated, info = env.step(player_id, env_action)
            
            # Update rewards
            if reward:
                rewards.update(reward)
        
        # Determine the expected outcome based on the test case name
        if "bluff_call_win" in name:
            # Assuming the bluff call results in a win
            self.assertTrue(terminated or truncated, "Game should have terminated due to a bluff call resulting in a win.")
            self.assertEqual(rewards.get(player_id, 0), 1, f"Player {player_id} should have received +1 for winning by bluff call.")
            self.assertEqual(rewards.get(1 - player_id, 0), -1, f"Player {1 - player_id} should have received -1 for losing by bluff call.")
        elif "bluff_call_lose" in name:
            # Assuming the bluff call results in a loss
            self.assertTrue(terminated or truncated, "Game should have terminated due to a bluff call resulting in a loss.")
            self.assertEqual(rewards.get(player_id, 0), -1, f"Player {player_id} should have received -1 for losing by bluff call.")
            self.assertEqual(rewards.get(1 - player_id, 0), 1, f"Player {1 - player_id} should have received +1 for winning by bluff call.")
        elif "invalid_bid" in name:
            player_id = 0 if "v0" in name else 1
            self.assertTrue(terminated or truncated, "Game should have terminated due to an invalid bid.")
            self.assertEqual(rewards.get(player_id, 0), -1, f"Player {player_id} should have received -1 for making an invalid bid.")
        elif "invalid_action" in name:
            player_id = 0
            self.assertTrue(terminated or truncated, "Game should have terminated due to an invalid action.")
            self.assertEqual(rewards.get(player_id, 0), -1, f"Player {player_id} should have received -1 for making an invalid action.")
        elif "normal_game" in name:
            # Normal game should not terminate unless a bluff is called
            self.assertFalse(terminated and truncated, "Normal game should not terminate prematurely.")
            # Rewards should remain neutral
            self.assertEqual(rewards, {0: 0, 1: 0}, "Players should have neutral rewards in a normal game without bluff calls.")
        else:
            self.fail(f"Unknown test case name: {name}")

def run_unit_tests():
    """
    Runs the unittest when this script is executed directly.
    """
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# Uncomment the following line to run tests when this script is executed
# run_unit_tests()
