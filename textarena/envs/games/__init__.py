""" Register all game environments """ 

from textarena.envs.registration import register, register_with_versions
from textarena.envs.games.utils.jury import OpenRouterJury
from textarena.wrappers import LLMObservationWrapper, ActionFormattingWrapper, GameMessagesAndCurrentBoardObservationWrapper, GameMessagesObservationWrapper, GameBoardObservationWrapper



# # Mastermind (single-player)
# register(id="Mastermind-v0", entry_point="textarena.envs.games.Mastermind.env:MastermindEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], code_length=4, num_numbers=6, max_turns=20, duplicate_numbers=False)
# register(id="Mastermind-v0-hard", entry_point="textarena.envs.games.Mastermind.env:MastermindEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], code_length=4, num_numbers=8, max_turns=30, duplicate_numbers=False)
# register(id="Mastermind-v0-extreme", entry_point="textarena.envs.games.Mastermind.env:MastermindEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], code_length=6, num_numbers=12, max_turns=50, duplicate_numbers=True)
# register(id="Mastermind-v0-raw", entry_point="textarena.envs.games.Mastermind.env:MastermindEnv", code_length=4, num_numbers=6, max_turns=20, duplicate_numbers=False)
# register(id="Mastermind-v0-raw-hard", entry_point="textarena.envs.games.Mastermind.env:MastermindEnv", code_length=4, num_numbers=8, max_turns=30, duplicate_numbers=False)
# register(id="Mastermind-v0-raw-extreme", entry_point="textarena.envs.games.Mastermind.env:MastermindEnv", code_length=6, num_numbers=12, max_turns=50, duplicate_numbers=True)
# register(id="Mastermind-v0-train", entry_point="textarena.envs.games.Mastermind.env:MastermindEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], code_length=4, num_numbers=6, max_turns=20, duplicate_numbers=False)
# register(id="Mastermind-v0-train-hard", entry_point="textarena.envs.games.Mastermind.env:MastermindEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], code_length=4, num_numbers=8, max_turns=30, duplicate_numbers=False)
# register(id="Mastermind-v0-train-extreme", entry_point="textarena.envs.games.Mastermind.env:MastermindEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], code_length=6, num_numbers=12, max_turns=50, duplicate_numbers=True)


# # Bandit (single-player)
# register(id="Bandit-v0", entry_point="textarena.envs.games.Bandit.env:BanditEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], buttons=['red', 'blue', 'green', 'yellow', 'purple'], p_gap=0.1, num_turns=20)
# register(id="Bandit-v0-train", entry_point="textarena.envs.games.Bandit.env:BanditEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], buttons=['red', 'blue', 'green', 'yellow', 'purple'], p_gap=0.1, num_turns=20)
# register(id="Bandit-v0-raw", entry_point="textarena.envs.games.Bandit.env:BanditEnv", buttons=['red', 'blue', 'green', 'yellow', 'purple'], p_gap=0.1, num_turns=20)
# register(id="Bandit-v0-hard", entry_point="textarena.envs.games.Bandit.env:BanditEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], buttons=['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'brown', 'gray', 'black'], p_gap=0.05, num_turns=40)



# # Blackjack (single-player)
# register(id="Blackjack-v0", entry_point="textarena.envs.games.Blackjack.env:BlackjackEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_hands=5)
# register(id="Blackjack-v0-long", entry_point="textarena.envs.games.Blackjack.env:BlackjackEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_hands=15)
# register(id="Blackjack-v0-raw", entry_point="textarena.envs.games.Blackjack.env:BlackjackEnv", num_hands=5)
# register(id="Blackjack-v0-raw-long", entry_point="textarena.envs.games.Blackjack.env:BlackjackEnv", num_hands=15)


# # Crosswords (single-player)
# register(id="Crosswords-v0", entry_point="textarena.envs.games.Crosswords.env:CrosswordsEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], hardcore=False, max_turns=30, num_words=3)
# register(id="Crosswords-v0-hardcore", entry_point="textarena.envs.games.Crosswords.env:CrosswordsEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], hardcore=True, max_turns=30, num_words=3)
# register(id="Crosswords-v0-raw", entry_point="textarena.envs.games.Crosswords.env:CrosswordsEnv", hardcore=False, max_turns=30, num_words=3)
# register(id="Crosswords-v0-raw-hardcore", entry_point="textarena.envs.games.Crosswords.env:CrosswordsEnv", hardcore=True, max_turns=30, num_words=3)
# register(id="Crosswords-v0-train", entry_point="textarena.envs.games.Crosswords.env:CrosswordsEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], hardcore=False, max_turns=30, num_words=3)
# register(id="Crosswords-v0-train-hardcore", entry_point="textarena.envs.games.Crosswords.env:CrosswordsEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], hardcore=True, max_turns=30, num_words=3)


# # FifteenPuzzle (single-player)
# register(id="FifteenPuzzle-v0", entry_point="textarena.envs.games.FifteenPuzzle.env:FifteenPuzzleEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_turns=50)
# register(id="FifteenPuzzle-v0-raw", entry_point="textarena.envs.games.FifteenPuzzle.env:FifteenPuzzleEnv", max_turns=50)
# register(id="FifteenPuzzle-v0-train", entry_point="textarena.envs.games.FifteenPuzzle.env:FifteenPuzzleEnv", default_wrappers=[GameBoardObservationWrapper, ActionFormattingWrapper], max_turns=50)


# # FrozenLake (single-player)
# register(id="FrozenLake-v0", entry_point="textarena.envs.games.FrozenLake.env:FrozenLakeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], size=4, num_holes=3, randomize_start_goal=False)
# register(id="FrozenLake-v0-random", entry_point="textarena.envs.games.FrozenLake.env:FrozenLakeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], size=4, num_holes=3, randomize_start_goal=True)
# register(id="FrozenLake-v0-hardcore", entry_point="textarena.envs.games.FrozenLake.env:FrozenLakeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], size=5, num_holes=6, randomize_start_goal=False)
# register(id="FrozenLake-v0-train", entry_point="textarena.envs.games.FrozenLake.env:FrozenLakeEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], size=4, num_holes=3, randomize_start_goal=False)
# register(id="FrozenLake-v0-train-random", entry_point="textarena.envs.games.FrozenLake.env:FrozenLakeEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], size=4, num_holes=3, randomize_start_goal=True)
# register(id="FrozenLake-v0-train-hardcore", entry_point="textarena.envs.games.FrozenLake.env:FrozenLakeEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], size=5, num_holes=6, randomize_start_goal=False)

# # GuessTheNumber (single-player)
# register(id="GuessTheNumber-v0", entry_point="textarena.envs.games.GuessTheNumber.env:GuessTheNumberEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], min_number=1, max_number=20, max_turns=10)
# register(id="GuessTheNumber-v0-hardcore", entry_point="textarena.envs.games.GuessTheNumber.env:GuessTheNumberEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], min_number=1, max_number=50, max_turns=10)
# register(id="GuessTheNumber-v0-raw", entry_point="textarena.envs.games.GuessTheNumber.env:GuessTheNumberEnv", min_number=1, max_number=20, max_turns=10)
# register(id="GuessTheNumber-v0-raw-hardcore", entry_point="textarena.envs.games.GuessTheNumber.env:GuessTheNumberEnv", min_number=1, max_number=50, max_turns=10)
# register(id="GuessTheNumber-v0-train", entry_point="textarena.envs.games.GuessTheNumber.env:GuessTheNumberEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], min_number=1, max_number=20, max_turns=10)
# register(id="GuessTheNumber-v0-train-hardcore", entry_point="textarena.envs.games.GuessTheNumber.env:GuessTheNumberEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], min_number=1, max_number=50, max_turns=10)


# # GuessWho (single-player)
# register(id="GuessWho-v0", entry_point="textarena.envs.games.GuessWho.env:GuessWhoEnv", default_wrappers=[LLMObservationWrapper], max_turns=20)
# register(id="GuessWho-v0-raw", entry_point="textarena.envs.games.GuessWho.env:GuessWhoEnv", max_turns=20)


# # Hangman (single-player)
# register(id="Hangman-v0", entry_point="textarena.envs.games.Hangman.env:HangmanEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], hardcore=False)
# register(id="Hangman-v0-hardcore", entry_point="textarena.envs.games.Hangman.env:HangmanEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], hardcore=True)
# register(id="Hangman-v0-raw", entry_point="textarena.envs.games.Hangman.env:HangmanEnv", hardcore=False)
# register(id="Hangman-v0-raw-hardcore", entry_point="textarena.envs.games.Hangman.env:HangmanEnv", hardcore=True)


# # LogicPuzzle (single-player)
# register(id="LogicPuzzle-v0", entry_point="textarena.envs.games.LogicPuzzle.env:LogicPuzzleEnv", default_wrappers=[LLMObservationWrapper], difficulty="easy")
# register(id="LogicPuzzle-v0-hard", entry_point="textarena.envs.games.LogicPuzzle.env:LogicPuzzleEnv", default_wrappers=[LLMObservationWrapper], difficulty="hard")
# register(id="LogicPuzzle-v0-raw", entry_point="textarena.envs.games.LogicPuzzle.env:LogicPuzzleEnv", difficulty="easy")
# register(id="LogicPuzzle-v0-raw-hard", entry_point="textarena.envs.games.LogicPuzzle.env:LogicPuzzleEnv", difficulty="hard")


# # Minesweeper (single-player)
# register(id="Minesweeper-v0", entry_point="textarena.envs.games.Minesweeper.env:MinesweeperEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], rows=8, cols=8, num_mines=10, max_turns=100)
# register(id="Minesweeper-v0-medium", entry_point="textarena.envs.games.Minesweeper.env:MinesweeperEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], rows=10, cols=10, num_mines=20, max_turns=100)
# register(id="Minesweeper-v0-hard", entry_point="textarena.envs.games.Minesweeper.env:MinesweeperEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], rows=12, cols=12, num_mines=30, max_turns=100)
# register(id="Minesweeper-v0-raw", entry_point="textarena.envs.games.Minesweeper.env:MinesweeperEnv", rows=8, cols=8, num_mines=10, max_turns=100)
# register(id="Minesweeper-v0-raw-medium", entry_point="textarena.envs.games.Minesweeper.env:MinesweeperEnv", rows=10, cols=10, num_mines=20, max_turns=100)
# register(id="Minesweeper-v0-raw-hard", entry_point="textarena.envs.games.Minesweeper.env:MinesweeperEnv", rows=12, cols=12, num_mines=30, max_turns=100)
# register(id="Minesweeper-v0-train", entry_point="textarena.envs.games.Minesweeper.env:MinesweeperEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], rows=8, cols=8, num_mines=10, max_turns=100)
# register(id="Minesweeper-v0-train-medium", entry_point="textarena.envs.games.Minesweeper.env:MinesweeperEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], rows=10, cols=10, num_mines=20, max_turns=100)
# register(id="Minesweeper-v0-train-hard", entry_point="textarena.envs.games.Minesweeper.env:MinesweeperEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], rows=12, cols=12, num_mines=30, max_turns=100)
# register(id="Minesweeper-v0-train-small", entry_point="textarena.envs.games.Minesweeper.env:MinesweeperEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], rows=5, cols=5, num_mines=5, max_turns=100)


# # Sudoku (single-player)
# register(id="Sudoku-v0", entry_point="textarena.envs.games.Sudoku.env:SudokuEnv", default_wrappers=[LLMObservationWrapper], clues=30, max_turns=100)
# register(id="Sudoku-v0-medium", entry_point="textarena.envs.games.Sudoku.env:SudokuEnv", default_wrappers=[LLMObservationWrapper], clues=40, max_turns=100)
# register(id="Sudoku-v0-hard", entry_point="textarena.envs.games.Sudoku.env:SudokuEnv", default_wrappers=[LLMObservationWrapper], clues=50, max_turns=100)
# register(id="Sudoku-v0-raw", entry_point="textarena.envs.games.Sudoku.env:SudokuEnv", clues=30, max_turns=100)
# register(id="Sudoku-v0-raw-medium", entry_point="textarena.envs.games.Sudoku.env:SudokuEnv", clues=40, max_turns=100)
# register(id="Sudoku-v0-raw-hard", entry_point="textarena.envs.games.Sudoku.env:SudokuEnv", clues=50, max_turns=100)
# register(id="Sudoku-v0-train", entry_point="textarena.envs.games.Sudoku.env:SudokuEnv", default_wrappers=[GameBoardObservationWrapper, ActionFormattingWrapper], clues=30, max_turns=100)
# register(id="Sudoku-v0-train-medium", entry_point="textarena.envs.games.Sudoku.env:SudokuEnv", default_wrappers=[GameBoardObservationWrapper, ActionFormattingWrapper], clues=40, max_turns=100)
# register(id="Sudoku-v0-train-hard", entry_point="textarena.envs.games.Sudoku.env:SudokuEnv", default_wrappers=[GameBoardObservationWrapper, ActionFormattingWrapper], clues=50, max_turns=100)


# # Sokoban (single-player)
# register(id="Sokoban-v0", entry_point="textarena.envs.games.Sokoban.env:SokobanEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], dim_room=(6,6), max_turns=30, num_boxes=3)
# register(id="Sokoban-v0-medium", entry_point="textarena.envs.games.Sokoban.env:SokobanEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], dim_room=(8,8), max_turns=50, num_boxes=5)
# register(id="Sokoban-v0-raw", entry_point="textarena.envs.games.Sokoban.env:SokobanEnv", dim_room=(6,6), max_turns=30, num_boxes=3)
# register(id="Sokoban-v0-raw-medium", entry_point="textarena.envs.games.Sokoban.env:SokobanEnv", dim_room=(8,8), max_turns=50, num_boxes=5)
# register(id="Sokoban-v0-train", entry_point="textarena.envs.games.Sokoban.env:SokobanEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], dim_room=(6,6), max_turns=30, num_boxes=3)
# register(id="Sokoban-v0-train-medium", entry_point="textarena.envs.games.Sokoban.env:SokobanEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], dim_room=(8,8), max_turns=50, num_boxes=5)



# # TowerOfHanoi (single-player)
# register(id="TowerOfHanoi-v0", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_disks=3, max_turns=14)
# register(id="TowerOfHanoi-v0-medium", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_disks=4, max_turns=30)
# register(id="TowerOfHanoi-v0-hard", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_disks=5, max_turns=62)
# register(id="TowerOfHanoi-v0-extreme", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_disks=7, max_turns=254)
# register(id="TowerOfHanoi-v0-raw", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", num_disks=3, max_turns=14)
# register(id="TowerOfHanoi-v0-raw-medium", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", num_disks=4, max_turns=30)
# register(id="TowerOfHanoi-v0-raw-hard", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", num_disks=5, max_turns=62)
# register(id="TowerOfHanoi-v0-raw-extreme", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", num_disks=7, max_turns=254)
# register(id="TowerOfHanoi-v0-train", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], num_disks=3, max_turns=14)
# register(id="TowerOfHanoi-v0-train-medium", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], num_disks=4, max_turns=30)
# register(id="TowerOfHanoi-v0-train-hard", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], num_disks=5, max_turns=62)
# register(id="TowerOfHanoi-v0-train-extreme", entry_point="textarena.envs.games.TowerOfHanoi.env:TowerOfHanoiEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], num_disks=7, max_turns=254)

# # TwentyQuestions (single-player)
# register(id="TwentyQuestions-v0", entry_point="textarena.envs.games.TwentyQuestions.env:TwentyQuestionsEnv", default_wrappers=[LLMObservationWrapper], hardcore=False)
# register(id="TwentyQuestions-v0-hardcore", entry_point="textarena.envs.games.TwentyQuestions.env:TwentyQuestionsEnv", default_wrappers=[LLMObservationWrapper], hardcore=True)
# register(id="TwentyQuestions-v0-raw", entry_point="textarena.envs.games.TwentyQuestions.env:TwentyQuestionsEnv", hardcore=False)
# register(id="TwentyQuestions-v0-raw-hardcore", entry_point="textarena.envs.games.TwentyQuestions.env:TwentyQuestionsEnv", hardcore=True)


# # WordLadder (single-player)
# register(id="WordLadder-v0", entry_point="textarena.envs.games.WordLadder.env:WordLadderEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], min_distance=5, max_distance=7, max_turns=100)
# register(id="WordLadder-v0-medium", entry_point="textarena.envs.games.WordLadder.env:WordLadderEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], min_distance=8, max_distance=12, max_turns=100)
# register(id="WordLadder-v0-hard", entry_point="textarena.envs.games.WordLadder.env:WordLadderEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], min_distance=13, max_distance=15, max_turns=100)
# register(id="WordLadder-v0-raw", entry_point="textarena.envs.games.WordLadder.env:WordLadderEnv", min_distance=5, max_distance=7, max_turns=100)
# register(id="WordLadder-v0-raw-medium", entry_point="textarena.envs.games.WordLadder.env:WordLadderEnv", min_distance=8, max_distance=12, max_turns=100)
# register(id="WordLadder-v0-raw-hard", entry_point="textarena.envs.games.WordLadder.env:WordLadderEnv", min_distance=13, max_distance=15, max_turns=100)


# # Wordle (single-player)
# register(id="Wordle-v0", entry_point="textarena.envs.games.Wordle.env:WordleEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], hardcore=False, word_length=5, num_guesses=6)
# register(id="Wordle-v0-hardcore", entry_point="textarena.envs.games.Wordle.env:WordleEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], hardcore=True, word_length=5, num_guesses=6)
# register(id="Wordle-v0-long", entry_point="textarena.envs.games.Wordle.env:WordleEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], hardcore=False, word_length=7, num_guesses=9)
# register(id="Wordle-v0-long-hardcore", entry_point="textarena.envs.games.Wordle.env:WordleEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], hardcore=True, word_length=7, num_guesses=9)
# register(id="Wordle-v0-raw", entry_point="textarena.envs.games.Wordle.env:WordleEnv", hardcore=False, word_length=5, num_guesses=6)
# register(id="Wordle-v0-raw-hardcore", entry_point="textarena.envs.games.Wordle.env:WordleEnv", hardcore=True, word_length=5, num_guesses=6)
# register(id="Wordle-v0-raw-long", entry_point="textarena.envs.games.Wordle.env:WordleEnv", hardcore=False, word_length=7, num_guesses=9)
# register(id="Wordle-v0-raw-long-hardcore", entry_point="textarena.envs.games.Wordle.env:WordleEnv", hardcore=True, word_length=7, num_guesses=9)
# register(id="Wordle-v0-train", entry_point="textarena.envs.games.Wordle.env:WordleEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], hardcore=False, word_length=5, num_guesses=6)
# register(id="Wordle-v0-train-hardcore", entry_point="textarena.envs.games.Wordle.env:WordleEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], hardcore=True, word_length=5, num_guesses=6)
# register(id="Wordle-v0-train-long", entry_point="textarena.envs.games.Wordle.env:WordleEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], hardcore=False, word_length=7, num_guesses=9)
# register(id="Wordle-v0-train-long-hardcore", entry_point="textarena.envs.games.Wordle.env:WordleEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], hardcore=True, word_length=7, num_guesses=9)


# # WordSearch (single-player)
# register(id="WordSearch-v0", entry_point="textarena.envs.games.WordSearch.env:WordSearchEnv", default_wrappers=[LLMObservationWrapper], hardcore=False)
# register(id="WordSearch-v0-hardcore", entry_point="textarena.envs.games.WordSearch.env:WordSearchEnv", default_wrappers=[LLMObservationWrapper], hardcore=True)
# register(id="WordSearch-v0-raw", entry_point="textarena.envs.games.WordSearch.env:WordSearchEnv", hardcore=False)
# register(id="WordSearch-v0-raw-hardcore", entry_point="textarena.envs.games.WordSearch.env:WordSearchEnv", hardcore=True)




# # Battleship (two-player)
# register(id="Battleship-v0", entry_point="textarena.envs.games.Battleship.env:BattleshipEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], grid_size=5)
# register(id="Battleship-v0-standard", entry_point="textarena.envs.games.Battleship.env:BattleshipEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], grid_size=10)
# register(id="Battleship-v0-large", entry_point="textarena.envs.games.Battleship.env:BattleshipEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], grid_size=14)
# register(id="Battleship-v0-extreme", entry_point="textarena.envs.games.Battleship.env:BattleshipEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], grid_size=20)
# register(id="Battleship-v0-raw", entry_point="textarena.envs.games.Battleship.env:BattleshipEnv", grid_size=5)
# register(id="Battleship-v0-raw-standard", entry_point="textarena.envs.games.Battleship.env:BattleshipEnv", grid_size=10)
# register(id="Battleship-v0-raw-large", entry_point="textarena.envs.games.Battleship.env:BattleshipEnv", grid_size=14)
# register(id="Battleship-v0-raw-extreme", entry_point="textarena.envs.games.Battleship.env:BattleshipEnv", grid_size=20)


# Breakthrough (two-player)
# register(id="Breakthrough-v0", entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv",             default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], train_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper],  board_size=8,   is_open=True    )
# register(id="Breakthrough-v0-small", entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv",       default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], train_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper],  board_size=6,   is_open=True    )
# register(id="Breakthrough-v0-large", entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv",       default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], train_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper],  board_size=10,  is_open=True    )
# register(id="Breakthrough-v0-blind", entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv",       default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], train_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper],  board_size=8,   is_open=False   )
# register(id="Breakthrough-v0-long", entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv",        default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], train_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper],  board_size=8,   is_open=True    )

register_with_versions(id="Breakthrough-v0",        entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv", wrappers={"default": [LLMObservationWrapper, ActionFormattingWrapper], "-train": [GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper]}, board_size=8,   is_open=True    )
register_with_versions(id="Breakthrough-v0-tiny",   entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv", wrappers={"default": [LLMObservationWrapper, ActionFormattingWrapper], "-train": [GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper]}, board_size=5,   is_open=True    )
register_with_versions(id="Breakthrough-v0-small",  entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv", wrappers={"default": [LLMObservationWrapper, ActionFormattingWrapper], "-train": [GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper]}, board_size=6,   is_open=True    )
register_with_versions(id="Breakthrough-v0-large",  entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv", wrappers={"default": [LLMObservationWrapper, ActionFormattingWrapper], "-train": [GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper]}, board_size=10,  is_open=True    )
register_with_versions(id="Breakthrough-v0-blind",  entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv", wrappers={"default": [LLMObservationWrapper, ActionFormattingWrapper], "-train": [GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper]}, board_size=8,   is_open=False   )
register_with_versions(id="Breakthrough-v0-long",   entry_point="textarena.envs.games.Breakthrough.env:BreakthroughEnv", wrappers={"default": [LLMObservationWrapper, ActionFormattingWrapper], "-train": [GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper]}, board_size=8,   is_open=True    )





# # Briscola (two-player)
# register(id="Briscola-v0", entry_point="textarena.envs.games.Briscola.env:BriscolaEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="Briscola-v0-raw", entry_point="textarena.envs.games.Briscola.env:BriscolaEnv")
# register(id="Briscola-v0-train", entry_point="textarena.envs.games.Briscola.env:BriscolaEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper])

# # Chess (two-player)
# register(id="Chess-v0", entry_point="textarena.envs.games.Chess.env:ChessEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], is_open=True, max_turns=100, show_valid=True)
# register(id="Chess-v0-long", entry_point="textarena.envs.games.Chess.env:ChessEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], is_open=True, max_turns=250, show_valid=True)
# register(id="Chess-v0-blind", entry_point="textarena.envs.games.Chess.env:ChessEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], is_open=False, max_turns=150, show_valid=False)
# register(id="Chess-v0-raw", entry_point="textarena.envs.games.Chess.env:ChessEnv", is_open=True, max_turns=100, show_valid=True)
# register(id="Chess-v0-raw-long", entry_point="textarena.envs.games.Chess.env:ChessEnv", is_open=True, max_turns=250, show_valid=True)
# register(id="Chess-v0-raw-blind", entry_point="textarena.envs.games.Chess.env:ChessEnv", is_open=False, max_turns=150, show_valid=False)
# register(id="Chess-v0-train", entry_point="textarena.envs.games.Chess.env:ChessEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], is_open=True, max_turns=100, show_valid=True)
# register(id="Chess-v0-train-long", entry_point="textarena.envs.games.Chess.env:ChessEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], is_open=True, max_turns=250, show_valid=True)
# register(id="Chess-v0-train-blind", entry_point="textarena.envs.games.Chess.env:ChessEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], is_open=False, max_turns=150, show_valid=False)


# # Checkers (two-player)
# register(id="Checkers-v0", entry_point="textarena.envs.games.Checkers.env:CheckersEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_turns=100)
# register(id="Checkers-v0-long", entry_point="textarena.envs.games.Checkers.env:CheckersEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_turns=300)
# register(id="Checkers-v0-raw", entry_point="textarena.envs.games.Checkers.env:CheckersEnv", max_turns=100)
# register(id="Checkers-v0-raw-long", entry_point="textarena.envs.games.Checkers.env:CheckersEnv", max_turns=300)

# # Chopsticks (two-player)
# register(id="Chopsticks-v0", entry_point="textarena.envs.games.Chopsticks.env:ChopsticksEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_turns=40)
# register(id="Chopsticks-v0-raw", entry_point="textarena.envs.games.Chopsticks.env:ChopsticksEnv", max_turns=40)
# register(id="Chopsticks-v0-train", entry_point="textarena.envs.games.Chopsticks.env:ChopsticksEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], max_turns=40)


# ConnectFour (two-player)
# register(id="ConnectFour-v0", entry_point="textarena.envs.games.ConnectFour.env:ConnectFourEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], is_open=True, num_rows=6, num_cols=7)
# register(id="ConnectFour-v0-blind", entry_point="textarena.envs.games.ConnectFour.env:ConnectFourEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], is_open=False, num_rows=6, num_cols=7)
# register(id="ConnectFour-v0-large", entry_point="textarena.envs.games.ConnectFour.env:ConnectFourEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], is_open=True, num_rows=12, num_cols=15)
# register(id="ConnectFour-v0-raw", entry_point="textarena.envs.games.ConnectFour.env:ConnectFourEnv", is_open=True, num_rows=6, num_cols=7)
# register(id="ConnectFour-v0-raw-blind", entry_point="textarena.envs.games.ConnectFour.env:ConnectFourEnv", is_open=False, num_rows=6, num_cols=7)
# register(id="ConnectFour-v0-raw-large", entry_point="textarena.envs.games.ConnectFour.env:ConnectFourEnv", is_open=True, num_rows=12, num_cols=15)
# register(id="ConnectFour-v0-train", entry_point="textarena.envs.games.ConnectFour.env:ConnectFourEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], is_open=True, num_rows=6, num_cols=7)
# register(id="ConnectFour-v0-train-blind", entry_point="textarena.envs.games.ConnectFour.env:ConnectFourEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], is_open=False, num_rows=6, num_cols=7)
# register(id="ConnectFour-v0-train-large", entry_point="textarena.envs.games.ConnectFour.env:ConnectFourEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], is_open=True, num_rows=12, num_cols=15)
 

# # DontSayIt (two-player)
# register(id="DontSayIt-v0", entry_point="textarena.envs.games.DontSayIt.env:DontSayItEnv", default_wrappers=[LLMObservationWrapper], hardcore=False, max_turns=20)
# register(id="DontSayIt-v0-hardcore", entry_point="textarena.envs.games.DontSayIt.env:DontSayItEnv", default_wrappers=[LLMObservationWrapper], hardcore=True, max_turns=30)
# register(id="DontSayIt-v0-unlimited", entry_point="textarena.envs.games.DontSayIt.env:DontSayItEnv", default_wrappers=[LLMObservationWrapper], hardcore=False, max_turns=None)
# register(id="DontSayIt-v0-raw", entry_point="textarena.envs.games.DontSayIt.env:DontSayItEnv", hardcore=False, max_turns=20)
# register(id="DontSayIt-v0-raw-hardcore", entry_point="textarena.envs.games.DontSayIt.env:DontSayItEnv", hardcore=True, max_turns=30)
# register(id="DontSayIt-v0-raw-unlimited", entry_point="textarena.envs.games.DontSayIt.env:DontSayItEnv", hardcore=False, max_turns=None)

# # GameOfPureStrategy (two-player)
# register(id="GameOfPureStrategy-v0", entry_point="textarena.envs.games.GameOfPureStrategy.env:GameOfPureStrategyEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="GameOfPureStrategy-v0-raw", entry_point="textarena.envs.games.GameOfPureStrategy.env:GameOfPureStrategyEnv")
# register(id="GameOfPureStrategy-v0-train", entry_point="textarena.envs.games.GameOfPureStrategy.env:GameOfPureStrategyEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper])

# # GermanWhist (two-player)
# register(id="GermanWhist-v0", entry_point="textarena.envs.games.GermanWhist.env:GermanWhistEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="GermanWhist-v0-raw", entry_point="textarena.envs.games.GermanWhist.env:GermanWhistEnv")
# register(id="GermanWhist-v0-train", entry_point="textarena.envs.games.GermanWhist.env:GermanWhistEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper])

# # Golf (two-player)
# register(id="Golf-v0", entry_point="textarena.envs.games.Golf.env:GolfEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_cards=6, num_columns=3)
# register(id="Golf-v0-medium", entry_point="textarena.envs.games.Golf.env:GolfEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_cards=9, num_columns=3)
# register(id="Golf-v0-raw", entry_point="textarena.envs.games.Golf.env:GolfEnv", num_cards=6, num_columns=3)
# register(id="Golf-v0-raw-medium", entry_point="textarena.envs.games.Golf.env:GolfEnv", num_cards=9, num_columns=3)
# register(id="Golf-v0-train", entry_point="textarena.envs.games.Golf.env:GolfEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_cards=6, num_columns=3)
# register(id="Golf-v0-train-medium", entry_point="textarena.envs.games.Golf.env:GolfEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_cards=9, num_columns=3)

# # KuhnPoker (two-player)
# register(id="KuhnPoker-v0", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=5)
# register(id="KuhnPoker-v0-medium", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=9)
# register(id="KuhnPoker-v0-long", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=15)
# register(id="KuhnPoker-v0-extreme", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=25)
# register(id="KuhnPoker-v0-raw", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", ante=1, max_rounds=5)
# register(id="KuhnPoker-v0-raw-medium", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", ante=1, max_rounds=9)
# register(id="KuhnPoker-v0-raw-long", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", ante=1, max_rounds=15)
# register(id="KuhnPoker-v0-raw-extreme", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", ante=1, max_rounds=25)
# register(id="KuhnPoker-v0-train", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=5)
# register(id="KuhnPoker-v0-train-medium", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=9)
# register(id="KuhnPoker-v0-train-long", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=15)
# register(id="KuhnPoker-v0-train-extreme", entry_point="textarena.envs.games.KuhnPoker.env:KuhnPokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=25)

# # IndianPoker (two-player)
# register(id="IndianPoker-v0", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=5)
# register(id="IndianPoker-v0-medium", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=9)
# register(id="IndianPoker-v0-long", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=15)
# register(id="IndianPoker-v0-extreme", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=25)
# register(id="IndianPoker-v0-raw", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", ante=1, max_rounds=5)
# register(id="IndianPoker-v0-raw-medium", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", ante=1, max_rounds=9)
# register(id="IndianPoker-v0-raw-long", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", ante=1, max_rounds=15)
# register(id="IndianPoker-v0-raw-extreme", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", ante=1, max_rounds=25)
# register(id="IndianPoker-v0-train", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=5)
# register(id="IndianPoker-v0-train-medium", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=9)
# register(id="IndianPoker-v0-train-long", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=15)
# register(id="IndianPoker-v0-train-extreme", entry_point="textarena.envs.games.IndianPoker.env:IndianPokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], ante=1, max_rounds=25)


# # LeducHoldem (two-player)
# register(id="LeducHoldem-v0", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_rounds=5)
# register(id="LeducHoldem-v0-medium", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_rounds=9)
# register(id="LeducHoldem-v0-long", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_rounds=15)
# register(id="LeducHoldem-v0-extreme", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_rounds=25)
# register(id="LeducHoldem-v0-raw", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", max_rounds=5)
# register(id="LeducHoldem-v0-raw-medium", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", max_rounds=9)
# register(id="LeducHoldem-v0-raw-long", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", max_rounds=15)
# register(id="LeducHoldem-v0-raw-extreme", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", max_rounds=25)
# register(id="LeducHoldem-v0-train", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], max_rounds=5)
# register(id="LeducHoldem-v0-train-medium", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], max_rounds=9)
# register(id="LeducHoldem-v0-train-long", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], max_rounds=15)
# register(id="LeducHoldem-v0-train-extreme", entry_point="textarena.envs.games.LeducHoldem.env:LeducHoldemEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], max_rounds=25)

# # LetterAuction (two-player)
# register(id="LetterAuction-v0", entry_point="textarena.envs.games.LetterAuction.env:LetterAuctionEnv", default_wrappers=[LLMObservationWrapper], starting_coins=100)
# register(id="LetterAuction-v0-medium", entry_point="textarena.envs.games.LetterAuction.env:LetterAuctionEnv", default_wrappers=[LLMObservationWrapper], starting_coins=50)
# register(id="LetterAuction-v0-hard", entry_point="textarena.envs.games.LetterAuction.env:LetterAuctionEnv", default_wrappers=[LLMObservationWrapper], starting_coins=25)
# register(id="LetterAuction-v0-raw", entry_point="textarena.envs.games.LetterAuction.env:LetterAuctionEnv", starting_coins=100)
# register(id="LetterAuction-v0-raw-medium", entry_point="textarena.envs.games.LetterAuction.env:LetterAuctionEnv", starting_coins=50)
# register(id="LetterAuction-v0-raw-hard", entry_point="textarena.envs.games.LetterAuction.env:LetterAuctionEnv", starting_coins=25)


# # MemoryGame (two-player)
# register(id="MemoryGame-v0", entry_point="textarena.envs.games.MemoryGame.env:MemoryGameEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], grid_size=4)
# register(id="MemoryGame-v0-medium", entry_point="textarena.envs.games.MemoryGame.env:MemoryGameEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], grid_size=6)
# register(id="MemoryGame-v0-hard", entry_point="textarena.envs.games.MemoryGame.env:MemoryGameEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], grid_size=8)
# register(id="MemoryGame-v0-raw", entry_point="textarena.envs.games.MemoryGame.env:MemoryGameEnv", grid_size=4)
# register(id="MemoryGame-v0-raw-medium", entry_point="textarena.envs.games.MemoryGame.env:MemoryGameEnv", grid_size=6)
# register(id="MemoryGame-v0-raw-hard", entry_point="textarena.envs.games.MemoryGame.env:MemoryGameEnv", grid_size=8)
# register(id="MemoryGame-v0-train", entry_point="textarena.envs.games.MemoryGame.env:MemoryGameEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], grid_size=4)
# register(id="MemoryGame-v0-train-medium", entry_point="textarena.envs.games.MemoryGame.env:MemoryGameEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], grid_size=6)
# register(id="MemoryGame-v0-train-hard", entry_point="textarena.envs.games.MemoryGame.env:MemoryGameEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], grid_size=8)


# # Nim (two-player)
# register(id="Nim-v0", entry_point="textarena.envs.games.Nim.env:NimEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], piles=[3, 4, 5])
# register(id="Nim-v0-small", entry_point="textarena.envs.games.Nim.env:NimEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], piles=[1, 2, 3])
# register(id="Nim-v0-large", entry_point="textarena.envs.games.Nim.env:NimEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], piles=[5, 7, 9])
# register(id="Nim-v0-raw", entry_point="textarena.envs.games.Nim.env:NimEnv", piles=[3, 4, 5])
# register(id="Nim-v0-raw-small", entry_point="textarena.envs.games.Nim.env:NimEnv", piles=[1, 2, 3])
# register(id="Nim-v0-raw-large", entry_point="textarena.envs.games.Nim.env:NimEnv", piles=[5, 7, 9])
# register(id="Nim-v0-train", entry_point="textarena.envs.games.Nim.env:NimEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], piles=[3, 4, 5])
# register(id="Nim-v0-train-small", entry_point="textarena.envs.games.Nim.env:NimEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], piles=[1, 2, 3])
# register(id="Nim-v0-train-large", entry_point="textarena.envs.games.Nim.env:NimEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], piles=[5, 7, 9])


# # Othello/Reversi (two-player)
# register(id="Othello-v0", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], show_valid=True)
# register(id="Othello-v0-tiny", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], board_size=4, show_valid=True)
# register(id="Othello-v0-small", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], board_size=6, show_valid=True)
# register(id="Othello-v0-big", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], board_size=10, show_valid=True)
# register(id="Othello-v0-huge", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], board_size=14, show_valid=True)
# register(id="Othello-v0-hard", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], show_valid=False)
# register(id="Othello-v0-raw", entry_point="textarena.envs.games.Othello.env:OthelloEnv", show_valid=True)
# register(id="Othello-v0-raw-tiny", entry_point="textarena.envs.games.Othello.env:OthelloEnv", board_size=4, show_valid=True)
# register(id="Othello-v0-raw-small", entry_point="textarena.envs.games.Othello.env:OthelloEnv", board_size=6, show_valid=True)
# register(id="Othello-v0-raw-big", entry_point="textarena.envs.games.Othello.env:OthelloEnv", board_size=10, show_valid=True)
# register(id="Othello-v0-raw-huge", entry_point="textarena.envs.games.Othello.env:OthelloEnv", board_size=14, show_valid=True)
# register(id="Othello-v0-raw-hard", entry_point="textarena.envs.games.Othello.env:OthelloEnv", show_valid=False)
# register(id="Othello-v0-train", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], show_valid=True)
# register(id="Othello-v0-train-tiny", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], board_size=4, show_valid=True)
# register(id="Othello-v0-train-small", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], board_size=6, show_valid=True)
# register(id="Othello-v0-train-big", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], board_size=10, show_valid=True)
# register(id="Othello-v0-train-huge", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], board_size=14, show_valid=True)
# register(id="Othello-v0-train-hard", entry_point="textarena.envs.games.Othello.env:OthelloEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], show_valid=False)


# # Pig (two-player)
# register(id="PigDice-v0", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], winning_score=100, max_turns=100)
# register(id="PigDice-v0-short", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], winning_score=50, max_turns=25)
# register(id="PigDice-v0-long", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], winning_score=500, max_turns=500)
# register(id="PigDice-v0-raw", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", winning_score=100, max_turns=100)
# register(id="PigDice-v0-raw-short", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", winning_score=50, max_turns=50)
# register(id="PigDice-v0-raw-long", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", winning_score=500, max_turns=500)
# register(id="PigDice-v0-train", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=100, max_turns=100)
# register(id="PigDice-v0-train-short", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=50, max_turns=50)
# register(id="PigDice-v0-train-long", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=500, max_turns=500)

# register(id="PigDice-v0-train-50", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=50, max_turns=50)
# register(id="PigDice-v0-train-100", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=100, max_turns=100)
# register(id="PigDice-v0-train-150", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=150, max_turns=150)
# register(id="PigDice-v0-train-200", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=200, max_turns=200)
# register(id="PigDice-v0-train-250", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=250, max_turns=250)
# register(id="PigDice-v0-train-300", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=300, max_turns=300)
# register(id="PigDice-v0-train-350", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=350, max_turns=350)
# register(id="PigDice-v0-train-400", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=400, max_turns=400)
# register(id="PigDice-v0-train-450", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=450, max_turns=450)
# register(id="PigDice-v0-train-500", entry_point="textarena.envs.games.PigDice.env:PigDiceEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], winning_score=500, max_turns=500)


# # ScenarioPlanning (two-player)
# register(id="ScenarioPlanning-v0", entry_point="textarena.envs.games.ScenarioPlanning.env:ScenarioPlanningEnv", default_wrappers=[LLMObservationWrapper], jury_class=OpenRouterJury, jury_size=11)
# register(id="ScenarioPlanning-v0-raw", entry_point="textarena.envs.games.ScenarioPlanning.env:ScenarioPlanningEnv", jury_class=OpenRouterJury, jury_size=11)


# # SpellingBee (two-player)
# register(id="SpellingBee-v0", entry_point="textarena.envs.games.SpellingBee.env:SpellingBeeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_letters=7)
# register(id="SpellingBee-v0-small", entry_point="textarena.envs.games.SpellingBee.env:SpellingBeeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_letters=4)
# register(id="SpellingBee-v0-large", entry_point="textarena.envs.games.SpellingBee.env:SpellingBeeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_letters=10)
# register(id="SpellingBee-v0-raw", entry_point="textarena.envs.games.SpellingBee.env:SpellingBeeEnv", num_letters=7)
# register(id="SpellingBee-v0-raw-small", entry_point="textarena.envs.games.SpellingBee.env:SpellingBeeEnv", num_letters=4)
# register(id="SpellingBee-v0-raw-large", entry_point="textarena.envs.games.SpellingBee.env:SpellingBeeEnv", num_letters=10)
# register(id="SpellingBee-v0-train", entry_point="textarena.envs.games.SpellingBee.env:SpellingBeeEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_letters=7)
# register(id="SpellingBee-v0-train-small", entry_point="textarena.envs.games.SpellingBee.env:SpellingBeeEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_letters=4)
# register(id="SpellingBee-v0-train-large", entry_point="textarena.envs.games.SpellingBee.env:SpellingBeeEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_letters=10)

# # Taboo (two-player)
# register(id="Taboo-v0", entry_point="textarena.envs.games.Taboo.env:TabooEnv", default_wrappers=[LLMObservationWrapper], max_turns=6, categories=["things"])
# register(id="Taboo-v0-animals", entry_point="textarena.envs.games.Taboo.env:TabooEnv", default_wrappers=[LLMObservationWrapper], max_turns=6, categories=["animals"])
# register(id="Taboo-v0-cars", entry_point="textarena.envs.games.Taboo.env:TabooEnv", default_wrappers=[LLMObservationWrapper], max_turns=6, categories=["cars"])
# register(id="Taboo-v0-city/country", entry_point="textarena.envs.games.Taboo.env:TabooEnv", default_wrappers=[LLMObservationWrapper], max_turns=6, categories=["city/country"])
# register(id="Taboo-v0-food", entry_point="textarena.envs.games.Taboo.env:TabooEnv", default_wrappers=[LLMObservationWrapper], max_turns=6, categories=["food"])
# register(id="Taboo-v0-literature", entry_point="textarena.envs.games.Taboo.env:TabooEnv", default_wrappers=[LLMObservationWrapper], max_turns=6, categories=["literature"])
# register(id="Taboo-v0-people", entry_point="textarena.envs.games.Taboo.env:TabooEnv", default_wrappers=[LLMObservationWrapper], max_turns=6, categories=["people"])
# register(id="Taboo-v0-tv", entry_point="textarena.envs.games.Taboo.env:TabooEnv", default_wrappers=[LLMObservationWrapper], max_turns=6, categories=["tv"])
# register(id="Taboo-v0-long", entry_point="textarena.envs.games.Taboo.env:TabooEnv", default_wrappers=[LLMObservationWrapper], max_turns=24, categories=["things"])
# register(id="Taboo-v0-full", entry_point="textarena.envs.games.Taboo.env:TabooEnv", default_wrappers=[LLMObservationWrapper], max_turns=6, categories=["animals", "cars", "city/country", "food", "literature", "people", "things", "tv"])
# register(id="Taboo-v0-raw", entry_point="textarena.envs.games.Taboo.env:TabooEnv", max_turns=6, categories=["things"])
# register(id="Taboo-v0-raw-animals", entry_point="textarena.envs.games.Taboo.env:TabooEnv", max_turns=6, categories=["animals"])
# register(id="Taboo-v0-raw-cars", entry_point="textarena.envs.games.Taboo.env:TabooEnv", max_turns=6, categories=["cars"])
# register(id="Taboo-v0-raw-city/country", entry_point="textarena.envs.games.Taboo.env:TabooEnv", max_turns=6, categories=["city/country"])
# register(id="Taboo-v0-raw-food", entry_point="textarena.envs.games.Taboo.env:TabooEnv", max_turns=6, categories=["food"])
# register(id="Taboo-v0-raw-literature", entry_point="textarena.envs.games.Taboo.env:TabooEnv", max_turns=6, categories=["literature"])
# register(id="Taboo-v0-raw-people", entry_point="textarena.envs.games.Taboo.env:TabooEnv", max_turns=6, categories=["people"])
# register(id="Taboo-v0-raw-tv", entry_point="textarena.envs.games.Taboo.env:TabooEnv", max_turns=6, categories=["tv"])
# register(id="Taboo-v0-raw-long", entry_point="textarena.envs.games.Taboo.env:TabooEnv", max_turns=24, categories=["things"])
# register(id="Taboo-v0-raw-full", entry_point="textarena.envs.games.Taboo.env:TabooEnv", max_turns=6, categories=["animals", "cars", "city/country", "food", "literature", "people", "things", "tv"])


# # TicTacToe (two-player)
# register(id="TicTacToe-v0", entry_point="textarena.envs.games.TicTacToe.env:TicTacToeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="TicTacToe-v0-raw", entry_point="textarena.envs.games.TicTacToe.env:TicTacToeEnv")
# register(id="TicTacToe-v0-train", entry_point="textarena.envs.games.TicTacToe.env:TicTacToeEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper])


# # WildTicTacToe (two-player)
# register(id="WildTicTacToe-v0", entry_point="textarena.envs.games.WildTicTacToe.env:WildTicTacToeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="WildTicTacToe-v0-raw", entry_point="textarena.envs.games.WildTicTacToe.env:WildTicTacToeEnv")


# # ReverseTicTacToe (two-player)
# register(id="ReverseTicTacToe-v0", entry_point="textarena.envs.games.ReverseTicTacToe.env:ReverseTicTacToeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="ReverseTicTacToe-v0-raw", entry_point="textarena.envs.games.ReverseTicTacToe.env:ReverseTicTacToeEnv")


# # RandomizedTicTacToe (two-player)
# register(id="RandomizedTicTacToe-v0", entry_point="textarena.envs.games.RandomizedTicTacToe.env:RandomizedTicTacToeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="RandomizedTicTacToe-v0-raw", entry_point="textarena.envs.games.RandomizedTicTacToe.env:RandomizedTicTacToeEnv")

# # QuantumTicTacToe (two-player)
# register(id="QuantumTicTacToe-v0", entry_point="textarena.envs.games.QuantumTicTacToe.env:QuantumTicTacToeEnv", default_wrappers=[LLMObservationWrapper])
# register(id="QuantumTicTacToe-v0-raw", entry_point="textarena.envs.games.QuantumTicTacToe.env:QuantumTicTacToeEnv")


# # IteratedPrisonersDilemma (two-player)
# register(id="IteratedPrisonersDilemma-v0", entry_point="textarena.envs.games.IteratedPrisonersDilemma.env:IteratedPrisonersDilemmaEnv", default_wrappers=[LLMObservationWrapper], num_rounds=10, communication_turns=3, cooperate_reward=3, defect_reward=5, sucker_reward=0, mutual_defect_reward=1)
# register(id="IteratedPrisonersDilemma-v0-raw", entry_point="textarena.envs.games.IteratedPrisonersDilemma.env:IteratedPrisonersDilemmaEnv", num_rounds=10, communication_turns=3, cooperate_reward=3, defect_reward=5, sucker_reward=0, mutual_defect_reward=1)


# # IteratedRockPaperScissors (two-player)
# register(id="IteratedRockPaperScissors-v0", entry_point="textarena.envs.games.IteratedRockPaperScissors.env:IteratedRockPaperScissorsEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_rounds=10)
# register(id="IteratedRockPaperScissors-v0-raw", entry_point="textarena.envs.games.IteratedRockPaperScissors.env:IteratedRockPaperScissorsEnv", num_rounds=10)
# register(id="IteratedRockPaperScissors-v0-train", entry_point="textarena.envs.games.IteratedRockPaperScissors.env:IteratedRockPaperScissorsEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_rounds=10)

# # IteratedTwoThirdsAverage (two-player) # TODO can be extended to multi-player
# register(id="IteratedTwoThirdsAverage-v0", entry_point="textarena.envs.games.IteratedTwoThirdsAverage.env:IteratedTwoThirdsAverageEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_rounds=10, min_guess=0.0, max_guess=100.0)
# register(id="IteratedTwoThirdsAverage-v0-raw", entry_point="textarena.envs.games.IteratedTwoThirdsAverage.env:IteratedTwoThirdsAverageEnv", num_rounds=10, min_guess=0.0, max_guess=100.0)
# register(id="IteratedTwoThirdsAverage-v0-train", entry_point="textarena.envs.games.IteratedTwoThirdsAverage.env:IteratedTwoThirdsAverageEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_rounds=10, min_guess=0.0, max_guess=100.0)

# # IteratedMatchingPennies (two-player)
# register(id="IteratedMatchingPennies-v0", entry_point="textarena.envs.games.IteratedMatchingPennies.env:IteratedMatchingPenniesEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_rounds=10)
# register(id="IteratedMatchingPennies-v0-raw", entry_point="textarena.envs.games.IteratedMatchingPennies.env:IteratedMatchingPenniesEnv", num_rounds=10)
# register(id="IteratedMatchingPennies-v0-train", entry_point="textarena.envs.games.IteratedMatchingPennies.env:IteratedMatchingPenniesEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_rounds=10)


# # Stratego (two-player)
# register(id="Stratego-v0", entry_point="textarena.envs.games.Stratego.env:StrategoEnv", default_wrappers=[LLMObservationWrapper])
# register(id="Stratego-v0-raw", entry_point="textarena.envs.games.Stratego.env:StrategoEnv")


# # SpiteAndMalice (two-player)
# register(id="SpiteAndMalice-v0", entry_point="textarena.envs.games.SpiteAndMalice.env:SpiteAndMaliceEnv", default_wrappers=[LLMObservationWrapper])
# register(id="SpiteAndMalice-v0-raw", entry_point="textarena.envs.games.SpiteAndMalice.env:SpiteAndMaliceEnv")


# # Tak (two-player)
# register(id="Tak-v0", entry_point="textarena.envs.games.Tak.env:TakEnv", default_wrappers=[LLMObservationWrapper], board_size=4, stones=15, capstones=1)
# register(id="Tak-v0-medium", entry_point="textarena.envs.games.Tak.env:TakEnv", default_wrappers=[LLMObservationWrapper], board_size=5, stones=21, capstones=1)
# register(id="Tak-v0-hard", entry_point="textarena.envs.games.Tak.env:TakEnv", default_wrappers=[LLMObservationWrapper], board_size=6, stones=30, capstones=1)
# register(id="Tak-v0-raw", entry_point="textarena.envs.games.Tak.env:TakEnv", board_size=4, stones=15, capstones=1)
# register(id="Tak-v0-raw-medium", entry_point="textarena.envs.games.Tak.env:TakEnv", board_size=5, stones=21, capstones=1)
# register(id="Tak-v0-raw-hard", entry_point="textarena.envs.games.Tak.env:TakEnv", board_size=6, stones=30, capstones=1)


# # SimpleTak (two-player)
# register(id="SimpleTak-v0", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], board_size=4)
# register(id="SimpleTak-v0-medium", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], board_size=5)
# register(id="SimpleTak-v0-large", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], board_size=6)
# register(id="SimpleTak-v0-extra-large", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], board_size=8)
# register(id="SimpleTak-v0-raw", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", board_size=4)
# register(id="SimpleTak-v0-raw-medium", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", board_size=5)
# register(id="SimpleTak-v0-raw-large", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", board_size=6)
# register(id="SimpleTak-v0-raw-extra-large", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", board_size=8)
# register(id="SimpleTak-v0-train", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], board_size=4)
# register(id="SimpleTak-v0-train-medium", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], board_size=5)
# register(id="SimpleTak-v0-train-large", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], board_size=6)
# register(id="SimpleTak-v0-train-extra-large", entry_point="textarena.envs.games.SimpleTak.env:SimpleTakEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], board_size=8)


# # TruthAndDeception (two-player) [TODO can extend to more players]
# register(id="TruthAndDeception-v0", entry_point="textarena.envs.games.TruthAndDeception.env:TruthAndDeceptionEnv", default_wrappers=[LLMObservationWrapper], max_turns=6)
# register(id="TruthAndDeception-v0-long", entry_point="textarena.envs.games.TruthAndDeception.env:TruthAndDeceptionEnv", default_wrappers=[LLMObservationWrapper], max_turns=12)
# register(id="TruthAndDeception-v0-extreme", entry_point="textarena.envs.games.TruthAndDeception.env:TruthAndDeceptionEnv", default_wrappers=[LLMObservationWrapper], max_turns=50)
# register(id="TruthAndDeception-v0-raw", entry_point="textarena.envs.games.TruthAndDeception.env:TruthAndDeceptionEnv", max_turns=6)
# register(id="TruthAndDeception-v0-raw-long", entry_point="textarena.envs.games.TruthAndDeception.env:TruthAndDeceptionEnv", max_turns=12)
# register(id="TruthAndDeception-v0-raw-extreme", entry_point="textarena.envs.games.TruthAndDeception.env:TruthAndDeceptionEnv", max_turns=50)


# # UltimateTicTacToe (two-player)
# register(id="UltimateTicTacToe-v0", entry_point="textarena.envs.games.UltimateTicTacToe.env:UltimateTicTacToeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="UltimateTicTacToe-v0-raw", entry_point="textarena.envs.games.UltimateTicTacToe.env:UltimateTicTacToeEnv")
# register(id="UltimateTicTacToe-v0-train", entry_point="textarena.envs.games.UltimateTicTacToe.env:UltimateTicTacToeEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper])


# # WordChains (two-player)
# register(id="WordChains-v0", entry_point="textarena.envs.games.WordChains.env:WordChainsEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="WordChains-v0-raw", entry_point="textarena.envs.games.WordChains.env:WordChainsEnv")
# register(id="WordChains-v0-train", entry_point="textarena.envs.games.WordChains.env:WordChainsEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper])


# # Debate (two-player)
# register(id="Debate-v0", entry_point="textarena.envs.games.Debate.env:DebateEnv", default_wrappers=[LLMObservationWrapper], max_turns=6, jury_class=OpenRouterJury, jury_size=7)
# register(id="Debate-v0-medium", entry_point="textarena.envs.games.Debate.env:DebateEnv", default_wrappers=[LLMObservationWrapper], max_turns=12, jury_class=OpenRouterJury, jury_size=9)
# register(id="Debate-v0-long", entry_point="textarena.envs.games.Debate.env:DebateEnv", default_wrappers=[LLMObservationWrapper], max_turns=30, jury_class=OpenRouterJury, jury_size=13)
# register(id="Debate-v0-raw", entry_point="textarena.envs.games.Debate.env:DebateEnv", max_turns=6, jury_class=OpenRouterJury, jury_size=7)
# register(id="Debate-v0-raw-medium", entry_point="textarena.envs.games.Debate.env:DebateEnv", max_turns=12, jury_class=OpenRouterJury, jury_size=9)
# register(id="Debate-v0-raw-long", entry_point="textarena.envs.games.Debate.env:DebateEnv", max_turns=30, jury_class=OpenRouterJury, jury_size=13)


# # SimpleNegotiation (two-player)
# register(id="SimpleNegotiation-v0", entry_point="textarena.envs.games.SimpleNegotiation.env:SimpleNegotiationEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_turns=10)
# register(id="SimpleNegotiation-v0-short", entry_point="textarena.envs.games.SimpleNegotiation.env:SimpleNegotiationEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_turns=6)
# register(id="SimpleNegotiation-v0-long", entry_point="textarena.envs.games.SimpleNegotiation.env:SimpleNegotiationEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], max_turns=30)
# register(id="SimpleNegotiation-v0-raw", entry_point="textarena.envs.games.SimpleNegotiation.env:SimpleNegotiationEnv", max_turns=10)
# register(id="SimpleNegotiation-v0-raw-short", entry_point="textarena.envs.games.SimpleNegotiation.env:SimpleNegotiationEnv", max_turns=6)
# register(id="SimpleNegotiation-v0-raw-long", entry_point="textarena.envs.games.SimpleNegotiation.env:SimpleNegotiationEnv", max_turns=30)
# register(id="SimpleNegotiation-v0-train", entry_point="textarena.envs.games.SimpleNegotiation.env:SimpleNegotiationEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], max_turns=10)
# register(id="SimpleNegotiation-v0-train-short", entry_point="textarena.envs.games.SimpleNegotiation.env:SimpleNegotiationEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], max_turns=6)
# register(id="SimpleNegotiation-v0-train-long", entry_point="textarena.envs.games.SimpleNegotiation.env:SimpleNegotiationEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], max_turns=30)


# # SimpleBlindAunction (two-player)
# register(id="SimpleBlindAuction-v0", entry_point="textarena.envs.games.SimpleBlindAuction.env:SimpleBlindAuctionEnv", default_wrappers=[LLMObservationWrapper], starting_capital=1000, num_items=5, conversation_rounds=3)
# register(id="SimpleBlindAuction-v0-quick", entry_point="textarena.envs.games.SimpleBlindAuction.env:SimpleBlindAuctionEnv", default_wrappers=[LLMObservationWrapper], starting_capital=750, num_items=3, conversation_rounds=1)
# register(id="SimpleBlindAuction-v0-rich", entry_point="textarena.envs.games.SimpleBlindAuction.env:SimpleBlindAuctionEnv", default_wrappers=[LLMObservationWrapper], starting_capital=2000,  num_items=5, conversation_rounds=5)
# register(id="SimpleBlindAuction-v0-raw", entry_point="textarena.envs.games.SimpleBlindAuction.env:SimpleBlindAuctionEnv", starting_capital=1000, num_items=5, conversation_rounds=3)
# register(id="SimpleBlindAuction-v0-raw-quick", entry_point="textarena.envs.games.SimpleBlindAuction.env:SimpleBlindAuctionEnv", starting_capital=750, num_items=3, conversation_rounds=1)
# register(id="SimpleBlindAuction-v0-raw-rich", entry_point="textarena.envs.games.SimpleBlindAuction.env:SimpleBlindAuctionEnv", starting_capital=2000,  num_items=5, conversation_rounds=5)

# # HighSociety (two-player)
# register(id="HighSociety-v0", entry_point="textarena.envs.games.HighSociety.env:HighSocietyEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="HighSociety-v0-raw", entry_point="textarena.envs.games.HighSociety.env:HighSocietyEnv")
# register(id="HighSociety-v0-train", entry_point="textarena.envs.games.HighSociety.env:HighSocietyEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper])

# # Negotiation (2-15 players)
# register(id="Negotiation-v0", entry_point="textarena.envs.games.Negotiation.env:NegotiationEnv", default_wrappers=[LLMObservationWrapper], turn_multiple=8)
# register(id="Negotiation-v0-long", entry_point="textarena.envs.games.Negotiation.env:NegotiationEnv", default_wrappers=[LLMObservationWrapper], turn_multiple=15)
# register(id="Negotiation-v0-raw", entry_point="textarena.envs.games.Negotiation.env:NegotiationEnv", turn_multiple=8)
# register(id="Negotiation-v0-raw-long", entry_point="textarena.envs.games.Negotiation.env:NegotiationEnv", turn_multiple=15)


# # BlindAuction (3-15 players)
# register(id="BlindAuction-v0", entry_point="textarena.envs.games.BlindAuction.env:BlindAuctionEnv", default_wrappers=[LLMObservationWrapper], starting_capital=1000, num_items=5, conversation_rounds=3)
# register(id="BlindAuction-v0-high", entry_point="textarena.envs.games.BlindAuction.env:BlindAuctionEnv", default_wrappers=[LLMObservationWrapper], starting_capital=2500, num_items=8, conversation_rounds=5)
# register(id="BlindAuction-v0-fast", entry_point="textarena.envs.games.BlindAuction.env:BlindAuctionEnv", default_wrappers=[LLMObservationWrapper], starting_capital=750,  num_items=3, conversation_rounds=1)
# register(id="BlindAuction-v0-complex", entry_point="textarena.envs.games.BlindAuction.env:BlindAuctionEnv", default_wrappers=[LLMObservationWrapper], starting_capital=1500, num_items=12, conversation_rounds=8)
# register(id="BlindAuction-v0-raw", entry_point="textarena.envs.games.BlindAuction.env:BlindAuctionEnv", starting_capital=1000, num_items=5, conversation_rounds=3)
# register(id="BlindAuction-v0-raw-high", entry_point="textarena.envs.games.BlindAuction.env:BlindAuctionEnv", starting_capital=2500, num_items=8, conversation_rounds=5)
# register(id="BlindAuction-v0-raw-fast", entry_point="textarena.envs.games.BlindAuction.env:BlindAuctionEnv", starting_capital=750,  num_items=3, conversation_rounds=1)
# register(id="BlindAuction-v0-raw-complex", entry_point="textarena.envs.games.BlindAuction.env:BlindAuctionEnv", starting_capital=1500, num_items=12, conversation_rounds=8)


# # Snake (2-15 players)
# register(id="Snake-v0", entry_point="textarena.envs.games.Snake.env:SnakeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], width=5, height=5, num_apples=2, max_turns=40)
# register(id="Snake-v0-standard", entry_point="textarena.envs.games.Snake.env:SnakeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], width=10, height=10, num_apples=3, max_turns=100)
# register(id="Snake-v0-large", entry_point="textarena.envs.games.Snake.env:SnakeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], width=15, height=15, num_apples=5, max_turns=250)
# register(id="Snake-v0-raw", entry_point="textarena.envs.games.Snake.env:SnakeEnv", width=5, height=5, num_apples=2, max_turns=40)
# register(id="Snake-v0-raw-standard", entry_point="textarena.envs.games.Snake.env:SnakeEnv", width=10, height=10, num_apples=3, max_turns=100)
# register(id="Snake-v0-raw-large", entry_point="textarena.envs.games.Snake.env:SnakeEnv", width=15, height=15, num_apples=5, max_turns=250)
# register(id="Snake-v0-train", entry_point="textarena.envs.games.Snake.env:SnakeEnv", default_wrappers=[GameBoardObservationWrapper, ActionFormattingWrapper], width=5, height=5, num_apples=2, max_turns=40)
# register(id="Snake-v0-train-small", entry_point="textarena.envs.games.Snake.env:SnakeEnv", default_wrappers=[GameBoardObservationWrapper, ActionFormattingWrapper], width=4, height=4, num_apples=1, max_turns=30)
# register(id="Snake-v0-train-standard", entry_point="textarena.envs.games.Snake.env:SnakeEnv", default_wrappers=[GameBoardObservationWrapper, ActionFormattingWrapper], width=10, height=10, num_apples=3, max_turns=100)
# register(id="Snake-v0-train-large", entry_point="textarena.envs.games.Snake.env:SnakeEnv", default_wrappers=[GameBoardObservationWrapper, ActionFormattingWrapper], width=15, height=15, num_apples=5, max_turns=250)


# # Surround (2-15 players)
# register(id="Surround-v0", entry_point="textarena.envs.games.Surround.env:SurroundEnv", default_wrappers=[LLMObservationWrapper], width=5, height=5, max_turns=40)
# register(id="Surround-v0-large", entry_point="textarena.envs.games.Surround.env:SurroundEnv", default_wrappers=[LLMObservationWrapper], width=10, height=10, max_turns=100)
# register(id="Surround-v0-huge", entry_point="textarena.envs.games.Surround.env:SurroundEnv", default_wrappers=[LLMObservationWrapper], width=15, height=15, max_turns=250)
# register(id="Surround-v0-raw", entry_point="textarena.envs.games.Surround.env:SurroundEnv", width=5, height=5, max_turns=40)
# register(id="Surround-v0-raw-large", entry_point="textarena.envs.games.Surround.env:SurroundEnv", width=10, height=10, max_turns=100)
# register(id="Surround-v0-raw-huge", entry_point="textarena.envs.games.Surround.env:SurroundEnv", width=15, height=15, max_turns=250)


# # LiarsDice (2-15 players)
# register(id="LiarsDice-v0-small", entry_point="textarena.envs.games.LiarsDice.env:LiarsDiceEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_dice=3)
# register(id="LiarsDice-v0", entry_point="textarena.envs.games.LiarsDice.env:LiarsDiceEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_dice=5)
# register(id="LiarsDice-v0-large", entry_point="textarena.envs.games.LiarsDice.env:LiarsDiceEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_dice=12)
# register(id="LiarsDice-v0-raw", entry_point="textarena.envs.games.LiarsDice.env:LiarsDiceEnv", num_dice=5)
# register(id="LiarsDice-v0-raw-large", entry_point="textarena.envs.games.LiarsDice.env:LiarsDiceEnv", num_dice=12)
# register(id="LiarsDice-v0-train-small", entry_point="textarena.envs.games.LiarsDice.env:LiarsDiceEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_dice=3)
# register(id="LiarsDice-v0-train", entry_point="textarena.envs.games.LiarsDice.env:LiarsDiceEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_dice=5)
# register(id="LiarsDice-v0-train-large", entry_point="textarena.envs.games.LiarsDice.env:LiarsDiceEnv", default_wrappers=[GameMessagesObservationWrapper, ActionFormattingWrapper], num_dice=12)

# # Poker (2-15 players)
# register(id="Poker-v0-small", entry_point="textarena.envs.games.Poker.env:PokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_rounds=5, starting_chips=1_000, small_blind=10, big_blind=20)
# register(id="Poker-v0", entry_point="textarena.envs.games.Poker.env:PokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_rounds=10, starting_chips=1_000, small_blind=10, big_blind=20)
# register(id="Poker-v0-long", entry_point="textarena.envs.games.Poker.env:PokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_rounds=15, starting_chips=1_000, small_blind=10, big_blind=20)
# register(id="Poker-v0-extreme", entry_point="textarena.envs.games.Poker.env:PokerEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper], num_rounds=50, starting_chips=1_000, small_blind=10, big_blind=20)
# register(id="Poker-v0-raw", entry_point="textarena.envs.games.Poker.env:PokerEnv", num_rounds=10, starting_chips=1_000, small_blind=10, big_blind=20)
# register(id="Poker-v0-raw-long", entry_point="textarena.envs.games.Poker.env:PokerEnv", num_rounds=15, starting_chips=1_000, small_blind=10, big_blind=20)
# register(id="Poker-v0-raw-extreme", entry_point="textarena.envs.games.Poker.env:PokerEnv", num_rounds=50, starting_chips=1_000, small_blind=10, big_blind=20)
# register(id="Poker-v0-train-small", entry_point="textarena.envs.games.Poker.env:PokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], num_rounds=5, starting_chips=1_000, small_blind=10, big_blind=20)
# register(id="Poker-v0-train", entry_point="textarena.envs.games.Poker.env:PokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], num_rounds=10, starting_chips=1_000, small_blind=10, big_blind=20)
# register(id="Poker-v0-train-long", entry_point="textarena.envs.games.Poker.env:PokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], num_rounds=15, starting_chips=1_000, small_blind=10, big_blind=20)
# register(id="Poker-v0-train-extreme", entry_point="textarena.envs.games.Poker.env:PokerEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper], num_rounds=50, starting_chips=1_000, small_blind=10, big_blind=20)


# # Character Conclave (3-15 players)
# register(id="CharacterConclave-v0", entry_point="textarena.envs.games.CharacterConclave.env:CharacterConclaveEnv", default_wrappers=[LLMObservationWrapper], character_budget=1_000)
# register(id="CharacterConclave-v0-long", entry_point="textarena.envs.games.CharacterConclave.env:CharacterConclaveEnv", default_wrappers=[LLMObservationWrapper], character_budget=5_000)
# register(id="CharacterConclave-v0-extreme", entry_point="textarena.envs.games.CharacterConclave.env:CharacterConclaveEnv", default_wrappers=[LLMObservationWrapper], character_budget=10_000)
# register(id="CharacterConclave-v0-raw", entry_point="textarena.envs.games.CharacterConclave.env:CharacterConclaveEnv", character_budget=1_000)
# register(id="CharacterConclave-v0-raw-long", entry_point="textarena.envs.games.CharacterConclave.env:CharacterConclaveEnv", character_budget=5_000)
# register(id="CharacterConclave-v0-raw-extreme", entry_point="textarena.envs.games.CharacterConclave.env:CharacterConclaveEnv", character_budget=10_000)

# # Diplomacy (3-7 players)
# register(id="Diplomacy-v0", entry_point="textarena.envs.games.Diplomacy.env:DiplomacyEnv", default_wrappers=[LLMObservationWrapper], max_turns=1_000)
# register(id="Diplomacy-v0-raw", entry_point="textarena.envs.games.Diplomacy.env:DiplomacyEnv", max_turns=1_000)


# # SecretMafia (5-15 players)
# register(id="SecretMafia-v0", entry_point="textarena.envs.games.SecretMafia.env:SecretMafiaEnv", default_wrappers=[LLMObservationWrapper], mafia_ratio=0.25, discussion_rounds=3) 
# register(id="SecretMafia-v0-raw", entry_point="textarena.envs.games.SecretMafia.env:SecretMafiaEnv", mafia_ratio=0.25, discussion_rounds=3) 


# # Codenames (4 players)
# register(id="Codenames-v0", entry_point="textarena.envs.games.Codenames.env:CodenamesEnv", default_wrappers=[LLMObservationWrapper], hardcore=False) 
# register(id="Codenames-v0-hardcore", entry_point="textarena.envs.games.Codenames.env:CodenamesEnv", default_wrappers=[LLMObservationWrapper], hardcore=True) 
# register(id="Codenames-v0-raw", entry_point="textarena.envs.games.Codenames.env:CodenamesEnv", hardcore=False) 
# register(id="Codenames-v0-raw-hardcore", entry_point="textarena.envs.games.Codenames.env:CodenamesEnv", hardcore=True) 


# # EmojiCharade (4 players)
# register(id="EmojiCharade-v0", entry_point="textarena.envs.games.EmojiCharade.env:EmojiCharadeEnv", default_wrappers=[LLMObservationWrapper]) 
# register(id="EmojiCharade-v0-raw", entry_point="textarena.envs.games.EmojiCharade.env:EmojiCharadeEnv") 

# # ThreePlayerTicTacToe (3 players)
# register(id="ThreePlayerTicTacToe-v0", entry_point="textarena.envs.games.ThreePlayerTicTacToe.env:ThreePlayerTicTacToeEnv", default_wrappers=[LLMObservationWrapper, ActionFormattingWrapper])
# register(id="ThreePlayerTicTacToe-v0-train", entry_point="textarena.envs.games.ThreePlayerTicTacToe.env:ThreePlayerTicTacToeEnv", default_wrappers=[GameMessagesAndCurrentBoardObservationWrapper, ActionFormattingWrapper])
# register(id="ThreePlayerTicTacToe-v0-raw", entry_point="textarena.envs.games.ThreePlayerTicTacToe.env:ThreePlayerTicTacToeEnv")
