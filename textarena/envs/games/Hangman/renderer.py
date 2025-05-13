from typing import Dict, Any


def create_board_str(game_state: Dict[str, Any]) -> str:
    """ Render the Hangman board showing the current guessed word and a hangman drawing based on tries left """
    board = game_state.get("board", [])
    # tries_left = game_state['tries_left'] #, 6)

    # Join the current word with spaces
    # word_display = " ".join(game_state[""])

    # Hangman ASCII art (indexed by remaining tries: 6 down to 0)
    hangman_stages = [
        [
            "  _______     ",
            " |/      |    ",
            " |      (X)   ",
            " |      /|\   ",
            " |      / \   ",
            " |            ",
            "_|___         "
        ],
        [
            "  _______     ",
            " |/      |    ",
            " |      (X)   ",
            " |      /|\   ",
            " |      /     ",
            " |            ",
            "_|___         "
        ],
        [
            "  _______     ",
            " |/      |    ",
            " |      (X)   ",
            " |      /|\   ",
            " |            ",
            " |            ",
            "_|___         "
        ],
        [
            "  _______     ",
            " |/      |    ",
            " |      (X)   ",
            " |      /|    ",
            " |            ",
            " |            ",
            "_|___         "
        ],
        [
            "  _______     ",
            " |/      |    ",
            " |      (X)   ",
            " |       |    ",
            " |            ",
            " |            ",
            "_|___         "
        ],
        [
            "  _______     ",
            " |/      |    ",
            " |      (X)   ",
            " |            ",
            " |            ",
            " |            ",
            "_|___         "
        ],
        [
            "  _______     ",
            " |/      |    ",
            " |            ",
            " |            ",
            " |            ",
            " |            ",
            "_|___         "
        ],
    ]

    hangman_drawing = hangman_stages[::-1][max(0, min(6, 6 - game_state['tries_left']))]

    return (
        f"🎯 Word: {game_state['target_word']}\n\n" +
        "\n".join(hangman_drawing) +
        f"\n\n❤️ Tries left: {game_state['tries_left']}"
    )