""" Register all environments """

from textarena.envs.registration import (
    make,
    register,
)  # , pprint_registry, register, registry, spec
from textarena.utils import batch_open_router_generate

from textarena.game_makers import GPTJudgeVote

######################################### Multi Player Games #########################################
register(
    id="LiarsDice-v0-multi",
    entry_point="textarena.envs.multi_player.liars_dice:LiarsDice",
    num_dice=5,
    num_players=5,
)


######################################### Single Player Games #########################################
register(
    id="Crosswords-v0",
    entry_point="textarena.envs.single_player.Crosswords.env:CrosswordsEnv",
    hardcore=False,
    max_turns=30,
    num_words=8,
)

register(
    id="Crosswords-v0-hardcore",
    entry_point="textarena.envs.single_player.Crosswords.env:CrosswordsEnv",
    hardcore=True,
    max_turns=30,
    num_words=8,
)

register(
    id="Sudoku-v0-easy",
    entry_point="textarena.envs.single_player.Sudoku.env:SudokuEnv",
    difficulty="easy",
    max_turns=31,
)

register(
    id="Sudoku-v0-medium",
    entry_point="textarena.envs.single_player.Sudoku.env:SudokuEnv",
    difficulty="medium",
    max_turns=41,
)

register(
    id="Sudoku-v0-hard",
    entry_point="textarena.envs.single_player.Sudoku.env:SudokuEnv",
    difficulty="hard",
    max_turns=51,
)

register(
    id="Hangman-v0",
    entry_point="textarena.envs.single_player.Hangman.env:HangmanEnv",
    hardcore=False,
)

register(
    id="Hangman-v0-hardcore",
    entry_point="textarena.envs.single_player.Hangman.env:HangmanEnv",
    hardcore=True,
)

register(
    id="GuessTheNumber-v0",
    entry_point="textarena.envs.single_player.GuessTheNumber.env:GuessTheNumberEnv",
    hardcore=False,
)

register(
    id="GuessTheNumber-v0-hardcore",
    entry_point="textarena.envs.single_player.GuessTheNumber.env:GuessTheNumberEnv",
    hardcore=True,
)

register(
    id="WordSearch-v0",
    entry_point="textarena.envs.single_player.WordSearch.env:WordSearchEnv",
    hardcore=False,
)

register(
    id="WordLadder-v0",
    entry_point="textarena.envs.single_player.word_ladder:WordLadderEnv",
)

######################################### Two Player Games #########################################
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
    entry_point="textarena.envs.two_player.negotiation:NegotiationEnv",
    max_turns=20,
)


register(
    id="Chess-v0",
    entry_point="textarena.envs.two_player.chess:ChessEnv",
    is_open=False,
    max_turns=30,
    show_valid=True,
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
    entry_point="textarena.envs.two_player.spelling_bee:SpellingBeeEnv",
)

register(
    id="LiarsDice-v0",
    entry_point="textarena.envs.two_player.liars_dice:LiarsDiceEnv",
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
    entry_point="textarena.envs.two_player.scenario_planning:ScenarioPlanningEnv",
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