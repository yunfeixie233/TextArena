from typing import Dict, List, Any

def render_deal_with_scores(deal_state: Dict[str, str], issues: Dict[str, Dict], 
                           player_scores: Dict[str, int], player_name: str) -> str:
    """Render the current deal with player's private scores inline."""
    if not deal_state:
        return "No current deal proposal."
    
    lines = [f"Current Deal & {player_name}'s Scores:"]
    lines.append("=" * 30)
    
    total_score = 0
    for issue_key, option in deal_state.items():
        if issue_key in issues:
            issue_info = issues[issue_key]
            issue_name = issue_info.get('name', issue_key)
            options_desc = issue_info.get('options', {})
            option_desc = options_desc.get(option, option)
            
            # Get player's score for this option
            score = 0
            if issue_key in player_scores and option in player_scores[issue_key]:
                score = player_scores[issue_key][option]
                total_score += score
            
            # Combine description with score
            lines.append(f"{issue_name}: {option} - {option_desc} ({score} points)")
    
    lines.append("=" * 30)
    lines.append(f"Total Score: {total_score} points")
    
    return "\n".join(lines)

def render_voting_status(votes: Dict[int, str], valid_players: List[int]) -> str:
    """Render the current voting status."""
    lines = ["Voting Status:"]
    lines.append("=" * 30)
    
    accept_count = 0
    reject_count = 0
    
    for player_id in valid_players:
        vote = votes.get(player_id, "No vote")
        lines.append(f"Player {player_id}: {vote}")
        if vote == "[Accept]":
            accept_count += 1
        elif vote == "[Reject]":
            reject_count += 1
    
    lines.append("-" * 30)
    lines.append(f"[Accept]: {accept_count}, [Reject]: {reject_count}")
    
    return "\n".join(lines)

def render_game_issues(issues: Dict[str, Dict]) -> str:
    """Render the available issues and options."""
    lines = ["Available Issues and Options:"]
    lines.append("=" * 30)
    
    for issue_key, issue_info in issues.items():
        issue_name = issue_info.get('name', issue_key)
        lines.append(f"\n{issue_name} ({issue_key}):")
        
        options = issue_info.get('options', {})
        for option_key, option_desc in options.items():
            lines.append(f"  {option_key}: {option_desc}")
    
    return "\n".join(lines)
