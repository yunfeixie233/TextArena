""" Negotiation Game Environment """

import random
import re
from typing import Any, Dict, Optional, Tuple

import textarena as ta




class NegotiationEnv(ta.Env):
    """ Environment for the Negotiation Game. """
    def __init__(self, max_turns: Optional[int]=10):
        """
        Initialize the Negotiation Game environment.

        Args:
            max_turns (Optional[int]): Maximum number of turns before the game is truncated.
        """
        self.resource_names = ["Wheat", "Wood", "Sheep", "Brick", "Ore"]
        self.base_values = {"Wheat": 5, "Wood": 10, "Sheep": 15, "Brick": 25, "Ore": 40}

        # Initialize game state variables
        self.state = ta.State(
            num_players=2,
            max_turns=max_turns,
            render_keys=["inventory_value"]
        )

        # Regex patterns for parsing actions
        self.accept_pattern = re.compile(r"\[Accept\]", re.IGNORECASE)
        self.deny_pattern = re.compile(r"\[Deny\]", re.IGNORECASE)
        self.offer_pattern = re.compile(r"\[Offer\](.*?)[\.]", re.IGNORECASE | re.DOTALL)


    def reset(self, seed: Optional[int]=None) -> Optional[ta.Observations]:
        """
        Reset the Negotiation Game to its initial state.

        Args:
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.

        Returns:
            Optional[ta.Observations]: Initial observations for both players as a dict.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        game_state = {
            "current_offer": None,
            "player_resources": {
                0: {resource: random.randint(5, 25) for resource in self.resource_names},
                1: {resource: random.randint(5, 25) for resource in self.resource_names},
            },
            "player_values": {}
        }

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
            game_state.setdefault("inventory_value", {})[player_id] = {
                "initial": initial_value,
                "current": initial_value,
                "change": 0,
            }

        # for prompt generation
        self.resources = game_state["player_resources"]
        self.resource_values = game_state["player_values"]

        return self.state.reset(
            game_state=game_state,
            player_prompt_function=self._generate_player_prompt
        )

    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the initial prompt for a player.

        Args:
            player_id (int): ID of the player (0 or 1).

        Returns:
            str: The initial prompt for the player.
        """
        resource_value_list = "; ".join(
            [
                f"{self.resources[player_id][res]} {res} (Value of each: {self.resource_values[player_id][res]})"
                for res in self.resources[player_id].keys()
            ]
        )
        prompt = (
            f"You are Player {player_id} in the Negotiation Game.\n"
            "You have some resources, and your task is to trade such that the total value of your resources increases.\n"
            f"The resources and associated values you currently have are: {resource_value_list}.\n"
            "At each turn, you can talk to your opponent or make an explicit trade offer.\n"
            "Use the following special tokens for actions:\n"
            "  - [Offer]: To make a trade offer.\n"
            "    Format: [Offer] I give [your resources]; You give [their resources].\n"
            "    Example: [Offer] I give 2 Wheat, 1 Ore; You give 3 Sheep.\n"
            "  - [Accept]: To accept an incoming offer.\n"
            "  - [Deny]: To deny an incoming offer.\n"
            "You can include additional text before or after these tokens.\n"
            "If responding to an offer, ensure your reply contains [Accept] or [Deny] as appropriate.\n"
        )
        if self.state.max_turns:
            prompt += f"The game lasts for {self.state.max_turns} turns in total.\n"
        else:
            prompt += "The game has no turn limit.\n"
        return prompt

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[ta.Observations], # Observations: Dict[int, Tuple[int, str]]
        Optional[ta.Rewards], # Rewards: Dict[int, int]
        bool, # Truncated
        bool, # Terminated
        ta.Info, # Info: Optional[Dict[str, Any]]
    ]:
        """
        Process the player's action.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The player's message or action.

        Returns:
            tuple: (observations, reward, truncated, terminated, info)
        """

        # check the player_id and action format
        self.state.check_action_format(
            action=action,
            player_id=player_id
        )

        # update the observations and log the action
        self.state.add_observation(
            from_id=player_id,
            to_id=-1, # Broadcast to all
            message=action,
            for_logging=True
        )

        # check for existing offers
        self._check_and_execute_existing_offer(
            player_id=player_id,
            action=action
        )


        # check for new offers
        self._check_for_new_offer(
            player_id=player_id,
            action=action
        )

        # if turn limit, determine winner
        if self.state.turn == self.state.max_turns:
            self._determine_winner()


        return self.state.step()



    def _check_and_execute_existing_offer(self, player_id: int, action: int) -> None:
        """
        Check if the player accepts or denies the current offer and execute accordingly.

        Args:
            player_id (int): ID of the player responding to the offer.
            action (str): The action string.
        """
        if self.state.game_state["current_offer"]:

            # check if the offer was accepted
            if self.accept_pattern.search(action):
                self._attempt_to_execute_trade(
                    player_id=player_id,
                    action=action
                )

            # check if the offer was denied
            elif self.deny_pattern.search(action):
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1, # Broadcast to all
                    message=f"Player {player_id} denied the trade offer."
                )
                self.state.game_state["current_offer"] = None # reset

            # if the offer was neither accepted or denied; throw and invalid move return
            else:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"Player {player_id} received a trade offer but neither accepted nor denied it."]
                )

    def _attempt_to_execute_trade(self, player_id: int, action: int) -> None:
        """ TODO """
        # check if the proposer has enough resources
        proposer_valid = self._check_and_execute_existing_offer(
            trade_resources=self.state.game_state["current_offer"]["offered_resources"],
            player_resources=self.state.game_state["player_resources"][1-player_id]
        )

        acceptor_valid = self._check_and_execute_existing_offer(
            trade_resources=self.state.game_state["current_offer"]["requested_resources"],
            player_resources=self.state.game_state["player_resources"][player_id]
        )

        # check if the trade can be executed
        if proposer_valid and acceptor_valid:
            # execute the trade
            for resource, qty in proposer_items.items():
                self.state.game_state["player_resources"][1-player_id][resource] -= qty
                self.state.game_state["player_resources"][player_id][resource] += qty
            for resource, qty in acceptor_items.items():
                self.state.game_state["player_resources"][player_id][resource] -= qty
                self.state.game_state["player_resources"][1-player_id][resource] += qty

            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1, # Broadcast to all
                message=f"Player {player_id} accepted the trade offer from Player {proposer_id}."
            )

            # update player inventory value
            self._update_inventory_values()

            # reset trade offer
            self.state.game_state["current_offer"] = None

        # if not, throw invalid move
        else:
            player_ids = []
            reasons = []
            if not proposer_valid:
                player_ids.append(proposer_id)
                reasons.append(f"Player {proposer_id} had a proposed trade accepted without having enough resources to execute it.")
            if not acceptor_valid:
                player_ids.append(player_id)
                reasons.append(f"Player {player_id} accepted a traded without having enough resources")

            self.state.set_invalid_move(
                player_ids=player_ids,
                reasons=reasons
            )

    def _check_if_sufficient_resources(self, trade_resources: Dict[str, int], player_resources: Dict[str, int]) -> bool:
        """
        Check if a player has sufficient resources for a trade.

        Args:
            trade_resources (Dict[str, int]): Resources required for the trade.
            player_resources (Dict[str, int]): Player's current resources.

        Returns:
            bool: True if sufficient, False otherwise.
        """
        for resource, qty in trade_resources.items():
            if player_resources.get(resource, 0) < qty:
                return False 
        return True


    def _check_for_new_offer(self, player_id: int, action: str):
        """
        Check if the player's action contains a new trade offer.

        Args:
            player_id (int): ID of the player making the offer.
            action (str): The action string.
        """
        # check if already done
        if not self.state.terminated:
            offer_match = self.offer_pattern.search(action)
            if offer_match:
                parsed_offer = self._parse_offer(offer_match.group(1).strip())
                if parsed_offer:
                    # add the offer to the game state
                    self.state.game_state["current_offer"] = parsed_offer 

                    self.state.add_observation(
                        from_id=ta.GAME_ID,
                        to_id=-1, # Broadcast to all
                        message=f"Player {player_id} made the following offer to Player {1-player_id}: {self._offer_to_str(parsed_offer)}"
                    )
                else:
                    # errornous offer
                    self.state.set_invalid_move(
                        player_ids=[player_id],
                        reasons=[f"Player {player_id} made a trade offer in an incorrect format."]
                    )

    def _parse_offer(self, offer_str: str) -> Optional[Dict[str, Dict[str, int]]]:
        """
        Parse a trade offer string into a structured dictionary.

        Args:
            offer_str (str): The offer string extracted from the action.

        Returns:
            Optional[Dict[str, Dict[str, int]]]: Parsed offer details or None if parsing fails.
        """
        try:
            # Remove any line breaks and extra spaces for robust parsing
            offer_str = ' '.join(offer_str.split())

            # Split by '; You give ' to separate the offers
            offer_parts = re.split(r';\s*You give\s*', offer_str, flags=re.IGNORECASE)
            if len(offer_parts) != 2:
                return None # errornous offer

            offered_items_str = re.sub(r'^I give\s*', '', offer_parts[0], flags=re.IGNORECASE).strip()
            requested_items_str = offer_parts[1].strip().rstrip('.')  # Remove trailing period if present

            offered_items = self._parse_resource_list(offered_items_str)
            requested_items = self._parse_resource_list(requested_items_str)

            if not offered_items or not requested_items:
                return None # errornous offer

            return  {'offered_items': offered_items, 'requested_items': requested_items}
        
        except Exception as e:
            input(e)
            return None

    def _parse_resource_list(self, resource_str: str) -> Optional[Dict[str, int]]:
        """
        Parse a string of resources and quantities into a dictionary.

        Args:
            resource_str (str): String containing resources, e.g., "2 Wheat, 1 Ore".

        Returns:
            Optional[Dict[str, int]]: Parsed resources or None if parsing fails.
        """
        resource_list = re.split(r',\s*|and\s*', resource_str)
        resources = {}
        for item in resource_list:
            item = item.strip()
            if not item:
                continue
            try:
                qty_str, resource_name = item.split(' ', 1)
                qty = int(qty_str)
                resource_name = resource_name.strip().title()  # Ensure consistent casing
                if resource_name not in self.resource_names or qty <= 0:
                    return None
                resources[resource_name] = qty
            except Exception as e:
                return None
        return resources

    def _offer_to_str(self, parsed_offer: Dict[str, Dict[str, int]]) -> str:
        """
        Convert a parsed offer dictionary to a readable string format.

        Args:
            parsed_offer (Dict[str, Dict[str, int]]): Parsed offer details.

        Returns:
            str: Readable string representation of the offer.
        """
        offered = ", ".join(f"{qty} {res}" for res, qty in parsed_offer["offered_items"].items())
        requested = ", ".join(f"{qty} {res}" for res, qty in parsed_offer["requested_items"].items())
        return f"Offered items: {offered}; Requested items: {requested}"

    def _determine_winner(self):
        """
        Determine the winner based on the change in inventory values.
        """
        # check if game is over
        if not self.state.terminated:
            if self.state.game_state["inventory_value"][0]["change"] == self.state.game_state["inventory_value"][1]["change"]:
                # draw
                self.state.set_draw(
                    reason=f"Same change in invetory value for all players. Draw."
                )
            else:
                winner_id = 0 if (
                    self.state.game_state["inventory_value"][0]["change"] > self.state.game_state["inventory_value"][1]["change"]
                ) else 1
                self.state.set_winner(
                    player_ids=[winner_id],
                    reason=f"Player {winner_id} won by having a larger gain in inventory value."
                )


    def _update_inventory_values(self):
        """
        Update the current inventory values and their changes for both players.
        """
        for player_id in range(self.state.num_players):
            # calculate current inventory value
            current_inventory_value = self._calculate_player_inventory_value(
                player_id=player_id,
                game_state=self.state.game_state
            )

            # update
            self.game_state["inventory_value"][player_id]["current"] = current_inventory_value
            self.game_state["inventory_value"][player_id]["change"] = (
                current_inventory_value-self.game_state["inventory_value"][player_id]["initial"]
            ) 


    def _calculate_player_inventory_value(self, player_id: int, game_state: Dict[str, Any]) -> float:
        """
        Calculate the total inventory value for a player.

        Args:
            player_id (int): ID of the player.
            game_state (Dict[str, Any]): Current game state.

        Returns:
            float: Total inventory value.
        """
        resources = game_state["player_resources"][player_id]
        values = game_state["player_values"][player_id]
        inventory_value = sum([qty * values[res] for res, qty in resources.items()])
        return inventory_value

    def render(self):
        """
        Render the current game state to the console.
        """
        print(f"Turn: {self.state.turn}/{self.max_turns}")
        print("Player Resources and Values:")
        for player_id in [0, 1]:
            resources = self.state.game_state["player_resources"][player_id]
            values = self.state.game_state["player_values"][player_id]
            resource_list = "; ".join(
                [
                    f"{resources[res]} {res} (Value: {values[res]})"
                    for res in resources.keys()
                ]
            )
            print(f"  Player {player_id}: {resource_list}")

        if self.state.game_state["current_offer"]:
            offer = self.state.game_state["current_offer"]
            print(
                f"\nCurrent offer from Player {offer['from_player']} to Player {offer['to_player']}:"
            )
            my_offer = "; ".join(
                [f"{qty} {res}" for res, qty in offer["offer"]["my_offer"].items()]
            )
            their_offer = "; ".join(
                [f"{qty} {res}" for res, qty in offer["offer"]["their_offer"].items()]
            )
            print(f"  I give: {my_offer}; You give: {their_offer}")
        else:
            print("\nNo trades have been made yet.")

        print("\nAction Logs:")
        for log in self.state.logs[-10:]:  # Display the last 10 logs
            sender_id, message = log
            if sender_id == ta.GAME_ID:
                print(f"[GAME] {message}")
            else:
                print(f"[Player {sender_id}] {message}")
        print("\n")