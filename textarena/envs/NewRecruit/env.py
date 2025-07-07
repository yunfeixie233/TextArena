import re, random
from typing import Any, Dict, Optional, Tuple, List

import textarena as ta
from textarena.envs.NewRecruit.renderer import create_board_str


class NewRecruitEnv(ta.Env):
    """
    New Recruit is a 2-player, turn-based negotiation game where players take on the roles of a recruiter and a candidate.
    Each player has preferences regarding 8 issues, with 5 choices per issue and different point values for each choice.
    Players take turns proposing choices for each issue and arguing to convince the other player to accept.
    The game ends when a proposal is accepted or after a maximum number of turns.
    """

    def __init__(self, max_turns: Optional[int] = 10):
        """
        Initialize the New Recruit environment.
        
        Args:
            max_turns (Optional[int]): Maximum number of turns before the game ends.
        """
        self.max_turns = max_turns
        
        # Define regex patterns for parsing player actions
        self.propose_pattern = re.compile(r"\[Propose:?\s*(.*?)\]", re.IGNORECASE | re.DOTALL)
        self.accept_pattern = re.compile(r"\[Accept\]", re.IGNORECASE)
        self.reject_pattern = re.compile(r"\[Reject\]", re.IGNORECASE)
        
        # Define the point value dictionary as provided in the task
        self.point_value_dict = {
            # distributive
            "Salary": {
                "$60,000": [-6000, 0],
                "$58,000": [-4500, -1500],
                "$56,000": [-3000, -3000],
                "$54,000": [-1500, -4500],
                "$52,000": [0, -6000]
            },
            "Signing Bonus": {
                "10%": [0, 4000],
                "8%": [1000, 3000],
                "6%": [2000, 2000],
                "4%": [3000, 1000],
                "2%": [4000, 0]
            },
            # compatible
            "Job Assignment": {
                "Division A": [0, 0],
                "Division B": [-600, -600],
                "Division C": [-1200, -1200],
                "Division D": [-1800, -1800],
                "Division E": [-2400, -2400]
            },
            "Company Car": {
                "LUX EX2": [1200, 1200],
                "MOD 250": [900, 900],
                "RAND XTR": [600, 600],
                "DE PAS 450": [300, 300],
                "PALO LSR": [0, 0]
            },
            # integrative
            "Starting Date": {
                "Jun 1": [1600, 0],
                "Jun 15": [1200, 1000],
                "Jul 1": [800, 2000],
                "Jul 15": [400, 3000],
                "Aug 1": [0, 4000]
            },
            "Vacation Days": {
                "30 days": [0, 1600],
                "25 days": [1000, 1200],
                "20 days": [2000, 800],
                "15 days": [3000, 400],
                "10 days": [4000, 0]
            },
            "Moving Expense Reimbursement": {
                "100%": [0, 3200],
                "90%": [200, 2400],
                "80%": [400, 1600],
                "70%": [600, 800],
                "60%": [800, 0]
            },
            "Insurance Coverage": {
                "Allen Insurance": [0, 800],
                "ABC Insurance": [800, 600],
                "Good Health Insurance": [1600, 400],
                "Best Insurance Co.": [2400, 200],
                "Insure Alba": [3200, 0]
            },
        }
        
        # Define issue categories for reference
        self.issue_categories = {
            "distributive": ["Salary", "Signing Bonus"],
            "compatible": ["Job Assignment", "Company Car"],
            "integrative": ["Starting Date", "Vacation Days", "Moving Expense Reimbursement", "Insurance Coverage"]
        }
        
        # List of all issues
        self.issues = list(self.point_value_dict.keys())

    def get_board_str(self):
        """
        Get the string representation of the game board.
        
        Returns:
            str: The string representation of the game board.
        """
        return create_board_str(
            game_state=self.state.game_state,
            player_id=self.state.current_player_id
        )

    def reset(self, num_players: int, seed: Optional[int] = None):
        """
        Reset the environment to its initial state.
        
        Args:
            num_players (int): Number of players in the game (must be 2).
            seed (Optional[int]): Seed for the random number generator.
        """
        # Initialize the state
        self.state = ta.TwoPlayerState(num_players=num_players, max_turns=self.max_turns, seed=seed)
        
        # Set up the game state
        game_state = {
            "roles": {0: "Recruiter", 1: "Candidate"},
            "current_proposal": None,
            "accepted_proposal": None,
            "proposal_history": [],
            "player_preferences": {
                0: {issue: {choice: self.point_value_dict[issue][choice][0] for choice in self.point_value_dict[issue]} for issue in self.issues},
                1: {issue: {choice: self.point_value_dict[issue][choice][1] for choice in self.point_value_dict[issue]} for issue in self.issues}
            }
        }
        
        # Reset the state with the game state and player prompt function
        self.state.reset(game_state=game_state, player_prompt_function=self._prompt)

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """
        Process a single step in the environment.
        
        Args:
            action (str): The action taken by the current player.
            
        Returns:
            Tuple[bool, ta.Info]: A tuple containing whether the episode has concluded and additional information.
        """
        # Add the player's action to the observations
        self.state.add_observation(
            from_id=self.state.current_player_id,
            message=action,
            observation_type=ta.ObservationType.PLAYER_ACTION
        )
        
        # Process the action
        self._process_action(action)
        
        # Check if the game should end due to turn limit
        if self.state.check_turn_limit():
            self._end_game_with_zero_points("Maximum number of turns reached without an accepted proposal.")
        
        # Step the state
        return self.state.step()

    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """
        Generate the prompt for a player.
        
        Args:
            player_id (int): The ID of the player.
            game_state (Dict[str, Any]): The current game state.
            
        Returns:
            str: The prompt for the player.
        """
        role = game_state["roles"][player_id]
        opponent_role = game_state["roles"][1 - player_id]
        
        # Create a string representation of the player's preferences
        preferences_str = ""
        for issue in self.issues:
            preferences_str += f"\n{issue}:\n"
            for choice, choices_dict in self.point_value_dict[issue].items():
                points = choices_dict[player_id]
                preferences_str += f"  - {choice}: {points} points\n"
        
        # Create the prompt
        prompt = (
            f"You are the {role} in the New Recruit negotiation game.\n\n"
            f"Your preferences for each issue are as follows (higher points are better):{preferences_str}\n"
            f"You are negotiating with the {opponent_role}. You can only see your own preferences, not theirs.\n\n"
            "Available actions:\n"
            "  - [Propose: choice1 for issue1, choice2 for issue2, ...]: Make a proposal for all issues.\n"
            "  - [Accept]: Accept the current proposal.\n"
            "  - [Reject]: Reject the current proposal.\n\n"
            f"The game will end after {self.max_turns} turns if no proposal is accepted, resulting in 0 points for both players.\n"
            "Your goal is to maximize your points by negotiating effectively."
        )
        
        # Add information about the current proposal if there is one
        if game_state["current_proposal"]:
            proposer_id = game_state["current_proposal"]["proposer_id"]
            proposer_role = game_state["roles"][proposer_id]
            proposal_str = self._proposal_to_str(game_state["current_proposal"]["choices"])
            prompt += f"\n\nCurrent proposal from {proposer_role}:\n{proposal_str}\n"
            prompt += "You can [Accept] or [Reject] this proposal."
        
        return prompt

    def _process_action(self, action: str):
        """
        Process a player's action.
        
        Args:
            action (str): The action taken by the current player.
        """
        current_player_id = self.state.current_player_id
        game_state = self.state.game_state
        
        # Check if the player is accepting a proposal
        if game_state["current_proposal"] and self.accept_pattern.search(action):
            self._accept_proposal()
            return
        
        # Check if the player is rejecting a proposal
        if game_state["current_proposal"] and self.reject_pattern.search(action):
            self._reject_proposal()
            return
        
        # Check if the player is making a new proposal
        propose_match = self.propose_pattern.search(action)
        if propose_match:
            proposal_text = propose_match.group(1).strip()
            parsed_proposal = self._parse_proposal(proposal_text)
            
            if parsed_proposal:
                # Create the proposal
                game_state["current_proposal"] = {
                    "proposer_id": current_player_id,
                    "choices": parsed_proposal
                }
                
                # Add to proposal history
                game_state["proposal_history"].append({
                    "proposer_id": current_player_id,
                    "choices": parsed_proposal,
                    "accepted": False
                })
                
                # Add observation about the new proposal
                self.state.add_observation(
                    message=f"Player {current_player_id} ({game_state['roles'][current_player_id]}) made a new proposal.",
                    observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
                )
            else:
                # Invalid proposal format
                self.state.set_invalid_move(reason="Invalid proposal format. Please use the format [Propose: choice1 for issue1, choice2 for issue2, ...]")
        else:
            # No valid action found
            self.state.add_observation(
                message=f"Player {current_player_id} ({game_state['roles'][current_player_id]}) did not make a valid action.",
                observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
            )

    def _parse_proposal(self, proposal_text: str) -> Optional[Dict[str, str]]:
        """
        Parse a proposal text into a dictionary mapping issues to choices.
        
        Args:
            proposal_text (str): The proposal text to parse.
            
        Returns:
            Optional[Dict[str, str]]: A dictionary mapping issues to choices, or None if parsing fails.
        """
        try:
            # Initialize the proposal dictionary
            proposal = {}
            
            # Debug: Print the proposal text
            print(f"Parsing proposal: {proposal_text}")
            
            # Special handling for salary with commas
            # Replace $XX,XXX with $XXXXX to avoid splitting on the comma
            proposal_text = re.sub(r'\$(\d+),(\d+)', r'$\1\2', proposal_text)
            
            # Split the proposal text by commas
            parts = [part.strip() for part in proposal_text.split(',')]
            
            # Debug: Print the parts
            print(f"Parts after preprocessing: {parts}")
            
            # Process each part
            for part in parts:
                print(f"Processing part: '{part}'")
                
                # Try to match "choice for issue" pattern
                match = re.match(r"(.*?)\s+for\s+(.*)", part)
                if match:
                    choice, issue = match.groups()
                    choice = choice.strip()
                    issue = issue.strip()
                    
                    print(f"Matched 'choice for issue' pattern: choice='{choice}', issue='{issue}'")
                    
                    # Special handling for salary - add the comma back
                    if issue == "Salary" and choice.startswith("$") and len(choice) > 3:
                        # Add comma back for display
                        dollars = choice[1:]  # Remove $
                        if len(dollars) > 3:
                            choice = f"${dollars[:-3]},{dollars[-3:]}"
                    
                    # Check if the issue exists (case-insensitive)
                    issue_match = None
                    for i in self.issues:
                        if i.lower() == issue.lower():
                            issue_match = i
                            break
                    
                    if issue_match is None:
                        print(f"Issue '{issue}' not found in issues: {self.issues}")
                        return None
                    
                    # Use the correctly cased issue name
                    issue = issue_match
                    
                    # Check if the choice exists for this issue
                    if choice not in self.point_value_dict[issue]:
                        print(f"Choice '{choice}' not found in choices for issue '{issue}': {list(self.point_value_dict[issue].keys())}")
                        return None
                    
                    # Add to the proposal
                    proposal[issue] = choice
                    print(f"Added to proposal: {issue} -> {choice}")
                else:
                    # Try to match "issue: choice" pattern
                    match = re.match(r"(.*?):\s*(.*)", part)
                    if match:
                        issue, choice = match.groups()
                        issue = issue.strip()
                        choice = choice.strip()
                        
                        print(f"Matched 'issue: choice' pattern: issue='{issue}', choice='{choice}'")
                        
                        # Special handling for salary - add the comma back
                        if issue == "Salary" and choice.startswith("$") and len(choice) > 3:
                            # Add comma back for display
                            dollars = choice[1:]  # Remove $
                            if len(dollars) > 3:
                                choice = f"${dollars[:-3]},{dollars[-3:]}"
                        
                        # Check if the issue exists (case-insensitive)
                        issue_match = None
                        for i in self.issues:
                            if i.lower() == issue.lower():
                                issue_match = i
                                break
                        
                        if issue_match is None:
                            print(f"Issue '{issue}' not found in issues: {self.issues}")
                            return None
                        
                        # Use the correctly cased issue name
                        issue = issue_match
                        
                        # Check if the choice exists for this issue
                        if choice not in self.point_value_dict[issue]:
                            print(f"Choice '{choice}' not found in choices for issue '{issue}': {list(self.point_value_dict[issue].keys())}")
                            return None
                        
                        # Add to the proposal
                        proposal[issue] = choice
                        print(f"Added to proposal: {issue} -> {choice}")
                    else:
                        # Could not parse this part
                        print(f"Could not parse part: '{part}'")
                        return None
            
            # Check if all issues are covered
            if set(proposal.keys()) != set(self.issues):
                print(f"Not all issues are covered. Proposal keys: {set(proposal.keys())}, Issues: {set(self.issues)}")
                return None
            
            print(f"Final proposal: {proposal}")
            return proposal
        except Exception as e:
            print(f"Exception during parsing: {e}")
            return None

    def _proposal_to_str(self, proposal: Dict[str, str]) -> str:
        """
        Convert a proposal dictionary to a string representation.
        
        Args:
            proposal (Dict[str, str]): The proposal dictionary.
            
        Returns:
            str: The string representation of the proposal.
        """
        return "\n".join([f"- {issue}: {choice}" for issue, choice in proposal.items()])

    def _accept_proposal(self):
        """
        Accept the current proposal and end the game.
        """
        game_state = self.state.game_state
        current_proposal = game_state["current_proposal"]
        
        if current_proposal:
            # Mark the proposal as accepted
            for i, proposal in enumerate(game_state["proposal_history"]):
                if (proposal["proposer_id"] == current_proposal["proposer_id"] and 
                    proposal["choices"] == current_proposal["choices"]):
                    game_state["proposal_history"][i]["accepted"] = True
                    break
            
            game_state["accepted_proposal"] = current_proposal
            
            # Calculate scores
            recruiter_score = self._calculate_score(0, current_proposal["choices"])
            candidate_score = self._calculate_score(1, current_proposal["choices"])
            
            # Add observation about the accepted proposal
            self.state.add_observation(
                message=f"Player {self.state.current_player_id} ({game_state['roles'][self.state.current_player_id]}) accepted the proposal.",
                observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
            )
            
            # Set the winner based on scores
            if recruiter_score > candidate_score:
                self.state.set_winner(player_id=0, reason=f"Recruiter wins with {recruiter_score} points vs Candidate's {candidate_score} points.")
            elif candidate_score > recruiter_score:
                self.state.set_winner(player_id=1, reason=f"Candidate wins with {candidate_score} points vs Recruiter's {recruiter_score} points.")
            else:
                self.state.set_draw(reason=f"Draw with both players scoring {recruiter_score} points.")

    def _reject_proposal(self):
        """
        Reject the current proposal and continue the game.
        """
        game_state = self.state.game_state
        
        # Add observation about the rejected proposal
        self.state.add_observation(
            message=f"Player {self.state.current_player_id} ({game_state['roles'][self.state.current_player_id]}) rejected the proposal.",
            observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
        )
        
        # Clear the current proposal
        game_state["current_proposal"] = None

    def _calculate_score(self, player_id: int, proposal: Dict[str, str]) -> int:
        """
        Calculate the score for a player based on a proposal.
        
        Args:
            player_id (int): The ID of the player.
            proposal (Dict[str, str]): The proposal dictionary.
            
        Returns:
            int: The score for the player.
        """
        score = 0
        for issue, choice in proposal.items():
            score += self.point_value_dict[issue][choice][player_id]
        return score

    def _end_game_with_zero_points(self, reason: str):
        """
        End the game with zero points for both players.
        
        Args:
            reason (str): The reason for ending the game.
        """
        self.state.set_draw(reason=reason)
        self.state.rewards = {0: 0, 1: 0}
