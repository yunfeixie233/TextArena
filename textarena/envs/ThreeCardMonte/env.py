import random, re
from typing import Dict, Tuple, Optional, Any, List

import textarena as ta


class ThreeCardMonteEnv(ta.Env):
    """
    Watch the cups shuffle, then guess which cup hides the ball.

    • `num_cups`  : how many cups (≥3)
    • `steps`     : how many random swaps before you guess
    • Action      : `[k]`  — choose cup index k (0-based)
    • Reward      : 1.0 if correct, 0.0 otherwise
    """

    _ACTION_RE = re.compile(r"\[\s*(\d+)\s*\]")

    def __init__(self, num_cups: int = 3, steps: int = 10):
        super().__init__()
        assert num_cups >= 3, "Need at least three cups."
        self.num_cups = num_cups
        self.steps = steps

        # Episode-mutable
        self.ball_pos: int
        self.awaiting_guess: bool

    # ───────────────────────────── TextArena hooks ─────────────────────────────

    def reset(self, num_players: int, seed: Optional[int] = None):
        rng = random.Random(seed)

        # Ball starts under a random cup
        self.ball_pos = rng.randrange(self.num_cups)

        self.state = ta.SinglePlayerState(num_players=num_players, seed=seed)
        self.state.reset(game_state={}, player_prompt_function=self._prompt)

        # Announce starting position
        start_line = " ".join("[O]" if idx == self.ball_pos else f"[{idx}]" for idx in range(self.num_cups))
        self.state.add_observation(f"Ball starts: {start_line}", observation_type=ta.ObservationType.GAME_MESSAGE)

        # Run the shuffle sequence up-front
        for step in range(1, self.steps + 1):
            i, j = rng.sample(range(self.num_cups), 2)  # distinct cups
            if self.ball_pos == i:      self.ball_pos = j
            elif self.ball_pos == j:    self.ball_pos = i
            self.state.add_observation(f"Shuffle {step}/{self.steps}: swapped cups {i} and {j}.", observation_type=ta.ObservationType.GAME_MESSAGE)

        # Show final cup indices and ask for guess
        self.awaiting_guess = True
        self._show_cups(prompt="(Guess NOW!)")

    def step(self, action: str):

        if not self.awaiting_guess:
            # Should never happen in this design
            self.state.set_invalid_move(0.0, "No action expected.")
            return self.state.step()

        m = self._ACTION_RE.fullmatch(action.strip())
        if not m:
            self.state.set_invalid_move(0.0, "Bad action. Use `[k]`.")
            return self.state.step()

        guess = int(m.group(1))
        if not (0 <= guess < self.num_cups):
            self.state.set_invalid_move(0.0, f"Index out of range 0–{self.num_cups-1}.")
            return self.state.step()

        reward = 1.0 if guess == self.ball_pos else 0.0
        msg = ("Correct! You found the ball."
               if reward else f"Wrong — ball was under cup {self.ball_pos}.")
        self.state.set_outcome(reward, msg)

        # Final board reveal
        self._show_cups(prompt=f"(Reveal: ball under {self.ball_pos})")

        return self.state.step()

    # ───────────────────────────── Helpers ─────────────────────────────

    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return ("Track the hidden ball while the cups are shuffled.\n"
                "After shuffling, guess its location with `[k]`.\n")

    def _show_cups(self, prompt: str):
        cup_line = " ".join(f"[{idx}]" for idx in range(self.num_cups))
        self.state.add_observation(
            ta.GAME_ID, -1, f"Cups: {cup_line}  {prompt}",
            ta.ObservationType.GAME_MESSAGE
        )
