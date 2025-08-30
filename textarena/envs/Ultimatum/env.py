import re
from typing import Any, Dict, Optional, Tuple, List

import textarena as ta
from spiral.envs.Ultimatum.renderer import create_board_str


class UltimatumEnv(ta.Env):
    """Environment for the Multi-Round Ultimatum Game.
    
    A two-player game where:
    - Players alternate as Proposer and Responder across rounds
    - Each round: Proposer has a pool of money and makes an offer to Responder
    - Responder can accept or reject the offer
    - If accepted: Proposer gets (pool - offer), Responder gets offer
    - If rejected: Both players get nothing for that round
    - Players accumulate money across multiple rounds
    """

    def __init__(self, pool: int = 10, max_turns: Optional[int] = 4):
        """
        Initialize the Multi-Round Ultimatum Game environment.
        
        Args:
            pool (int): Amount of money available each round
            max_turns (int): Maximum number of turns (should be even for balanced gameplay)
        """
        self.pool = pool
        self.max_turns = max_turns
        
        # Regex patterns for parsing player actions
        self.offer_pattern = re.compile(
            r"\[Offer:\s*\$?(\d+)\]", re.IGNORECASE
        )
        self.accept_pattern = re.compile(r"\[Accept\]", re.IGNORECASE)
        self.reject_pattern = re.compile(r"\[Reject\]", re.IGNORECASE)

    def get_board_str(self):
        """Get the current board state as a string."""
        return create_board_str(
            pool=self.state.game_state["pool"],
            current_offer=self.state.game_state.get("current_offer"),
            game_phase=self.state.game_state["phase"],
            round_number=self.state.game_state["round_number"],
            total_rounds=self.max_turns // 2,
            player_totals=self.state.game_state["player_totals"],
            round_history=self.state.game_state["round_history"],
            current_proposer=self.state.game_state["current_proposer"],
        )

    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        """Generate the prompt for a player including history."""
        round_num = game_state["round_number"]
        total_rounds = self.max_turns // 2
        current_proposer = game_state["current_proposer"]
        player_totals = game_state["player_totals"]
        round_history = game_state["round_history"]
        
        # Build history summary
        history_str = self._build_history_summary(round_history, player_id)
        
        # Current totals
        totals_str = f"Your current total: ${player_totals[player_id]} | Opponent's total: ${player_totals[1-player_id]}"
        
        if player_id == current_proposer:  # Current Proposer
            prompt = (
                f"You are Player {player_id} (Proposer) in Round {round_num}/{total_rounds} of the Multi-Round Ultimatum Game.\n"
                f"{totals_str}\n\n"
                f"You have ${game_state['pool']} to split this round between yourself and Player {1-player_id}.\n"
                "You must make an offer to the other player. They can either accept or reject your offer.\n"
                "If they accept: You get ${pool - offer}, they get ${offer} (added to your totals)\n"
                "If they reject: Both of you get $0 this round\n\n"
                f"{history_str}\n"
                "Use the following format to make your offer:\n"
                "  - [Offer: $X] where X is the amount you offer to the other player\n"
                "    Example: [Offer: $3]\n"
                f"You can offer any amount from $0 to ${game_state['pool']}.\n"
                "YOU CAN INCLUDE ADDITIONAL TEXT BEFORE AND/OR AFTER THE OFFER TOKEN.\n"
                '    Example: "Based on our history, I think this is fair. [Offer: $5]"\n'
            )
        else:  # Current Responder
            current_offer = game_state.get("current_offer")
            if current_offer is not None:
                prompt = (
                    f"You are Player {player_id} (Responder) in Round {round_num}/{total_rounds} of the Multi-Round Ultimatum Game.\n"
                    f"{totals_str}\n\n"
                    f"Player {current_proposer} has offered you ${current_offer} out of this round's ${game_state['pool']}.\n"
                    f"If you accept: You get ${current_offer}, they get ${game_state['pool'] - current_offer} (added to your totals)\n"
                    "If you reject: Both of you get $0 this round\n\n"
                    f"{history_str}\n"
                    "Use the following format to respond:\n"
                    "  - [Accept] to accept the offer\n"
                    "  - [Reject] to reject the offer\n"
                    "YOU CAN INCLUDE ADDITIONAL TEXT BEFORE AND/OR AFTER THESE TOKENS.\n"
                    '    Example: "Considering our past rounds, this seems fair. [Accept]" or "This is too low! [Reject]"\n'
                )
            else:
                prompt = (
                    f"You are Player {player_id} (Responder) in Round {round_num}/{total_rounds} of the Multi-Round Ultimatum Game.\n"
                    f"{totals_str}\n\n"
                    f"You are waiting for Player {current_proposer} to make an offer.\n"
                    f"{history_str}\n"
                    "Once they make an offer, you can choose to [Accept] or [Reject] it.\n"
                )
        
        return prompt

    def _build_history_summary(self, round_history: List[Dict], player_id: int) -> str:
        """Build a summary of previous rounds for the player."""
        if not round_history:
            return "Previous Rounds: None (this is the first round)"
        
        history_lines = ["Previous Rounds:"]
        for i, round_data in enumerate(round_history, 1):
            proposer = round_data["proposer"]
            responder = round_data["responder"] 
            offer = round_data["offer"]
            decision = round_data["decision"]
            proposer_gain = round_data["proposer_gain"]
            responder_gain = round_data["responder_gain"]
            
            if player_id == proposer:
                role = "You (Proposer)"
                other_role = f"Player {responder} (Responder)"
                your_gain = proposer_gain
                their_gain = responder_gain
            else:
                role = "You (Responder)"
                other_role = f"Player {proposer} (Proposer)"
                your_gain = responder_gain
                their_gain = proposer_gain
            
            history_lines.append(
                f"  Round {i}: {other_role} offered ${offer} → You {decision.lower()}ed → "
                f"You gained ${your_gain}, they gained ${their_gain}"
            )
        
        return "\n".join(history_lines)

    def reset(self, num_players: int = 2, seed: Optional[int] = None):
        """Reset the Multi-Round Ultimatum Game to its initial state."""
        # Initialize game state
        self.state = ta.State(
            num_players=2, min_players=2, max_players=2, max_turns=self.max_turns
        )

        game_state = {
            "pool": self.pool,
            "phase": "offering",  # "offering" or "responding" 
            "round_number": 1,
            "current_proposer": 0,  # Player 0 starts as proposer
            "current_offer": None,
            "player_totals": {0: 0, 1: 0},  # Accumulated money across rounds
            "round_history": [],  # History of all previous rounds
        }

        self.state.reset(
            seed=seed,
            game_state=game_state,
            player_prompt_function=self._generate_player_prompt,
        )

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """Process the player's action."""
        # Update the observations and log the action
        self.state.add_observation(
            from_id=self.state.current_player_id, to_id=-1, message=action
        )

        current_player = self.state.current_player_id
        game_phase = self.state.game_state["phase"]
        current_proposer = self.state.game_state["current_proposer"]

        if game_phase == "offering" and current_player == current_proposer:
            # Proposer is making an offer
            self._handle_proposer_action(action)
        elif game_phase == "responding" and current_player != current_proposer:
            # Responder is responding to the offer
            self._handle_responder_action(action)
        else:
            # Invalid turn
            reason = f"Player {current_player} cannot act during {game_phase} phase."
            self.state.set_invalid_move(player_id=current_player, reason=reason)

        return self.state.step()

    def _handle_proposer_action(self, action: str) -> None:
        """Handle the proposer's offer action."""
        offer_match = self.offer_pattern.search(action)
        
        if not offer_match:
            reason = "Proposer must make an offer using the format [Offer: $X]."
            self.state.set_invalid_move(player_id=self.state.current_player_id, reason=reason)
            return

        try:
            offer = int(offer_match.group(1))
        except ValueError:
            reason = "Offer amount must be a valid integer."
            self.state.set_invalid_move(player_id=self.state.current_player_id, reason=reason)
            return

        # Validate offer amount
        if offer < 0 or offer > self.state.game_state["pool"]:
            reason = f"Offer must be between $0 and ${self.state.game_state['pool']}."
            self.state.set_invalid_move(player_id=self.state.current_player_id, reason=reason)
            return

        # Valid offer - update game state
        self.state.game_state["current_offer"] = offer
        self.state.game_state["phase"] = "responding"
        
        # Broadcast the offer
        proposer_id = self.state.game_state["current_proposer"]
        responder_id = 1 - proposer_id
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=f"Round {self.state.game_state['round_number']}: Player {proposer_id} offers ${offer} to Player {responder_id} (keeping ${self.state.game_state['pool'] - offer})."
        )

    def _handle_responder_action(self, action: str) -> None:
        """Handle the responder's accept/reject action."""
        current_offer = self.state.game_state["current_offer"]
        
        if current_offer is None:
            reason = "No current offer to respond to."
            self.state.set_invalid_move(player_id=self.state.current_player_id, reason=reason)
            return

        if self.accept_pattern.search(action):
            # Offer accepted
            self._execute_accepted_offer()
        elif self.reject_pattern.search(action):
            # Offer rejected
            self._execute_rejected_offer()
        else:
            reason = "Responder must either [Accept] or [Reject] the offer."
            self.state.set_invalid_move(player_id=self.state.current_player_id, reason=reason)

    def _execute_accepted_offer(self) -> None:
        """Execute the round when offer is accepted."""
        offer = self.state.game_state["current_offer"]
        pool = self.state.game_state["pool"]
        proposer_id = self.state.game_state["current_proposer"]
        responder_id = 1 - proposer_id
        
        # Calculate gains for this round
        proposer_gain = pool - offer
        responder_gain = offer
        
        # Update total money
        self.state.game_state["player_totals"][proposer_id] += proposer_gain
        self.state.game_state["player_totals"][responder_id] += responder_gain
        
        # Add to history
        self.state.game_state["round_history"].append({
            "round": self.state.game_state["round_number"],
            "proposer": proposer_id,
            "responder": responder_id,
            "offer": offer,
            "decision": "Accept",
            "proposer_gain": proposer_gain,
            "responder_gain": responder_gain,
        })
        
        # Broadcast result
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=f"Player {responder_id} accepted! Round {self.state.game_state['round_number']} gains: Player {proposer_id} +${proposer_gain}, Player {responder_id} +${responder_gain}. New totals: Player 0: ${self.state.game_state['player_totals'][0]}, Player 1: ${self.state.game_state['player_totals'][1]}."
        )
        
        self._advance_to_next_round()

    def _execute_rejected_offer(self) -> None:
        """Execute the round when offer is rejected."""
        proposer_id = self.state.game_state["current_proposer"]
        responder_id = 1 - proposer_id
        offer = self.state.game_state["current_offer"]
        
        # Add to history (no gains)
        self.state.game_state["round_history"].append({
            "round": self.state.game_state["round_number"],
            "proposer": proposer_id,
            "responder": responder_id,
            "offer": offer,
            "decision": "Reject",
            "proposer_gain": 0,
            "responder_gain": 0,
        })
        
        # Broadcast result
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=f"Player {responder_id} rejected the offer! Round {self.state.game_state['round_number']} gains: Both players +$0. Totals remain: Player 0: ${self.state.game_state['player_totals'][0]}, Player 1: ${self.state.game_state['player_totals'][1]}."
        )
        
        self._advance_to_next_round()

    def _advance_to_next_round(self) -> None:
        """Advance to the next round or end the game."""
        # Check if we've completed all rounds
        if self.state.game_state["round_number"] >= (self.max_turns // 2):
            # Game is complete
            self._determine_final_winner()
        else:
            # Move to next round
            self.state.game_state["round_number"] += 1
            self.state.game_state["current_proposer"] = 1 - self.state.game_state["current_proposer"]  # Switch roles
            self.state.game_state["phase"] = "offering"
            self.state.game_state["current_offer"] = None
            
            # Broadcast round change
            new_proposer = self.state.game_state["current_proposer"]
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1,
                message=f"--- Round {self.state.game_state['round_number']} begins! Player {new_proposer} is now the Proposer ---"
            )

    def _determine_final_winner(self) -> None:
        """Determine the winner based on total accumulated money."""
        total_0 = self.state.game_state["player_totals"][0]
        total_1 = self.state.game_state["player_totals"][1]
        
        if total_0 > total_1:
            self.state.set_winners(
                player_ids=[0], 
                reason=f"Player 0 won with ${total_0} total vs Player 1's ${total_1}."
            )
        elif total_1 > total_0:
            self.state.set_winners(
                player_ids=[1], 
                reason=f"Player 1 won with ${total_1} total vs Player 0's ${total_0}."
            )
        else:
            self.state.set_draw(
                reason=f"Draw! Both players finished with ${total_0} total."
            ) 