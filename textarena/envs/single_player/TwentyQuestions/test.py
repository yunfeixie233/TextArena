import unittest
from parameterized import parameterized
from textarena.envs.single_player.TwentyQuestions.env import TwentyQuestionsEnv

## helper functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a TwentyQuestions game.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["Is it a living thing?",]

def generate_correct_answer_sequence():
    """
    Generates an action sequence leading to a correct completion of a TwentyQuestions game.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[science]","[Science]","I know the answer. It is [SCIENCE]."]

def generate_invalid_answer_sequence():
    """
    Generates an action sequence with an invalid answer format.
    """
    return ["[imagination]"]  # Invalid answer

class TestTwentyQuestionsEnv(unittest.TestCase):

    ## define the environment variants as class attributes
    env_variants = [
        {"hardcore": False},
        {"hardcore": True}
    ]

    ## define the test cases as class attributes
    test_cases = {
        "correct_moves": {
            "hardcore": False,
            "actions": generate_correct_move_sequence()
        },
        "correct_answer": {
            "hardcore": False,
            "actions": generate_correct_answer_sequence()
        },
        "invalid_answer": {
            "hardcore": False,
            "actions": generate_invalid_answer_sequence()
        }
    }

    @parameterized.expand([
        (name, details['hardcore'], details['actions'])
        for name, details in test_cases.items()
    ])
    def test_twentyquestions_outcomes(self, name, hardcore, action_sequence):
        """
        Test various outcomes of the TwentyQuestions game.
        """
        ## initialize the environment based on the hardcore level
        env_config = next((env for env in self.env_variants if env['hardcore'] == hardcore), None)
        self.assertIsNotNone(env_config, f"Invalid hardcore level: {hardcore}")

        env = TwentyQuestionsEnv(hardcore=env_config["hardcore"])

        _ = env.reset(seed=490)

        terminated = False
        truncated = False

        for i, action in enumerate(action_sequence):
            if terminated or truncated:
                break
            player_id = 0

            ## execute the actions
            observations, reward, truncated, terminated, info = env.step(player_id, action)

            ## test different outcomes based on the test case name
            if "correct_moves" in name:
                self.assertFalse(truncated, "Game should not truncate for correct moves.")
                self.assertFalse(terminated, "Game should not terminate for correct moves.")
            elif "correct_answer" in name:
                self.assertFalse(truncated, "Game should not truncate for correct answer.")
                self.assertTrue(terminated, "Game should terminate for correct answer.")
                self.assertEqual(reward[0], 1, "Player should receive a reward for correct answer.")
            elif "invalid_answer" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid answer.")
                self.assertEqual(reward[0], -1, "Player should receive -1 reward for an invalid answer.")
            else:
                self.fail(f"Invalid test case: {name}")

    def run_unit_test():
        print("Running TwentyQuestionsEnv tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False) 

