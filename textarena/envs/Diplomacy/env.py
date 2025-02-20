import re
import random
from typing import Any, Dict, Optional, Tuple, List, Set
import textarena as ta
from textarena.envs.Diplomacy.game_engine import DiplomacyGameEngine

class DiplomacyEnv(ta.Env):
    """Environment for Diplomacy with negotiation support"""
    broadcast_pattern = re.compile(
        r"(?:"
        r"\s*\[Broadcast\s*:\s*(.*?)\]"            # [Broadcast: message]
        r"|"
        r"\s*\[Broadcast((?:\s+).*?)\]"            # [Broadcast message]
        r"|"
        r"\s*\[Broadcast\](\s+.*?)(?=\s*\[|$)"     # [Broadcast] message
        r")",
        re.IGNORECASE | re.DOTALL
    )
    
    # Whisper to another player
    whisper_pattern = re.compile(
        r"\s*\[Whisper\s+(?:to\s+)?(?:Player\s+)?(\d+)(?:\s+\(([A-Z]+)\))?\s*:\s*(.*?)\]",
        re.IGNORECASE | re.DOTALL
    )
    
    # Submit orders for the current phase
    submit_orders_pattern = re.compile(
        r"\[Submit\s+Orders\]([\s\S]*?)(?=\[|$)",
        re.IGNORECASE
    )

    def __init__(self, max_turns: int = 30, 
                negotiations_per_phase: int = 3):
        """
        Initialize the Diplomacy game environment

        Args:
            max_turns (int): Maximum number of game years before ending in a draw
            negotiations_per_phase (int): How many negotiation rounds per game phase
        """
        self.max_turns = max_turns
        self.negotiations_per_phase = negotiations_per_phase
        
        # Game state
        self.engine = None
        self.player_power_map = {}
        self.power_player_map = {}
        self.current_negotiation_round = 0
        self.orders_submitted = set()  # Track which players submitted orders
        self.pending_orders = {}       # Store orders until processing
        self.current_season = None
        self.current_year = None
        self.current_phase = None
        

    def reset(self, num_players: int, seed: Optional[int] = None):
        """ Reset the environment and start a new game """
        self.state = ta.State(num_players=num_players, min_players=3, max_players=7)
        
        # Initialize game engine
        self.engine = DiplomacyGameEngine(max_turns=self.max_turns)
        self.player_power_map = self.engine.setup_game(num_players)
        self.power_player_map = {power: player for player, power in self.player_power_map.items()}
        
        # Reset game state tracking
        self.current_negotiation_round = 0
        self.orders_submitted = set()
        self.pending_orders = {}
        self.current_season = self.engine.season
        self.current_year = self.engine.year
        self.current_phase = self.engine.phase
        self.offers = {}
        self.next_offer_id = 1
        self.agreements = {}
        
        # Initialize game state for players
        game_state = self.engine.get_state()
        game_state['player_power_map'] = self.player_power_map
        game_state['powers_info'] = {power: {
            'home_centers': self.engine.powers[power].home_centers,
            'controlled_centers': self.engine.powers[power].controlled_centers,
            'units': [str(unit) for unit in self.engine.powers[power].units],
        } for power in self.player_power_map.values()}
        game_state['current_negotiation_round'] = 0
        game_state['total_negotiation_rounds'] = self.negotiations_per_phase
        
        input(self.engine.get_ascii_map())

        # Initialize the state
        self.state.reset(
            seed=seed, 
            game_state=game_state, 
            role_mapping=self.player_power_map,
            player_prompt_function=self._generate_player_prompt
        )
        
        # Send initial game state announcement to all players
        self._announce_game_state()
        
        return self.state

    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """
        Generate a comprehensive prompt for the player at the beginning of the game
        
        Args:
            player_id (int): ID of the player
            game_state (Dict): Current game state
                
        Returns:
            str: Prompt for the player
        """
        power_name = game_state['player_power_map'].get(player_id)
        if not power_name:
            return "You are not an active player in this game."
            
        power_state = game_state['powers_info'].get(power_name, {})
        
        # Build the comprehensive prompt
        prompt = [
            f"# DIPLOMACY GAME - YOU ARE {power_name} (PLAYER {player_id})",
            "",
            "## GAME OVERVIEW",
            "Diplomacy is a strategic board game of negotiation, alliance-building, and tactical warfare set in pre-WWI Europe.",
            "The game revolves around diplomatic relations, military maneuvers, and territorial control.",
            "",
            "### GAME STRUCTURE",
            "- Each game year consists of Spring and Fall seasons, plus a Winter adjustment phase",
            "- Each season has a Movement phase and possibly a Retreat phase",
            "- After Fall, there's an Adjustment phase where you build new units or disband excess units",
            "- The game lasts until one power controls 18+ supply centers or until the maximum number of turns",
            f"- This game will last at most {self.max_turns} years",
            "",
            "### YOUR OBJECTIVE",
            "To win, you must control the majority of supply centers (currently 18 out of 34). This requires:",
            "1. Forming strategic alliances with other powers",
            "2. Coordinating attacks against common enemies",
            "3. Eventually outmaneuvering your allies to claim victory",
            "",
            "## YOUR POWER: " + power_name,
            f"Starting position: {', '.join(power_state.get('units', []))}",
            f"Home supply centers: {', '.join(power_state.get('home_centers', []))}",
            f"Currently controlled centers: {', '.join(power_state.get('controlled_centers', []))}",
            "",
            "## OTHER POWERS"
        ]
        
        for other_power, other_player_id in self.power_player_map.items():
            if other_power != power_name:
                other_info = game_state['powers_info'].get(other_power, {})
                prompt.append(
                    f"- Player {other_player_id} ({other_power}): "
                    f"{len(other_info.get('units', []))} units, "
                    f"{len(other_info.get('controlled_centers', []))} supply centers"
                )
        
        prompt.extend([
            "",
            "## GAME MECHANICS",
            "",
            "### UNITS",
            "- Armies (A): Move on land, can be convoyed across water by fleets",
            "- Fleets (F): Move on water and coastal provinces, can convoy armies",
            "",
            "### ORDERS",
            "During Movement phases, you can issue these orders:",
            "- Hold: A unit stays in place (e.g., 'A PAR H')",
            "- Move: A unit moves to an adjacent territory (e.g., 'A PAR - BUR')",
            "- Support: A unit supports another unit's position or move (e.g., 'A PAR S A MAR' or 'A PAR S A MAR - BUR')",
            "- Convoy: A fleet transports an army across water (e.g., 'F NTH C A LON - BEL')",
            "",
            "During Retreat phases, you can:",
            "- Retreat: Move a dislodged unit to an empty adjacent territory (e.g., 'A PAR R BUR')",
            "- Disband: Remove a dislodged unit from play (e.g., 'A PAR D')",
            "",
            "During Adjustment phases, depending on your center count vs. unit count:",
            "- Build: Create new units in your unoccupied home centers (e.g., 'A PAR B')",
            "- Disband: Remove existing units if you have too many (e.g., 'A PAR D')",
            "- Waive: Choose not to build an allowed unit (e.g., 'WAIVE')",
            "",
            "### COMBAT RESOLUTION",
            "- All units have equal strength (1)",
            "- Support adds +1 strength per supporting unit",
            "- The unit with highest strength wins; equal strength units bounce (no movement)",
            "- A unit supporting a move is cut if attacked (unless the attack comes from the unit being supported)",
            "- A dislodged unit must retreat or be disbanded",
            "",
            f"## NEGOTIATION PROCESS ({self.negotiations_per_phase} ROUNDS PER PHASE)",
            f"Each game phase has {self.negotiations_per_phase} negotiation rounds before orders are submitted.",
            "Use these rounds to coordinate with other players through messages and form agreements.",
            "In the final negotiation round, you must submit your orders.",
            "",
            "## COMMUNICATION OPTIONS",
            "You can interact in the following ways:",
            "",
            "1. **Broadcast messages** - Send a message to all players",
            "   Example: [Broadcast: I propose we all focus on containing Russia this turn]",
            "   Alternative: [Broadcast] Let's coordinate our attacks against Turkey",
            "",
            "2. **Whisper messages** - Send a private message to another player",
            "   Example: [Whisper to 2: Would you be interested in coordinating against Germany?]",
            "   Alternative: [Whisper to 3 (ITALY): I can support your move to Trieste]",
            "",
            "3. **Submit orders** (final negotiation round only) - Send your orders for the current phase",
            "   Example:",
            "   ```",
            "   [Submit Orders]",
            "   A PAR - BUR",
            "   A MAR S A PAR - BUR",
            "   F BRE - MAO",
            "   ```",
            "",
            "You can combine multiple communication types in a single response:",
            "",
            "```",
            "[Broadcast: I'm looking to form alliances this turn]",
            "",
            "[Whisper to 1: I noticed England is threatening your northern border. I could help you against them if you agree not to attack me.]",
            "",
            "[Whisper to 3: Let's coordinate our fleets in the Mediterranean]",
            "```",
            "",
            "## STRATEGY TIPS",
            "1. Diplomacy is primarily a game of negotiation - communicate actively",
            "2. Form mutually beneficial alliances, but be prepared to break them when necessary",
            "3. Try to coordinate attacks with allies to ensure successful movements",
            "4. Defend your supply centers while looking for opportunities to capture others",
            "5. Balance short-term tactical gains with long-term strategic positioning",
            "",
            "## CURRENT GAME STATE",
            f"It is {game_state['season']} {game_state['year']}, {game_state['phase']} phase.",
            f"This is negotiation round 1 of {game_state['total_negotiation_rounds']}.",
            "",
            "The game has just begun. Use this first negotiation round to establish initial diplomacy.",
            "",
            "Good luck, and may your diplomacy be successful!"
        ])
        
        return "\n".join(prompt)

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """
        Process player actions
        
        Args:
            action (str): Player's action as a multi-line string
            
        Returns:
            Tuple[bool, ta.Info]: Game completion status and additional info
        """
        current_pid = self.state.current_player
        power_name = self.player_power_map.get(current_pid)
        
        if not power_name:
            self._rotate_current_player()
            return False, ta.Info()
        
        # Always add the player's full action as an observation to themselves
        self.state.add_observation(from_id=current_pid, to_id=current_pid, message=action)
        
        # Process communications and orders
        game_state_changed = self._process_player_action(current_pid, power_name, action)
        
        if game_state_changed:
            # Check if game is over
            game_completed = self.engine.game_over
            if game_completed:
                self._announce_game_result()
                return True, ta.Info()
                
        # Move to next player or negotiate a new round
        self._rotate_current_player()
        
        # If we've completed a full round of negotiations
        if self.state.current_player == 0 and not game_state_changed:
            self._advance_negotiation_round()
            
        return False, ta.Info()

    def _process_player_action(self, player_id: int, power_name: str, action: str) -> bool:
        """
        Process a player's action string, extracting communications and orders
        
        Args:
            player_id (int): The player ID
            power_name (str): The power name
            action (str): The action string
            
        Returns:
            bool: True if game state was changed (orders processed)
        """
        game_state_changed = False
        
        # Process broadcasts
        for match in self.broadcast_pattern.finditer(action):
            message = match.group(1) or match.group(2) or match.group(3)
            if message:
                # broadcast to all 
                self.state.add_observation(from_id=player_id, to_id=-1, message=message)

        
        # Process whispers
        for match in self.whisper_pattern.finditer(action):
            target_id = int(match.group(1))
            target_power = match.group(2)
            message = match.group(3)
            
            # Validate target_power if provided
            if target_power and self.player_power_map.get(target_id) != target_power:
                continue
            
            # add observation to the whisperee
            self.state.add_observation(from_id=player_id, to_id=target_id, message=message)
        
     
        # Process order submission
        if self.current_negotiation_round == self.negotiations_per_phase - 1:
            for match in self.submit_orders_pattern.finditer(action):
                orders_text = match.group(1).strip()
                if orders_text:
                    self._handle_orders_submission(player_id, power_name, orders_text)
            
            # Check if all players have submitted orders and it's time to process them
            if len(self.orders_submitted) == len(self.player_power_map):
                game_state_changed = self._process_orders()
        
        return game_state_changed



    def _handle_orders_submission(self, player_id: int, power_name: str, orders_text: str):
        """Handle order submission from a player"""
        # Parse orders line by line
        orders = [line.strip() for line in orders_text.split('\n') 
                 if line.strip() and not line.strip().startswith('#')]
        
        # Store pending orders and mark player as submitted
        self.pending_orders[power_name] = orders
        self.orders_submitted.add(player_id)
        
        # Notify player their orders were received
        msg = f"[Orders received for {power_name} ({len(orders)} orders)]"
        self.state.add_observation(from_id=ta.GAME_ID, to_id=player_id, message=msg)

    def _process_orders(self) -> bool:
        """Process all submitted orders"""
        # Submit orders to the engine
        phase_changed, new_state = self.engine.resolve_orders(self.pending_orders)
        
        # Update game state
        new_state['player_power_map'] = self.player_power_map
        self.state.game_state = new_state
        
        # Update phase tracking
        self.current_season = self.engine.season
        self.current_year = self.engine.year
        self.current_phase = self.engine.phase
        
        # Announce results to all players
        self._announce_order_results()
        
        # Reset for next phase
        self.orders_submitted = set()
        self.pending_orders = {}
        self.current_negotiation_round = 0
        
        # Update game state
        self.state.game_state['current_negotiation_round'] = 0
        
        return True

    def _advance_negotiation_round(self):
        """Advance to the next negotiation round"""
        self.current_negotiation_round += 1
        self.state.game_state['current_negotiation_round'] = self.current_negotiation_round
        
        # Notify all players about the new negotiation round
        if self.current_negotiation_round < self.negotiations_per_phase:
            message=(f"[Negotiation Round {self.current_negotiation_round + 1} of "
                       f"{self.negotiations_per_phase} begins]")
            self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message)
                
            # If this is the final round, notify players to submit orders
            if self.current_negotiation_round == self.negotiations_per_phase - 1:
                message="[Final negotiation round: Please submit your orders]"
                self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message)
        else:
            # Force order processing if we've somehow exceeded max rounds
            if self.pending_orders:
                self._process_orders()


    def _announce_game_state(self):
        """Announce the current game state to all players"""
        phase_type = self.engine.phase.value
        season = self.engine.season.value
        year = self.engine.year
        
        # Create announcement message
        announcement = (
            f"===== {season} {year} {phase_type} Phase Begins =====\n"
            f"Current supply center counts:\n"
        )
        
        # Add supply center counts for each power
        for power_name, player_id in self.power_player_map.items():
            centers = len(self.engine.powers[power_name].controlled_centers)
            units = len(self.engine.powers[power_name].units)
            announcement += f"- Player {player_id} ({power_name}): {centers} centers, {units} units\n"
        
        # Send to all players
        for player_id in self.player_power_map.keys():
            self.state.add_observation(from_id=ta.GAME_ID, to_id=player_id, message=announcement)

    def _announce_order_results(self):
        """Announce order results to all players"""
        # Create basic announcement
        base_announcement = (
            f"===== Order Results: {self.current_season.value} {self.current_year} =====\n"
        )
        
        # Create individualized announcements with detailed results
        for player_id, power_name in self.player_power_map.items():
            power_announcement = base_announcement
            
            # Add own orders and results
            if power_name in self.pending_orders:
                power_announcement += f"\nYour orders ({power_name}):\n"
                for order in self.pending_orders[power_name]:
                    power_announcement += f"- {order}\n"
            
            # Add public information about other powers' orders
            power_announcement += "\nOther powers' orders:\n"
            for other_power, orders in self.pending_orders.items():
                if other_power != power_name:
                    power_announcement += f"\n{other_power}:\n"
                    for order in orders:
                        power_announcement += f"- {order}\n"
            
            # Send to player
            self.state.add_observation(from_id=ta.GAME_ID, to_id=player_id, message=power_announcement)
        
        # Announce new phase
        self._announce_game_state()

    def _announce_game_result(self):
        """Announce the game result to all players"""
        if self.engine.winners:
            # Victory announcement
            winners_text = ", ".join(self.engine.winners)
            winning_players = [self.power_player_map[power] for power in self.engine.winners]
            winning_players_text = ", ".join(f"Player {pid}" for pid in winning_players)
            
            reason = (
                f"Victory achieved by: {winners_text} ({winning_players_text})\n\n"
                f"Final supply center counts:\n"
            )
            self.state.set_winners(player_ids=winning_players, reason=reason)
        else:
            # Draw announcement
            reason = (
                f"Game ended in a DRAW after {self.engine.turn_number} turns.\n\n"
                f"Final supply center counts:\n"
            )
            self.state.set_draw(reason=reason)
        
        # # Add final supply center counts
        # for power_name, player_id in self.power_player_map.items():
        #     if power_name in self.engine.powers:
        #         centers = len(self.engine.powers[power_name].controlled_centers)
        #         announcement += f"- Player {player_id} ({power_name}): {centers} centers\n"
        
        # # Add game history summary
        # announcement += "\nGame Summary:\n"
        # for entry in self.engine.history:
        #     announcement += f"- {entry['phase']}\n"
        
        # # Send to all players
        # for player_id in self.player_power_map.keys():
        #     self.state.add_observation(from_id=ta.GAME_ID, to_id=player_id, message=announcement)