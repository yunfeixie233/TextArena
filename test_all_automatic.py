""" Run tests for all environments """
import unittest
import textarena as ta 
from textarena.envs.two_player import ConnectFour, DontSayIt, Debate

# Import test modules with unique aliases to avoid name conflicts
from textarena.envs.two_player.ConnectFour import test as ConnectFourTest
from textarena.envs.two_player.DontSayIt import test as DontSayItTest
from textarena.envs.two_player.Debate import test as DebateTest
from textarena.envs.two_player.ScenarioPlanning import test as ScenarioPlanningTest
from textarena.envs.two_player.SpellingBee import test as SpellingBeeTest
from textarena.envs.two_player.Negotiation import test as NegotiationTest
from textarena.envs.two_player.LiarsDice import test as LiarsDiceTest
from textarena.envs.two_player.Chess import test as ChessTest
from textarena.envs.two_player.Taboo import test as TabooTest


# single_player games
from textarena.envs.single_player.Sudoku import test as SudokuTest
from textarena.envs.single_player.FifteenPuzzle import test as FifteenPuzzleTest
from textarena.envs.single_player.WordSearch import test as WordSearchTest
from textarena.envs.single_player.WordLadder import test as WordLadderTest
from textarena.envs.single_player.LogicPuzzle import test as LogicPuzzleTest
from textarena.envs.single_player.Crosswords import test as CrosswordsTest
from textarena.envs.single_player.Hangman import test as HangmanTest
from textarena.envs.single_player.GuessTheNumber import test as GuessTheNumberTest

# Function to run all tests
def run_all_tests():
    # Test Connect Four 
    print("Testing Connect Four")
    ConnectFourTest.run_unit_test()
    
    # Test Don't Say It
    print("Testing Don't Say It")
    DontSayItTest.run_unit_test()
    
    # Test Debate
    print("Testing Debate")
    DebateTest.run_unit_test()

    # Test Scenario Planning
    print("Testing Scenario Planning")
    ScenarioPlanningTest.run_unit_test()

    # Test Scenario Planning
    print("Testing Spelling Bee")
    SpellingBeeTest.run_unit_test()

    # Test Negotiation
    print("Testing Negotiation")
    NegotiationTest.run_unit_test()

    # Test Liars Dice
    print("Testing Liar's Dice")
    LiarsDiceTest.run_unit_test()
    
    # Test Sudoku
    print("Testing Sudoku")
    SudokuTest.run_unit_test()

    # Test Fifteen Puzzle
    print("Testing Fifteen Puzzle")
    FifteenPuzzleTest.run_unit_test()

    # Test Word Search
    print("Testing Word Search")
    WordSearchTest.run_unit_test()

    # Test Word Ladder
    print("Testing Word Ladder")
    WordLadderTest.run_unit_test()

    # Test Logic Puzzle
    print("Testing Logic Puzzle")
    LogicPuzzleTest.run_unit_test()

    # Test Crosswords
    print("Testing Crosswords")
    CrosswordsTest.run_unit_test()

    # Test Hangman
    print("Testing Hangman")
    HangmanTest.run_unit_test()

    # Test Guess The Number
    print("Testing Guess The Number")
    GuessTheNumberTest.run_unit_test()

    # Test Chess
    print("Testing Chess (2-player)")
    ChessTest.run_unit_test()

    # Test Taboo
    print("Testing Taboo (2-player)")
    TabooTest.run_unit_test()

if __name__ == "__main__":
    run_all_tests()
