import unittest
from parameterized import parameterized
from textarena.envs.two_player.DontSayIt.env import DontSayItEnv
import json

# Helper Functions
def generate_normal_game_sequence(player_messages):
    """
    Generates a sequence of valid player messages without triggering any win or loss conditions.
    
    Args:
        player_messages (List[str]): List of messages from players alternating.
    
    Returns:
        List[str]: Action sequence of player messages.
    """
    actions = []
    for msg in player_messages:
        actions.append(msg)
    return actions

def generate_player_says_opponent_word_sequence(player_id, opponent_word):
    """
    Generates an action sequence where a player says the opponent's secret word, resulting in a loss.
    
    Args:
        player_id (int): ID of the player who will say the opponent's word.
        opponent_word (str): The word to be said by the player.
    
    Returns:
        List[str]: Action sequence leading to the player saying the opponent's word.
    """
    actions = []
    actions.append("Let's talk about something interesting.")
    actions.append(f"I really like the word {opponent_word}.")
    return actions

def generate_player_says_own_word_sequence(player_id, own_word):
    """
    Generates an action sequence where a player accidentally says their own secret word, resulting in a loss.
    
    Args:
        player_id (int): ID of the player who will say their own word.
        own_word (str): The player's own secret word.
    
    Returns:
        List[str]: Action sequence leading to the player saying their own word.
    """
    actions = []
    actions.append("I was reading a fascinating book recently.")
    actions.append(f"The main character's name was {own_word}.")
    return actions

class TestDontSayItEnv(unittest.TestCase):
    
    # Define environment variants as class attributes
    env_variants = [
        {"env_id": "DontSayIt-v0", "hardcore": False, "max_turns": 10, "render": False, "data_path": "words.json"},
        {"env_id": "DontSayIt-v0-hardcore", "hardcore": True, "max_turns": 20, "render": True, "data_path": "words_hardcore.json"},
    ]
    
    # Define test cases as class attributes
    test_cases = {
        "normal_game_v0": {
            "env_id": "DontSayIt-v0",
            "actions": generate_normal_game_sequence([
                "Hi there!",
                "Hello! How are you?",
                "I'm good, thanks. What's new?",
                "Not much, just enjoying the weather."
            ])
        },
        "player_says_opponent_word_v0": {
            "env_id": "DontSayIt-v0",
            "actions": generate_player_says_opponent_word_sequence(player_id=0, opponent_word="Python")
        },
        "player_says_own_word_v0": {
            "env_id": "DontSayIt-v0",
            "actions": generate_player_says_own_word_sequence(player_id=1, own_word="Secret")
        },
        "normal_game_hardcore": {
            "env_id": "DontSayIt-v0-hardcore",
            "actions": generate_normal_game_sequence([
                "Good morning!",
                "Good morning to you too!",
                "Have you seen the latest news?",
                "Yes, it's quite intriguing."
            ])
        },
        "player_says_opponent_word_hardcore": {
            "env_id": "DontSayIt-v0-hardcore",
            "actions": generate_player_says_opponent_word_sequence(player_id=1, opponent_word="Quantum")
        },
        # Add more test cases as needed
    }
    
    @parameterized.expand([
        (name, details["env_id"], details["actions"])
        for name, details in test_cases.items()
    ])
    def test_dont_say_it_outcomes(self, name, env_id, action_sequence):
        """
        Test various Don't Say It outcomes using predefined action sequences across different environment variants.
        
        Args:
            name (str): Test case name.
            env_id (str): Environment ID to test.
            action_sequence (List[str]): List of action strings to execute.
        """
        # Initialize the environment based on env_id
        env_config = next((env for env in self.env_variants if env["env_id"] == env_id), None)
        self.assertIsNotNone(env_config, f"Environment config for {env_id} not found.")
        
        env = DontSayItEnv(
            hardcore=env_config["hardcore"],
            max_turns=env_config["max_turns"],
        )
        observations, secret_words = env.reset(seed=42)
        
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
        if "says_opponent_word" in name:
            losing_player = int(name.split("_")[1][-1])
            winning_player = 1 - losing_player
            self.assertTrue(terminated or truncated, "Game should have terminated due to a player saying the opponent's word.")
            self.assertEqual(rewards[losing_player], -1, f"Player {losing_player} should have received -1 for saying the opponent's word.")
            self.assertEqual(rewards[winning_player], 1, f"Player {winning_player} should have received +1 for winning.")
        elif "says_own_word" in name:
            losing_player = int(name.split("_")[1][-1])
            self.assertTrue(terminated or truncated, "Game should have terminated due to a player saying their own word.")
            self.assertEqual(rewards[losing_player], -1, f"Player {losing_player} should have received -1 for saying their own word.")
        elif "normal_game" in name:
            self.assertTrue(truncated or not terminated, "Game should have either been truncated or not terminated.")
            if env_config["max_turns"]:
                self.assertTrue(truncated, "Game should have been truncated due to reaching the maximum number of turns.")
                self.assertEqual(rewards[0], 0, "Player 0 should have received 0 reward for a draw.")
                self.assertEqual(rewards[1], 0, "Player 1 should have received 0 reward for a draw.")
        else:
            self.fail(f"Unknown test case name: {name}")

def run_unit_test():
    unittest.main()
