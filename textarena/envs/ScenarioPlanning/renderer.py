import textwrap

def create_board_str(game_state: dict) -> str:
    scenario = game_state.get("scenario", "Unknown Scenario")
    strategies = game_state.get("strategies", {})
    votes = game_state.get("votes", {0: {"Votes": 0}, 1: {"Votes": 0}})

    # Wrap scenario to max 75 chars per line, max 3 lines
    wrapped_scenario = textwrap.wrap(scenario, width=75)[:3]
    while len(wrapped_scenario) < 3:
        wrapped_scenario.append("")

    lines = []
    lines.append("┌─ SCENARIO ────────────────────────────────────────────────────────────────┐")
    for line in wrapped_scenario:
        lines.append(f"│ {line.ljust(75)}│")
    lines.append("├────────────────────────────────────────────────────────────────────────────┤")

    for pid in [0, 1]:
        strategy = strategies.get(pid)
        if strategy is not None:
            wrapped_strategy = textwrap.wrap(strategy, width=73)
            lines.append(f"│ Player {pid} Strategy:".ljust(77) + "│")
            for line in wrapped_strategy:
                lines.append(f"│   {line.ljust(73)}│")
        else:
            lines.append(f"│ Player {pid} has not submitted a strategy yet.".ljust(77) + "│")
        lines.append("├────────────────────────────────────────────────────────────────────────────┤")

    lines.append("│ 🗳️  Judge Votes:")
    lines.append(f"│   Player 0: {votes[0]['Votes']} votes".ljust(75) + "│")
    lines.append(f"│   Player 1: {votes[1]['Votes']} votes".ljust(75) + "│")
    lines.append("└────────────────────────────────────────────────────────────────────────────┘")

    return "\n".join(lines)
