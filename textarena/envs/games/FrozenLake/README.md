# Frozen Lake Environment Documentation

## Overview

**Frozen Lake** is a deterministic, single‑player grid‑navigation puzzle. The agent starts at the **top‑left** corner of an $N\times N$ lake and must reach the **Goal** tile (`G`) at the **bottom‑right**, avoiding hidden **Holes** (`H`). All other tiles are solid ice (shown as a blank space). There is **no slipping**—each action moves exactly one cell if the move is valid.

The environment is implemented in **`env.py`** (see source) and is suitable for reinforcement‑learning agents, planning algorithms, or interactive play via the TextArena framework.

---

## Symbols

| Symbol    | Meaning                               |
| --------- | ------------------------------------- |
| `P`       | Player’s current position             |
| `G`       | Goal — reach this to win              |
| `H`       | Hole — stepping here ends the episode |
| *(blank)* | Safe frozen ice                       |

Example 4 × 4 board after two moves:

```text
+-----+-----+-----+-----+
|     |     |     |  H  |
+-----+-----+-----+-----+
|  P  |  H  |     |     |
+-----+-----+-----+-----+
|     |     |     |     |
+-----+-----+-----+-----+
|     |     |     |  G  |
+-----+-----+-----+-----+
```

---

## Action Space

Commands are **case‑insensitive** and must contain a bracketed direction token. The first well‑formed token is parsed.

| Primary   | Alias | Example Input         |
| --------- | ----- | --------------------- |
| `[up]`    | `[w]` | `I go [up] now`       |
| `[down]`  | `[s]` | `[down]`              |
| `[left]`  | `[a]` | `step [a]`            |
| `[right]` | `[d]` | `move [right] please` |

Invalid formatting or moving into a wall terminates the episode (details below).

---

## Episode Flow

1. **Reset**   A new grid is generated with exactly `num_holes` holes (default `3`). The generator retries until at least one path from start to goal exists.
2. **Turn**    The agent submits a direction. The environment:

   * validates the string,
   * updates the player position if the move stays within bounds,
   * checks the landing tile (`H`, `G`, or safe ice),
   * emits an updated board render and status message.
3. **Termination**   An episode ends when **any** of the following occur:

   * Player steps on `G` → **success**.
   * Player steps on `H` → **failure**.
   * Move is invalid (bad format *or* hits the outer wall).
   * 100 turns elapse (configurable via `max_turns`).

---

## Reward Scheme

| Event                              | Reward (`float`)        | Notes                                 |
| ---------------------------------- | ----------------------- | ------------------------------------- |
| Reach `G` (win)                    | **1.0**                 | Episode ends.                         |
| Failure (hole, invalid move, time) | $p$ (0.10 ≤ *p* ≤ 0.95) | *Progress‑based shaping* — see below. |

### Progress‑based shaping

When an episode ends prematurely the environment awards a fractional reward proportional to how far the agent advanced toward the goal:

$$
p = \frac{\text{shortest‑path}(\text{start}, \text{current})}{\text{shortest‑path}(\text{start}, \text{goal})}\,.
$$

Distances are computed **ignoring holes** to reflect theoretical best progress. The value is clipped to $[0.10, 0.95]$ to ensure at least a small positive signal for exploration and to keep failures sub‑optimal relative to success.

---

## Parameters

| Argument    | Default | Description                                                                             |
| ----------- | ------- | --------------------------------------------------------------------------------------- |
| `size`      | `4`     | Board side length (≥ 2).                                                                |
| `num_holes` | `3`     | Exact number of holes. Must allow a path; the generator reduces the count if necessary. |
| `max_turns` | `100`   | Automatic episode timeout.                                                              |

Create a custom environment:

```python
import textarena as ta
env = ta.make(
    env_id="FrozenLake-v0",
    size=6,
    num_holes=8,  # more obstacles
)
obs = env.reset()
```

---

## Observation Format

### Reset Observation

```
Welcome to Frozen Lake!

You are represented by 'P' on the grid.
Grid symbols:
  ' ' = Frozen surface (safe to walk on)
  'H' = Hole (fall in and lose!)
  'G' = Goal (reach this to win!)
  'P' = Your current position

Available actions: up, down, left, right (or w, a, s, d)
Type your action as: [up], [down], [left], [right] or [w], [a], [s], [d]

Objective: Navigate from the start (top-left) to the goal (bottom-right) without falling into any holes!

Current Board:
<ASCII grid>
```

### Step Observation

After each action the agent receives:

* Updated ASCII board with the new `P` location.
* Natural‑language message summarising the move (e.g. *“You moved left to (1, 0).”*).
* Prompt listing the legal action tokens.

---

## Tips for Training Agents

* **Reward shaping** allows dense feedback—useful for curriculum learning.
* Because boards are regenerated every reset, consider setting a random seed for reproducibility during testing.
* Larger boards and higher hole counts dramatically increase planning depth—start with small grids.

---

## Contact

Questions or bug reports? Email **[chengxy@i2r.a-star.edu.sg](mailto:chengxy@i2r.a-star.edu.sg)**.

