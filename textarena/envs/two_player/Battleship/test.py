import unittest
from parameterized import parameterized
from textarena.envs.two_player.Battleship.env import BattleshipEnv

## helper functions
def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct move of a Battleship puzzle.
    """
    return ["I have seen the opponent attempt to hit me at A4. I shall try to aim at their A4. My final coordinate is [A4].", "I think we can go with [J8]."]

def generate_invalid_move_sequence():
    """
    Generates an action sequence leading to an invalid move of a Battleship puzzle.
    """
    return ["I have seen the opponent attempt to hit me at A4. I shall try to aim at their A4. My final coordinate is A4.", "I think we can go with (J8)."]

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with out-of-bounds coordinates.
    """
    return ["I have seen the opponent attempt to hit me at A4. I shall try to aim at their Z100. My final coordinate is [Z100]."]

def generate_player_winning_seqeunce():
    """
    Generates an action sequence leading to a win condition.
    """
    return ['[A1]', '[E7]', '[A2]', '[F7]', '[A3]', '[G7]', '[A4]', '[H7]', '[A5]', '[I7]', '[E4]', '[C7]', '[F4]', '[D7]', '[F8]', '[F6]', '[G8]', '[G6]', '[H8]', '[H6]', '[G4]', '[H3]', '[G5]', '[I3]', '[G6]', '[J3]', '[C4]', '[J5]', '[C5]', '[J6]', '[C6]', '[J7]', '[C7]']

class TestBattleshipEnv(unittest.TestCase):
    """
    Test class for Battleship environment.
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
    def test_battleship_outcomes(self, name, difficulty, actions):
        """
        Test the outcomes of the Battleship game.

        Args:
            name (str): Name of the test case.
            difficulty (str): Difficulty level of the game.
            actions (list): List of actions to take in the game.
        """
        env_config = next((env for env in self.env_variants if env['difficulty'] == difficulty), None)
        self.assertIsNotNone(env_config, f"Environment configuration not found for difficulty level: {difficulty}")

        env = BattleshipEnv(difficulty=env_config['difficulty'])

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
            observations, reward, truncated, terminated, info = env.step(player_id=player_id, action=env_action)

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
        print("Running Battleship tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)