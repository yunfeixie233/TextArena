import random
import re
from typing import Any, Dict, Optional, Tuple
import textarena as ta

class LeHavreEnv(ta.Env):
    """Environment for the Le Havre board game."""
    def __init__(self, max_turns: Optional[int] = 20):
        """
        Initialize the Le Havre game environment.

        Args:
            max_turns (Optional[int]): Maximum number of turns before game truncation.
        """
        self.resource_names = [
            "Wood", "Clay", "Iron", "Grain", "Fish", 
            "Coal", "Coke", "Cattle", "Bread", "Meat",
            "Smoked Fish", "Charcoal", "Brick", "Steel", "Franc"
        ]
        
        # Base values and food values for resources
        self.food_values = {
            "Fish": 1,
            "Bread": 2,
            "Meat": 3,
            "Smoked Fish": 2,
            "Franc": 1
        }

        # Initialize game state
        self.state = ta.State(
            num_players=2,
            max_turns=max_turns
        )

        # Action parsing patterns
        self.enter_building_pattern = re.compile(
            r"\[Enter:\s*([^\[\]]+?)\s*\]",
            re.IGNORECASE | re.DOTALL
        )
        self.take_resources_pattern = re.compile(
            r"\[Take:\s*([^\[\]]+?)\s*\]",
            re.IGNORECASE | re.DOTALL
        )
        self.build_pattern = re.compile(
            r"\[Build:\s*([^\[\]]+?)\s*\]",
            re.IGNORECASE | re.DOTALL
        )
        self.process_pattern = re.compile(
            r"\[Process:\s*([^\[\]]+?)\s*->\s*([^\[\]]+?)\s*\]",
            re.IGNORECASE | re.DOTALL
        )
        self.pay_loan_pattern = re.compile(
            r"\[Pay Loan:\s*(\d+)\s*\]",
            re.IGNORECASE
        )
        self.take_loan_pattern = re.compile(
            r"\[Take Loan:\s*(\d+)\s*\]",
            re.IGNORECASE
        )

    def reset(self, seed: Optional[int] = None) -> Optional[ta.Observations]:
        """
        Reset the Le Havre game to its initial state.

        Args:
            seed (Optional[int]): Random seed for reproducibility.

        Returns:
            Optional[ta.Observations]: Initial observations for players.
        """
        # Initialize game state
        game_state = {
            "supply": {resource: 0 for resource in self.resource_names},
            "player_resources": {},
            "buildings": {
                "Construction Firm": {
                    "cost": {},
                    "entry_fee_food": 2,
                    "entry_fee_francs": 0,
                    "worker": None,
                    "produces": {"Wood": 2}
                },
                "Clay Mound": {
                    "cost": {},
                    "entry_fee_food": 1,
                    "entry_fee_francs": 0,
                    "worker": None,
                    "produces": {"Clay": 1}
                },
                # Add more buildings...
            },
            "current_building": None,
            "food_requirement": {
                0: 3,
                1: 3
            }
        }

        # Initialize starting resources
        for player_id in [0, 1]:
            game_state["player_resources"][player_id] = {
                "Wood": 2,
                "Clay": 1,
                "Fish": 2,
                "Franc": 2,
                "Loan": 0
            }

        # Initialize supply
        starting_supply = {
            "Wood": 4,
            "Clay": 4,
            "Fish": 4,
            "Franc": 4
        }
        game_state["supply"].update(starting_supply)

        # Initialize resource offers for upcoming turns
        game_state["resource_offers"] = self._generate_resource_offers()

        return self.state.reset(
            seed=seed,
            game_state=game_state,
            player_prompt_function=self._generate_player_prompt
        )

    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        """Generate the initial prompt for a player."""
        resources_list = "; ".join(
            [f"{qty} {res}" for res, qty in game_state["player_resources"][player_id].items() if qty > 0]
        )
        
        buildings_list = "\n".join([
            f"- {name}: Entry fee: {bld['entry_fee_food']} food or {bld['entry_fee_francs']} francs" +
            (f" (Occupied by Player {bld['worker']})" if bld['worker'] is not None else "")
            for name, bld in game_state["buildings"].items()
        ])

        prompt = (
            f"You are Player {player_id} in Le Havre.\n"
            f"Your current resources: {resources_list}\n\n"
            f"Available buildings:\n{buildings_list}\n\n"
            "Available actions:\n"
            "1. Enter a building: [Enter: Building Name]\n"
            "2. Take resources: [Take: Resource Name]\n"
            "3. Build something: [Build: Building Name]\n"
            "4. Process resources: [Process: Input Resources -> Output Resources]\n"
            "5. Take loan: [Take Loan: Amount]\n"
            "6. Pay loan: [Pay Loan: Amount]\n\n"
            f"Food requirement this round: {game_state['food_requirement'][player_id]}\n"
        )
        return prompt

    def step(
        self,
        action: str,
    ) -> Tuple[Optional[ta.Rewards], bool, bool, ta.Info]:
        """Process the player's action.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The player's action string.

        Returns:
            tuple: (observations, reward, truncated, terminated, info)
        """
        # Validate player_id and action format
        self.state.check_action_format(
            action=action,
        )

        player_id = self.state.current_player_id


        # Log the action
        self.state.add_observation(
            from_id=player_id,
            to_id=-1,
            message=action,
            for_logging=True
        )

        # If this is the first action of a new round, add new resources
        if self.state.turn % self.state.num_players == 0:
            self._add_new_resources()
            self._return_workers()

        # Track if player has made a main action this turn
        made_main_action = False

        # Check for each type of action
        if self.enter_building_pattern.search(action):
            success = self._handle_enter_building(player_id, action)
            made_main_action = success
        elif self.take_resources_pattern.search(action):
            success = self._handle_take_resources(player_id, action)
            made_main_action = success
        elif self.build_pattern.search(action):
            success = self._handle_build(player_id, action)
            made_main_action = success
        elif self.process_pattern.search(action):
            success = self._handle_process(player_id, action)
            made_main_action = success
        elif self.pay_loan_pattern.search(action) or self.take_loan_pattern.search(action):
            success = self._handle_loans(player_id, action)
            # Loan actions are considered special actions (don't count as main action)
        else:
            # Invalid action
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[f"Player {player_id} made an invalid action."]
            )
            return self.state.step()

        # If player made a successful main action, move to next player
        if made_main_action:
            self.state.current_player_id = (self.state.current_player_id + 1) % self.state.num_players

        # Check for feeding phase
        if self._is_feeding_phase():
            self._handle_feeding_phase()

        # Check for round end and resource accumulation
        if self._is_round_end():
            self._accumulate_resources()

        # Check for game end
        if self.state.turn >= self.state.max_turns:
            self._end_game()
            return self.state.step()

        # Update rewards based on inventory value changes
        # rewards = {
        #     pid: self._calculate_player_value(pid) - self._calculate_previous_value(pid)
        #     for pid in range(self.state.num_players)
        # }
        # self.state.rewards.update(rewards)

        return self.state.step()


    def _add_new_resources(self) -> None:
        """Add new resources at the start of a round."""
        if self.state.turn // self.state.num_players < len(self.state.game_state["resource_offers"]):
            new_resources = self.state.game_state["resource_offers"][
                self.state.turn // self.state.num_players
            ]
            for resource, amount in new_resources.items():
                self.state.game_state["supply"][resource] = \
                    self.state.game_state["supply"].get(resource, 0) + amount

            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1,
                message=f"Added new resources to supply: {self._resources_to_str(new_resources)}"
            )

    def _return_workers(self) -> None:
        """Return all workers from buildings at the start of a round."""
        for building in self.state.game_state["buildings"].values():
            if building["worker"] is not None:
                worker_id = building["worker"]
                building["worker"] = None
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1,
                    message=f"Worker returned from {building['name']} to Player {worker_id}"
                )

    def _is_round_end(self) -> bool:
        """Check if it's the end of a round."""
        return self.state.turn > 0 and \
               self.state.turn % self.state.num_players == 0

    def _accumulate_resources(self) -> None:
        """Accumulate uncollected resources at round end."""
        for resource in self.resource_names:
            if resource in self.state.game_state["supply"] and \
               self.state.game_state["supply"][resource] > 0:
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1,
                    message=f"{self.state.game_state['supply'][resource]} {resource} remained uncollected"
                )

    def _calculate_player_value(self, player_id: int) -> int:
        """Calculate total value for a player including buildings, resources, and loans."""
        value = 0
        resources = self.state.game_state["player_resources"][player_id]
        
        # Add resource values
        for resource, amount in resources.items():
            if resource != "Loan":
                # Add appropriate value for each resource type
                # This would need to be expanded with proper resource values
                value += amount * 1  

        # Subtract loans (each loan is -5 points)
        value -= resources.get("Loan", 0) * 5

        # Add building values
        for building in self.state.game_state["buildings"].values():
            if building.get("owner") == player_id:
                value += building.get("victory_points", 0)

        return value

    def _end_game(self) -> None:
        """Handle game end and determine winner."""
        player_scores = {
            pid: self._calculate_player_value(pid)
            for pid in range(self.state.num_players)
        }

        winner_id = max(player_scores.items(), key=lambda x: x[1])[0]
        self.state.set_winners(
            player_ids=[winner_id],
            reason=f"Player {winner_id} won with {player_scores[winner_id]} points!"
        )

    def _handle_enter_building(self, player_id: int, action: str) -> bool:
        """Handle entering a building."""
        match = self.enter_building_pattern.search(action)
        if not match:
            return False

        building_name = match.group(1).strip()
        if building_name not in self.state.game_state["buildings"]:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[f"Building {building_name} does not exist."]
            )
            return True

        building = self.state.game_state["buildings"][building_name]
        if building["worker"] is not None:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[f"Building {building_name} is occupied."]
            )
            return True

        # Check if player can pay entry fee
        player_resources = self.state.game_state["player_resources"][player_id]
        food_value = sum(qty * self.food_values.get(res, 0) 
                        for res, qty in player_resources.items())

        if (building["entry_fee_food"] > 0 and food_value < building["entry_fee_food"]) or \
           (building["entry_fee_francs"] > 0 and player_resources.get("Franc", 0) < building["entry_fee_francs"]):
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[f"Cannot pay entry fee for {building_name}."]
            )
            return True

        # Pay entry fee and occupy building
        if building["entry_fee_francs"] > 0:
            self.state.game_state["player_resources"][player_id]["Franc"] -= building["entry_fee_francs"]
        
        building["worker"] = player_id
        self.state.game_state["current_building"] = building_name

        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=f"Player {player_id} entered {building_name}."
        )
        return True

    def _handle_take_resources(self, player_id: int, action: str) -> bool:
        """Handle taking resources from supply."""
        match = self.take_resources_pattern.search(action)
        if not match:
            return False

        resource_name = match.group(1).strip()
        if resource_name not in self.resource_names:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[f"Invalid resource: {resource_name}."]
            )
            return True

        if self.state.game_state["supply"].get(resource_name, 0) <= 0:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[f"No {resource_name} available in supply."]
            )
            return True

        # Transfer resource
        self.state.game_state["supply"][resource_name] -= 1
        self.state.game_state["player_resources"][player_id][resource_name] = \
            self.state.game_state["player_resources"][player_id].get(resource_name, 0) + 1

        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=f"Player {player_id} took 1 {resource_name} from supply."
        )
        return True

    def _handle_loans(self, player_id: int, action: str) -> bool:
        """Handle taking or paying loans."""
        take_match = self.take_loan_pattern.search(action)
        pay_match = self.pay_loan_pattern.search(action)
        
        if take_match:
            amount = int(take_match.group(1))
            self.state.game_state["player_resources"][player_id]["Loan"] = \
                self.state.game_state["player_resources"][player_id].get("Loan", 0) + amount
            self.state.game_state["player_resources"][player_id]["Franc"] = \
                self.state.game_state["player_resources"][player_id].get("Franc", 0) + (amount * 4)
            
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1,
                message=f"Player {player_id} took {amount} loan(s)."
            )
            return True
            
        elif pay_match:
            amount = int(pay_match.group(1))
            current_loans = self.state.game_state["player_resources"][player_id].get("Loan", 0)
            current_francs = self.state.game_state["player_resources"][player_id].get("Franc", 0)
            
            if amount > current_loans:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"Player {player_id} doesn't have {amount} loans to repay."]
                )
                return True
                
            if amount * 5 > current_francs:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"Player {player_id} doesn't have enough Francs to repay {amount} loans."]
                )
                return True
                
            self.state.game_state["player_resources"][player_id]["Loan"] -= amount
            self.state.game_state["player_resources"][player_id]["Franc"] -= amount * 5
            
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1,
                message=f"Player {player_id} repaid {amount} loan(s)."
            )
            return True
            
        return False

    def _generate_resource_offers(self) -> list:
        """Generate the sequence of resource offers for the game."""
        basic_offers = [
            {"Wood": 1, "Clay": 1},
            {"Fish": 1, "Grain": 1},
            {"Wood": 1, "Iron": 1},
            {"Clay": 1, "Cattle": 1},
            {"Fish": 1, "Wood": 1},
            {"Grain": 1, "Clay": 1}
        ]
        offers = basic_offers.copy()
        random.shuffle(offers)
        return offers

    def _is_feeding_phase(self) -> bool:
        """Check if it's time for a feeding phase."""
        return self.state.turn > 0 and self.state.turn % 7 == 0

    def _handle_feeding_phase(self) -> None:
        """Handle the feeding phase."""
        for player_id in range(self.state.num_players):
            food_req = self.state.game_state["food_requirement"][player_id]
            resources = self.state.game_state["player_resources"][player_id]
            
            # Calculate available food
            food_value = sum(qty * self.food_values.get(res, 0) 
                           for res, qty in resources.items())
            
            if food_value < food_req:
                # Player must take loans to cover food
                needed_food = food_req - food_value
                loans_needed = (needed_food + 3) // 4  # Round up division
                
                self.state.game_state["player_resources"][player_id]["Loan"] = \
                    resources.get("Loan", 0) + loans_needed
                self.state.game_state["player_resources"][player_id]["Franc"] = \
                    resources.get("Franc", 0) + (loans_needed * 4) - needed_food
                
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1,
                    message=f"Player {player_id} took {loans_needed} loan(s) to pay for food."
                )
            else:
                # Deduct food value from player's resources
                remaining_food = food_req
                for resource in ["Fish", "Bread", "Meat", "Smoked Fish", "Franc"]:
                    if remaining_food <= 0:
                        break


    def _handle_feeding_phase(self) -> None:
        """Handle the feeding phase."""
        for player_id in range(self.state.num_players):
            food_req = self.state.game_state["food_requirement"][player_id]
            resources = self.state.game_state["player_resources"][player_id]
            
            # Calculate available food
            food_value = sum(qty * self.food_values.get(res, 0) 
                           for res, qty in resources.items())
            
            if food_value < food_req:
                # Player must take loans to cover food
                needed_food = food_req - food_value
                loans_needed = (needed_food + 3) // 4  # Round up division
                
                self.state.game_state["player_resources"][player_id]["Loan"] = \
                    resources.get("Loan", 0) + loans_needed
                self.state.game_state["player_resources"][player_id]["Franc"] = \
                    resources.get("Franc", 0) + (loans_needed * 4) - needed_food
                
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1,
                    message=f"Player {player_id} took {loans_needed} loan(s) to pay for food."
                )
            else:
                # Deduct food value from player's resources
                remaining_food = food_req
                for resource in ["Fish", "Bread", "Meat", "Smoked Fish", "Franc"]:
                    if remaining_food <= 0:
                        break
                        
                    available = resources.get(resource, 0)
                    if available > 0:
                        food_per_unit = self.food_values[resource]
                        units_needed = min(
                            available,
                            (remaining_food + food_per_unit - 1) // food_per_unit
                        )
                        
                        resources[resource] -= units_needed
                        remaining_food -= units_needed * food_per_unit
                
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1,
                    message=f"Player {player_id} paid {food_req} food."
                )

            # Increase food requirement for next feeding phase
            self.state.game_state["food_requirement"][player_id] += 1

    def _handle_process(self, player_id: int, action: str) -> bool:
        """Handle processing resources in buildings."""
        match = self.process_pattern.search(action)
        if not match:
            return False

        input_resources = self._parse_resource_list(match.group(1))
        output_resources = self._parse_resource_list(match.group(2))
        
        if not input_resources or not output_resources:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=["Invalid resource format in processing action."]
            )
            return True

        # Check if player is in a building
        if not self.state.game_state["current_building"]:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=["Must be in a building to process resources."]
            )
            return True

        # Check if player has required resources
        player_resources = self.state.game_state["player_resources"][player_id]
        for resource, amount in input_resources.items():
            if player_resources.get(resource, 0) < amount:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"Not enough {resource} to process."]
                )
                return True

        # Process the resources
        for resource, amount in input_resources.items():
            player_resources[resource] -= amount
            
        for resource, amount in output_resources.items():
            player_resources[resource] = player_resources.get(resource, 0) + amount

        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=f"Player {player_id} processed resources: {self._resources_to_str(input_resources)} -> {self._resources_to_str(output_resources)}"
        )
        return True

    def _handle_build(self, player_id: int, action: str) -> bool:
        """Handle building construction."""
        match = self.build_pattern.search(action)
        if not match:
            return False

        building_name = match.group(1).strip()
        if building_name not in self.state.game_state["buildings"]:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[f"Building {building_name} does not exist."]
            )
            return True

        building = self.state.game_state["buildings"][building_name]
        player_resources = self.state.game_state["player_resources"][player_id]

        # Check if player has required resources
        for resource, amount in building["cost"].items():
            if player_resources.get(resource, 0) < amount:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"Not enough {resource} to build {building_name}."]
                )
                return True

        # Pay resources and build
        for resource, amount in building["cost"].items():
            player_resources[resource] -= amount

        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=f"Player {player_id} built {building_name}."
        )
        return True

    def _parse_resource_list(self, resource_str: str) -> Optional[Dict[str, int]]:
        """Parse a string of resources into a dictionary."""
        resources = {}
        items = re.split(r',\s*|\s+and\s+', resource_str.strip())
        
        for item in items:
            if not item:
                continue
            match = re.match(r'^(\d+)\s+(.+)$', item.strip())
            if not match:
                return None
                
            amount = int(match.group(1))
            resource = match.group(2).strip().title()
            
            if resource not in self.resource_names or amount <= 0:
                return None
                
            resources[resource] = resources.get(resource, 0) + amount
            
        return resources

    def _resources_to_str(self, resources: Dict[str, int]) -> str:
        """Convert a resource dictionary to a readable string."""
        return ", ".join(f"{amount} {resource}" for resource, amount in resources.items())

    # def get_current_player_id(self) -> int:
    #     """Get the ID of the current player."""
    #     return self.state.current_player

    def close(self):
        """Clean up any resources."""
        pass