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
    num_words=3,
)

register(
    id="Crosswords-v0-hardcore",
    entry_point="textarena.envs.single_player.Crosswords.env:CrosswordsEnv",
    hardcore=True,
    max_turns=30,
    num_words=3,
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
    id="WordSearch-v0-hardcore",
    entry_point="textarena.envs.single_player.WordSearch.env:WordSearchEnv",
    hardcore=True,
)

register(
    id="WordLadder-v0",
    entry_point="textarena.envs.single_player.WordLadder.env:WordLadderEnv",
    hardcore=False,
    word_len=5,
)

register(
    id="WordLadder-v0-hardcore",
    entry_point="textarena.envs.single_player.WordLadder.env:WordLadderEnv",
    hardcore=True,
    word_len=5,
)

register(
    id="WordLadder-v0-hardcore-10",
    entry_point="textarena.envs.single_player.WordLadder.env:WordLadderEnv",
    hardcore=True,
    word_len=10,
)

register(
    id="FifteenPuzzle-v0",
    entry_point="textarena.envs.single_player.FifteenPuzzle.env:FifteenPuzzleEnv",
)

register(
    id="LogicPuzzle-v0",
    entry_point="textarena.envs.single_player.LogicPuzzle.env:LogicPuzzleEnv",
    difficulty="easy",
)

register(
    id="LogicPuzzle-v0-hard",
    entry_point="textarena.envs.single_player.LogicPuzzle.env:LogicPuzzleEnv",
    difficulty="hard",
)

register(
    id="TwentyQuestions-v0",
    entry_point="textarena.envs.single_player.TwentyQuestions.env:TwentyQuestionsEnv",
    hardcore=False,
)

register(
    id="TwentyQuestions-v0-hardcore",
    entry_point="textarena.envs.single_player.TwentyQuestions.env:TwentyQuestionsEnv",
    hardcore=True,
)

register(
    id="TowerOfHanoi-v0-easy",
    entry_point="textarena.envs.single_player.TowerOfHanoi.env:TowerOfHanoiEnv",
    difficulty="easy"
)

register(
    id="TowerOfHanoi-v0-medium",
    entry_point="textarena.envs.single_player.TowerOfHanoi.env:TowerOfHanoiEnv",
    difficulty="medium"
)

register(
    id="TowerOfHanoi-v0-hard",
    entry_point="textarena.envs.single_player.TowerOfHanoi.env:TowerOfHanoiEnv",
    difficulty="hard"
)

register(
    id="Minesweeper-v0-easy",
    entry_point="textarena.envs.single_player.Minesweeper.env:MinesweeperEnv",
    difficulty="easy",
)

register(
    id="Minesweeper-v0-medium",
    entry_point="textarena.envs.single_player.Minesweeper.env:MinesweeperEnv",
    difficulty="medium",
)

register(
    id="Minesweeper-v0-hard",
    entry_point="textarena.envs.single_player.Minesweeper.env:MinesweeperEnv",
    difficulty="hard",
)

register(
    id="GuessWho-v0",
    entry_point="textarena.envs.single_player.GuessWho.env:GuessWhoEnv",
)

register(
    id="Chess-v0-singleplayer",
    entry_point="textarena.envs.single_player.Chess.env:ChessEnv",
)

register(
    id="ConnectFour-v0-singleplayer",
    entry_point="textarena.envs.single_player.ConnectFour.env:ConnectFourEnv",
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
    entry_point="textarena.envs.two_player.TruthAndDeception.env:TruthAndDeceptionEnv",
    max_turns=6,
)
register(
    id="TruthAndDeception-v0-long",
    entry_point="textarena.envs.two_player.TruthAndDeception.env:TruthAndDeceptionEnv",
    max_turns=12,
)
register(
    id="TruthAndDeception-v0-super-long",
    entry_point="textarena.envs.two_player.TruthAndDeception.env:TruthAndDeceptionEnv",
    max_turns=50,
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
    num_letters=6,
)
register(
    id="SpellingBee-v0-small",
    entry_point="textarena.envs.two_player.SpellingBee.env:SpellingBeeEnv",
    num_letters=4,
)
register(
    id="SpellingBee-v0-large",
    entry_point="textarena.envs.two_player.SpellingBee.env:SpellingBeeEnv",
    num_letters=10,
)

register(
    id="LiarsDice-v0",
    entry_point="textarena.envs.two_player.LiarsDice.env:LiarsDiceEnv",
    num_dice=5,
)
register(
    id="LiarsDice-v0-large",
    entry_point="textarena.envs.two_player.LiarsDice.env:LiarsDiceEnv",
    num_dice=12,
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
    entry_point="textarena.envs.two_player.Taboo.env:TabooEnv",
    max_turns=6,
    categories=["things"],
)
register(
    id="Taboo-v0-animals",
    entry_point="textarena.envs.two_player.Taboo.env:TabooEnv",
    max_turns=6,
    categories=["animals"],
)
register(
    id="Taboo-v0-cars",
    entry_point="textarena.envs.two_player.Taboo.env:TabooEnv",
    max_turns=6,
    categories=["cars"],
)
register(
    id="Taboo-v0-city/country",
    entry_point="textarena.envs.two_player.Taboo.env:TabooEnv",
    max_turns=6,
    categories=["city/country"],
)
register(
    id="Taboo-v0-food",
    entry_point="textarena.envs.two_player.Taboo.env:TabooEnv",
    max_turns=6,
    categories=["food"],
)
register(
    id="Taboo-v0-literature",
    entry_point="textarena.envs.two_player.Taboo.env:TabooEnv",
    max_turns=6,
    categories=["literature"],
)
register(
    id="Taboo-v0-people",
    entry_point="textarena.envs.two_player.Taboo.env:TabooEnv",
    max_turns=6,
    categories=["people"],
)
register(
    id="Taboo-v0-tv",
    entry_point="textarena.envs.two_player.Taboo.env:TabooEnv",
    max_turns=6,
    categories=["tv"],
)
register(
    id="Taboo-v0-long",
    entry_point="textarena.envs.two_player.Taboo.env:TabooEnv",
    max_turns=24,
    categories=["things"],
)
register(
    id="Taboo-v0-full",
    entry_point="textarena.envs.two_player.Taboo.env:TabooEnv",
    max_turns=6,
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
    entry_point="textarena.envs.two_player.IteratedPrisonersDilemma.env:PrisonersDilemmaEnv",
    max_turns=30,
)

register(
    "MemoryGame-v0-easy",
    entry_point="textarena.envs.two_player.MemoryGame.env:MemoryGameEnv",
    difficulty="easy",
)

register(
    "MemoryGame-v0-medium",
    entry_point="textarena.envs.two_player.MemoryGame.env:MemoryGameEnv",
    difficulty="medium",
)

register(
    "MemoryGame-v0-hard",
    entry_point="textarena.envs.two_player.MemoryGame.env:MemoryGameEnv",
    difficulty="hard",
)

register(
    "Battleship-v0-easy",
    entry_point="textarena.envs.two_player.Battleship.env:BattleshipEnv",
    difficulty="easy",
)

register(
    "Battleship-v0-medium",
    entry_point="textarena.envs.two_player.Battleship.env:BattleshipEnv",
    difficulty="medium",
)

register(
    "Battleship-v0-hard",
    entry_point="textarena.envs.two_player.Battleship.env:BattleshipEnv",
    difficulty="hard",
)

register(
    "Mastermind-v0-easy",
    entry_point="textarena.envs.two_player.Mastermind.env:MastermindEnv",
    difficulty="easy",
)

register(
    "Mastermind-v0-medium",
    entry_point="textarena.envs.two_player.Mastermind.env:MastermindEnv",
    difficulty="medium",
)

register(
    "Mastermind-v0-hard",
    entry_point="textarena.envs.two_player.Mastermind.env:MastermindEnv",
    difficulty="hard",
)

register(
    "LetterAuction-v0-easy",
    entry_point="textarena.envs.two_player.LetterAuction.env:LetterAuctionEnv",
    difficulty="easy"
)

register(
    "LetterAuction-v0-medium",
    entry_point="textarena.envs.two_player.LetterAuction.env:LetterAuctionEnv",
    difficulty="medium"
)

register(
    "LetterAuction-v0-hard",
    entry_point="textarena.envs.two_player.LetterAuction.env:LetterAuctionEnv",
    difficulty="hard"
)

register(
    "SpiteAndMalice-v0",
    entry_point="textarena.envs.two_player.SpiteAndMalice.env:SpiteAndMaliceEnv",
)