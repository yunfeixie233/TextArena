from abc import ABC, abstractmethod
from typing import Any, Dict

from tqdm import tqdm
from textarena.games import build_games

from textarena.game_wrappers.interface import TwoPlayerGameInterface


class TwoPlayerBaseWrapper(TwoPlayerGameInterface):
    def __init__(
        self, 
        game_name: str,
        agent_1: Any,
        agent_2: Any,
        num_rounds: int = 1,
        verbose: bool = True,
        game_kwargs: Dict[str, Any] = {}
    ):
        """
        Initialize the TwoPlayerBaseWrapper with the specified game and agents.

        Args:
            game_name (str): The name of the game to be played.
            agent_1 (Any): The first agent participating in the game.
            agent_2 (Any): The second agent participating in the game.
            num_rounds (int, optional): The number of game rounds to play. Defaults to 1.
            verbose (bool, optional): Flag to enable or disable progress tracking. Defaults to True.
            game_kwargs (Dict[str, Any], optional): Additional keyword arguments for game initialization.
        """
        # Build the game instance using the provided game name and arguments
        self.game = build_games(
            game_name=game_name,
            game_kwargs=game_kwargs
        )
        self.num_rounds = num_rounds
        self.verbose = verbose

        # Assign the agents to the wrapper
        self.agent_1 = agent_1 
        self.agent_2 = agent_2 


    def play_game(self) -> Dict[str, Any]:
        """
        Play the specified number of game rounds between the two agents.

        Returns:
            Dict[str, Any]: A dictionary containing logs and scores for each agent,
                            as well as overall game statistics like the number of turns and reasons for completion.
        """
        # Initialize logging structure to capture game data
        logging_dict = {
            "num_turns": [],  # Number of turns taken in each round
            "reasons": [],    # Reasons for game completion in each round
            self.agent_1.unique_identifier: {
                "logs": [],   # Detailed logs for agent 1
                "scores": 0   # Cumulative score for agent 1
            },
            self.agent_2.unique_identifier: {
                "logs": [],   # Detailed logs for agent 2
                "scores": 0   # Cumulative score for agent 2
            }
        }

        # Determine whether to use tqdm for progress tracking based on verbosity
        round_iterator = tqdm(
            range(self.num_rounds), 
            desc=f"Player {self.game.name}", 
            unit="rounds"
        ) if self.verbose else range(self.num_rounds)

        # Iterate over each round
        for round_num in round_iterator:
            # Reset the game to its initial state and obtain initial prompts and observation
            (
                game_prompt_player_1, 
                game_prompt_player_2,
                observation,
            ) = self.game.reset()

            # Reset both agents with their respective initial game prompts
            self.agent_1.reset(game_prompt=game_prompt_player_1)
            self.agent_2.reset(game_prompt=game_prompt_player_2)

            # Initialize game state flags and local logs for the current episode
            done = False
            episode_logs = {
                agent_id: [] for agent_id in (
                    self.agent_1.unique_identifier, 
                    self.agent_2.unique_identifier
                )
            }

            # Main game loop that continues until the game signals completion
            while not done:
                # Iterate over each player in turn (Player 1 and Player 2)
                for player_id, agent in enumerate((self.agent_1, self.agent_2)):
                    # Retrieve the set of valid actions for the current player
                    valid_actions = self.game.get_valid_actions(player_id=player_id)

                    # Request an action from the agent based on the current observation and valid actions
                    action, agent_state = agent.get_action(
                        observation=observation,
                        valid_actions=valid_actions,
                    )

                    # Execute the chosen action within the game and obtain the new state
                    new_observation, reward, done, info = self.game.step(
                        player_id=player_id,
                        action=action
                    )

                    # Log the action and associated details for later analysis
                    episode_logs[agent.unique_identifier].append({
                        "observation": observation,
                        "agent_state": agent_state,
                        "action": action,
                        "info": info
                    })

                    # If the game has ended after this action, exit the loop
                    if done:
                        break 
                    
                    # Update the observation for the next turn based on the game's new state
                    observation = new_observation

            # After the game concludes, process and store the results
            for player_id, agent in enumerate((self.agent_1, self.agent_2)):
                agent_id = agent.unique_identifier

                # Append the final reward to each action log for the agent
                for log_entry in episode_logs[agent_id]:
                    log_entry["reward"] = reward[player_id]

                # Consolidate the episode logs into the overall logging dictionary
                logging_dict[agent_id]["logs"].extend(episode_logs[agent_id])

                # Accumulate the agent's score based on the reward received
                logging_dict[agent_id]["scores"] += reward[player_id]

            # Record the number of turns and the reason for game completion
            logging_dict["num_turns"].append(self.game.get_info().get("num_turns", None))
            logging_dict["reasons"].append(info.get("reason", "Not Specified"))

        return logging_dict
