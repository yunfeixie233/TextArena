from typing import Optional, List, Dict


def create_board_str(
    pool: int,
    current_offer: Optional[int],
    game_phase: str,
    round_number: int,
    total_rounds: int,
    player_totals: Dict[int, int],
    round_history: List[Dict],
    current_proposer: int,
) -> str:
    """
    Create a string representation of the current Multi-Round Ultimatum game state.
    
    Args:
        pool (int): Total amount of money available each round
        current_offer (Optional[int]): Current offer amount, None if no offer made
        game_phase (str): Current phase of the game ("offering", "responding")
        round_number (int): Current round number
        total_rounds (int): Total number of rounds in the game
        player_totals (Dict[int, int]): Accumulated money for each player
        round_history (List[Dict]): History of all previous rounds
        current_proposer (int): ID of current proposer
    
    Returns:
        str: Formatted string representation of the game state
    """
    board_str = "=" * 60 + "\n"
    board_str += "         MULTI-ROUND ULTIMATUM GAME\n"
    board_str += "=" * 60 + "\n\n"
    
    # Round information
    board_str += f"🎲 Round {round_number}/{total_rounds} | Pool this round: ${pool}\n\n"
    
    # Current totals
    board_str += f"💰 Player Totals:\n"
    board_str += f"   Player 0: ${player_totals[0]} | Player 1: ${player_totals[1]}\n\n"
    
    # Current roles
    current_responder = 1 - current_proposer
    board_str += f"🎭 Current Roles:\n"
    board_str += f"   Player {current_proposer}: Proposer (has ${pool} to split)\n"
    board_str += f"   Player {current_responder}: Responder (decides on offer)\n\n"
    
    # Phase information
    phase_display = {
        "offering": f"📝 OFFERING PHASE - Waiting for Player {current_proposer}'s offer",
        "responding": f"🤔 RESPONDING PHASE - Waiting for Player {current_responder}'s decision", 
    }
    board_str += f"Phase: {phase_display.get(game_phase, game_phase)}\n\n"
    
    # Current offer information
    if current_offer is not None:
        board_str += f"Current Offer:\n"
        board_str += f"  • Player {current_proposer} offers: ${current_offer} to Player {current_responder}\n"
        board_str += f"  • Player {current_proposer} would keep: ${pool - current_offer}\n\n"
    else:
        board_str += "Current Offer: None\n\n"
    
    # Round history
    if round_history:
        board_str += "📜 Round History:\n"
        for round_data in round_history:
            round_num = round_data["round"]
            proposer = round_data["proposer"]
            responder = round_data["responder"]
            offer = round_data["offer"]
            decision = round_data["decision"]
            prop_gain = round_data["proposer_gain"]
            resp_gain = round_data["responder_gain"]
            
            result_emoji = "✅" if decision == "Accept" else "❌"
            board_str += f"   Round {round_num}: P{proposer} offered ${offer} to P{responder} → {result_emoji} {decision}ed\n"
            board_str += f"              Gains: P{proposer} +${prop_gain}, P{responder} +${resp_gain}\n"
        board_str += "\n"
    else:
        board_str += "📜 Round History: None (first round)\n\n"
    
    # Rules reminder
    board_str += "-" * 60 + "\n"
    board_str += "Rules:\n"
    board_str += "• Players alternate as Proposer/Responder each round\n"
    board_str += "• Each round: Proposer offers part of $10 to Responder\n"
    board_str += "• Responder can ACCEPT (both get their shares) or REJECT (both get $0)\n"
    board_str += "• Money accumulates across rounds - highest total wins!\n"
    board_str += "=" * 60
    
    return board_str 