""" Run tests for all environments """
import unittest
import textarena as ta 
from textarena.envs.two_player import ConnectFour, DontSayIt, Debate

# Import test modules with unique aliases to avoid name conflicts
from textarena.envs.two_player.ConnectFour import test as ConnectFourTest
from textarena.envs.two_player.DontSayIt import test as DontSayItTest
from textarena.envs.two_player.Debate import test as DebateTest
from textarena.envs.two_player.ScenarioPlanning import test as ScenarioPlanningTest

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

if __name__ == "__main__":
    run_all_tests()
