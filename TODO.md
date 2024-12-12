
# WIP: TODO

TODOs:
- game completion message should be more clear
<!-- - show player to name translation in render -->
<!-- - create tkinter render wrapper -->
<!-- - create video recording wrapper (or make it part of tkinter render wrapper) -->
- update requirements
- add a truncating action wrapper for the leaderboard
- make sure ppl can't join the queue w/o a valid model token [can join if token=None (why? lol)]
- offer two different time-based timeout options (i.e. fast and slow)
<!-- - on step, check for terminated, truncated and tell user to reset first before stepping again.  -->
<!-- - save model_token in local .env [test] -->

<!-- - for online playing change env.print_results() to env.close -->
- add api call for removing model from matchmaking (and add it as a finally when the client closes the object)


<!-- - make sure ppl can't play against their own agents [maybe go by email address] -->
- api call to pretty print the leaderboard and current pos
- offline env.print_results()

- maybe create an online pretty render that puts the elos etc. on top (maybe even the matchmaking queue)
<!-- - debug pytests  -->

- poker, player went to negative balance
- poker, game didn't end when no chips were left

- register sets of games (both for online and offline)

KIV
- might be worth having a mode where the players only see the game-state (to prevent the other play from just focusing on confusing this player)
- colorcode [ERROR] in game-log rendering (PrettyRenderWrapper)
- display a table of all active games in the main text-arena

- add logging wrapper to store as file


Current TODO:
- add to .make the subsets of games (i.e. randomly initializing any of the games from the subset when .make is used)
- create list of subset games and the status of implementation
- create list of all current games and the status of implementation
- update online play code (both client and server side)
- online humanity
- update online website
- update render wrapper for subset games
- create render wrapper for online playing
- update requirements
- on .close, return result information for local, and full result information for online
- add api call for removing model from matchmaking (and add it as a finally when the client closes the object)



Future work:
- mention the intend to publish full multi-player version of this