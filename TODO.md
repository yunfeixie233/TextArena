
# WIP: TODO

TODOs:
- game completion message should be more clear
- show player to name translation in render
- create tkinter render wrapper
- create video recording wrapper (or make it part of tkinter render wrapper)
- update requirements
- add a truncating action wrapper for the leaderboard
- make sure ppl can't join the queue w/o a valid model token [can join if token=None (why? lol)]
- offer two different time-based timeout options (i.e. fast and slow)



- make sure ppl can't play against their own agents [maybe go by email address]
- api call to pretty print the leaderboard and current pos
- offline env.print_results()

- maybe create an online pretty render that puts the elos etc. on top (maybe even the matchmaking queue)
- debug pytests 

KIV
- might be worth having a mode where the players only see the game-state (to prevent the other play from just focusing on confusing this player)
- colorcode [ERROR] in game-log rendering (PrettyRenderWrapper)
- display a table of all active games in the main text-arena

- add logging wrapper to store as file