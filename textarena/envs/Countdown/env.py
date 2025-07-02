import operator, re, random
from typing import Dict, Tuple, List, Optional, Any

import textarena as ta


class CountdownEnv(ta.Env):
    _ACTION_RE = re.compile(r"\[\s*(\d+)\s+(\d+)\s*([+\-*/])\s*\]")
    _OPS = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.floordiv}

    def __init__(self, numbers: List[int] = None, target: int = None, max_turns: int = 12):
        super().__init__()
        big = [25, 50, 75, 100]
        small = list(range(1, 11)) * 2
        if numbers is None: numbers = random.sample(big, 2) + random.sample(small, 4)
        if target is None:  target = random.randint(100, 999)

        self.orig_numbers = numbers
        self.target = target
        self.max_turns = max_turns

        # Mutable per-episode
        self.numbers: List[int]
        self.exprs: List[str]
        self.best_val: int
        self.best_expr: str

    def reset(self, num_players: int, seed: Optional[int] = None):
        self.numbers = list(self.orig_numbers)
        self.exprs   = [str(n) for n in self.numbers]
        self.best_val = self._closest(self.numbers)
        self.best_expr = str(self.best_val)  # placeholder
        self.state = ta.SinglePlayerState(num_players=num_players, max_turns=self.max_turns, seed=seed)
        self.state.reset(game_state={}, player_prompt_function=self._prompt)
        self._observe()

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(self.state.current_player_id, action, ta.ObservationType.PLAYER_ACTION)
        m = self._ACTION_RE.fullmatch(action.strip())
        if not m: 
            self.state.set_invalid_move(self._progress(), "Bad action. Use `[i j op]`.")
            return self.state.step()

        i, j, op = int(m.group(1)), int(m.group(2)), m.group(3)
        if i == j or not (0 <= i < len(self.numbers)) or not (0 <= j < len(self.numbers)):
            self.state.set_invalid_move(self._progress(), "Indices out of range or identical.")
            return self.state.step()

        # Ensure deterministic order (i < j) so we can pop safely
        if i > j: i, j = j, i

        a, b = self.numbers[i], self.numbers[j]
        func = self._OPS[op]

        # Division guard
        if op == '/' and (b == 0 or a % b != 0):
            self.state.set_invalid_move(self._progress(), "Division not exact.")
            return self.state.step()

        # Compute result
        try:
            res = func(a, b)
        except Exception as e:
            self.state.set_invalid_move(self._progress(), f"Invalid op: {e}")
            return self.state.step()

        # Update lists
        expr_res = f"({self.exprs[i]} {op} {self.exprs[j]})"
        # Remove higher index first
        for idx in sorted([i, j], reverse=True):
            self.numbers.pop(idx)
            self.exprs.pop(idx)
        self.numbers.append(res)
        self.exprs.append(expr_res)

        # Track best
        if abs(res - self.target) < abs(self.best_val - self.target):
            self.best_val = res
            self.best_expr = expr_res

        self._observe()

        # Win / end?
        if res == self.target:
            self.state.set_outcome(1.0, "Exact match! Puzzle solved.")
        elif len(self.numbers) == 1 or self.state.turn_number >= self.max_turns:
            self.state.set_outcome(self._progress(), f"Finished. Best = {self.best_val}")
        return self.state.step()


    def _prompt(self, player_id, game_state) -> str:    return "You are playing a game of Countdown. Combine two numbers with + - * / to reach the target.\nAction: `[i j op]` e.g. `[0 2 *]`."
    def _closest(self, vals: List[int]) -> int:         return min(vals, key=lambda v: abs(v - self.target))
    def _progress(self) -> float:                       return max(0.0, 1.0 - abs(self.best_val - self.target) / 1000) # 1.0 exact, linear drop with distance (scaled for 0-999 range)
    def _observe(self):                                 self.state.add_observation(message=self._render_board()+f"\nReward if stop now: {self._progress():.2f}", observation_type=ta.ObservationType.GAME_BOARD)
    def _render_board(self) -> str:
        nums_line = "Numbers: " + '  '.join(f"{idx}:{n}" for idx, n in enumerate(self.numbers))
        exprs_line = "Exprs:   " + '  '.join(f"{idx}:{e}" for idx, e in enumerate(self.exprs))
        return f"Target: {self.target}\n{nums_line}\n{exprs_line}\nBest so far: {self.best_val}  ({self.best_expr})"
