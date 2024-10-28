import unittest
from parameterized import parameterized
from textarena.envs.single_player.LogicPuzzle.env import LogicPuzzleEnv

## Helper functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a LogicPuzzle puzzle.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[wednesday Alice O]", "[tuesday Charlie O]"]  # Example sequence

def generate_invalid_format_sequence():
    """
    Generates an action sequence with an invalid move.
    """
    return ["[day_people wednesday Alice O]", "(tuesday Charlie X)"]  # Invalid move

def generate_complete_sequence():
    """
    Generates an action sequence leading to a correct completion of a LogicPuzzle puzzle.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[wednesday Alice O] [wednesday Bob X] [wednesday Charlie X] [monday Alice X] [monday Bob O] [monday Charlie X] [tuesday Alice X] [tuesday Bob X] [tuesday Charlie O] [wednesday soccer O] [wednesday basketball X] [wednesday tennis X] [monday soccer X] [monday basketball O] [monday tennis X] [tuesday soccer X] [tuesday basketball X] [tuesday tennis O]"]  # Example sequence


class TestLogicPuzzleEnv(unittest.TestCase):

    ## define environment variants as class attributes
    env_variants = [
        {"difficulty": "easy"},
        {"difficulty": "hard"}
    ]

    ## define test cases as class attributes
    test_cases = {
        "correct_move_easy": {
            "difficulty": "easy",
            "actions": generate_correct_move_sequence()
        },
        "invalid_format_easy": {
            "difficulty": "easy",
            "actions": generate_invalid_format_sequence()
        },
        "complete_easy": {
            "difficulty": "easy",
            "actions": generate_complete_sequence()
        }
    }

    @parameterized.expand([
        (name, details['difficulty'], details['actions'])
        for name, details in test_cases.items()
    ])
    def test_logicpuzzle_outcomes(self, name, difficulty, actions):
        ## Initialize the environment
        env_config = next((env for env in self.env_variants if env['difficulty'] == difficulty), None)
        self.assertIsNotNone(env_config, f"Invalid difficulty level: {difficulty}")

        env = LogicPuzzleEnv(difficulty=difficulty)

        _ = env.reset(seed=490)

        terminated = False
        truncated = False

        for i, action in enumerate(actions):
            if terminated or truncated:
                break
            player_id = 0

            ## execute the action sequence
            observations, reward, truncated, terminated, info = env.step(player_id, action)

            ## test different outcomes based on the test case name
            if "correct_move" in name:
                self.assertFalse(terminated, f"Test case {name}: The game terminated unexpectedly.")
                self.assertFalse(truncated, f"Test case {name}: The game was truncated unexpectedly.")
            elif "invalid_format" in name:
                self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move format.")
                self.assertEqual(reward[0], -1, "Player should receive -1 reward for an invalid move format.")
            elif "complete" in name:
                self.assertTrue(terminated, "Game should terminate after completing the puzzle.")
                self.assertEqual(reward[0], 1, "Player should receive 1 reward for completing the puzzle.")
            else:
                raise ValueError(f"Invalid test case: {name}")
            
def run_unit_test():
    print("Running LogicPuzzleEnv tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
