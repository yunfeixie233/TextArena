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
    lines = []
    
    # Game header
    lines.append("┌─────────────────────────────────────────────────────────────────────────────┐")
    lines.append("│                        MULTI-ROUND ULTIMATUM GAME                          │")
    lines.append("│─────────────────────────────────────────────────────────────────────────────│")
    lines.append(f"│ Round {round_number}/{total_rounds}                     Pool this round: ${pool:<47}│")
    lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
    lines.append("")
    
    # Player totals
    lines.append("┌──────────────────────────── Player Totals ─────────────────────────────────┐")
    lines.append(f"│ Player 0: ${player_totals[0]:<10}                                                      │")
    lines.append(f"│ Player 1: ${player_totals[1]:<10}                                                      │")
    lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
    lines.append("")
    
    # Current roles and phase
    current_responder = 1 - current_proposer
    lines.append("┌──────────────────────────── Current Status ────────────────────────────────┐")
    lines.append(f"│ Proposer:  Player {current_proposer} (has ${pool} to split)                                       │")
    lines.append(f"│ Responder: Player {current_responder} (decides on offer)                                       │")
    lines.append("│                                                                             │")
    
    if game_phase == "offering":
        lines.append(f"│ Phase: OFFERING - Waiting for Player {current_proposer}'s offer                           │")
    else:
        lines.append(f"│ Phase: RESPONDING - Waiting for Player {current_responder}'s decision                      │")
    
    lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
    lines.append("")
    
    # Current offer
    lines.append("┌──────────────────────────── Current Offer ─────────────────────────────────┐")
    if current_offer is not None:
        lines.append(f"│ Player {current_proposer} offers: ${current_offer:<10} to Player {current_responder}                            │")
        lines.append(f"│ Player {current_proposer} keeps:  ${pool - current_offer:<10}                                              │")
        lines.append("│                                                                             │")
        lines.append(f"│ Player {current_responder}'s turn to respond: [Accept] or [Reject]                          │")
    else:
        lines.append("│                                                                             │")
        lines.append("│                        No current offer pending                            │")
        lines.append("│                                                                             │")
    lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
    
    # Round history
    if round_history:
        lines.append("")
        lines.append("┌──────────────────────────── Round History ─────────────────────────────────┐")
        for round_data in round_history:
            round_num = round_data["round"]
            proposer = round_data["proposer"]
            responder = round_data["responder"]
            offer = round_data["offer"]
            decision = round_data["decision"]
            prop_gain = round_data["proposer_gain"]
            resp_gain = round_data["responder_gain"]
            
            decision_str = "ACCEPTED" if decision == "Accept" else "REJECTED"
            lines.append(f"│ Round {round_num}: P{proposer} offered ${offer:<3} to P{responder} -> {decision_str:<8}                          │")
            lines.append(f"│         Gains: P{proposer} +${prop_gain:<3}, P{responder} +${resp_gain:<3}                                       │")
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
    
    # Rules
    lines.append("")
    lines.append("┌────────────────────────────── Game Rules ──────────────────────────────────┐")
    lines.append("│ • Players alternate as Proposer/Responder each round                       │")
    lines.append("│ • Each round: Proposer offers part of the pool to Responder                │")
    lines.append("│ • Responder can ACCEPT (both get their shares) or REJECT (both get $0)     │")
    lines.append("│ • Money accumulates across rounds - highest total wins!                    │")
    lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
    
    return "\n".join(lines) 