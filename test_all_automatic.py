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


if __name__ == "__main__":
    run_all_tests()
