"""Implements the word ladder game"""

import textarena as ta
import networkx as nx
import nltk
from nltk.corpus import words
import random
import re

nltk.download("words")
WORD_LIST_REGEX = re.compile(r"^[a-zA-Z]+$")


class WordLadderGame(ta.Env):
    """Environment for playing the word ladder game,
    finding a sequence of words that connect two given words of the same length
    by changing one letter at a time.

    Reward is inversely proportional to the number of steps taken to reach the target word.
    """

    def __init__(self, word_len: int = 4):
        super().__init__()
        self.word_graph = None
        self.build_word_graph(word_len=word_len)

    def build_word_graph(self, word_len: int):
        """Builds a graph where each word is a node and two words are connected
        if they differ by exactly one letter.
        """
        graph = nx.Graph()
        k_len_words = [word for word in words.words() if len(word) == word_len]
        graph.add_nodes_from(k_len_words)
        for i, word in enumerate(k_len_words):
            for other_word in k_len_words[i + 1 :]:
                if sum(a != b for a, b in zip(word, other_word)) == 1:
                    graph.add_edge(word, other_word)
        self.word_graph = graph

    def reset(self, seed=None) -> tuple[ta.Observation, ta.Info]:
        """Reset the environment to its initial state.

        chooses two random words of the same length from the word list.
        Conducts a random walk on the word graph to find two connected words.
        """
        # choose words of same length by random walk on the word graph
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()
        start_word = random.choice(list(self.word_graph.nodes()))
        current_word = start_word
        for _ in range(100):
            current_word = random.choice(list(self.word_graph.neighbors(current_word)))
        target_word = current_word
        assert target_word != start_word
        self.game_state = ta.State(
            render={"start_word": start_word, "target_word": target_word},
            logs=[],
            player_map={0: "Player"},
        )
        return (
            {0: [(ta.GAME_ID, self._get_prompt(start_word, target_word))]},
            {"start_word": start_word, "target_word": target_word},
        )

    def _get_prompt(self, start_word, target_word):
        """Returns a prompt for the player."""
        return (
            "You are playing the word ladder game."
            f"Find a sequence of words to convert '{start_word}' to '{target_word}'"
        )

    def step(self, player_id, action):
        """Take a step in the environment."""
        message = (0, action)
        start_word = self.game_state.render["start_word"]
        target_word = self.game_state.render["target_word"]
        match = WORD_LIST_REGEX.match(action)
        if not match:
            return (
                {0: [message, (ta.GAME_ID, "Invalid word list format.")]},
                {0: -1},
                False,
                False,
                {},
            )
        word_list = action.split(",")
        word_list = [word.strip() for word in word_list]
        if word_list[0] != start_word or word_list[-1] != target_word:
            return (
                {
                    0: [
                        message,
                        (
                            ta.GAME_ID,
                            "Word list must start and end with the given words.",
                        ),
                    ]
                },
                {0: -1},
                False,
                False,
                {},
            )
        if not all(
            sum(a != b for a, b in zip(word_list[i], word_list[i + 1])) == 1
            for i in range(len(word_list) - 1)
        ):
            return (
                {
                    0: [
                        message,
                        (ta.GAME_ID, "Words must differ by exactly one letter."),
                    ]
                },
                {0: -1},
                False,
                False,
                {},
            )
        if word_list[-1] != target_word:
            return (
                {0: [message, (ta.GAME_ID, "The last word must be the target word.")]},
                {0: -1},
                False,
                False,
                {},
            )
        return (
            {0: [message, (ta.GAME_ID, "You found the word ladder!")]},
            {0: 1},
            False,
            True,
            {},
        )
