from textarena.games.dont_say_it import DontSayItGame

GAME_DICT = {
    "dont_say_it": DontSayItGame
}

def build_games(game_name, game_kwargs):
    """ Build the specified game with given arguments. """
    assert game_name in GAME_DICT, \
        f"{game_name} not a valid game option. Valid options: {list(GAME_DICT.keys())}"

    try:
        return GAME_DICT[game_name](**game_kwargs)
    except Exception as exc:
        raise RuntimeError(
            f"Failed building the game (textarena/games/setup.py). Reason: {exc}"
        ) from exc
