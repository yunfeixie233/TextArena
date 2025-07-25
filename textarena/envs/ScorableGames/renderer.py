from typing import Dict, List, Any

def render_current_deal(deal_state: Dict[str, str], issues: Dict[str, Dict]) -> str:
    """Render the current deal proposal in a readable format."""
    if not deal_state:
        return "No current deal proposal."
    
    lines = ["Current Deal Proposal:"]
    lines.append("=" * 25)
    
    for issue_key, option in deal_state.items():
        if issue_key in issues:
            issue_info = issues[issue_key]
            issue_name = issue_info.get('name', issue_key)
            options_desc = issue_info.get('options', {})
            option_desc = options_desc.get(option, option)
            lines.append(f"{issue_name}: {option} - {option_desc}")
    
    return "\n".join(lines)

def render_player_scores(player_scores: Dict[str, int], deal_state: Dict[str, str], 
                        player_name: str) -> str:
    """Render a player's private scores for the current deal."""
    if not deal_state or not player_scores:
        return f"{player_name}'s scores: Not available"
    
    lines = [f"{player_name}'s Private Scores:"]
    lines.append("=" * 30)
    
    total_score = 0
    for issue_key, option in deal_state.items():
        if issue_key in player_scores:
            issue_scores = player_scores[issue_key]
            if option in issue_scores:
                score = issue_scores[option]
                total_score += score
                lines.append(f"{issue_key}: {option} = {score} points")
    
    lines.append("-" * 20)
    lines.append(f"Total Score: {total_score} points")
    
    return "\n".join(lines)

def render_negotiation_summary(history: List[Dict], current_deal: Dict[str, str], 
                             round_num: int, max_rounds: int) -> str:
    """Render a summary of the negotiation progress."""
    lines = [f"Negotiation Round {round_num}/{max_rounds}"]
    lines.append("=" * 40)
    
    if current_deal:
        deal_str = ", ".join([f"{k}:{v}" for k, v in current_deal.items()])
        lines.append(f"Current Proposal: {deal_str}")
    else:
        lines.append("Current Proposal: None")
    
    lines.append("")
    
    # Show recent actions (last 3)
    if history:
        lines.append("Recent Actions:")
        lines.append("-" * 15)
        recent_actions = history[-3:] if len(history) > 3 else history
        for action in recent_actions:
            player_id = action.get('player_id', 'Unknown')
            action_type = action.get('action_type', 'Unknown')
            lines.append(f"Player {player_id}: {action_type}")
    
    return "\n".join(lines)

def render_voting_status(votes: Dict[int, str], valid_players: List[int]) -> str:
    """Render the current voting status."""
    lines = ["Voting Status:"]
    lines.append("=" * 15)
    
    accept_count = 0
    reject_count = 0
    
    for player_id in valid_players:
        vote = votes.get(player_id, "No vote")
        lines.append(f"Player {player_id}: {vote}")
        if vote == "ACCEPT":
            accept_count += 1
        elif vote == "REJECT":
            reject_count += 1
    
    lines.append("-" * 15)
    lines.append(f"ACCEPT: {accept_count}, REJECT: {reject_count}")
    
    return "\n".join(lines)

def render_game_issues(issues: Dict[str, Dict]) -> str:
    """Render the available issues and options."""
    lines = ["Available Issues and Options:"]
    lines.append("=" * 35)
    
    for issue_key, issue_info in issues.items():
        issue_name = issue_info.get('name', issue_key)
        lines.append(f"\n{issue_name} ({issue_key}):")
        
        options = issue_info.get('options', {})
        for option_key, option_desc in options.items():
            lines.append(f"  {option_key}: {option_desc}")
    
    return "\n".join(lines)
