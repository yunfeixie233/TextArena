import unittest
from parameterized import parameterized
import warnings
from typing import Dict, List, Optional

from textarena.envs.two_player.TruthAndDeception.env import TruthAndDeceptionEnv

# Suppress warnings for cleaner test output
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)



def action_list_correct_guess(correct_fact):
    return [
        "Convincing Argument", "Nice Reply",
        "Convincing Argument", "Nice Reply",
        "Convincing Argument", 
        correct_fact
    ]

def action_list_wrong_guess(correct_fact):
    guess_fact = "[Fact 1]" if correct_fact == "[Fact 2]" else "[Fact 2]"
    return [
        "Convincing Argument", "Nice Reply",
        "Convincing Argument", "Nice Reply",
        "Convincing Argument", 
        guess_fact
    ]

def wrong_format_guess(correct_fact):
    return [
        "Convincing Argument", "Nice Reply",
        "Convincing Argument", "Nice Reply",
        "Convincing Argument", 
        "I invoke the 5th"
    ]


class TestTruthAndDeceptionEnv(unittest.TestCase):
    """
    Unit test suite for the 'TruthAndDeceptionEnv' environment. This class tests various scenarios
    to ensure the environment behaves as expected under different conditions.
    """
    
    # Define test cases as class attributes
    test_cases = {
        "Correct Guess After Full Conversation": {
            "env_id": "TruthAndDeception-v0",
            "actions": action_list_correct_guess,
            "expected_rewards": {0: -1, 1: 1},  # Guesser wins if they pick the correct fact
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Incorrect Guess After Full Conversation": {
            "env_id": "TruthAndDeception-v0",
            "actions": action_list_wrong_guess,
            "expected_rewards": {0: 1, 1: -1},  # Deceiver wins if Guesser guesses wrong
            "expected_truncated": False,
            "expected_terminated": True,
        },
        "Invalid Guess Format": {
            "env_id": "TruthAndDeception-v0",
            "actions": wrong_format_guess,
            "expected_rewards": {0: 0, 1: -1},  # Guesser penalized for invalid format
            "expected_truncated": False,
            "expected_terminated": True,
        },
        # "Early Guess Without Full Turns": {
        #     "env_id": "TruthAndDeception-v0",
        #     "actions": ["Message"] * 2 + ["[Fact 1]"],
        #     "expected_rewards": {0: 1, 1: -1},  # Penalized for guessing early
        #     "expected_truncated": True,
        #     "expected_terminated": False,
        # },
    }

    @parameterized.expand([
        (
            name,
            details["env_id"],
            details["actions"],
            details["expected_rewards"],
            details["expected_truncated"],
            details["expected_terminated"]
        )
        for name, details in test_cases.items()
    ])
    def test_truth_and_deception_env_outcomes(
        self,
        name: str,
        env_id: str,
        actions: List[str],
        expected_rewards: Optional[Dict[int, int]],
        expected_truncated: bool,
        expected_terminated: bool
    ):
        """
        Parameterized test method that verifies the outcomes of different game scenarios
        in the 'TruthAndDeceptionEnv' environment.

        Args:
            name (str): The name of the test case.
            env_id (str): The identifier for the environment variant to be tested.
            actions (List[str]): A list of actions to be executed in sequence.
            expected_rewards (Optional[Dict[int, int]]): The expected rewards for each player at the end
                of the game.
            expected_truncated (bool): Whether the game is expected to be truncated.
            expected_terminated (bool): Whether the game is expected to be terminated.
        """
        with self.subTest(test_case=name):
            try:
                # Initialize the environment
                env = TruthAndDeceptionEnv(
                    max_turns=6
                )
            except Exception as e:
                self.fail(f"Failed to initialize environment '{env_id}': {e}")

            try:
                # Reset the environment with a fixed seed for reproducibility
                observations = env.reset(seed=42)
            except Exception as e:
                self.fail(f"Failed to reset the environment '{env_id}': {e}")

            # Initialize game state flags
            terminated = False
            truncated = False

            actions = actions("[Fact 1]" if env.state.game_state["fact1"]["is_correct"] else "[Fact 2]")

            for i, action in enumerate(actions):
                player_id = i % 2

                try:
                    # Execute the action in the environment
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
