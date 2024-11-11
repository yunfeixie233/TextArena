import unittest
from parameterized import parameterized
from textarena.envs.two_player.SpiteAndMalice.env import SpiteAndMaliceEnv

## helper functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct move of a SpiteAndMalice puzzle.
    """
    return ["I play the card: [play K♠ 0]", "I discard the card: [discard J♣ 2]", "I will draw cards. [draw]"]

def generate_invalid_move_sequence():
    """
    Generates an action sequence leading to an invalid move of a SpiteAndMalice puzzle.
    """
    return ["I play the card: play K♠ 0", "I discard the card: discard Q♣ 2", "I will draw cards. draw"]

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with out-of-bounds card values.
    """
    return ["I play the card: [play Q♣ 2]", "I play the card: [play K♠ 4]", "I discard the card: [discard Q♣ 20]"]

class TestSpiteAndMaliceEnv(unittest.TestCase):
    """
    Test class for SpiteAndMalice environment.
    """

    ## test cases
    test_cases = {
        "correct_move_easy": {
            "actions": generate_correct_move_sequence()
        },
        "invalid_move_easy": {
            "actions": generate_invalid_move_sequence()
        },
        "out_of_bounds_easy": {
            "actions": generate_out_of_bounds_sequence()
        }
    }

    @parameterized.expand([
        (name, details["actions"])
        for name, details in test_cases.items()
    ])
    def test_spiteandmalice_outcomes(self, name, actions):
        """
        Test the outcomes of the SpiteAndMalice game.
        
        Args:
            name (str): Name of the test case.
            actions (list): List of actions to test.
        """
        ## initialize the environment
        env = SpiteAndMaliceEnv()

        ## reset the environment
        observations = env.reset(seed=490)

        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}

        for i, action in enumerate(actions):
            if terminated or truncated:
                break

            player_id = i % 2
            
            env_action = action

            ## execute
            observations, reward, truncated, terminated, info = env.step(player_id, env_action)

            ## update the rewards
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
        print("Running SpiteAndMalice tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
