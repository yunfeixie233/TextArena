import random
from typing import Dict, Tuple, Optional, Any, List

import textarena as ta


class BlackjackEnv(ta.Env):
    def __init__(self, num_hands: int):
        super().__init__()
        self.num_hands = num_hands
        self.ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        self.suits = ['♠','♥','♦','♣']

    def reset(self, num_players: int, seed: Optional[int] = None):
        self.state = ta.State(num_players=1, min_players=1, max_players=1, seed=seed)
        game_state = {
            "hand_number": 1, "num_hands": self.num_hands, "player_hand": [], "dealer_hand": [],
            "player_done": False, "results_summary": {"win":0, "lose":0, "draw":0},
        }
        self.state.reset(game_state=game_state, player_prompt_function=self._generate_player_prompt)
        self._deal_initial_cards() # deal first hand
        self._observe_state()

    def _draw_card(self) -> str: # infinite deck
        rank = random.choice(self.ranks)
        suit = random.choice(self.suits)
        return f"{rank}{suit}"

    def _deal_initial_cards(self):
        self.state.game_state["player_hand"] = [self._draw_card(), self._draw_card()]
        self.state.game_state["dealer_hand"] = [self._draw_card(), self._draw_card()]

    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            "You are playing Blackjack against the dealer.\n"
            "Your goal is to get as close to 21 as possible without going over.\n"
            "On your turn, choose '[Hit]' to draw another card or '[Stand]' to hold.\n"
            "J/Q/K = 10 points; A = 11 or 1, whichever is better.\n"
        )

    def _hand_score(self, hand: List[str]) -> int:
        total, aces = 0, 0
        for card in hand:
            rank = card[:-1]
            if rank in ['J','Q','K']:
                total += 10
            elif rank == 'A':
                total += 11
                aces += 1
            else:
                total += int(rank)
        while total > 21 and aces: # downgrade aces from 11 → 1 as needed
            total -= 10
            aces -= 1
        return total

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        pid = self.state.current_player_id
        self.state.add_observation(from_id=pid, to_id=-1, message=action)

        if "[hit]" in action.lower():
            self._handle_hit()
        elif "[stand]" in action.lower():
            self._handle_stand()
        else:
            reason="Invalid action. Use '[Hit]' or '[Stand]'."
            self.state.set_invalid_move(player_id=pid, reason=reason)
            return False, {}

        self._observe_state()
        return self.state.step(rotate_player=False)

    def _handle_hit(self):
        self.state.game_state["player_hand"].append(self._draw_card())
        score = self._hand_score(self.state.game_state["player_hand"])
        if score > 21: # player busts → record loss, then advance
            self.state.game_state["results_summary"]["lose"] += 1
            self._advance_or_finish("bust")

    def _handle_stand(self):
        while self._hand_score(self.state.game_state["dealer_hand"]) < 17: # dealer draws until ≥17
            self.state.game_state["dealer_hand"].append(self._draw_card())
        # compare scores
        p = self._hand_score(self.state.game_state["player_hand"])
        d = self._hand_score(self.state.game_state["dealer_hand"])
        if d > 21 or p > d:
            self.state.game_state["results_summary"]["win"] += 1
            outcome = "win"
        elif p == d:
            self.state.game_state["results_summary"]["draw"] += 1
            outcome = "draw"
        else:
            self.state.game_state["results_summary"]["lose"] += 1
            outcome = "lose"
        self._advance_or_finish(outcome)

    def _advance_or_finish(self, outcome: str):
        """After a hand ends, either start the next one or finish env."""
        # announce this hand’s result
        message = f"Hand {self.state.game_state['hand_number']}: you {outcome}. Your final {self._hand_score(self.state.game_state['player_hand'])}, Dealer {self._hand_score(self.state.game_state['dealer_hand'])}."
        self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message)

        if self.state.game_state["hand_number"] < self.state.game_state["num_hands"]: # prepare next hand
            self.state.game_state["hand_number"] += 1
            self.state.game_state["player_hand"].clear()
            self.state.game_state["dealer_hand"].clear()
            self.state.game_state["player_done"] = False
            self._deal_initial_cards()
            # self._observe_state()
        else: # determine winner
            wins = self.state.game_state["results_summary"]["win"]
            losses= self.state.game_state["results_summary"]["lose"]
            draws = self.state.game_state["results_summary"]["draw"]
            summary = f"=== All {self.state.game_state['num_hands']} hands complete ===\nWins: {wins}, Losses: {losses}, Draws: {draws}\n"
            self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=summary)
            if wins > losses:
                player_reward_dict={0:1}
                reason=f"Overall you won more hands. Dealer: {losses}, You: {wins}, Draws: {draws}"
            elif wins == losses:
                player_reward_dict={0:0}
                reason=f"Overall it was a tie. Dealer: {losses}, You: {wins}, Draws: {draws}"
            else:
                player_reward_dict={0:-1}
                reason=f"Overall dealer won more hands. Dealer: {losses}, You: {wins}, Draws: {draws}"
            self.state.set_custom_game_outcome(player_reward_dict=player_reward_dict, reason=reason)

    def _observe_state(self):
        """Show current player hand and dealer's up-card."""
        hand = self.state.game_state["player_hand"]
        up = self.state.game_state["dealer_hand"][0]
        msg = (
            f"Hand {self.state.game_state['hand_number']}/{self.state.game_state['num_hands']}\n"
            f"Your hand: {', '.join(hand)} (Score: {self._hand_score(hand)})\n"
            f"Dealer shows: {up}"
        )
        self.state.add_observation(from_id=ta.GAME_ID, to_id=0, message=msg)
