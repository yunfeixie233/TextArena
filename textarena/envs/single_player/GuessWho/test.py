import unittest
from parameterized import parameterized
from textarena.envs.single_player.GuessWho.env import GuessWhoEnv

## Helper Functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a GuessWho game.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["Does the character have blue eyes?","Does the character have long hair?"]  # Example sequence

def generate_correct_guess_sequence():
    """
    Generates an action sequence leading to a correct completion of a GuessWho game.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["The character is [Tom]"]

def generate_invalid_guess_sequence():
    """
    Generates an action sequence with an invalid guess.
    """
    return ["The character is Tom!"]  # Invalid guess

class TestGuessWhoEnv(unittest.TestCase):
    """
    Test class for the GuessWho environment.
    """


    test_cases = {
        "correct_move": {
            "actions": generate_correct_move_sequence()
        },
        "correct_guess": {
            "actions": generate_correct_guess_sequence()
        },
        "invalid_guess": {
            "actions": generate_invalid_guess_sequence()
        },
    }

    @parameterized.expand([
        (name, details['actions'])
        for name, details in test_cases.items()
    ])
    def test_guesswho_env(self, name, action_sequence):
        """
        Test method for the GuessWho environment.
        """
        env = GuessWhoEnv()

        observations = env.reset(seed=490)

        terminated = False
        truncated = False

        for i, action in enumerate(action_sequence):
            if terminated or truncated:
                break
            player_id = 0

            ## execute the action in the environment
            observations, rewards, truncated, terminated, info = env.step(player_id, action)

            ## test different outcomes based on the test case name
            if "correct_move" in name:
                self.assertFalse(truncated, "Game should not truncate for correct moves.")
                self.assertFalse(terminated, "Game should not terminate for correct moves.")
            elif "correct_guess" in name:
                self.assertFalse(truncated, "Game should not truncate for correct answer.")
                self.assertTrue(terminated, "Game should terminate for correct answer.")
                self.assertEqual(rewards[0], 1, "Player should receive a reward for correct answer.")
            elif "invalid_guess" in name:
                self.assertFalse(truncated, "Game should not truncate for incorrect format of answer.")
                self.assertFalse(terminated, "Game should not terminate for incorrect format of answer.")
            else:
                self.fail(f"Invalid test case: {name}")

    def run_unit_test():
        print("Running TwentyQuestionsEnv tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False) 
    