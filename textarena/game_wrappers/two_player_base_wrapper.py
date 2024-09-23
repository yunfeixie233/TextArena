from tqdm import tqdm 
from textarena.games import build_games


class TwoPlayerBaseWrapper:
    def __init__(
        self, 
        game_name,
        agent_1,
        agent_2,
        num_rounds=1,
        verbose=True,
        game_kwargs={}
    ):
        """
        TODO
        """

        # build the game
        self.game = build_games(
            game_name=game_name,
            game_kwargs=game_kwargs
        )
        self.num_rounds = num_rounds

        # set agents
        self.agent_1 = agent_1 
        self.agent_2 = agent_2 


    def play_game(self):
        """
        TODO
        """

        # Initialize agent logs per agent_id
        logging_dict = {
            "num_turns": [],
            "reasons": [],
            self.agent_1.unique_identifier: {
                "logs": [],
                "score": 0
            },
            self.agent_2.unique_identifier: {
                "logs": [],
                "scores": 0
            }
        }


        # Wrap the outer loop with tqdm for progress tracking if verbose TODO
        for round_num in tqdm(range(self.num_rounds), desc=f"Player {self.game.name}", unit="rounds"):
            # reset the game 
            (
                game_prompt_player_1, 
                game_prompt_player_2,
                observation,
            ) = self.game.reset()

            # reset the agents and provide game prompt
            self.agent_1.reset(
                game_prompt=game_prompt_player_1
            )
            self.agent_2.reset(
                game_prompt=game_prompt_player_2
            )

            # reset standard game parameters and local logging
            done = False
            episode_logs = {
                agent_id: [] for agent_id in (
                    self.agent_1.unique_identifier, 
                    self.agent_2.unique_identifier
                )
            }

            # start the main game loop
            while not done:
                # agents take turns
                for player_id, agent in enumerate((self.agent_1, self.agent_2)):
                    # get valid action subset
                    valid_actions = self.game.get_valid_actions(player_id=player_id)

                    # get action from the agent
                    action, agent_state = agent.get_action(
                        observation=observation,
                        valid_actions=valid_actions,
                    )

                    # execute the action in the game
                    new_observation, reward, done, info = self.game.step(
                        player_id=player_id,
                        action=action
                    )

                    # log it to the agents
                    episode_logs[agent.unique_identifier].append({
                        "observation": observation,
                        "agent_state": agent_state,
                        "action": action,
                        "info": info
                    }) # since only end-of-game rewards are provided,
                    # we add them at the end of the game

                    # check if done
                    if done:
                        break 
                    
                    # update observation
                    observation = new_observation

            
            # Game finished, add reward to all agent logs and set agent scores
            for player_id, agent in enumerate((self.agent_1, self.agent_2)):
                agent_id = agent.unique_identifier

                # update the episode logs with the final reward
                for i in range(len(episode_logs[agent_id])):
                    episode_logs[agent_id][i]["reward"] = reward[player_id]

                # extend agent logs with episode logs
                logging_dict[agent_id]["logs"].extend(episode_logs[agent_id])

                # add agent scores
                logging_dict[agent_id]["scores"] += reward[player_id]

            # note the number of turns and completion reason
            logging_dict["num_turns"].append(self.game.get_info().get("num_turns", None))
            logging_dict["reasons"].append(info.get("reason", "Not Specified"))

        
        return logging_dict
