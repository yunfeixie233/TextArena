from textarena.envs.two_player.DontSayIt.env import DontSayItEnv

import warnings
import unittest
from parameterized import parameterized

# Suppress specific warnings to keep test output clean
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


# Yield functions
def yield_normal_game_sequence(num_turns, secret_word):
    """
    Generator that yields a sequence of empty actions representing a normal game play
    where no player mentions the secret word.

    Args:
        num_turns (int): The total number of turns in the game.
        secret_word (str): The secret word that should not be mentioned.

    Yields:
        str: An empty action (represented by a single space) for each turn.
    """
    for _ in range(num_turns):
        yield " "

def yield_word_mentioned_sequence(num_turns, secret_word):
    """
    Generator that yields a sequence of actions where the player accidentally mentions
    the opponent's secret word after a certain number of turns.

    Args:
        num_turns (int): The total number of turns in the game.
        secret_word (str): The opponent's secret word to be mentioned.

    Yields:
        str: An action string. Initially empty actions are yielded, and after a quarter
             of the total turns, the secret word is mentioned.
    """
    for i in range(num_turns):
        if i > num_turns//4:
            yield f"Omg, I accidentally mentioned: {secret_word}"
        else:
            yield " "

class TestDontSayItEnv(unittest.TestCase):
    """
    Unit test suite for the 'DontSayIt' environment variants. This class tests different
    scenarios to ensure the environment behaves as expected under various conditions.
    """
    # Define test cases as class attributes
    test_cases = {
        "Normal Game (Draw)": {
            "env_id": "DontSayIt-v0",
            "actions": {
                0: yield_normal_game_sequence,
                1: yield_normal_game_sequence,
            },
            "expected_rewards": {0: 0, 1: 0},
            "expected_truncated": True,
            "expected_terminated": False,
            "num_turns": 31
        },
        "Player 0 says opponent word": {
            "env_id": "DontSayIt-v0",
            "actions": {
                0: yield_word_mentioned_sequence,
                1: yield_normal_game_sequence,
            },
            "expected_rewards": {0: -1, 1: 1},
            "expected_truncated": False,
            "expected_terminated": True,
            "num_turns": 31
        },
        "Player 1 says opponent word": {
            "env_id": "DontSayIt-v0",
            "actions": {
                0: yield_normal_game_sequence,
                1: yield_word_mentioned_sequence,
            },
            "expected_rewards": {0: 1, 1: -1},
            "expected_truncated": False,
            "expected_terminated": True,
            "num_turns": 31
        },

        "Normal Game (Draw) [DontSayIt-v0-hardcore]": {
            "env_id": "DontSayIt-v0-hardcore",
            "actions": {
                0: yield_normal_game_sequence,
                1: yield_normal_game_sequence,
            },
            "expected_rewards": {0: 0, 1: 0},
            "expected_truncated": True,
            "expected_terminated": False,
            "num_turns": 31
        },
        "Player 0 says opponent word [DontSayIt-v0-hardcore]": {
            "env_id": "DontSayIt-v0-hardcore",
            "actions": {
                0: yield_word_mentioned_sequence,
                1: yield_normal_game_sequence,
            },
            "expected_rewards": {0: -1, 1: 1},
            "expected_truncated": False,
            "expected_terminated": True,
            "num_turns": 31
        },
        "Player 1 says opponent word [DontSayIt-v0-hardcore]": {
            "env_id": "DontSayIt-v0-hardcore",
            "actions": {
                0: yield_normal_game_sequence,
                1: yield_word_mentioned_sequence,
            },
            "expected_rewards": {0: 1, 1: -1},
            "expected_truncated": False,
            "expected_terminated": True,
            "num_turns": 31
        },
    }



    @parameterized.expand([
        (name, details["env_id"], details["actions"], details["num_turns"], details["expected_rewards"],
         details["expected_truncated"], details["expected_terminated"])
        for name, details in test_cases.items()
    ])
    def test_dont_say_it_outcomes(
        self, 
        name, 
        env_id, 
        action_yield_fns, 
        num_turns,
        expected_rewards,
        expected_truncated,
        expected_terminated
    ):
        """
        Parameterized test method that verifies the outcomes of different game scenarios
        in the 'DontSayIt' environment.

        Args:
            name (str): The name of the test case.
            env_id (str): The identifier for the environment variant to be tested.
            action_yield_fns (Dict[int, callable]): A dictionary mapping player IDs to their
                respective action generator functions.
            num_turns (int): The number of turns to simulate in the game.
            expected_rewards (Dict[int, int]): The expected rewards for each player at the end
                of the game.
            expected_truncated (bool): Whether the game is expected to be truncated.
            expected_terminated (bool): Whether the game is expected to be terminated.
        """
        try:
            # Initialize the enviornment
            env = DontSayItEnv(
                max_turns=30,
                hardcore=True if "hardcore" in env_id else False
            )
        except Exception as e:
            self.fail(f"Failed to initialize environment '{env_id}': {e}")


        try:
            # Reset the environment
            observations = env.reset(seed=42)
        except Exception as e:
            self.fail(f"Failed to reset the environment {env_id}: {e}")


        p0_secret = env.state.game_state["target_words"][0]
        p1_secret = env.state.game_state["target_words"][1]
        
        # get generators
        p0_yield = action_yield_fns[0](num_turns, p1_secret)
        p1_yield = action_yield_fns[1](num_turns, p0_secret)


        # Initialize game state
        terminated = False 
        truncated = False 

        # Run game loop
        while not (terminated or truncated):
            for player_id, yield_fn in enumerate([p0_yield, p1_yield]):
                action = next(yield_fn)

                # Execute the action
                try:
                    step_result = env.step(player_id, action)
                    if len(step_result) != 5:
                        self.fail(f"env.step() returned {len(step_result)} elements, expected 5.")
                    observations, rewards, truncated, terminated, info = step_result
                except Exception as e:
                    self.fail(f"env.step() raised an unexpected exception for player {player_id}: {e}")

                if terminated or truncated:
                    break 

        # Check the expected outcome
        self.assertEqual(
            rewards, 
            expected_rewards, 
            f"The rewards did not match. Expected {expected_rewards}; received {rewards}"
        )

        self.assertEqual(
            terminated,
            expected_terminated,
            f"Terminated flag mismatch. Expected {expected_terminated}; received {terminated}"
        )

        self.assertEqual(
            truncated,
            expected_truncated,
            f"Truncated flag mismatch. Expected {expected_truncated}; received {truncated}"
        )

# Run the tests
if __name__ == '__main__':
    unittest.main()
