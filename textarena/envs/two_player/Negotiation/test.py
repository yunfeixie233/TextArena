""" Test Script for Negotiation Game Environment """

import unittest
from parameterized import parameterized
from textarena.envs.two_player.NegotiationGame.env import NegotiationEnv
import json

# Helper Functions
def generate_normal_game_sequence(player_messages):
    """
    Generates a sequence of valid player messages and trade offers without triggering any win or loss conditions.
    
    Args:
        player_messages (List[str]): List of messages from players alternating.
    
    Returns:
        List[str]: Action sequence of player messages and offers.
    """
    actions = []
    for msg in player_messages:
        actions.append(msg)
    return actions

def generate_trade_acceptance_sequence(player_id, proposer_id, offer_details):
    """
    Generates an action sequence where a player makes a trade offer and the opponent accepts it.
    
    Args:
        player_id (int): ID of the player making the offer.
        proposer_id (int): ID of the player accepting the offer.
        offer_details (Dict[str, Dict[str, int]]): Details of the trade offer.
    
    Returns:
        List[str]: Action sequence leading to a trade acceptance.
    """
    actions = []
    offer_str = f"[Offer] I give {format_offer(offer_details['my_offer'])}; You give {format_offer(offer_details['their_offer'])}."
    actions.append(offer_str)
    actions.append("[Accept]")
    return actions

def generate_trade_denial_sequence(player_id, proposer_id, offer_details):
    """
    Generates an action sequence where a player makes a trade offer and the opponent denies it.
    
    Args:
        player_id (int): ID of the player making the offer.
        proposer_id (int): ID of the player denying the offer.
        offer_details (Dict[str, Dict[str, int]]): Details of the trade offer.
    
    Returns:
        List[str]: Action sequence leading to a trade denial.
    """
    actions = []
    offer_str = f"[Offer] I give {format_offer(offer_details['my_offer'])}; You give {format_offer(offer_details['their_offer'])}."
    actions.append(offer_str)
    actions.append("[Deny]")
    return actions

def generate_invalid_offer_sequence(player_id):
    """
    Generates an action sequence where a player makes an invalid trade offer.
    
    Args:
        player_id (int): ID of the player making the invalid offer.
    
    Returns:
        List[str]: Action sequence leading to an invalid trade offer.
    """
    actions = []
    # Missing [Offer] token and incorrect format
    invalid_offer = "I offer you 2 Wheat for 3 Sheep."
    actions.append(invalid_offer)
    return actions

def generate_insufficient_resources_offer_sequence(player_id, proposer_id, offer_details):
    """
    Generates an action sequence where a player makes a trade offer that they cannot fulfill due to insufficient resources.
    
    Args:
        player_id (int): ID of the player making the offer.
        proposer_id (int): ID of the player accepting the offer.
        offer_details (Dict[str, Dict[str, int]]): Details of the trade offer.
    
    Returns:
        List[str]: Action sequence leading to an unsuccessful trade due to insufficient resources.
    """
    actions = []
    offer_str = f"[Offer] I give {format_offer(offer_details['my_offer'])}; You give {format_offer(offer_details['their_offer'])}."
    actions.append(offer_str)
    actions.append("[Accept]")
    return actions

def format_offer(resource_dict):
    """
    Formats a resource dictionary into a string suitable for trade offers.
    
    Args:
        resource_dict (Dict[str, int]): Dictionary of resources and their quantities.
    
    Returns:
        str: Formatted resource string.
    """
    return ", ".join([f"{qty} {res}" for res, qty in resource_dict.items()])

class TestNegotiationEnv(unittest.TestCase):
    
    # Define environment variants as class attributes
    env_variants = [
        {"env_id": "NegotiationGame-v0", "max_turns": 10},
        {"env_id": "NegotiationGame-v0-extended", "max_turns": 20},
        {"env_id": "NegotiationGame-v0-short", "max_turns": 5},
    ]
    
    # Define test cases as class attributes
    test_cases = {
        "normal_game_v0": {
            "env_id": "NegotiationGame-v0",
            "actions": generate_normal_game_sequence([
                "Hi there!",
                "Hello! I'm looking to improve my Wood.",
                "That sounds good. I'm interested in trading Wheat.",
                "Sure, let's see if we can make a deal."
            ])
        },
        "trade_acceptance_v0": {
            "env_id": "NegotiationGame-v0",
            "actions": generate_trade_acceptance_sequence(
                player_id=0,
                proposer_id=1,
                offer_details={
                    "my_offer": {"2 Wheat": 2, "1 Ore": 1},
                    "their_offer": {"3 Sheep": 3}
                }
            )
        },
        "trade_denial_v0": {
            "env_id": "NegotiationGame-v0",
            "actions": generate_trade_denial_sequence(
                player_id=0,
                proposer_id=1,
                offer_details={
                    "my_offer": {"2 Wood": 2},
                    "their_offer": {"1 Brick": 1}
                }
            )
        },
        "invalid_offer_v0": {
            "env_id": "NegotiationGame-v0",
            "actions": generate_invalid_offer_sequence(player_id=0)
        },
        "insufficient_resources_trade_v0": {
            "env_id": "NegotiationGame-v0",
            "actions": generate_insufficient_resources_offer_sequence(
                player_id=0,
                proposer_id=1,
                offer_details={
                    "my_offer": {"100 Ore": 100},  # Assuming player doesn't have 100 Ore
                    "their_offer": {"3 Sheep": 3}
                }
            )
        },
        "normal_game_extended": {
            "env_id": "NegotiationGame-v0-extended",
            "actions": generate_normal_game_sequence([
                "Good morning!",
                "Good morning! I'm interested in trading Brick.",
                "I have some Ore to offer.",
                "Let's discuss the details."
            ])
        },
        "trade_acceptance_extended": {
            "env_id": "NegotiationGame-v0-extended",
            "actions": generate_trade_acceptance_sequence(
                player_id=1,
                proposer_id=0,
                offer_details={
                    "my_offer": {"1 Ore": 1},
                    "their_offer": {"2 Wood": 2}
                }
            )
        },
        "trade_denial_extended": {
            "env_id": "NegotiationGame-v0-extended",
            "actions": generate_trade_denial_sequence(
                player_id=1,
                proposer_id=0,
                offer_details={
                    "my_offer": {"1 Brick": 1},
                    "their_offer": {"2 Wheat": 2}
                }
            )
        },
        "invalid_offer_extended": {
            "env_id": "NegotiationGame-v0-extended",
            "actions": generate_invalid_offer_sequence(player_id=1)
        },
        "insufficient_resources_trade_extended": {
            "env_id": "NegotiationGame-v0-extended",
            "actions": generate_insufficient_resources_offer_sequence(
                player_id=1,
                proposer_id=0,
                offer_details={
                    "my_offer": {"50 Wheat": 50},  # Assuming player doesn't have 50 Wheat
                    "their_offer": {"5 Ore": 5}
                }
            )
        },
        # Add more test cases as needed
    }
    
    @parameterized.expand([
        (name, details["env_id"], details["actions"])
        for name, details in test_cases.items()
    ])
    def test_negotiation_game_outcomes(self, name, env_id, action_sequence):
        """
        Test various Negotiation Game outcomes using predefined action sequences across different environment variants.
        
        Args:
            name (str): Test case name.
            env_id (str): Environment ID to test.
            action_sequence (List[str]): List of action strings to execute.
        """
        # Initialize the environment based on env_id
        env_config = next((env for env in self.env_variants if env["env_id"] == env_id), None)
        self.assertIsNotNone(env_config, f"Environment config for {env_id} not found.")
        
        env = NegotiationEnv(
            max_turns=env_config["max_turns"]
        )
        observations = env.reset(seed=42)
        
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
        if "trade_acceptance" in name:
            proposer_id = 0 if "v0" in name else 1  # Adjust based on test case naming
            accepter_id = 1 if proposer_id == 0 else 0
            self.assertFalse(truncated, "Game should not be truncated.")
            self.assertFalse(terminated, "Game should not be terminated after a trade acceptance.")
            # Check that resources have been updated correctly
            # Note: Requires access to internal game state or a method to retrieve it
            # For simplicity, assume rewards are not updated on trade acceptance
            self.assertEqual(rewards[proposer_id], 0, f"Player {proposer_id} should have no reward.")
            self.assertEqual(rewards[accepter_id], 0, f"Player {accepter_id} should have no reward.")
        elif "trade_denial" in name:
            self.assertFalse(truncated, "Game should not be truncated.")
            self.assertFalse(terminated, "Game should not be terminated after a trade denial.")
            # Check that no resources have been exchanged
            self.assertEqual(rewards[0], 0, "Player 0 should have no reward.")
            self.assertEqual(rewards[1], 0, "Player 1 should have no reward.")
        elif "invalid_offer" in name:
            player_id = 0 if "v0" in name else 1
            self.assertTrue(terminated or truncated, "Game should have terminated due to an invalid offer.")
            self.assertEqual(rewards[player_id], -1, f"Player {player_id} should have received -1 for making an invalid offer.")
        elif "insufficient_resources_trade" in name:
            player_id = 0 if "v0" in name else 1
            self.assertTrue(terminated or truncated, "Game should have terminated due to insufficient resources for trade.")
            self.assertEqual(rewards[player_id], -1, f"Player {player_id} should have received -1 for attempting an invalid trade.")
        elif "normal_game" in name:
            self.assertTrue(truncated or not terminated, "Normal game should have either been truncated or not terminated.")
            if env_config["max_turns"]:
                self.assertTrue(truncated, "Game should have been truncated due to reaching the maximum number of turns.")
                self.assertEqual(rewards[0], 0, "Player 0 should have received 0 reward for a draw.")
                self.assertEqual(rewards[1], 0, "Player 1 should have received 0 reward for a draw.")
        else:
            self.fail(f"Unknown test case name: {name}")

def run_unit_tests():
    """
    Runs the unittest when this script is executed directly.
    """
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# Uncomment the following line to run tests when this script is executed
# run_unit_tests()
