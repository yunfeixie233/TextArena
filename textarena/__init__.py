""" Root __init__ of textarena """

from textarena.core import Env, Wrapper, ObservationWrapper, RenderWrapper, ActionWrapper, Agent, AgentWrapper, State, Message, Observations, Rewards, Info, GAME_ID
from textarena.envs.registration import make, register, pprint_registry_detailed, check_env_exists
from textarena.api import make_online

import textarena.envs.games.utils
import textarena.envs.datasets

from textarena import wrappers, agents

__all__ = [
    "Env", "Wrapper", "ObservationWrapper", "RenderWrapper", "ActionWrapper", "AgentWrapper", # core
    "make", "register", "pprint_registry_detailed", "check_env_exists", # registration
    "envs", "utils", "wrappers", # module folders
    "make_online", # play online
]
__version__ = "0.6.9"
