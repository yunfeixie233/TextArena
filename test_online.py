import textarena as ta 
import time 


model_name = f"Model_{time.time()}"
model_description = "A test model"
email = "Guertlerlo@cfar.a-star.edu.sg"


# first, register the model
model_token = ta.register_online_model(
    model_name=model_name,
    model_description=model_description,
    email=email
)


print(model_token)
# # initialize the actual model
agent = ta.basic_agents.GPTAgent(
    model_name="gpt-4o-mini"
)


# make the environment
env, player_id = ta.make_online(
    env_id="DontSayIt-v0",
    model_name=model_name,
    model_token=model_token
)

observations = env.reset()


done = False 
while not done:
    action = agent(observations[player_id])

    observations, _, truncated, terminated, _ = env.step(
        player_id=player_id,
        action=action
    )

    done = truncated or terminated

    

# env.print_results()
# TODO reason for invalid move (disconnection, too slow, etc. etc.)


# General
# give an easy option to give feedback for hackathons etc. etc. (esp. for TextArena)


# easy example script

# is it possible to schedule notebooks // at the very least provide a sample script for freely hosted notebook [collab/kaggle]



# double-check if cold weight is possible 


# encourage people to add themselves to this (i.e. as agents)



# make sure ppl can enter the queue multiple times but 
# don't match against themselves 


# allow ppl to add their model as a permanent opponents (base set)

# maybe limit it to a single day a week [timer that says this is the next tiem for matchmaking]
# sleep until competition time


"""
In the background:
    - register player for matchmaking
    - keep checking until opponent found (with appropriate printing)
    - once found, return the reset observation to the online env wrapper
    - return env object and player id to user
    - on reset, just get the observation

"""

# leaderboard time cut-off


# report average time to reply


# default to run at least three rounds of games in a single match