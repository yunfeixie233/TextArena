import unittest
from parameterized import parameterized
from textarena.envs.two_player.LetterAuction.env import LetterAuctionEnv

## helper functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct move of a LetterAuction puzzle.
    """
    return ["I bid 5 coins for the letter: [bid 5]", "I pass on the letter. [pass]", "I bid 10! [BID 10]", "I pass on the letter. [PASS]"]

def generate_invalid_move_sequence():
    """
    Generates an action sequence leading to an invalid move of a LetterAuction puzzle.
    """
    return ["I bid 5 coins for the letter: bid 5", "I pass on the letter. pass", "I bid 10! BID 10", "I pass on the letter. PASS"]

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with out-of-bounds bid values.
    """
    return ["I bid 5 coins for the letter: [bid 1000]", "I bid 100! [BID 1000]"]

class TestLetterAuctionEnv(unittest.TestCase):
    """
    Test class for LetterAuction environment.
    """

    ## define environment variants as class attributes
    env_variants = [
        {"difficulty": "easy"},
        {"difficulty": "medium"},
        {"difficulty": "hard"},
    ]

    ## test cases
    test_cases = {
        "correct_move_easy": {
            "difficulty": "easy",
            "actions": generate_correct_move_sequence()
        },
        "invalid_move_easy": {
            "difficulty": "easy",
            "actions": generate_invalid_move_sequence()
        },
        "out_of_bounds_easy": {
            "difficulty": "easy",
            "actions": generate_out_of_bounds_sequence()
        }
    }

    @parameterized.expand([
        (name, details["difficulty"], details["actions"])
        for name, details in test_cases.items()
    ])
    def test_letterauction_outcomes(self, name, difficulty, actions):
        """
        Test the outcomes of the LetterAuction game.
        
        Args:
            name (str): Name of the test case.
            difficulty (str): Difficulty level of the game.
            actions (list): List of actions to take in the game.
        """
        env_config = next((env for env in self.env_variants if env["difficulty"] == difficulty), None)
        self.assertIsNotNone(env_config, f"Environment configuration not found for difficulty level: {difficulty}")

        env = LetterAuctionEnv(difficulty=env_config["difficulty"])

        observations = env.reset(seed=490)

        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}

        for i, action in enumerate(actions):
            if terminated or truncated:
                break

            player_id = i % 2
            
            env_action = action

            ## take action
            observations, reward, truncated, terminated, info = env.step(player_id, env_action)

            ## update rewards
            if reward:
                rewards.update(reward)

        if "correct_move" in name:
            self.assertFalse(truncated, "Game should not truncate for correct moves.")
            self.assertFalse(terminated, "Game should not terminate until the game is complete.")
        elif "invalid_move" in name:
            self.assertTrue(truncated or terminated, "Game should truncate for invalid moves.")
            self.assertEqual(rewards[player_id], -1, "Player should receive -1 reward for an invalid move.")
        elif "out_of_bounds" in name:
            self.assertTrue(truncated or terminated, "Game should truncate for out-of-bounds moves.")
            self.assertEqual(rewards[player_id], -1, "Player should receive -1 reward for an out-of-bounds move.")
        else:
            raise ValueError("Invalid test case name.")
    
    def run_unit_test():
        print("Running LetterAuction tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
