import re, random
from typing import Any, Dict, Optional, Tuple

import textarena as ta
from textarena.envs.SimpleNegotiation.renderer import create_board_str


class SimpleNegotiationEnv(ta.Env):
    def __init__(self, max_turns: Optional[int] = 10, render_board: bool = True, prompt_template: str = "basic"):
        self.max_turns = max_turns
        self.render_board = render_board
        self.prompt_template = prompt_template
        self.resource_names = ["Wheat", "Wood", "Sheep", "Brick", "Ore"]
        self.base_values = {"Wheat": 5, "Wood": 10, "Sheep": 15, "Brick": 25, "Ore": 40}
        self.accept_pattern = re.compile(r"\[Accept\]", re.IGNORECASE)
        self.deny_pattern = re.compile(r"\[Deny\]", re.IGNORECASE)
        self.offer_pattern = re.compile(r"\[Offer:?\s*(?:I\s+(?:give|offer)\s+)?([^\[\]]+?)\s*\.*\]", re.IGNORECASE | re.DOTALL)
        
    def get_board_str(self):
        if not self.render_board:
            return "Rendering disabled"
        return create_board_str(
            player_resources=self.state.game_state["player_resources"], player_values=self.state.game_state["player_values"], 
            inventory_values=self.state.game_state["inventory_value"], current_offer=self.state.game_state["current_offer"]
        )

    def reset(self, num_players: int, seed: Optional[int] = None):
        self.state = ta.TwoPlayerState(num_players=num_players, max_turns=self.max_turns, seed=seed)
        player_resources = {0: {resource: random.randint(5, 25) for resource in self.resource_names}, 1: {resource: random.randint(5, 25) for resource in self.resource_names}}
        game_state = {"current_offer": None, "player_resources": player_resources, "player_values": {}, "trade_history": []}

        # Generate player-specific values for each resource type (±20% of base value, capped at 5 and 40)
        for player_id in [0, 1]:
            game_state["player_values"][player_id] = {}
            for resource in self.resource_names:
                base_value = self.base_values[resource]
                variation = int(0.2 * base_value)
                min_value = max(base_value - variation, 5)
                max_value = min(base_value + variation, 40)
                value = random.randint(min_value, max_value)
                game_state["player_values"][player_id][resource] = value

        # Keep track of the inventory (both initial and current)
        for player_id in [0, 1]:
            initial_value = self._calculate_player_inventory_value(player_id, game_state)
            game_state.setdefault("inventory_value", {})[player_id] = {"initial": initial_value, "current": initial_value, "change": 0}

        self.state.reset(game_state=game_state, player_prompt_function=self._prompt)

    def _prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        if self.prompt_template == "basic":
            return self._basic_prompt(player_id, game_state)
        elif self.prompt_template == "basic_variant_1":
            return self._basic_prompt_variant_1(player_id, game_state)
        elif self.prompt_template == "basic_variant_2":
            return self._basic_prompt_variant_2(player_id, game_state)
        elif self.prompt_template == "basic_variant_3":
            return self._basic_prompt_variant_3(player_id, game_state)
        elif self.prompt_template == "basic_variant_4":
            return self._basic_prompt_variant_4(player_id, game_state)
        elif self.prompt_template == "basic_variant_5":
            return self._basic_prompt_variant_5(player_id, game_state)
        elif self.prompt_template == "few_shot":
            return self._few_shot_prompt(player_id, game_state)
        elif self.prompt_template == "chain_of_thought":
            return self._chain_of_thought_prompt(player_id, game_state)
        elif self.prompt_template == "tree_of_thoughts":
            return self._tree_of_thoughts_prompt(player_id, game_state)
        elif self.prompt_template == "generated_knowledge":
            return self._generated_knowledge_prompt(player_id, game_state)
        else:
            raise ValueError(f"Invalid prompt template: {self.prompt_template}")

    def _basic_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        resource_value_list = "\n\t+ ".join(
            [f"{f'[{res}]':{' '}<8}  Qty: {game_state['player_resources'][player_id][res]:{' '}<2}   Value: {game_state['player_values'][player_id][res]}" for res in game_state['player_resources'][player_id].keys()]
        )
        return (
            f"You are Player {player_id} in the Negotiation Game.\nYou have some resources, and your task is to trade such that the total value of your resources increases.\n"
            f"The resources and associated values you currently have are:\n\t+ {resource_value_list}\nAt each turn, you can talk to your opponent and make a trade offer.\n"
            "Use the following special tokens for actions:\n"
            "  - '[Offer: 3 Sheep, 2 Ore -> 5 Brick, 2 Sheep]': [Offer: Offered Resources -> Requested Resources]\n"
            "  - '[Accept]': To accept an incoming offer.\n"
            "  - '[Deny]': To deny an incoming offer (default).\n"
            f"The game lasts for {self.state.max_turns} turns in total."
        )

    def _basic_prompt_variant_1(self, player_id: int, game_state: Dict[int, Any]) -> str:
        resource_value_list = "\n\t+ ".join(
            [f"{f'[{res}]':{' '}<8}  Qty: {game_state['player_resources'][player_id][res]:{' '}<2}   Value: {game_state['player_values'][player_id][res]}" for res in game_state['player_resources'][player_id].keys()]
        )
        return (
            f"Welcome to the Trading Arena! You are Player {player_id} in this competitive resource exchange game.\nYour goal is to maximize your wealth by strategically trading resources with your opponent.\n"
            f"Your current resource portfolio includes:\n\t+ {resource_value_list}\nEach turn provides an opportunity to negotiate with your trading partner.\n"
            "To interact effectively, use these action commands:\n"
            "  - '[Offer: 4 Wood, 1 Brick -> 2 Ore, 3 Wheat]': Format - [Offer: What_You_Give -> What_You_Want]\n"
            "  - '[Accept]': Use this to accept any pending trade proposal.\n"
            "  - '[Deny]': Use this to reject any pending trade proposal (this is the default response).\n"
            f"This trading session will continue for exactly {self.state.max_turns} rounds."
        )

    def _basic_prompt_variant_2(self, player_id: int, game_state: Dict[int, Any]) -> str:
        resource_value_list = "\n\t+ ".join(
            [f"{f'[{res}]':{' '}<8}  Qty: {game_state['player_resources'][player_id][res]:{' '}<2}   Value: {game_state['player_values'][player_id][res]}" for res in game_state['player_resources'][player_id].keys()]
        )
        return (
            f"You have entered a resource trading simulation as Player {player_id}.\nYour mission: enhance your economic position by conducting profitable trades that boost your total asset value.\n"
            f"Your starting inventory consists of:\n\t+ {resource_value_list}\nDuring each round, engage in commerce by proposing mutually beneficial exchanges.\n"
            "Execute your trading decisions using these specific formats:\n"
            "  - '[Offer: 2 Sheep, 6 Wheat -> 3 Brick, 1 Wood]': Structure - [Offer: Resources_To_Trade -> Resources_To_Acquire]\n"
            "  - '[Accept]': Approve and execute the current trade offer.\n"
            "  - '[Deny]': Decline the current trade offer (happens automatically if no explicit response).\n"
            f"The complete trading period spans {self.state.max_turns} turns total."
        )

    def _basic_prompt_variant_3(self, player_id: int, game_state: Dict[int, Any]) -> str:
        resource_value_list = "\n\t+ ".join(
            [f"{f'[{res}]':{' '}<8}  Qty: {game_state['player_resources'][player_id][res]:{' '}<2}   Value: {game_state['player_values'][player_id][res]}" for res in game_state['player_resources'][player_id].keys()]
        )
        return (
            f"As Player {player_id} in this Resource Exchange Challenge, you control a collection of valuable materials.\nSucceed by making smart trades that increase the overall worth of your resource collection.\n"
            f"Currently under your management:\n\t+ {resource_value_list}\nYour turn allows you to communicate and propose business deals with the other player.\n"
            "Communicate your intentions through these standardized commands:\n"
            "  - '[Offer: 1 Ore, 4 Sheep -> 6 Wood, 2 Brick]': Template - [Offer: Items_You_Provide -> Items_You_Request]\n"
            "  - '[Accept]': Confirm your agreement to the proposed exchange.\n"
            "  - '[Deny]': Refuse the proposed exchange (default action if unspecified).\n"
            f"You have {self.state.max_turns} opportunities to make deals before the game concludes."
        )

    def _basic_prompt_variant_4(self, player_id: int, game_state: Dict[int, Any]) -> str:
        resource_value_list = "\n\t+ ".join(
            [f"{f'[{res}]':{' '}<8}  Qty: {game_state['player_resources'][player_id][res]:{' '}<2}   Value: {game_state['player_values'][player_id][res]}" for res in game_state['player_resources'][player_id].keys()]
        )
        return (
            f"Greetings, Player {player_id}! You are now participating in an economic trading game.\nYour objective is straightforward: grow your fortune by engaging in resource exchanges that add value to your holdings.\n"
            f"Your available assets for trading are:\n\t+ {resource_value_list}\nEvery turn presents a chance to negotiate and strike deals with your fellow trader.\n"
            "Utilize these action tokens to communicate your decisions:\n"
            "  - '[Offer: 5 Wheat, 2 Wood -> 1 Ore, 4 Sheep]': Pattern - [Offer: Your_Contribution -> Your_Demand]\n"
            "  - '[Accept]': Agree to and finalize the current offer.\n"
            "  - '[Deny]': Reject and dismiss the current offer (automatic if no action taken).\n"
            f"The game will run for {self.state.max_turns} complete turns before determining the winner."
        )

    def _basic_prompt_variant_5(self, player_id: int, game_state: Dict[int, Any]) -> str:
        resource_value_list = "\n\t+ ".join(
            [f"{f'[{res}]':{' '}<8}  Qty: {game_state['player_resources'][player_id][res]:{' '}<2}   Value: {game_state['player_values'][player_id][res]}" for res in game_state['player_resources'][player_id].keys()]
        )
        return (
            f"You are operating as Player {player_id} in this Strategic Resource Trading Game.\nAim to outperform your competitor by making clever trades that amplify the total value of your resource stockpile.\n"
            f"Your current resource reserves are:\n\t+ {resource_value_list}\nEach turn allows for discussion and deal-making with your trading adversary.\n"
            "Make your moves clear using these required action formats:\n"
            "  - '[Offer: 3 Brick, 1 Ore -> 8 Wheat, 3 Wood]': Formula - [Offer: Resources_You_Surrender -> Resources_You_Gain]\n"
            "  - '[Accept]': Seal the deal on the existing trade proposal.\n"
            "  - '[Deny]': Turn down the existing trade proposal (occurs by default if no explicit choice).\n"
            f"This competitive session will last for {self.state.max_turns} turns before final scoring."
        )

    def _few_shot_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        resource_value_list = "\n\t+ ".join(
            [f"{f'[{res}]':{' '}<8}  Qty: {game_state['player_resources'][player_id][res]:{' '}<2}   Value: {game_state['player_values'][player_id][res]}" for res in game_state['player_resources'][player_id].keys()]
        )
        return (
            f"You are Player {player_id} in the Negotiation Game.\nYour task is to trade such that the total value of your resources increases.\n"
            f"The resources and associated values you currently have are:\n\t+ {resource_value_list}\n\n"
            "Here are some examples of good trading decisions:\n\n"
            "Example 1: A player has 5 Wheat (value 4 each) and sees opponent needs Wheat. "
            "They offer '[Offer: 3 Wheat -> 1 Ore]' because 1 Ore (value 35) is worth more than 3 Wheat (value 12).\n\n"
            "Example 2: Player receives offer '2 Wood -> 4 Sheep'. They calculate: 2 Wood = 20 value, 4 Sheep = 60 value. "
            "Since they're giving less value than receiving, they respond '[Accept]'.\n\n"
            "Example 3: Player has excess low-value resources and offers '[Offer: 8 Wheat, 3 Wood -> 2 Brick]' "
            "to convert multiple cheap resources into fewer valuable ones.\n\n"
            "Use the following special tokens for actions:\n"
            "  - '[Offer: 3 Sheep, 2 Ore -> 5 Brick, 2 Sheep]': [Offer: Offered Resources -> Requested Resources]\n"
            "  - '[Accept]': To accept an incoming offer.\n"
            "  - '[Deny]': To deny an incoming offer (default).\n"
            f"The game lasts for {self.state.max_turns} turns in total."
        )

    def _chain_of_thought_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        resource_value_list = "\n\t+ ".join(
            [f"{f'[{res}]':{' '}<8}  Qty: {game_state['player_resources'][player_id][res]:{' '}<2}   Value: {game_state['player_values'][player_id][res]}" for res in game_state['player_resources'][player_id].keys()]
        )
        return (
            f"You are Player {player_id} in the Negotiation Game.\nYour task is to trade such that the total value of your resources increases.\n"
            f"The resources and associated values you currently have are:\n\t+ {resource_value_list}\n\n"
            "Before making any trading decision, think step-by-step about your approach.\n\n"
            "Some possible directions to consider (but feel free to think about whatever is most relevant):\n"
            "- What is your current situation and what are your goals?\n"
            "- How do you evaluate potential trades or offers?\n"
            "- What factors influence your decision-making?\n"
            "- What might your opponent be thinking or needing?\n\n"
            "Work through your reasoning step by step, then make your decision.\n\n"
            "Use the following special tokens for actions:\n"
            "  - '[Offer: 3 Sheep, 2 Ore -> 5 Brick, 2 Sheep]': [Offer: Offered Resources -> Requested Resources]\n"
            "  - '[Accept]': To accept an incoming offer.\n"
            "  - '[Deny]': To deny an incoming offer (default).\n"
            f"The game lasts for {self.state.max_turns} turns in total."
        )

    def _tree_of_thoughts_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        resource_value_list = "\n\t+ ".join(
            [f"{f'[{res}]':{' '}<8}  Qty: {game_state['player_resources'][player_id][res]:{' '}<2}   Value: {game_state['player_values'][player_id][res]}" for res in game_state['player_resources'][player_id].keys()]
        )
        return (
            f"You are Player {player_id} in the Negotiation Game.\nYour task is to trade such that the total value of your resources increases.\n"
            f"The resources and associated values you currently have are:\n\t+ {resource_value_list}\n\n"
            "Imagine three different trading experts are advising you on this decision.\n"
            "Each expert will write down one step of their thinking, then share it with the group.\n"
            "Then all experts will go on to the next step, and so on.\n"
            "If any expert realizes they're wrong at any point, they leave.\n\n"
            "Consider what types of experts would be most helpful for this trading decision, then have them analyze the situation from their different perspectives.\n\n"
            "Use the following special tokens for actions:\n"
            "  - '[Offer: 3 Sheep, 2 Ore -> 5 Brick, 2 Sheep]': [Offer: Offered Resources -> Requested Resources]\n"
            "  - '[Accept]': To accept an incoming offer.\n"
            "  - '[Deny]': To deny an incoming offer (default).\n"
            f"The game lasts for {self.state.max_turns} turns in total."
        )

    def _generated_knowledge_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        resource_value_list = "\n\t+ ".join(
            [f"{f'[{res}]':{' '}<8}  Qty: {game_state['player_resources'][player_id][res]:{' '}<2}   Value: {game_state['player_values'][player_id][res]}" for res in game_state['player_resources'][player_id].keys()]
        )
        return (
            f"You are Player {player_id} in the Negotiation Game.\nYour task is to trade such that the total value of your resources increases.\n"
            f"The resources and associated values you currently have are:\n\t+ {resource_value_list}\n\n"
            "Before making a trading decision, first generate relevant knowledge about resource trading and negotiation that applies to your situation.\n\n"
            "Generate Knowledge: What key principles, strategies, or insights about resource trading and negotiation are most relevant to your current situation?\n\n"
            "After generating this knowledge, apply it to make your trading decision.\n\n"
            "Use the following special tokens for actions:\n"
            "  - '[Offer: 3 Sheep, 2 Ore -> 5 Brick, 2 Sheep]': [Offer: Offered Resources -> Requested Resources]\n"
            "  - '[Accept]': To accept an incoming offer.\n"
            "  - '[Deny]': To deny an incoming offer (default).\n"
            f"The game lasts for {self.state.max_turns} turns in total."
        )

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(from_id=self.state.current_player_id, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)
        self._check_and_execute_existing_offer(player_id=self.state.current_player_id, action=action) # Check if the player is responding to an existing offer
        self._check_for_new_offer(player_id=self.state.current_player_id, action=action) # Check if the player's action contains a new trade offer
        if self.state.check_turn_limit(): self._determine_winner() # If turn limit, determine winner
        return self.state.step()

    def _check_and_execute_existing_offer(self, player_id: int, action: str) -> None:
        # check if an offer exists, and whether it was accepted
        if self.state.game_state["current_offer"] and self.accept_pattern.search(action): 
            self._attempt_to_execute_trade(player_id=player_id, action=action)
        elif self.state.game_state["current_offer"]:
            self.state.add_observation(message=f"Player {self.state.current_player_id} rejected the trade offer.", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)
        else: 
            self.state.game_state["current_offer"] = None  # make sure the offer is reset

    def _attempt_to_execute_trade(self, player_id: int, action: str) -> None:
        """ Attempt to execute the trade if both players have sufficient resources """
        current_offer = self.state.game_state["current_offer"]
        proposer_id = current_offer["from_player"]
        acceptor_id = player_id

        # # Check if the trade can be executed
        # if proposer_valid and acceptor_valid:
        if self._check_if_sufficient_resources(trade_resources=current_offer["requested_resources"], player_resources=self.state.game_state["player_resources"][acceptor_id]):
            # Execute the trade
            for resource, qty in current_offer["offered_resources"].items():
                self.state.game_state["player_resources"][proposer_id][resource] -= qty
                self.state.game_state["player_resources"][acceptor_id][resource] += qty
            for resource, qty in current_offer["requested_resources"].items():
                self.state.game_state["player_resources"][acceptor_id][resource] -= qty
                self.state.game_state["player_resources"][proposer_id][resource] += qty
            self.state.add_observation(message=f"Player {acceptor_id} accepted the trade offer from Player {proposer_id}.", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)

            # Update trade history with outcome
            self.state.game_state["trade_history"].append({
                "from_player": proposer_id, "to_player": acceptor_id, "offered_resources": current_offer["offered_resources"],
                "requested_resources": current_offer["requested_resources"], "outcome": "Accepted"
            })

            self._update_inventory_values() # Update player inventory value
            self.state.game_state["current_offer"] = None # Reset trade offer
        else: self.state.set_invalid_move(reason="Player tried accepting a trade without having the necessary resources.") # If not, throw invalid move

    def _check_if_sufficient_resources(self, trade_resources: Dict[str, int], player_resources: Dict[str, int]) -> bool:
        """ Check if a player has sufficient resources for a trade """
        for resource, qty in trade_resources.items():
            if player_resources.get(resource, 0) < qty: return False
        return True

    def _check_for_new_offer(self, player_id: int, action: str):
        """ Check if the player's action contains a new trade offer """
        # Check if the game has already done
        if not self.state.done:
            offer_match = self.offer_pattern.search(action)
            if offer_match:
                matched_offer = offer_match.group(1).strip()
                parsed_offer = self._parse_offer(matched_offer)
                if parsed_offer:
                    # check if necessary resourcs
                    if self._check_if_sufficient_resources(trade_resources=parsed_offer["offered_resources"], player_resources=self.state.game_state["player_resources"][player_id]):
                        # Add the offer to the game state with consistent keys
                        self.state.game_state["current_offer"] = {
                            "from_player": player_id, "to_player": 1 - player_id,
                            "offered_resources": parsed_offer["offered_resources"], "requested_resources": parsed_offer["requested_resources"]
                        }
                        # Update trade history with the new offer
                        self.state.game_state["trade_history"].append({
                            "from_player": player_id, "to_player": 1 - player_id, "offered_resources": parsed_offer["offered_resources"],
                            "requested_resources": parsed_offer["requested_resources"], "outcome": None  # To be updated upon acceptance
                        })
                        self.state.add_observation(message=f"Player {player_id} made the following offer to Player {1 - player_id}: {self._offer_to_str(parsed_offer)}", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)
                    else: self.state.set_invalid_move(reason=f"Player {player_id} tried to make a trade offer without having the necessary resources.")
                else: self.state.set_invalid_move(reason=f"Player {player_id} made a trade offer in an incorrect format.")
            else: self.state.add_observation(message=f"Player {player_id} made no new trade offer.", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)

    def _parse_offer(self, offer_str: str) -> Optional[Dict[str, Dict[str, int]]]:
        """Parse a trade offer string into a structured dictionary"""
        try:
            offer_str = ' '.join(offer_str.split()) # Remove any line breaks and extra spaces for robust parsing
            offer_str = re.sub(r'[.,!?]+$', '', offer_str) # Remove trailing punctuation (e.g., period)
            offer_str = re.sub(r'^(I\s+(?:give|offer)\s+)', '', offer_str, flags=re.IGNORECASE) # Remove leading phrases like "I give" or "I offer"
            offer_parts = re.split(r'\s*->\s*', offer_str) # Split by '->' to separate offered and requested resources
            if len(offer_parts) != 2: return None  # Erroneous offer
            offered_items_str = offer_parts[0].strip()
            requested_items_str = offer_parts[1].strip()
            offered_items = self._parse_resource_list(offered_items_str)
            requested_items = self._parse_resource_list(requested_items_str)
            if not offered_items or not requested_items: return None  # Erroneous offer
            return {'offered_resources': offered_items, 'requested_resources': requested_items}
        except Exception as e: return None

    def _parse_resource_list(self, resource_str: str) -> Optional[Dict[str, int]]:
        pairs = re.findall(r'(\d+)\s+([A-Za-z]+)', resource_str, re.IGNORECASE)
        if not pairs: return None # nothing recognised
        resources: Dict[str, int] = {}
        for qty_str, raw_name in pairs:
            qty = int(qty_str)
            name = {"Sheeps": "Sheep", "Woods": "Wood"}.get(raw_name.title(), raw_name.title())
            if name not in self.resource_names or qty <= 0: return None # invalid entry
            resources[name] = resources.get(name, 0) + qty
        return resources

    def _offer_to_str(self, parsed_offer: Dict[str, Dict[str, int]]) -> str:
        offered = ", ".join(f"{qty} {res}" for res, qty in parsed_offer["offered_resources"].items())
        requested = ", ".join(f"{qty} {res}" for res, qty in parsed_offer["requested_resources"].items())
        return f"Offered items: {offered} -> Requested items: {requested}"

    def _determine_winner(self):
        if not self.state.done:
            if self.state.game_state["inventory_value"][0]["change"] == self.state.game_state["inventory_value"][1]["change"]:
                self.state.set_draw(reason=f"Same change in inventory value for all players. Draw.")
            else:
                winner_id = 0 if (self.state.game_state["inventory_value"][0]["change"] > self.state.game_state["inventory_value"][1]["change"]) else 1
                self.state.set_winner(player_id=winner_id, reason=f"Player {winner_id} won by having a larger gain in inventory value.")

    def _update_inventory_values(self):
        for player_id in range(self.state.num_players):
            current_inventory_value = self._calculate_player_inventory_value(player_id=player_id, game_state=self.state.game_state) # Calculate current inventory value
            self.state.game_state["inventory_value"][player_id]["current"] = current_inventory_value
            self.state.game_state["inventory_value"][player_id]["change"] = current_inventory_value - self.state.game_state["inventory_value"][player_id]["initial"]

    def _calculate_player_inventory_value(self, player_id: int, game_state: Dict[str, Any]) -> float:
        return sum([qty * game_state["player_values"][player_id][res] for res, qty in game_state["player_resources"][player_id].items()])
