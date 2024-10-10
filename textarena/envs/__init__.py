""" Register all environments """

from textarena.envs.registration import (
    make,
    register,
)  # , pprint_registry, register, registry, spec


# Single Player Games
register(
    id="TwentyQuestions-v0",
    entry_point="textarena.envs.single_player.twenty_questions:TwentyQuestions",
    num_questions=20,
)


# Two Player Games
register(
    id="DontSayIt-v0",
    entry_point="textarena.envs.two_player.dont_say_it:DontSayItEnv",
    hardcore=False,
    max_turns=30,
)
register(
    id="DontSayIt-v0-hardcore",
    entry_point="textarena.envs.two_player.dont_say_it:DontSayItEnv",
    hardcore=True,
    max_turns=30,
)
register(
    id="DontSayIt-v0-unlimited",
    entry_point="textarena.envs.two_player.dont_say_it:DontSayItEnv",
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
    entry_point="textarena.envs.two_player.connect_four:ConnectFourEnv",
    is_open=True,
    num_rows=6,
    num_cols=7,
)
register(
    id="ConnectFour-v0-blind",
    entry_point="textarena.envs.two_player.connect_four:ConnectFourEnv",
    is_open=False,
    num_rows=6,
    num_cols=7,
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
    entry_point="textarena.envs.two_player.debate:DebateEnv",
    max_turns=6,
    num_judges=11,
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
    entry_point="textarena.envs.two_player.iterated_prisoners_dilemma:IteratedPrisonersDilemmaEnv",
    chat_turns_per_round=1,
    max_turns=30,
)
# Multi Player Games
