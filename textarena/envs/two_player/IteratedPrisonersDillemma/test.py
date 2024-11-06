import unittest
from parameterized import parameterized
from iterated_prisoners_dilemma import (
    PrisonersDilemmaEnv,
)  # Adjust the import path as necessary


class TestIPDEnv(unittest.TestCase):

    # Define test cases as class attributes
    test_cases = {
        # "valid_move_white": {
        #     "env_id": "Chess-v0",
        #     "actions": ["[Move] e2e4"],
        #     "expected_rewards": {0: 0, 1: 0},
        #     "expected_terminated": False,
        # },
        "valid_move_both": {
            "env_id": "IPD-fixed-1",
            "actions": ["cooperate", "cooperate"],
            "expected_rewards": {0: 0, 1: 0},
            "expected_terminated": True,
        },
        "valid_move_w_messages": {
            "env_id": "IPD-fixed-1",
            "actions": ["I will cooperate\ndefect", "I will cooperate\ndefect"],
            "expected_rewards": {0: 0, 1: 0},
            "expected_terminated": True,
        },
        "correct_payoff_0_winner": {
            "env_id": "IPD-fixed-1",
            "actions": ["cooperate", "defect"],
            "expected_rewards": {0: -1, 1: 1},
            "expected_terminated": True,
        },
        "correct_payoff_1_winner": {
            "env_id": "IPD-fixed-1",
            "actions": ["defect", "cooperate"],
            "expected_rewards": {0: 1, 1: -1},
            "expected_terminated": True,
        },
        "unfinished_game": {
            "env_id": "IPD-fixed-1",
            "actions": ["cooperate"],
            "expected_rewards": {0: 0, 1: 0},
            "expected_terminated": False,
        },
        "invalid_move_p0": {
            "env_id": "IPD-fixed-1",
            "actions": ["[Move] e2e4"],
            "expected_rewards": {0: -1, 1: 0},
            "expected_terminated": True,
        },
        "invalid_move_p1": {
            "env_id": "IPD-fixed-1",
            "actions": ["cooperate", "invalid"],
            "expected_rewards": {0: 0, 1: -1},
            "expected_terminated": True,
        },
    }

    @parameterized.expand(
        [
            (
                name,
                details["env_id"],
                details["actions"],
                details["expected_rewards"],
                details["expected_terminated"],
            )
            for name, details in test_cases.items()
        ]
    )
    def test_iterated_prisoners_dilemma(
        self, name, env_id, actions, expected_rewards, expected_terminated
    ):
        """
        Tests various scenarios in the IPD environment.
        Args:
            name (str): Name of the test case.
            env_id (str): Environment ID.
            actions (List[str]): List of actions to take.
            expected_rewards (Dict[int, int]): Expected rewards for each player.
            expected_terminated (bool): Expected termination status.
        """
        if env_id == "IPD-fixed-1":
            env = PrisonersDilemmaEnv(max_rounds=1, mode="fixed")
        env.reset()

        terminated = False
        truncated = False
        rewards = {0: 0, 1: 0}

        for i, action in enumerate(actions):
            if terminated or truncated:
                break
            player_id = i % 2  # Player 0 and Player 1 alternate
            env_action = action

            # Execute the action
            observations, reward, truncated, terminated, info = env.step(
                player_id, env_action
            )

            # Update rewards
            if reward:
                rewards.update(reward)

        # Check if the game termination status matches expectation
        self.assertEqual(
            terminated or truncated,
            expected_terminated,
            f"Test '{name}' failed on termination status.",
        )

        # Check if the rewards match expectation
        self.assertEqual(rewards, expected_rewards, f"Test '{name}' failed on rewards.")

    def run_unit_tests():
        """
        Runs the unittest when this script is executed directly.
        """
        unittest.main(argv=["first-arg-is-ignored"], exit=False)


# Uncomment the following lines to run tests when this script is executed directly
if __name__ == "__main__":
    TestIPDEnv.run_unit_tests()
