# Colonel Blotto Environment Documentation

## Overview
**Colonel Blotto** is a strategic two-player zero-sum game that presents a conflict between two players (officers) who are tasks to simultaneously allocate limited units across multiple battlefields[1]. In each round, players have to allocate all of their units across all fields. The outcome of each battlefield skirmish is based on who has the most units on that battlefield gaining a point for each such majority, and the outcome of the round is set according to who has won the most battlefields.

The game does not allow communications between the agents before each allocation, and only allows the player to learn and improve it's understanding of its opponent based on  previous rounds. 

## Gameplay
1.  **Allocation Phase:** At the start of each round, you will be prompted to allocate your total number of units across all available fields.
2.  **Reveal & Battle:** Once both players have submitted their allocations, the results are revealed. For each field, the player who assigned more units wins that field. If both players assign the same number of units, it is a tie for that field.
3.  **Round Winner:** The player who won more individual fields is declared the winner of the round. If both players win an equal number of fields, the round is a draw.
4.  **Game End:** The game continues for a fixed number of rounds. The player who has won the most rounds at the end is the overall winner of the game.

## How to Play
When prompted, enter your allocation as a comma-separated list of `FIELD:UNITS` pairs.

**Example Action:**
If there are three fields (A, B, C) and you have 20 units, a valid move would be:
`A:10, B:5, C:5`

**Important Rules:**
- The sum of the units you allocate must equal the total number of units you are given for the round.
- You must provide an allocation for every field.
- You cannot allocate a negative, or non-integer number of units.

## References
[1] Borel, Emile. “The Theory of Play and Integral Equations with Skew Symmetric Kernels.” Econometrica, vol. 21, no. 1, 1953, pp. 97–100. JSTOR, https://doi.org/10.2307/1906946.