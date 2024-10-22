""" Run tests for all environments """
import unittest
import textarena as ta 
from textarena.envs import two_player
from textarena.envs.two_player import (
    ConnectFour,
    DontSayIt
)
from textarena.envs.two_player.ConnectFour import test
from textarena.envs.two_player.DontSayIt import test

# test Connect Four 
ta.envs.two_player.ConnectFour.test.run_unit_test()


# test Dont Say It
ta.envs.two_player.DontSayIt.test.run_unit_test()