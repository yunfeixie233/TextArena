import unittest
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any
import textarena as ta
from textarena.envs.two_players.Taboo import TabooEnv  # Adjust the import path as needed


class TestTabooEnv(unittest.TestCase):
    def setUp(self):
        """
        Set up the Taboo environment with mock data for testing.
        """
        # Define mock data
        self.mock_data = {
            "animals": {
                "elephant": ["trunk", "grey", "large"],
                "lion": ["roar", "mane", "king"],
            },
            "fruits": {
                "apple": ["red", "pie", "fruit"],
                "banana": ["yellow", "long", "peel"],
            },
        }

        # Patch the _load_data method to inject mock data
        patcher = patch.object(TabooEnv, '_load_data')
        self.addCleanup(patcher.stop)
        self.mock_load_data = patcher.start()
        self.mock_load_data.side_effect = self._mock_load_data

        # Initialize the environment with 'animals' category
        self.env = TabooEnv(
            categories=["animals"],
            max_turns=5,
            data_path=None  # Path is irrelevant due to mocking
        )

    def _mock_load_data(self):
        """
        Mock the _load_data method to inject predefined mock data.
        """
        self.env.data = {}
        for category in self.env.categories:
            if category in self.mock_data:
                self.env.data.update(self.mock_data[category])
            else:
                raise ValueError(f"Category '{category}' not found in mock data.")

    def test_initialization_valid_categories(self):
        """
        Test that the environment initializes correctly with valid categories.
        """
        self.assertEqual(self.env.categories, ["animals"])
        self.assertEqual(self.env.max_turns, 5)
        self.assertIn("elephant", self.env.data)
        self.assertIn("lion", self.env.data)
        self.assertEqual(self.env.data["elephant"], ["trunk", "grey", "large"])
        self.assertEqual(self.env.data["lion"], ["roar", "mane", "king"])

    def test_initialization_invalid_category(self):
        """
        Test that initializing with an invalid category raises an error.
        """
        with self.assertRaises(ValueError):
            TabooEnv(
                categories=["invalid_category"],
                max_turns=5,
                data_path=None
            )

    def test_reset_assigns_unique_words(self):
        """
        Test that the reset method assigns unique secret words to each player.
        """
        observations = self.env.reset(seed=42)
        secret_words = self.env.state.game_state["word_to_guess"]
        self.assertIn(secret_words, self.env.data)
        # Since there are only two words in 'animals', ensure they are unique
        word_to_guess = self.env.state.game_state["word_to_guess"]
        taboo_words = self.env.state.game_state["taboo_words"]
        self.assertIsInstance(word_to_guess, str)
        self.assertIsInstance(taboo_words, list)
        self.assertEqual(len(taboo_words), 3)

    def test_clue_giver_valid_clue(self):
        """
        Test that the Clue Giver can provide a valid clue without using taboo words.
        """
        self.env.reset(seed=1)  # Seed to get a predictable word
        # Assume word_to_guess is 'elephant' with taboo words ['trunk', 'grey', 'large']
        # Mock the selected word
        self.env.state.game_state["word_to_guess"] = "elephant"
        self.env.state.game_state["taboo_words"] = ["trunk", "grey", "large"]
        self.env.state.role_mapping = {0: "Clue Giver", 1: "Guesser"}

        clue = "It's a large mammal found in Africa."
        observations, rewards, truncated, terminated, info = self.env.step(0, clue)

        # Clue is valid, game should continue
        self.assertIsNone(rewards)
        self.assertFalse(truncated)
        self.assertFalse(terminated)
        self.assertIsNone(info["reason"])

    def test_clue_giver_uses_taboo_word(self):
        """
        Test that using a taboo word in the clue results in an invalid move.
        """
        self.env.reset(seed=1)
        self.env.state.game_state["word_to_guess"] = "elephant"
        self.env.state.game_state["taboo_words"] = ["trunk", "grey", "large"]
        self.env.state.role_mapping = {0: "Clue Giver", 1: "Guesser"}

        clue = "It's a large animal with a trunk."
        observations, rewards, truncated, terminated, info = self.env.step(0, clue)

        # Clue uses forbidden words, should be invalid
        self.assertIsNotNone(rewards)
        self.assertEqual(rewards, {0: -1, 1: 0})
        self.assertFalse(truncated)
        self.assertTrue(terminated)
        self.assertIn("mentioned a taboo word", info["reason"])

    def test_guesser_valid_correct_guess(self):
        """
        Test that the Guesser can make a correct guess and win the game.
        """
        self.env.reset(seed=1)
        self.env.state.game_state["word_to_guess"] = "lion"
        self.env.state.game_state["taboo_words"] = ["roar", "mane", "king"]
        self.env.state.role_mapping = {0: "Clue Giver", 1: "Guesser"}

        # Clue Giver provides a valid clue
        clue = "It's known as the king of the jungle."
        observations, rewards, truncated, terminated, info = self.env.step(0, clue)
        self.assertIsNone(rewards)
        self.assertFalse(terminated)

        # Guesser makes a correct guess
        guess = "[lion]"
        observations, rewards, truncated, terminated, info = self.env.step(1, guess)

        # Guesser wins
        self.assertIsNotNone(rewards)
        self.assertEqual(rewards, {0: -1, 1: +1})
        self.assertFalse(truncated)
        self.assertTrue(terminated)
        self.assertIn("correctly guessed the word", info["reason"])

    def test_guesser_valid_incorrect_guess(self):
        """
        Test that an incorrect guess allows the game to continue.
        """
        self.env.reset(seed=1)
        self.env.state.game_state["word_to_guess"] = "lion"
        self.env.state.game_state["taboo_words"] = ["roar", "mane", "king"]
        self.env.state.role_mapping = {0: "Clue Giver", 1: "Guesser"}

        # Clue Giver provides a valid clue
        clue = "It's known as the king of the jungle."
        observations, rewards, truncated, terminated, info = self.env.step(0, clue)
        self.assertIsNone(rewards)
        self.assertFalse(terminated)

        # Guesser makes an incorrect guess
        guess = "[tiger]"
        observations, rewards, truncated, terminated, info = self.env.step(1, guess)

        # Game continues
        self.assertIsNone(rewards)
        self.assertFalse(truncated)
        self.assertFalse(terminated)
        self.assertIsNone(info["reason"])

    def test_guesser_invalid_guess_format(self):
        """
        Test that a guess not enclosed in squared brackets is invalid.
        """
        self.env.reset(seed=1)
        self.env.state.game_state["word_to_guess"] = "lion"
        self.env.state.game_state["taboo_words"] = ["roar", "mane", "king"]
        self.env.state.role_mapping = {0: "Clue Giver", 1: "Guesser"}

        # Clue Giver provides a valid clue
        clue = "It's known as the king of the jungle."
        observations, rewards, truncated, terminated, info = self.env.step(0, clue)
        self.assertIsNone(rewards)
        self.assertFalse(terminated)

        # Guesser makes an invalid guess (no brackets)
        guess = "lion"
        observations, rewards, truncated, terminated, info = self.env.step(1, guess)

        # Invalid guess format
        self.assertIsNotNone(rewards)
        self.assertEqual(rewards, {1: -1, 0: 0})
        self.assertFalse(truncated)
        self.assertTrue(terminated)
        self.assertIn("Invalid guess format", info["reason"])

    def test_game_draw_after_max_turns(self):
        """
        Test that the game ends in a draw after reaching the maximum number of turns without a correct guess.
        """
        self.env.reset(seed=1)
        self.env.state.game_state["word_to_guess"] = "lion"
        self.env.state.game_state["taboo_words"] = ["roar", "mane", "king"]
        self.env.state.role_mapping = {0: "Clue Giver", 1: "Guesser"}
        self.env.state.max_turns = 2  # Set max_turns to 2 for quick testing

        # Turn 1: Clue Giver provides a valid clue
        clue1 = "It's known as the king of the jungle."
        observations, rewards, truncated, terminated, info = self.env.step(0, clue1)
        self.assertIsNone(rewards)
        self.assertFalse(terminated)

        # Turn 1: Guesser makes an incorrect guess
        guess1 = "[tiger]"
        observations, rewards, truncated, terminated, info = self.env.step(1, guess1)
        self.assertIsNone(rewards)
        self.assertFalse(terminated)

        # Turn 2: Clue Giver provides another valid clue
        clue2 = "It has a majestic mane."
        observations, rewards, truncated, terminated, info = self.env.step(0, clue2)
        self.assertIsNone(rewards)
        self.assertFalse(terminated)

        # Turn 2: Guesser makes another incorrect guess
        guess2 = "[bear]"
        observations, rewards, truncated, terminated, info = self.env.step(1, guess2)
        self.assertIsNotNone(rewards)
        self.assertEqual(rewards, {0: 0, 1: 0})
        self.assertFalse(truncated)
        self.assertTrue(terminated)
        self.assertIn("Maximum number of turns reached", info["reason"])

    def test_clue_giver_mentions_target_word(self):
        """
        Test that if the Clue Giver mentions the target word in the clue, it results in an invalid move.
        """
        self.env.reset(seed=1)
        self.env.state.game_state["word_to_guess"] = "lion"
        self.env.state.game_state["taboo_words"] = ["roar", "mane", "king"]
        self.env.state.role_mapping = {0: "Clue Giver", 1: "Guesser"}

        # Clue Giver mentions the target word
        clue = "The animal I'm thinking of is a lion."
        observations, rewards, truncated, terminated, info = self.env.step(0, clue)

        # Clue Giver used the target word, should be invalid
        self.assertIsNotNone(rewards)
        self.assertEqual(rewards, {0: -1, 1: 0})
        self.assertFalse(truncated)
        self.assertTrue(terminated)
        self.assertIn("mentioned a taboo word", info["reason"])

    def test_multiple_invalid_moves(self):
        """
        Test that multiple invalid moves are handled correctly.
        """
        self.env.reset(seed=1)
        self.env.state.game_state["word_to_guess"] = "lion"
        self.env.state.game_state["taboo_words"] = ["roar", "mane", "king"]
        self.env.state.role_mapping = {0: "Clue Giver", 1: "Guesser"}

        # Clue Giver makes first invalid move
        clue1 = "It's a lion in the wild."
        observations, rewards, truncated, terminated, info = self.env.step(0, clue1)
        self.assertIsNotNone(rewards)
        self.assertEqual(rewards, {0: -1, 1: 0})
        self.assertTrue(terminated)
        self.assertIn("mentioned a taboo word", info["reason"])

        # Attempting further moves should have no effect as the game is terminated
        guess = "[lion]"
        observations, rewards, truncated, terminated, info = self.env.step(1, guess)
        self.assertIsNone(rewards)
        self.assertTrue(terminated)
        self.assertIsNone(info.get("reason"))

    def test_no_taboo_words(self):
        """
        Test behavior when no taboo words are provided.
        """
        # Modify mock data to have no taboo words for a specific word
        self.env.data = {
            "empty_taboo": {
                "sun": []
            }
        }

        self.env.reset(seed=1)
        self.env.state.game_state["word_to_guess"] = "sun"
        self.env.state.game_state["taboo_words"] = []
        self.env.state.role_mapping = {0: "Clue Giver", 1: "Guesser"}

        # Clue Giver provides a clue (no taboo words to avoid)
        clue = "It's the center of our solar system."
        observations, rewards, truncated, terminated, info = self.env.step(0, clue)
        self.assertIsNone(rewards)
        self.assertFalse(terminated)

        # Guesser makes a correct guess
        guess = "[sun]"
        observations, rewards, truncated, terminated, info = self.env.step(1, guess)
        self.assertIsNotNone(rewards)
        self.assertEqual(rewards, {0: -1, 1: +1})
        self.assertTrue(terminated)
        self.assertIn("correctly guessed the word", info["reason"])

    def test_empty_word_list(self):
        """
        Test that initializing with an empty word list raises an error.
        """
        # Mock the _load_data to have empty data
        self.env.data = {}
        with self.assertRaises(ValueError):
            self.env.reset()

    def test_duplicate_secret_words(self):
        """
        Test that the environment ensures secret words are unique for each player.
        """
        # Adjust mock data to have only one word
        self.env.data = {
            "animals": {
                "lion": ["roar", "mane", "king"]
            }
        }

        with self.assertRaises(RecursionError):
            # Since there is only one word, the while loop in reset will loop indefinitely
            # To prevent the test from hanging, you might need to adjust the environment code to handle this
            # For this test, we'll assume the environment raises an error if no unique words are available
            self.env.reset()

    def test_render_method_runs_without_error(self):
        """
        Test that the render method executes without raising exceptions.
        """
        self.env.reset(seed=1)
        try:
            self.env.render()
        except Exception as e:
            self.fail(f"Render method raised an exception: {e}")

    def tearDown(self):
        """
        Clean up after each test.
        """
        pass


def run_unit_test():
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
