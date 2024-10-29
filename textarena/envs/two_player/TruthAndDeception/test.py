import unittest
from parameterized import parameterized
from truth_and_deception_env import TruthAndDeceptionEnv  # Adjust the import path as necessary


class TestTruthAndDeceptionEnv(unittest.TestCase):

    # Define test cases as class attributes
    test_cases = {
        "valid_conversation_and_correct_guess": {
            "env_id": "TruthDeception-v0",
            "max_turns": 5,
            "actions": [
                "I believe [Fact 1] is more plausible.",
                "I think [Fact 2] is the real one.",
                "Don't you agree that [Fact 1] makes more sense?",
                "I'm convinced that [Fact 2] is accurate.",
                "Finally, [Fact 1] seems the true fact.",
                "[Fact 1]"  # Guesser's guess
            ],
            "expected_rewards": {0: -1, 1: 1},
            "expected_terminated": True
        },
        "valid_conversation_and_incorrect_guess": {
            "env_id": "TruthDeception-v0",
            "max_turns": 5,
            "actions": [
                "I believe [Fact 1] is more plausible.",
                "I think [Fact 2] is the real one.",
                "Don't you agree that [Fact 1] makes more sense?",
                "I'm convinced that [Fact 2] is accurate.",
                "Finally, [Fact 1] seems the true fact.",
                "[Fact 2]"  # Guesser's guess
            ],
            "expected_rewards": {0: 1, 1: -1},
            "expected_terminated": True
        },
        "resign_deceiver": {
            "env_id": "TruthDeception-v0",
            "max_turns": 5,
            "actions": [
                "[Resign]"
            ],
            "expected_rewards": {0: -1, 1: 1},
            "expected_terminated": True
        },
        "resign_guesser": {
            "env_id": "TruthDeception-v0",
            "max_turns": 5,
            "actions": [
                "I believe [Fact 1] is more plausible.",
                "[Resign]"
            ],
            "expected_rewards": {0: 0, 1: -1},
            "expected_terminated": True
        },
        "invalid_action_format": {
            "env_id": "TruthDeception-v0",
            "max_turns": 5,
            "actions": [
                "I believe Fact 1 is more plausible."  # Missing brackets
            ],
            "expected_rewards": {0: -1, 1: 0},
            "expected_terminated": True
        },
        "multiple_action_tokens": {
            "env_id": "TruthDeception-v0",
            "max_turns": 5,
            "actions": [
                "I believe [Fact 1] is correct. [Resign]"
            ],
            "expected_rewards": {0: -1, 1: 0},
            "expected_terminated": True
        },
        "invalid_guess_format": {
            "env_id": "TruthDeception-v0",
            "max_turns": 5,
            "actions": [
                "I believe [Fact 1] is more plausible.",
                "I think [Fact 2] is the real one.",
                "Don't you agree that [Fact 1] makes more sense?",
                "I'm convinced that [Fact 2] is accurate.",
                "Finally, [Fact 1] seems the true fact.",
                "Fact 1"  # Guesser's guess without brackets
            ],
            "expected_rewards": {0: 0, 1: -1},
            "expected_terminated": True
        },
        "guesser_no_guess": {
            "env_id": "TruthDeception-v0",
            "max_turns": 5,
            "actions": [
                "I believe [Fact 1] is more plausible.",
                "I think [Fact 2] is the real one.",
                "Don't you agree that [Fact 1] makes more sense?",
                "I'm convinced that [Fact 2] is accurate.",
                "Finally, [Fact 1] seems the true fact.",
                ""  # Guesser's empty guess
            ],
            "expected_rewards": {0: 0, 1: -1},
            "expected_terminated": True
        },
        "max_turns_reached_without_guess": {
            "env_id": "TruthDeception-v0-short",
            "max_turns": 3,
            "actions": [
                "I believe [Fact 1] is more plausible.",
                "I think [Fact 2] is the real one.",
                "Don't you agree that [Fact 1] makes more sense.",
                "I cannot make a guess."  # Exceeding max_turns
            ],
            "expected_rewards": {0: 0, 1: 0},
            "expected_terminated": True
        },
    }

    @parameterized.expand([
        (name, details["env_id"], details["max_turns"], details["actions"], details["expected_rewards"], details["expected_terminated"])
        for name, details in test_cases.items()
    ])
    def test_truth_and_deception_env_outcomes(self, name, env_id, max_turns, actions, expected_rewards, expected_terminated):
        """
        Test various Truth and Deception outcomes using predefined action sequences across different environment variants.

        Args:
            name (str): Test case name.
            env_id (str): Environment ID to test.
            max_turns (int): Maximum number of turns for the game.
            actions (List[str]): List of action strings to execute.
            expected_rewards (Dict[int, int]): Expected rewards after actions.
            expected_terminated (bool): Whether the game should terminate after actions.
        """
        # Initialize the environment based on env_id
        if env_id == "TruthDeception-v0":
            env = TruthAndDeceptionEnv(max_turns=max_turns)
        elif env_id == "TruthDeception-v0-short":
            env = TruthAndDeceptionEnv(max_turns=max_turns)
        else:
            env = TruthAndDeceptionEnv(max_turns=max_turns)

        # Reset the environment
        observations, info = env.reset(seed=42)

        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}

        for i, action in enumerate(actions):
            if terminated or truncated:
                break
            player_id = i % 2  # Player 0 and Player 1 alternate
            env_action = action

            # Execute the action
            observations, reward, truncated, terminated, info = env.step(player_id, env_action)

            # Update rewards
            if reward:
                rewards.update(reward)

        # Check if the game termination status matches expectation
        self.assertEqual(terminated or truncated, expected_terminated, f"Test '{name}' failed on termination status.")

        # Check if the rewards match expectation
        self.assertEqual(rewards, expected_rewards, f"Test '{name}' failed on rewards.")

    def run_unit_tests():
        """
        Runs the unittest when this script is executed directly.
        """
        unittest.main(argv=['first-arg-is-ignored'], exit=False)


# Uncomment the following lines to run tests when this script is executed directly
# if __name__ == '__main__':
#     run_unit_tests()
