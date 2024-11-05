import unittest
from parameterized import parameterized
from textarena.envs.two_player.MemoryGame.env import MemoryGameEnv
import json

## Helper Functions
def generate_normal_game_sequence(player_moves):
    """
    Generates a sequence of valid player moves without triggering any win or loss conditions.
    
    Args:
        player_moves (List[int]): List of moves from players alternating.
    
    Returns:
        List[int]: Action sequence of player moves.
    """
    actions = []
    for move in player_moves:
        actions.append(move)
    return actions

def generate_correct_move_sequence():
    """
    Generates an action sequence leading to a correct completion of a Memory Game puzzle.
    Note: This assumes that the board setup supports the sequence.
    """
    return ["[2 1 2 2]", "[0 1 1 3]"]

def generate_invalid_move_sequence():
    """
    Generates an action sequence where a player attempts to flip a card that is already matched.
    """
    return ["(0 0) (1 2)", "[0 0] [1 2]", "[0 0 0 0]"]

def generate_out_of_bounds_sequence():
    """
    Generates an action sequence with out-of-bounds card indices.
    """
    return ["[10 10 11 11]"]

def generate_draw_winning_seqeunce():
    """
    Generates an action sequence leading to a win condition.
    """
    return ["[0 0 3 2]", "[0 1 1 3]", "[0 2 3 0]", "[0 3 1 2]", "[1 0 2 3]", "[1 1 2 0]", "[2 1 2 2]", "[3 1 3 3]"]

def generate_player_winning_seqeunce():
    """
    Generates an action sequence leading to a win condition.
    """
    return ["[0 0 3 2]", "[0 1 1 3]", "[0 2 3 0]", "[0 3 1 2]", "[1 0 2 3]", "[1 1 2 1]", "[1 1 2 0]", "[2 1 2 2]", "[3 1 3 3]"] # [1 1 2 1] is the incorrect move

class TestMemoryGameEnv(unittest.TestCase):
    """
    Test class for Memory Game environment.
    """

    ## define environment variants as class attributes
    env_variants = [
        {"difficulty": "easy"},
        {"difficulty": "medium"},
        {"difficulty": "hard"}
    ]

    ## define test cases as class attributes
    test_cases = {
        "normal_game_easy": {
            "difficulty": "easy",
            "actions": generate_normal_game_sequence([
                "[0 0 1 1]", "[2 2 3 3]", "[0 1 2 3]", "[0 1 2 3]"
            ])
        },
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
        "draw_winning_easy": {
            "difficulty": "easy",
            "actions": generate_draw_winning_seqeunce()
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
    def test_memorygame_outcomes(self, name, difficulty, actions):
        """
        Test the outcomes of the Memory Game environment.
        
        Args:
            name (str): Name of the test case.
            difficulty (str): Difficulty level of the game.
            actions (List[str]): List of actions to be taken by the players.
        """
        env_config = next((env for env in self.env_variants if env['difficulty'] == difficulty), None)
        self.assertIsNotNone(env_config, f"Invalid difficulty level: {difficulty}")

        env = MemoryGameEnv(difficulty=env_config['difficulty'])
        
        observations = env.reset(seed=490)

        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}

        for i, action in enumerate(actions):
            if terminated or truncated:
                break
            player_id = i % 2
            
            env_action = action

            ## Execute the action
            observations, reward, truncated, terminated, info = env.step(player_id, env_action)

            ## update rewards
            if reward:
                rewards.update(reward)

        if "normal_game" in name:
            self.assertFalse(truncated, "Game should not truncate for normal moves.")
            self.assertFalse(terminated, "Game should not terminate until the puzzle is complete.")
        elif "correct_move" in name:
            self.assertFalse(truncated, "Game should not truncate for correct moves.")
            self.assertFalse(terminated, "Game should not terminate until the puzzle is complete.")
        elif "invalid_move" in name:
            self.assertTrue(truncated or terminated, "Game should terminate due to an invalid move.")
            self.assertEqual(rewards[player_id], -1, "Player should receive -1 reward for an invalid move.")
        elif "out_of_bounds" in name:
            self.assertTrue(truncated or terminated, "Game should terminate due to an out-of-bounds move.")
            self.assertEqual(rewards[player_id], -1, "Player should receive -1 reward for an out-of-bounds move.")
        elif "draw_winning" in name:
            self.assertTrue(terminated, "Game should terminate due to a draw.")
            self.assertEqual(rewards[player_id], 0, "Player 0 should have received 0 reward for a draw.")
            self.assertEqual(rewards[1 - player_id], 0, "Player 1 should have received 0 reward for a draw.")
        elif "player_winning" in name:
            self.assertTrue(terminated, "Game should terminate due to a player winning.")
            self.assertEqual(rewards[player_id], 1, f"Player {player_id} should have received +1 for winning.")
            self.assertEqual(rewards[1 - player_id], -1, f"Player {1 - player_id} should have received -1 for losing.")
        else:
            self.fail(f"Unknown test case name: {name}")

    def run_unit_test():
        print("Running MemoryGame tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
