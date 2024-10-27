""" Register all environments """

from textarena.envs.registration import (
    make,
    register,
)  # , pprint_registry, register, registry, spec
from textarena.utils import batch_open_router_generate

from textarena.game_makers import GPTJudgeVote

# Multi Player Games
register(
    id="LiarsDice-v0-multi",
    entry_point="textarena.envs.multi_player.liars_dice:LiarsDice",
    num_dice=5,
    num_players=5,
)


# Single Player Games
# register(
#     id="TwentyQuestions-v0",
#     entry_point="textarena.envs.single_player.twenty_questions:TwentyQuestions",
#     num_questions=20,
# )

register(
    id="sudoku-v0",
    entry_point="textarena.envs.single_player.sudoku:SudokuEnv",
)

register(
    id="WordLadder-v0",
    entry_point="textarena.envs.single_player.word_ladder:WordLadderEnv",
)

# Two Player Games
register(
    id="DontSayIt-v0",
    entry_point="textarena.envs.two_player.DontSayIt.env:DontSayItEnv",
    hardcore=False,
    max_turns=30,
)
register(
    id="DontSayIt-v0-hardcore",
    entry_point="textarena.envs.two_player.DontSayIt.env:DontSayItEnv",
    hardcore=True,
    max_turns=30,
)
register(
    id="DontSayIt-v0-unlimited",
    entry_point="textarena.envs.two_player.DontSayIt.env:DontSayItEnv",
    hardcore=False,
    max_turns=None,
)

register(
    id="Negotiation-v0",
    entry_point="textarena.envs.two_player.Negotiation.env:NegotiationEnv",
    max_turns=20,
)
register(
    id="Negotiation-v0-short",
    entry_point="textarena.envs.two_player.Negotiation.env:NegotiationEnv",
    max_turns=10,
)
register(
    id="Negotiation-v0-long",
    entry_point="textarena.envs.two_player.Negotiation.env:NegotiationEnv",
    max_turns=50,
)


register(
    id="Chess-v0",
    entry_point="textarena.envs.two_player.Chess.env:ChessEnv",
    is_open=False,
    max_turns=30,
    show_valid=True,
)
register(
    id="Chess-v0-open",
    entry_point="textarena.envs.two_player.Chess.env:ChessEnv",
    is_open=True,
    max_turns=30,
    show_valid=False,
)
register(
    id="Chess-v0-long",
    entry_point="textarena.envs.two_player.Chess.env:ChessEnv",
    is_open=False,
    max_turns=50,
    show_valid=True,
)
register(
    id="Chess-v0-blind",
    entry_point="textarena.envs.two_player.Chess.env:ChessEnv",
    is_open=False,
    max_turns=50,
    show_valid=False,
)


register(
    id="TruthAndDeception-v0",
    entry_point="textarena.envs.two_player.truth_and_deception:TruthAndDeceptionEnv",
    max_turns=6,
)
register(
    id="TruthAndDeception-v0-long",
    entry_point="textarena.envs.two_player.truth_and_deception:TruthAndDeceptionEnv",
    max_turns=12,
)

register(
    id="WordChains-v0",
    entry_point="textarena.envs.two_player.word_chains:WordChainsEnv",
    max_turns=100,
)
register(
    id="WordChains-v0-infinite",
    entry_point="textarena.envs.two_player.word_chains:WordChainsEnv",
    max_turns=None,
)

register(
    id="ConnectFour-v0",
    entry_point="textarena.envs.two_player.ConnectFour.env:ConnectFourEnv",
    is_open=True,
    num_rows=6,
    num_cols=7,
)
register(
    id="ConnectFour-v0-blind",
    entry_point="textarena.envs.two_player.ConnectFour.env:ConnectFourEnv",
    is_open=False,
    num_rows=6,
    num_cols=7,
)
register(
    id="ConnectFour-v0-large",
    entry_point="textarena.envs.two_player.ConnectFour.env:ConnectFourEnv",
    is_open=True,
    num_rows=12,
    num_cols=15,
)

register(
    id="SpellingBee-v0",
    entry_point="textarena.envs.two_player.SpellingBee.env:SpellingBeeEnv",
    num_letters=6
)
register(
    id="SpellingBee-v0-small",
    entry_point="textarena.envs.two_player.SpellingBee.env:SpellingBeeEnv",
    num_letters=4
)
register(
    id="SpellingBee-v0-large",
    entry_point="textarena.envs.two_player.SpellingBee.env:SpellingBeeEnv",
    num_letters=10
)

register(
    id="LiarsDice-v0",
    entry_point="textarena.envs.two_player.LiarsDice.env:LiarsDiceEnv",
    num_dice=5
)
register(
    id="LiarsDice-v0-large",
    entry_point="textarena.envs.two_player.LiarsDice.env:LiarsDiceEnv",
    num_dice=12
)

register(
    id="SimplifiedPoker-v0",
    entry_point="textarena.envs.two_player.poker:SimplifiedPokerEnv",
    starting_chips=1_000,
    fixed_bet=10,
    num_rounds=10,
)

register(
    id="Taboo-v0",
    entry_point="textarena.envs.two_player.taboo:TabooEnv",
    max_turns=10,
    categories=["things"],
)
register(
    id="Taboo-v0-full",
    entry_point="textarena.envs.two_player.taboo:TabooEnv",
    max_turns=10,
    categories=[
        "animals",
        "cars",
        "city/country",
        "food",
        "literature",
        "people",
        "things",
        "tv",
    ],
)

register(
    id="Debate-v0",
    entry_point="textarena.envs.two_player.Debate.env:DebateEnv",
    max_turns=6,
    judge_class=GPTJudgeVote,
    num_judges=7,
)
register(
    id="Debate-v0-long",
    entry_point="textarena.envs.two_player.Debate.env:DebateEnv",
    max_turns=12,
    judge_class=GPTJudgeVote,
    num_judges=11,
)
register(
    id="Debate-v0-super-long",
    entry_point="textarena.envs.two_player.Debate.env:DebateEnv",
    max_turns=30,
    judge_class=GPTJudgeVote,
    num_judges=15,
)


register(
    id="ScenarioPlanning-v0",
    entry_point="textarena.envs.two_player.ScenarioPlanning.env:ScenarioPlanningEnv",
    num_judges=11,
)

register(
    id="CarPuzzle-v0",
    entry_point="textarena.envs.two_player.car_puzzle:CarPuzzleEnv",
)

register(
    "IteratedPrisonersDilemma-v0",
    entry_point="textarena.envs.two_player.iterated_prisoners_dilemma:IteratedPrisonersDilemma",
    chat_turns_per_round=1,
    max_turns=30,
)
# Multi Player Games
