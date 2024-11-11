import unittest
from parameterized import parameterized
from textarena.envs.two_player.Mastermind.env import MastermindEnv

## Helper functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct move of a Mastermind puzzle.
    """
    return ["Let's make the first code guess attempt of [1 2 3 4].", "Seems like 1 2 4 3 gave 2 black pegs and 2 white pegs. Let's reorder the last two digts. My guess is [1 2 3 4]."]

def generate_invalid_move_sequence():
    """
    Generates an action sequence leading to an invalid move of a Mastermind puzzle.
    """
    return ["Let's make the first code guess attempt of (1 2 3 4).", "Seems like 1 2 4 3 gave 2 black pegs and 2 white pegs. Let's reorder the last two digts. My guess is 1 2 3 4."]

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with out-of-bounds code values.
    """
    return ["Let's make the first code guess attempt of (1 2 3 100).", "Seems like 1 2 4 3 gave 2 black pegs and 2 white pegs. Let's reorder the last two digts. My guess is 100 20 3 4."]

def generate_player_winning_seqeunce():
    """
    Generates an action sequence leading to a win condition.
    """
    return ["I think the answer is [6 1 3 2]"]

class TestMastermindEnv(unittest.TestCase):
    """
    Test class for Mastermind environment.
    """

    ## Define environment variants as class attributes
    env_variants = [
        {"difficulty": "easy"},
        {"difficulty": "medium"},
        {"difficulty": "hard"},
    ]

    ## Test cases
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
        },
        "player_winning_easy": {
            "difficulty": "easy",
            "actions": generate_player_winning_seqeunce()
        }
    }

    @parameterized.expand([
        (name, details['difficulty'], details['actions'])
        for name, details in test_cases.items()
    ])
    def test_mastermind_outcomes(self, name, difficulty, actions):
        """
        Test the outcomes of the Mastermind environment.
        
        Args:
            name (str): Name of the test case.
            difficulty (str): Difficulty level of the environment.
            actions (List[str]): List of actions to be taken in the environment.
        """
        env_config = next((env for env in self.env_variants if env['difficulty'] == difficulty), None)
        self.assertIsNotNone(env_config, f"Environment configuration not found for difficulty level: {difficulty}")

        env = MastermindEnv(difficulty=env_config['difficulty'])

        observations = env.reset(seed=490)

        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}

        for i, action in enumerate(actions):
            if terminated or truncated:
                break
            player_id = i % 2

            env_action = action

            ## make the action
            observations, reward, truncated, terminated, info = env.step(player_id, env_action)

            ## update rewards
            if reward:
                rewards.update(reward)

        if "correct_move" in name:
            self.assertFalse(truncated, "Game should not truncate for correct moves.")
            self.assertFalse(terminated, "Game should not terminate until the puzzle is complete.")
        elif "invalid_move" in name:
            self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move.")
            self.assertEqual(rewards[player_id], -1, "Player should receive -1 reward for an invalid move.")
        elif "out_of_bounds" in name:
            self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move.")
            self.assertEqual(rewards[player_id], -1, "Player should receive -1 reward for an invalid move.")
        elif "player_winning" in name:
            self.assertTrue(terminated, "Game should terminate due to a player winning.")
            self.assertEqual(rewards[player_id], 1, f"Player {player_id} should have received +1 for winning.")
            self.assertEqual(rewards[1 - player_id], -1, f"Player {1 - player_id} should have received -1 for losing.")
        else:
            raise ValueError(f"Invalid test case name: {name}")
    
    def run_unit_test():
        print("Running Mastermind tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)