import unittest
from parameterized import parameterized
from chess_env import ChessEnv  # Adjust the import path as necessary


class TestChessEnv(unittest.TestCase):

    # Define test cases as class attributes
    test_cases = {
        "valid_move_white": {
            "env_id": "Chess-v0",
            "actions": [
                "[Move] e2e4"
            ],
            "expected_rewards": {0: 0, 1: 0},
            "expected_terminated": False
        },
        "valid_move_black": {
            "env_id": "Chess-v0",
            "actions": [
                "[Move] e2e4",
                "[Move] e7e5"
            ],
            "expected_rewards": {0: 0, 1: 0},
            "expected_terminated": False
        },
        "resign_white": {
            "env_id": "Chess-v0",
            "actions": [
                "[Resign]"
            ],
            "expected_rewards": {0: -1, 1: 1},
            "expected_terminated": True
        },
        "resign_black": {
            "env_id": "Chess-v0",
            "actions": [
                "[Move] e2e4",
                "[Resign]"
            ],
            "expected_rewards": {0: 0, 1: -1},
            "expected_terminated": True
        },
        "invalid_move_format": {
            "env_id": "Chess-v0",
            "actions": [
                "I move to e2e4"  # Missing [Move] token
            ],
            "expected_rewards": {0: -1, 1: 0},
            "expected_terminated": True
        },
        "multiple_action_tokens": {
            "env_id": "Chess-v0",
            "actions": [
                "[Move] e2e4 [Resign]"
            ],
            "expected_rewards": {0: -1, 1: 0},
            "expected_terminated": True
        },
        "illegal_move_white": {
            "env_id": "Chess-v0",
            "actions": [
                "[Move] e2e5"  # Illegal pawn move
            ],
            "expected_rewards": {0: -1, 1: 0},
            "expected_terminated": True
        },
        "illegal_move_black": {
            "env_id": "Chess-v0",
            "actions": [
                "[Move] e2e4",
                "[Move] e7e6",
                "[Move] e4e5",
                "[Move] e6e5"  # Black pawn takes white pawn
            ],
            "expected_rewards": {0: 0, 1: 0},
            "expected_terminated": False
        },
        "draw_by_max_turns": {
            "env_id": "Chess-v0-short",
            "actions": [
                "[Move] e2e4",
                "[Move] e7e5",
                "[Move] g1f3",
                "[Move] b8c6",
                "[Move] f1c4",
                "[Move] g8f6",
                "[Move] d2d3",
                "[Move] f8c5",
                "[Move] c1g5",
                "[Move] d7d6",
                # Exceeding max_turns=10
                "[Move] b1c3",
                "[Move] c8g4",
                "[Move] g5f6",
                "[Move] g7g6",
                "[Move] g5e3",
                "[Move] h7h5",
                "[Move] e3c5",
                "[Move] d6c5",
                "[Move] d1d3",
                "[Move] c5d4",
            ],
            "expected_rewards": {0: 0, 1: 0},
            "expected_terminated": True
        },
    }

    @parameterized.expand([
        (name, details["env_id"], details["actions"], details["expected_rewards"], details["expected_terminated"])
        for name, details in test_cases.items()
    ])
    def test_chess_env_outcomes(self, name, env_id, actions, expected_rewards, expected_terminated):
        """
        Test various Chess outcomes using predefined action sequences across different environment variants.
        Args:
            name (str): Test case name.
            env_id (str): Environment ID to test.
            actions (List[str]): List of action strings to execute.
            expected_rewards (Dict[int, int]): Expected rewards after actions.
            expected_terminated (bool): Whether the game should terminate after actions.
        """
        # Initialize the environment based on env_id
        # For this example, we assume all env_ids use ChessEnv with appropriate parameters
        if env_id == "Chess-v0":
            env = ChessEnv(is_open=True, max_turns=30, show_valid=True)
        elif env_id == "Chess-v0-short":
            env = ChessEnv(is_open=True, max_turns=10, show_valid=True)
        else:
            env = ChessEnv()

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
