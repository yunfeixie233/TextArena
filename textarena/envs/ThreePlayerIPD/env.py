import itertools, re
from typing import Any, Dict, Optional, Tuple

import textarena as ta


class IteratedPrisonersDilemma3PDirectedEnv(ta.Env):
    """
    Three-player Iterated Prisoner’s Dilemma with pair-specific actions.

    • Decision syntax inside one turn:
          [1 defect] [2 cooperate]          # you defect vs P1, cooperate vs P2
      Order doesn’t matter; mix upper/lower case.

    • Edges you omit → treated as 'cooperate' automatically.

    Pay-off for each unordered pair {i, j} is the classic matrix T > R > P > S.
    """

    # ─────────────────────────────── initialisation ──────────────────────────────
    def __init__(
        self,
        num_rounds: int = 5,
        communication_turns: int = 3,
        cooperate_reward: int = 3,     # R
        defect_reward: int = 5,        # T
        sucker_reward: int = 0,        # S
        mutual_defect_reward: int = 1  # P
    ):
        self.num_rounds = num_rounds
        self.conversation_rounds = communication_turns

        # pay-off constants
        self.R, self.T, self.S, self.P = (
            cooperate_reward,
            defect_reward,
            sucker_reward,
            mutual_defect_reward,
        )

        # decision token  →  "[pid   cooperate/defect]"
        self.token_pat = re.compile(
            r"\[\s*(\d+)\s+(cooperate|defect)\s*\]", re.I
        )

    # ────────────────────────────────  reset  ───────────────────────────────────
    def reset(self, num_players: int = 3, seed: Optional[int] = None):
        assert num_players == 3, "Environment is hard-coded for exactly three players."
        self.state = ta.FFAMultiPlayerState(num_players=num_players, seed=seed)

        game_state = {
            # progress
            "round": 1,
            "num_rounds": self.num_rounds,
            "phase": "conversation",
            "conversation_round": 0,
            "total_conversation_rounds": self.conversation_rounds,
            # actions and scores
            "decisions": {
                p: {q: None for q in range(num_players) if q != p}
                for p in range(num_players)
            },
            "scores": {p: 0 for p in range(num_players)},
            # track whether each player has *submitted* in the decision phase
            "acted": {p: False for p in range(num_players)},
        }
        self.state.reset(game_state=game_state, player_prompt_function=self._prompt)

    # ──────────────────────────  player prompt helper  ──────────────────────────
    def _prompt(self, pid: int, gs: Dict[str, Any]) -> str:
        return (
            f"You are **Player {pid}** in a 3-player Iterated Prisoner’s Dilemma.\n"
            f"The match lasts **{gs['num_rounds']} rounds**.\n\n"
            f"Round structure:\n"
            f"• **{gs['total_conversation_rounds']} free-chat turns**\n"
            f"• **1 decision turn** – submit one token per opponent:\n"
            f"      [<opp-id> cooperate]   or   [<opp-id> defect]\n"
            f"  Example:  `[1 defect] [2 cooperate]`\n"
            f"  Missing tokens are treated as **cooperate**.\n\n"
            f"Pair-wise payoff matrix (applied to each unordered pair):\n"
            f"  – Both cooperate  →  {self.R}\n"
            f"  – Both defect     →  {self.P}\n"
            f"  – You defect, they cooperate → {self.T}\n"
            f"  – You cooperate, they defect → {self.S}"
        )

    # ─────────────────────────────────── step ───────────────────────────────────
    def step(self, action: str) -> Tuple[bool, ta.Info]:
        cid = self.state.current_player_id
        # log raw text
        self.state.add_observation(
            from_id=cid,
            to_id=cid,
            message=action,
            observation_type=ta.ObservationType.PLAYER_ACTION,
        )

        phase = self.state.game_state["phase"]
        if phase == "conversation":
            self._conversation_phase(action)
        else:  # decision
            self._decision_phase(action)

        return self.state.step()

    # ─────────────────────────  phase handlers  ────────────────────────────────
    def _conversation_phase(self, msg: str):
        cid = self.state.current_player_id
        # broadcast chat to others
        for pid in range(self.state.num_players):
            if pid != cid:
                self.state.add_observation(
                    from_id=cid,
                    to_id=pid,
                    message=msg.strip(),
                    observation_type=ta.ObservationType.PLAYER_ACTION,
                )

        # increment counter after the last speaker
        if cid == self.state.num_players - 1:
            gs = self.state.game_state
            gs["conversation_round"] += 1
            if gs["conversation_round"] >= gs["total_conversation_rounds"]:
                gs["phase"] = "decision"
                self.state.add_observation(
                    message=(
                        f"Chat finished for round {gs['round']}. "
                        "Submit your decisions, one token per opponent: "
                        "`[id cooperate]` or `[id defect]`."
                    ),
                    observation_type=ta.ObservationType.GAME_BOARD,
                )

    def _decision_phase(self, msg: str):
        cid = self.state.current_player_id
        gs = self.state.game_state
        # parse all valid tokens
        for pid_str, choice in self.token_pat.findall(msg):
            tgt = int(pid_str)
            if tgt == cid or tgt not in gs["decisions"][cid]:
                continue  # ignore bad ids / self-targets
            gs["decisions"][cid][tgt] = (
                "defect" if choice.lower().startswith("d") else "cooperate"
            )

        gs["acted"][cid] = True  # player has taken their decision turn

        # When every player has *acted* once, resolve round.
        if all(gs["acted"].values()):
            # fill unspecified edges with *cooperate*
            for p, row in gs["decisions"].items():
                for q in row:
                    if row[q] is None:
                        row[q] = "cooperate"
            self._resolve_round()

            # next round or finish
            gs["round"] += 1
            if gs["round"] > gs["num_rounds"]:
                self._end_game()
            else:
                # reset for next round
                gs.update(
                    {
                        "phase": "conversation",
                        "conversation_round": 0,
                        "decisions": {
                            p: {q: None for q in range(self.state.num_players) if q != p}
                            for p in range(self.state.num_players)
                        },
                        "acted": {p: False for p in range(self.state.num_players)},
                    }
                )
                self.state.add_observation(
                    message=f"─── Starting Round {gs['round']} ───",
                    observation_type=ta.ObservationType.GAME_MESSAGE,
                )

    # ─────────────────────────────  game logic  ────────────────────────────────
    def _pair_payoff(self, a: str, b: str) -> Tuple[int, int]:
        if a == b == "cooperate":
            return self.R, self.R
        if a == b == "defect":
            return self.P, self.P
        # one cooperates, one defects
        return (self.S, self.T) if a == "cooperate" else (self.T, self.S)

    def _resolve_round(self):
        gs = self.state.game_state
        decisions = gs["decisions"]
        round_gain = {p: 0 for p in decisions}

        # compute pair-wise rewards
        for i, j in itertools.combinations(range(self.state.num_players), 2):
            pi, pj = self._pair_payoff(decisions[i][j], decisions[j][i])
            round_gain[i] += pi
            round_gain[j] += pj

        # accumulate scores
        for p, inc in round_gain.items():
            gs["scores"][p] += inc

        # summary
        def edge_str(p, q):
            return f"P{p}→P{q}:{decisions[p][q][0].upper()}"
        edges = ", ".join(
            edge_str(p, q)
            for p in range(self.state.num_players)
            for q in range(self.state.num_players)
            if p < q
        )
        pay_str = ", ".join(
            f"P{p}:{'+' if g>=0 else ''}{g} (total {gs['scores'][p]})"
            for p, g in round_gain.items()
        )
        self.state.add_observation(
            message=(
                f"Round {gs['round']} results: {edges}\n"
                f"Rewards: {pay_str}"
            ),
            observation_type=ta.ObservationType.GAME_MESSAGE,
        )

    # ─────────────────────────────  game end  ──────────────────────────────────
    def _end_game(self):
        scores = self.state.game_state["scores"]
        top = max(scores.values())
        winners = [p for p, s in scores.items() if s == top]

        if len(winners) == 1:
            self.state.set_winner(
                winners[0], reason=f"Player {winners[0]} wins with {top} points!"
            )
        else:
            self.state.set_draw(
                reason=f"Draw! Players {', '.join(map(str, winners))} tie at {top} pts."
            )
