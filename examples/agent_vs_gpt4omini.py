"""
debugging
"""
import os, openai 

from textarena.llm_wrappers.gpt_agent_wrapper import GPTAgent
from textarena.game_wrappers.two_player_base_wrapper import TwoPlayerBaseWrapper
from textarena.games import build_games


test_game_list = [
    {
        "game_name":"dont_say_it",
        "num_rounds": 4,
        "verbose": True,
        "game_kwargs": {
            "max_turns":10,
            "render":True
        }
    }
]

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    # set agents
    agent_1 = GPTAgent(
        unique_identifier=0,
        api_key=api_key,
        max_tokens=1_000,
        model_name="gpt-4o-mini"
    )
    agent_2 = GPTAgent(
        unique_identifier=0,
        api_key=api_key,
        max_tokens=1_000,
        model_name="gpt-4o-mini"
    )

    # init game
    for game_dict in test_game_list:
        # load the game
        wrapped_game = TwoPlayerBaseWrapper(
            game_name=game_dict["game_name"],
            num_rounds=game_dict["num_rounds"],
            verbose=game_dict["verbose"],
            agent_1=agent_1,
            agent_2=agent_2,
            game_kwargs=game_dict["game_kwargs"]
        )


        # play the game 
        agent_logs = wrapped_game.play_game()

        # extract the scores and reasons
        agent_1_score = agent_logs[agent_1.unique_identifier]["scores"]
        agent_2_score = agent_logs[agent_2.unique_identifier]["scores"]

        # print
        print(f"Scores; Agent_1: {agent_1_score}, Agent_2: {agent_2_score}")
        print(f"Reasons: {agent_logs['reasons']}")
        print(f"Num turns: {agent_logs['num_turns']}")

