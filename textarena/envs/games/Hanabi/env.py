# hanabi_env.py
import random, re
from typing import Any, Dict, List, Optional, Tuple

import textarena as ta


_COLORS = ["R", "Y", "G", "B", "W"] # basic 5-colour game
_DISTR = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1} # copies per rank
_PLAY_RE = re.compile(r"\[play (\d)]", re.I) # “[Play 2]”
_DISCARD_RE = re.compile(r"\[discard (\d)]", re.I) # “[Discard 0]”
_CLUE_NUM_RE = re.compile(r"\[clue (\d) num ([1-5])]", re.I) # “[Clue 1 Num 3]”
_CLUE_COL_RE = re.compile(r"\[clue (\d) col ([A-Za-z])]",re.I) # “[Clue 2 Col R]”

def _make_deck() -> List[Tuple[str,int]]:
    """Return a shuffled full deck of (color, rank) tuples."""
    deck = [(c, r) for c in _COLORS for r, n in _DISTR.items() for _ in range(n)]
    random.shuffle(deck)
    return deck

def _card_str(card: Tuple[str,int]) -> str: return f"{card[0]}{card[1]}"

def _board_ascii(fireworks: Dict[str,int], clues:int, fuses:int, discards:Dict[str,int]) -> str:
    lines = [
        "=== Hanabi ===",
        "Fireworks: " + " ".join(f"{c}{fireworks[c]}" for c in _COLORS),
        f"Clue tokens: {clues}  |  Fuse tokens: {fuses}",
        "Discards:  " + " ".join(f"{c}{r}×{n}" for (c,r),n in discards.items()),
        "================"
    ]
    return "\n".join(lines)

# ────────────────────────────────────────────────────────────────────────────
class HanabiEnv(ta.Env):
    def __init__(self, max_clues:int=8, max_fuses:int = 3):
        self.max_clues = max_clues
        self.max_fuses = max_fuses

    def get_board_str(self) -> str:
        return _board_ascii(self.state.game_state["fireworks"], self.state.game_state["clues"], self.state.game_state["fuses"], self.state.game_state["discards"])

    def reset(self, num_players: int, seed: Optional[int]=None):
        assert 2 <= num_players <= 5, "Hanabi supports 2-5 players"
        self.state = ta.FFAMultiPlayerState(num_players=num_players, seed=seed)
        random.seed(seed)

        deck  = _make_deck()
        hsize = 5 if num_players <= 3 else 4
        hands = {pid:[deck.pop() for _ in range(hsize)] for pid in range(num_players)}

        gs = dict(
            deck = deck,
            hands = hands,
            fireworks = {c:0 for c in _COLORS},              # top number per colour
            discards = {},                                   # (c,r)->count
            clues = self.max_clues,
            fuses = self.max_fuses,
            final_turns_left = None,                         # set to n_players after deck empties
            current_player = 0
        )
        self.state.reset(game_state=gs, player_prompt_function=self._prompt)

        self._broadcast_board()

    # --------------------------------------------------------------------- prompts & observations
    def _prompt(self, pid:int, gs:Dict[str,Any]) -> str:
        others = ", ".join(
            f"P{op}:{' '.join(_card_str(c) for c in gs['hands'][op])}"
            for op in range(self.state.num_players) if op!=pid
        )
        hand_sz = len(gs["hands"][pid])
        acts = (
            "• [Play i]     – play the i-th card (0-based)\n"
            "• [Discard i]  – discard the i-th card\n"
            "• [Clue j Num n] – tell player j all rank-n cards (cost 1 clue)\n"
            "• [Clue j Col C] – tell player j all colour-C cards (cost 1 clue)"
        )
        return (
            f"You are Player {pid}. You DO NOT see your own {hand_sz} cards.\n"
            f"Other hands: {others}\n\n"
            f"{self.get_board_str()}\n\nActions:\n{acts}"
        )

    def _broadcast_board(self):
        self.state.add_observation(
            from_id=ta.GAME_ID, to_id=-1,
            message=self.get_board_str(),
            observation_type=ta.ObservationType.GAME_BOARD
        )

    # --------------------------------------------------------------------- step
    def step(self, action:str) -> Tuple[bool, ta.Info]:
        gs   = self.state.game_state
        pid  = gs["current_player"]

        # ------------------------------------------------ parse
        if (m:=_PLAY_RE.fullmatch(action)):        ok = self._play(pid,int(m.group(1)))
        elif (m:=_DISCARD_RE.fullmatch(action)):   ok = self._discard(pid,int(m.group(1)))
        elif (m:=_CLUE_NUM_RE.fullmatch(action)):  ok = self._clue(pid,int(m.group(1)),num=int(m.group(2)))
        elif (m:=_CLUE_COL_RE.fullmatch(action)):  ok = self._clue(pid,int(m.group(1)),col=m.group(2).upper())
        else:
            self.state.set_invalid_move("Unrecognised action.")
            return self.state.step(rotate_player=False)

        if not ok:  # invalid inside helper
            return self.state.step(rotate_player=False)

        # ------------------------------------------------ turn rotation
        self._maybe_end_game_or_continue()

        return self.state.step(rotate_player=False)

    # --------------------------------------------------------------------- helpers (play/discard/clue)
    def _play(self, pid:int, idx:int)->bool:
        gs = self.state.game_state
        hand = gs["hands"][pid]
        if not (0<=idx<len(hand)):
            self.state.set_invalid_move("Index out of range.")
            return False
        card = hand.pop(idx)

        colour, rank = card
        if gs["fireworks"][colour] == rank-1:           # successful play
            gs["fireworks"][colour] = rank
            self.state.add_observation(message=f"P{pid} successfully played {colour}{rank}.", observation_type=ta.ObservationType.GAME_MESSAGE)
            if rank==5 and gs["clues"]<self.max_clues: gs["clues"] += 1    # bonus clue
        else:                                           # mis-play
            gs["fuses"] -= 1
            gs["discards"][(colour,rank)] = gs["discards"].get((colour,rank),0)+1
            self.state.add_observation(message=f"💥 P{pid} mis-played {colour}{rank}! Fuse lost.", observation_type=ta.ObservationType.GAME_MESSAGE)

        self._draw_if_possible(pid)
        return True

    def _discard(self, pid:int, idx:int)->bool:
        gs = self.state.game_state
        if gs["clues"]==self.max_clues:
            self.state.set_invalid_move("Clue pile already full; cannot discard.")
            return False
        hand = gs["hands"][pid]
        if not (0<=idx<len(hand)):
            self.state.set_invalid_move("Index out of range.")
            return False
        card = hand.pop(idx)
        gs["discards"][(card[0],card[1])] = gs["discards"].get((card[0],card[1]),0)+1
        gs["clues"] += 1
        self.state.add_observation(message=f"P{pid} discards {_card_str(card)} (+1 clue).", observation_type=ta.ObservationType.GAME_MESSAGE)
        self._draw_if_possible(pid)
        return True

    def _clue(self, pid:int, target:int, num:int|None=None, col:str|None=None)->bool:
        gs = self.state.game_state
        if pid==target or target<0 or target>=self.state.num_players:
            self.state.set_invalid_move("Illegal clue target.")
            return False
        if gs["clues"]==0:
            self.state.set_invalid_move("No clue tokens left.")
            return False
        if (num is None) == (col is None):
            self.state.set_invalid_move("Specify exactly one of number or colour.")
            return False
        hand = gs["hands"][target]
        matches = [i for i,c in enumerate(hand) if (num is not None and c[1]==num) or (col is not None and c[0]==col)]
        if not matches:
            self.state.set_invalid_move("Clue gives no information.")
            return False

        gs["clues"] -= 1
        tag = f"number {num}" if num else f"colour {col}"
        self.state.add_observation(
            message=f"P{pid} clues P{target} about {tag}: matching positions {matches}.",
            observation_type=ta.ObservationType.GAME_MESSAGE
        )
        return True

    def _draw_if_possible(self, pid:int):
        gs = self.state.game_state
        if gs["deck"]:
            gs["hands"][pid].append(gs["deck"].pop())
        elif gs["final_turns_left"] is None:          # deck emptied just now
            gs["final_turns_left"] = self.state.num_players

    # --------------------------------------------------------------------- progression / ending
    def _maybe_end_game_or_continue(self):
        gs = self.state.game_state

        # loss by fuses
        if gs["fuses"]<=0:
            self._finish_game(reason="All fuses blown – fireworks ruined!")
            return

        # perfect completion
        if all(v==5 for v in gs["fireworks"].values()):
            self._finish_game(reason="All stacks completed – perfect show!")
            return

        # handle final-turn countdown
        if gs["final_turns_left"] is not None:
            gs["final_turns_left"] -= 1
            if gs["final_turns_left"]==0:
                self._finish_game(reason="Deck empty; final round over.")
                return

        # else simply pass turn
        gs["current_player"] = (gs["current_player"]+1) % self.state.num_players
        self.state.manually_set_current_player_id(gs["current_player"])
        self._broadcast_board()

    def _finish_game(self, reason:str):
        score = sum(self.state.game_state["fireworks"].values())  # 0-25
        rew   = -1.0 + (score/25.0)*2.0
        rewards = {pid:rew for pid in range(self.state.num_players)}
        self.state.set_game_outcome(reward_dict=rewards, reason=f"{reason}  Final score: {score}/25")
        self.state.game_state["fuses"] = 0
        self._broadcast_board()
