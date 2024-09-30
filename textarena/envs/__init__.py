""" Register all environments """
from textarena.envs.registration import make, register #, pprint_registry, register, registry, spec

# Single Player Games



# Two Player Games
register(
    id="DontSayIt-v0",
    entry_point="textarena.envs.two_player.dont_say_it:DontSayItEnv",
    hardcore=False,
    max_turns=30
)

register(
    id="DontSayIt-v0-hardcore",
    entry_point="textarena.envs.two_player.dont_say_it:DontSayItEnv",
    hardcore=True,
    max_turns=30
)

register(
    id="DontSayIt-v0-unlimited",
    entry_point="textarena.envs.two_player.dont_say_it:DontSayItEnv",
    hardcore=False,
    max_turns=None
)



# Multi Player Games