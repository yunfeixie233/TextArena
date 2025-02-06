from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional, Callable

import random

GAME_ID = -1  # literal for use in game messages
Message = Tuple[int, str]  # maps role to content
Observations = dict[
    int, List[Message]
]  # consists of the message seen by each player after the action
Rewards = Dict[int, int]  # maps player ID to reward
Info = Dict[str, Any]  # additional information about the environment


class State:
    """
    A class to manage the state of the game,
    including observations, rewards, and some game logic.
    """

    def __init__(
        self,
        num_players: int,
        max_turns: Optional[int] = None,
        role_mapping: Optional[Dict[int, str]] = {},
        check_truncated: Optional[bool] = True,
        error_allowance: Optional[int] = 1,
    ):
        """
        Initialize the State object.

        Args:
            num_players (int): Number of players in the game.
            max_turns (Optional[int]): Maximum number of turns before the game is truncated.
            role_mapping (Optional[Dict[int, str]]): Mapping from player IDs to role names.
            check_truncated (Optional[bool]): Whether to check for truncated games.
            error_allowance (Optional[int]): Number of errors allowed before a player loses the game.
        """
        self.num_players = num_players
        self.max_turns = max_turns
        self.check_truncated = check_truncated
        self.error_allowance = error_allowance

        # set standard state parameters
        self.logs = []
        self.turn = 0
        self.current_player_id = 0

        self.role_mapping = role_mapping
        self.role_mapping[-1] = "GAME"


    def reset(
        self,
        game_state: Dict[str, Any],
        player_prompt_function: Callable,
        executable_on_reset: Optional[List[Callable]] = None,
    ):
        """
        Reset the game state.

        Args:
            game_state (Dict[str, Any]): Initial game state to be set.
        """
        self.game_state = game_state
        self.current_player_id = 0
        self.turn = 0

        self.logs.append((GAME_ID, "Game started."))

        # set the error allowance tracker
        self.error_allowance_tracker  = {pid: self.error_allowance for pid in range(self.num_players)}

        self._reset_game_parameters()

        # generate the player prompts
        for player_id in range(self.num_players):
            self.add_observation(
                from_id=GAME_ID,
                to_id=player_id,
                message=player_prompt_function(
                    player_id=player_id,
                    game_state=self.game_state
                ),
                for_logging=False,
            )

        # try to execute relevant functions
        if executable_on_reset is not None:
            for executable in executable_on_reset:
                executable()

        return self.observations

    def _reset_game_parameters(self):
        """
        Reset the game parameters at the start of the game or after each step.
        """
        self.done = False 
        self.info = {}
        self.rewards = None
        self.observations = {pid: [] for pid in range(self.num_players)}


    def add_observation(
        self, from_id: int, to_id: int, message: str, for_logging: bool = True
    ):
        """
        Add an observation message to the observations and logs.

        Args:
            from_id (int): The ID of the sender (player or game).
            to_id (int): The ID of the receiver (-1 for all players).
            message (str): The message content.
            for_logging (bool): If True, the message is added to the logs.
        """
        if for_logging:
            # log the observation
            self.logs.append((from_id, message))

        # add to observations
        if to_id == -1:
            for pid in range(self.num_players): #self.observations:
                self.observations[pid].append((from_id, message))
        else:
            assert (
                to_id in self.observations
            ), f"The provided 'to_id' {to_id} does not exists. ({list(self.observations.keys())})"
            self.observations[to_id].append((from_id, message))

    def add_log(self, from_id: int, message: str):
        """TODO"""
        self.logs.append((from_id, message))

    def step(self, rotate_player : bool = True):
        """
        Advance the game state by one turn.

        Args:
            rotate_player  (bool): Whether to rotate the current player after the step.

        Returns:
            Tuple[
                bool,                               # done
                Dict[str, Any],                     # info
            ]: The updated game state after the step.
        """
        if self.done:  # if game happens to be terminated on last turn...
            return (True, self.info)

        # increment turn counter
        self.turn += 1

        # check if the turn limit has been reached
        if (
            self.max_turns is not None
            and self.turn >= self.max_turns
            and self.check_truncated
        ):
            # set the rewards
            self.rewards = {pid: 0 for pid in range(self.num_players)}

            # log the reason & update info
            reason = "Turn limit reached"
            self.logs.append((GAME_ID, reason))
            self.info["detailed_reason"] = reason
            self.info["reason"] = "Draw."
            self.done = True

        info = self.info
        done = self.done
        rewards = self.rewards

        # update current player
        if rotate_player :
            prev_player = self.current_player_id
            self.current_player_id = (self.current_player_id + 1) % self.num_players

        self.info = {}
        self.reward = None

        return (done, info)


    def close(self):
        return self.rewards

    def set_winners(self, player_ids: List[int], reason: Optional[str]):
        """
        Set the winners of the game.

        Args:
            player_ids (List[int]): List of player IDs who have won.
            reason (Optional[str]): Reason for winning.
        """

        # set the rewards
        self.rewards = {}
        for player_id in range(self.num_players):
            if player_id in player_ids:
                self.rewards[player_id] = 1
            else:
                self.rewards[player_id] = -1

        # log the reason & update info
        self.logs.append((GAME_ID, reason))
        self.add_observation(
            from_id=GAME_ID,
            to_id=-1,
            message=f"Player {player_ids[0]} won the game. Reason: {reason}",
            for_logging=False
        )
        self.info["reason"] = reason
        self.done = True

    def set_draw(self, reason: Optional[str]):
        """
        Declare the game as a draw.

        Args:
            reason (Optional[str]): Reason for the draw.
        """
        # set the rewards
        self.rewards = {pid: 0 for pid in range(self.num_players)}

        # log the reason & update info
        self.logs.append((GAME_ID, reason))
        self.add_observation(
            from_id=GAME_ID,
            to_id=-1,
            message=f"The game ended in a draw. Reason: {reason}",
            for_logging=False
        )
        self.info["reason"] = reason
        self.done = True

    def set_invalid_move(self, player_ids: List[int], reasons: Optional[List[str]]):
        """
        Handle an invalid move made by a player.

        Args:
            player_ids (List[int]): List of player IDs who made an invalid move.
            reason (Optional[str]): Reason for the invalid move.
        """

        ## ! - This won't handle 3 or more players in a game.
        if any(self.error_allowance_tracker[pid] > 0 for pid in player_ids):
            self.current_player_id = (self.current_player_id - 1) % self.num_players
            opponent_feedback = [(
                f"Player {', '.join(map(str, player_ids))} attempted an invalid move within its error allowance. Remember to follow the game rules to avoid penalties."
            )]
            log_feedback = [(
                f"Player {', '.join(map(str, player_ids))}'s move was invalid. Awaiting a new move."
            )]

            self.logs.append((GAME_ID, "; ".join(log_feedback)))
            for pid in player_ids:
                self.error_allowance_tracker[pid] -= 1
                player_feedback = [(
                    f"You've attempted an invalid move.\n"
                    f"You have {self.error_allowance_tracker[pid]} {'error allowances' if self.error_allowance_tracker[pid] > 1 else 'error allowance'} remaining.{' If another invalid move occurs, you will lose the game.' if self.error_allowance_tracker [pid] == 0 else ''}\n"
                    f"Please resubmit a valid move and remember to follow the game rules to avoid penalties."
                )]
                self.add_observation(
                    from_id=GAME_ID,
                    to_id=pid,
                    message="; ".join(player_feedback),
                    for_logging=False
                )

            ## Inform all other players of the invalid move
            for pid in range(self.num_players):
                if pid not in player_ids:
                    self.add_observation(
                        from_id=GAME_ID,
                        to_id=pid,
                        message="; ".join(opponent_feedback),
                        for_logging=False
                    )

            self.info["reason"] = f"Turn forfeited due to invalid move: {'; '.join(opponent_feedback)}"
        
        else:
            # set the rewards
            self.rewards = {}
            for player_id in range(self.num_players):
                if player_id in player_ids:
                    self.rewards[player_id] = -1
                else:
                    self.rewards[player_id] = 0

            # log the reason & update info
            self.logs.append((GAME_ID, "; ".join(reasons)))
            self.add_observation(
                from_id=GAME_ID,
                to_id=-1,
                message=f"Player {player_ids[0]} lost the game by way of invalid move. Reason: {'; '.join(reasons)}",
                for_logging=False
            )
            self.info["reason"] = f"Invalid Move: {'; '.join(reasons)}"
            self.done = True


class Env(ABC):
    """
    Abstract base class for text-based game environments.

    This class outlines the interface for the environment, including methods for resetting the environment,
    stepping through the environment (taking actions), and rendering the environment state.
    """

    # environment_name: str  # the name of the environment
    game_state: State  # the state of the environment

    @abstractmethod
    def reset(self, seed: Optional[int]=None):
        """
        Resets the environment to an initial state.

        Args:
            observations (Optional[Dict[int, str]]): Initial observations for the players.
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.

        Returns:
            Depending on implementation, should return initial observations and any additional info.
        """
        raise NotImplementedError

    @abstractmethod
    def step(self, action: str) -> Tuple[bool, Info]:
        """
        Performs a single step in the environment.

        Args:
            player_id (int): The ID of the player taking the action.
            action (str): The action to be taken by the player.

        Returns:
            Tuple containing:
                - done (bool): Whether the episode has concluded
                - info (Dict[str, Any]): Additional information about the environment.
        """
        raise NotImplementedError

    def get_observation(self):
        return self.state.current_player_id, self.state.observations[self.state.current_player_id]

    def close(self):
        rewards = self.state.close()
        return rewards


class Wrapper(Env):
    """ Base class for environment wrappers. """

    def __init__(self, env: Env):
        self.env = env
        self.state = env.state
        assert isinstance(env, Env)

    def __getattr__(self, name):
        return getattr(self.env, name)

    def reset(self, seed: Optional[int]=None):
        return self.env.reset(seed=seed)

    def step(self, action: str) -> Tuple[bool, Info]:
        return self.env.step(action=action)

    def get_observation(self):
        return self.env.get_observation()

    def close(self):
        return self.env.close()



class ObservationWrapper(Wrapper):

    def get_observation(self):
        player_id, observation = self.env.get_observation()
        return player_id, self.observation(player_id, observation)

    def observation(self):
        raise NotImplementedError


class RenderWrapper(Wrapper):
    def step(self, action: str) -> Tuple[bool, Optional[Info]]:
        return self.env.step(action=action)

class ActionWrapper(Wrapper):
    def step(self, action: str) -> Tuple[bool, Optional[Info]]:
        return self.env.step(action=self.action(action))

    def action(self, action: str) -> str:
        """
        Transforms the action.

        Args:
            action (str): The original action.

        Returns:
            str: The transformed action.
        """
        raise NotImplementedError


class Agent(ABC):
    """
    Generic agent class that defines the basic structure of an agent.
    """
    @abstractmethod
    def __call__(self, observation: str) -> str:
        """
        Process the observation and return the action.

        Args:
            observation (str): The input string to process.

        Returns:
            str: The response generated by the agent.
        """
        pass


class AgentWrapper(Agent):
    """ TODO """
    def __init__(self, agent: Agent):
        """ TODO """
        self.agent = agent 
        assert isinstance(agent, Agent)

    def __getattr__(self, name):
        """ TODO """
        return getattr(self.agent, name)

    def __call__(self, observation: str) -> str:
        return self.agent(observation=observation)





class GameMaker(ABC):
    """TODO"""

    @abstractmethod
    def __call__(self, text_input: str) -> str:
        """TODO"""
        raise NotImplementedError


class JudgeVote(ABC):
    """TODO"""

    @abstractmethod
    def __init__(self, optinos: List[str], num_judges: int):
        """TODO"""
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, transcript: str) -> Dict[str, int]:
        """TODO"""
        raise NotImplementedError


class GameMasterAction(ABC):
    """
    Interface for a game master that responds to player actions and maintains game continuity.
    """

    @abstractmethod
    def __init__(self, options: List[str]):
        """
        Initialize the game master with a specific answer and settings for interaction.

        Args:
            secret_answer (str): The target answer or solution the players are trying to guess.
            num_judges (int): Number of judges or agents to simulate for complex voting scenarios.
        """
        raise NotImplementedError

    @abstractmethod
    def respond_to_action(self, player_action: str) -> str:
        """
        Respond to the player's action (e.g., question in "20 Questions") based on the game's state.

        Args:
            player_action (str): The action or question posed by the player.

        Returns:
            str: The game master's response.
        """
        raise NotImplementedError
