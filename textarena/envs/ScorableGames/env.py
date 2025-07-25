import os
import re
import random
from typing import Any, Dict, List, Optional, Tuple

import textarena as ta
from .renderer import (
    render_current_deal, render_player_scores, render_negotiation_summary,
    render_voting_status, render_game_issues
)


class ScorableGamesEnv(ta.Env):
    """
    Multi-player negotiation environment based on LLM-Deliberation research.
    Players negotiate over multiple issues with private scoring functions.
    """
    
    def __init__(self, game_config: str = "base", max_rounds: int = 24, 
                 invalid_action_default: str = "ACCEPT"):
        """
        Initialize the ScorableGames environment.
        
        Args:
            game_config: Name of game configuration folder in games_descriptions/
            max_rounds: Maximum number of negotiation rounds
            invalid_action_default: Default vote for invalid actions ("ACCEPT" or "REJECT")
        """
        self.game_config = game_config
        self.max_rounds = max_rounds
        self.invalid_action_default = invalid_action_default
        
        # Validate parameters
        assert invalid_action_default in ["ACCEPT", "REJECT"], \
            "invalid_action_default must be 'ACCEPT' or 'REJECT'"
        
        # Game configuration data
        self.game_dir = os.path.join(os.path.dirname(__file__), "games_descriptions", game_config)
        self.global_instructions = ""
        self.issues = {}  # Issue definitions and options
        self.player_configs = {}  # Player configurations from config.txt
        self.player_scores = {}  # Private scoring functions
        self.player_instructions = {}  # Individual instructions
        
        # Game state
        self.current_deal = {}  # Current deal proposal
        self.negotiation_history = []  # History of actions
        self.player_votes = {}  # Current round votes
        self.valid_actions_this_round = set()  # Players with valid actions
        
    def reset(self, num_players: int, seed: Optional[int] = None):
        """Reset the environment to initial state."""
        # Load game configuration
        self._load_game_configuration()
        
        # Validate number of players matches config
        if len(self.player_configs) != num_players:
            raise ValueError(f"Game config expects {len(self.player_configs)} players, got {num_players}")
        
        # Initialize TextArena state
        self.state = ta.State(
            num_players=num_players,
            max_turns=self.max_rounds,
            seed=seed
        )
        
        # Initialize game state
        game_state = {
            "current_deal": {},
            "negotiation_history": [],
            "player_votes": {},
            "valid_actions_this_round": set(),
            "round_number": 0,
            "voting_phase": False,
            "deal_accepted": False
        }
        
        self.state.standard_resets(
            game_state=game_state,
            player_prompt_function=self._generate_player_prompt
        )
        
        # Reset instance variables
        self.current_deal = {}
        self.negotiation_history = []
        self.player_votes = {}
        self.valid_actions_this_round = set()
    
    def _load_game_configuration(self):
        """Load game configuration from files."""
        if not os.path.exists(self.game_dir):
            raise FileNotFoundError(f"Game configuration directory not found: {self.game_dir}")
        
        # Load global instructions
        global_file = os.path.join(self.game_dir, "global_instructions.txt")
        with open(global_file, 'r') as f:
            self.global_instructions = f.read().strip()
        
        # Parse issues from global instructions
        self._parse_issues_from_global_instructions()
        
        # Load player configurations
        config_file = os.path.join(self.game_dir, "config.txt")
        self._load_player_configurations(config_file)
        
        # Load player scores and instructions
        self._load_player_data()
    
    def _parse_issues_from_global_instructions(self):
        """Parse issue definitions from global instructions."""
        self.issues = {}
        
        # Find all issues (Issue A:, Issue B:, etc.)
        issue_pattern = r'Issue ([A-Z]):\s*"([^"]+)"(.*?)(?=Issue [A-Z]:|$)'
        matches = re.findall(issue_pattern, self.global_instructions, re.DOTALL)
        
        for issue_key, issue_name, content in matches:
            # Parse options (A1, A2, etc.)
            option_pattern = rf'{issue_key}(\d+)\s*"([^"]+)":\s*([^.]+\.)'
            option_matches = re.findall(option_pattern, content)
            
            options = {}
            for option_num, option_name, option_desc in option_matches:
                option_key = f"{issue_key}{option_num}"
                options[option_key] = f"{option_name}: {option_desc.strip()}"
            
            self.issues[issue_key] = {
                "name": issue_name,
                "options": options
            }
    
    def _load_player_configurations(self, config_file: str):
        """Load player configurations from config.txt."""
        self.player_configs = {}
        
        with open(config_file, 'r') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = [part.strip() for part in line.split(',')]
                if len(parts) != 5:
                    raise ValueError(f"Invalid config line {line_num + 1}: {line}")
                
                agent_name, file_name, role, incentive, model = parts
                player_id = len(self.player_configs)
                
                self.player_configs[player_id] = {
                    "agent_name": agent_name,
                    "file_name": file_name,
                    "role": role,
                    "incentive": incentive,
                    "model": model
                }
    
    def _load_player_data(self):
        """Load player scores and individual instructions."""
        self.player_scores = {}
        self.player_instructions = {}
        
        for player_id, config in self.player_configs.items():
            file_name = config["file_name"]
            incentive = config["incentive"]
            
            # Load scores
            scores_file = os.path.join(self.game_dir, "scores_files", f"{file_name}.txt")
            self.player_scores[player_id] = self._load_player_scores(scores_file)
            
            # Load individual instructions
            instructions_file = os.path.join(
                self.game_dir, "individual_instructions", incentive, f"{file_name}.txt"
            )
            with open(instructions_file, 'r') as f:
                self.player_instructions[player_id] = f.read().strip()
    
    def _load_player_scores(self, scores_file: str) -> Dict[str, Dict[str, int]]:
        """Load player scoring function from scores file."""
        scores = {}
        
        with open(scores_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        # Map lines to issues (A, B, C, etc.)
        issue_keys = sorted(self.issues.keys())
        
        for i, line in enumerate(lines[:-1]):  # Last line is threshold
            if i < len(issue_keys):
                issue_key = issue_keys[i]
                score_values = [int(x.strip()) for x in line.split(',')]
                
                # Map scores to options (A1, A2, etc.)
                issue_options = sorted(self.issues[issue_key]["options"].keys())
                issue_scores = {}
                
                for j, score in enumerate(score_values):
                    if j < len(issue_options):
                        option_key = issue_options[j]
                        issue_scores[option_key] = score
                
                scores[issue_key] = issue_scores
        
        # Store minimum threshold
        if lines:
            scores["threshold"] = int(lines[-1])
        
        return scores
    
    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """Generate initial prompt for a player."""
        config = self.player_configs[player_id]
        agent_name = config["agent_name"]
        
        # Replace agent name in global instructions
        global_text = self.global_instructions.replace(f'"{agent_name}"', f'"{agent_name}" (represented by you)')
        
        # Get individual instructions with scores filled in
        individual_text = self._fill_scores_in_instructions(player_id)
        
        # Game rules and actions
        rules_text = f"""

GAME RULES:
- This is a {self.state.num_players}-player negotiation game with {self.max_rounds} rounds maximum.
- You must negotiate to reach an agreement on all issues.
- Your goal is to maximize your total score from the final deal.

AVAILABLE ACTIONS:
- PROPOSE: A1,B2,C3,D1,E4 - Propose a complete deal (specify all issues)
- ACCEPT - Accept the current proposal
- REJECT - Reject the current proposal  
- DISCUSS: [your message] - Make a statement or argument

SCORING:
- You can see your own scores for different options below.
- Other players have different preferences (hidden from you).
- Your minimum acceptable score is {self.player_scores[player_id].get('threshold', 0)} points.

IMPORTANT:
- You must propose complete deals covering all issues.
- Invalid actions will default to {self.invalid_action_default}.
- The game ends when a deal is accepted by majority or max rounds reached.
"""
        
        # Show available issues
        issues_text = "\n" + render_game_issues(self.issues)
        
        # Show player's private scores
        if self.current_deal:
            scores_text = "\n" + render_player_scores(
                self.player_scores[player_id], self.current_deal, agent_name
            )
        else:
            scores_text = f"\n{agent_name}'s Private Scoring Function:\n"
            scores_text += "=" * 40 + "\n"
            for issue_key, issue_scores in self.player_scores[player_id].items():
                if issue_key != "threshold":
                    scores_text += f"{issue_key}: {issue_scores}\n"
        
        return global_text + "\n" + individual_text + rules_text + issues_text + scores_text
    
    def _fill_scores_in_instructions(self, player_id: int) -> str:
        """Fill score placeholders in individual instructions."""
        instructions = self.player_instructions[player_id]
        scores = self.player_scores[player_id]
        
        # Replace score placeholders like #A1_NUM, #A_MAX_NUM, etc.
        for issue_key, issue_scores in scores.items():
            if issue_key == "threshold":
                continue
                
            # Replace individual option scores
            for option_key, score in issue_scores.items():
                placeholder = f"#{option_key}_NUM"
                instructions = instructions.replace(placeholder, str(score))
            
            # Replace max score for issue
            max_score = max(issue_scores.values()) if issue_scores else 0
            max_placeholder = f"#{issue_key}_MAX_NUM"
            instructions = instructions.replace(max_placeholder, str(max_score))
        
        return instructions
    
    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """Process a player's action."""
        current_pid = self.state.current_player_id
        
        # Log the action
        self.state.add_observation(
            from_id=current_pid,
            to_id=current_pid,
            message=f"Your action: {action}",
            observation_type=ta.ObservationType.PLAYER_ACTION
        )
        
        # Process the action
        if self._is_valid_action(action):
            self.valid_actions_this_round.add(current_pid)
            self._process_valid_action(current_pid, action)
        else:
            self._handle_invalid_action(current_pid, action)
        
        # Check for game end conditions
        if self._check_deal_accepted() or self.state.turn >= self.max_rounds - 1:
            self._end_game()
        
        return self.state.step()
    
    def _is_valid_action(self, action: str) -> bool:
        """Check if an action is valid."""
        action = action.strip()
        
        # Check for valid action types
        if action.upper().startswith("PROPOSE:"):
            return self._is_valid_proposal(action)
        elif action.upper() in ["ACCEPT", "REJECT"]:
            return True
        elif action.upper().startswith("DISCUSS:"):
            return len(action) > 8  # Must have content after "DISCUSS:"
        
        return False
    
    def _is_valid_proposal(self, action: str) -> bool:
        """Check if a proposal is valid."""
        try:
            # Extract proposal part
            proposal_part = action[8:].strip()  # Remove "PROPOSE:"
            
            # Parse deal (A1,B2,C3,D1,E4)
            deal_parts = [part.strip() for part in proposal_part.split(',')]
            
            # Check if all issues are covered
            expected_issues = set(self.issues.keys())
            proposed_issues = set()
            
            for part in deal_parts:
                if len(part) >= 2:
                    issue_key = part[0]
                    if issue_key in expected_issues:
                        proposed_issues.add(issue_key)
                        # Check if option exists
                        if part not in self.issues[issue_key]["options"]:
                            return False
            
            return proposed_issues == expected_issues
            
        except Exception:
            return False
    
    def _process_valid_action(self, player_id: int, action: str):
        """Process a valid action."""
        action = action.strip()
        action_upper = action.upper()
        
        if action_upper.startswith("PROPOSE:"):
            self._process_proposal(player_id, action)
        elif action_upper == "ACCEPT":
            self._process_vote(player_id, "ACCEPT")
        elif action_upper == "REJECT":
            self._process_vote(player_id, "REJECT")
        elif action_upper.startswith("DISCUSS:"):
            self._process_discussion(player_id, action)
    
    def _process_proposal(self, player_id: int, action: str):
        """Process a deal proposal."""
        proposal_part = action[8:].strip()  # Remove "PROPOSE:"
        
        # Parse the deal
        new_deal = {}
        deal_parts = [part.strip() for part in proposal_part.split(',')]
        
        for part in deal_parts:
            if len(part) >= 2:
                issue_key = part[0]
                new_deal[issue_key] = part
        
        self.current_deal = new_deal
        self.state.game_state["current_deal"] = new_deal
        
        # Clear previous votes
        self.player_votes = {}
        self.state.game_state["player_votes"] = {}
        
        # Announce the proposal
        config = self.player_configs[player_id]
        deal_str = ", ".join([f"{k}:{v}" for k, v in new_deal.items()])
        
        message = f"{config['agent_name']} proposes: {deal_str}"
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=message,
            observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
        )
        
        # Show updated scores to each player
        self._show_deal_scores_to_players()
        
        # Record in history
        self.negotiation_history.append({
            "player_id": player_id,
            "action_type": "PROPOSE",
            "content": deal_str,
            "round": self.state.turn
        })
    
    def _process_vote(self, player_id: int, vote: str):
        """Process an accept/reject vote."""
        if not self.current_deal:
            self.state.game_info[player_id]["invalid_move"] = True
            self.state.step_info[f"invalid_move_player_{player_id}"] = "No current proposal to vote on. Someone must propose a deal first."
            return
        
        self.player_votes[player_id] = vote
        self.state.game_state["player_votes"] = self.player_votes
        
        config = self.player_configs[player_id]
        message = f"{config['agent_name']} votes: {vote}"
        
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=message,
            observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
        )
        
        # Record in history
        self.negotiation_history.append({
            "player_id": player_id,
            "action_type": vote,
            "content": "",
            "round": self.state.turn
        })
    
    def _process_discussion(self, player_id: int, action: str):
        """Process a discussion statement."""
        message_content = action[8:].strip()  # Remove "DISCUSS:"
        config = self.player_configs[player_id]
        
        message = f"{config['agent_name']} says: {message_content}"
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=message,
            observation_type=ta.ObservationType.GAME_MESSAGE
        )
        
        # Record in history
        self.negotiation_history.append({
            "player_id": player_id,
            "action_type": "DISCUSS",
            "content": message_content,
            "round": self.state.turn
        })
    
    def _handle_invalid_action(self, player_id: int, action: str):
        """Handle an invalid action."""
        # Determine the reason
        if action.upper().startswith("PROPOSE:"):
            reason = "Invalid proposal format. Use: PROPOSE: A1,B2,C3,D1,E4 (cover all issues with valid options)"
        elif not any(action.upper().startswith(prefix) for prefix in ["PROPOSE:", "ACCEPT", "REJECT", "DISCUSS:"]):
            reason = "Invalid action. Use: PROPOSE: [deal], ACCEPT, REJECT, or DISCUSS: [message]"
        else:
            reason = "Invalid action format"
        
        self.state.game_info[player_id]["invalid_move"] = True
        self.state.step_info[f"invalid_move_player_{player_id}"] = reason
        
        # If there's a current deal being voted on, apply default vote
        if self.current_deal and action.upper() in ["ACCEPT", "REJECT", ""] or not self._is_valid_action(action):
            self.player_votes[player_id] = self.invalid_action_default
            
            config = self.player_configs[player_id]
            message = f"{config['agent_name']} had invalid action, defaulting vote to {self.invalid_action_default}"
            
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1,
                message=message,
                observation_type=ta.ObservationType.GAME_ADMIN
            )
    
    def _show_deal_scores_to_players(self):
        """Show each player their private scores for the current deal."""
        for player_id in range(self.state.num_players):
            config = self.player_configs[player_id]
            scores_text = render_player_scores(
                self.player_scores[player_id], 
                self.current_deal, 
                config["agent_name"]
            )
            
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=player_id,
                message=scores_text,
                observation_type=ta.ObservationType.GAME_BOARD
            )
    
    def _check_deal_accepted(self) -> bool:
        """Check if the current deal has been accepted by majority."""
        if not self.current_deal or not self.player_votes:
            return False
        
        # Count votes (including defaults for invalid actions)
        total_players = self.state.num_players
        accept_votes = 0
        
        for player_id in range(total_players):
            vote = self.player_votes.get(player_id, "")
            if vote == "ACCEPT":
                accept_votes += 1
        
        # Need majority to accept
        majority_threshold = (total_players // 2) + 1
        return accept_votes >= majority_threshold
    
    def _end_game(self):
        """End the game and determine winners."""
        if self._check_deal_accepted():
            # Deal was accepted
            self._finalize_accepted_deal()
        else:
            # No deal reached
            self._handle_no_deal()
        
        self.state.done = True
    
    def _finalize_accepted_deal(self):
        """Finalize an accepted deal and determine scores."""
        deal_str = ", ".join([f"{k}:{v}" for k, v in self.current_deal.items()])
        
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=f"DEAL ACCEPTED: {deal_str}",
            observation_type=ta.ObservationType.GAME_ADMIN
        )
        
        # Calculate final scores
        final_scores = {}
        for player_id in range(self.state.num_players):
            score = self._calculate_player_score(player_id, self.current_deal)
            final_scores[player_id] = score
            
            config = self.player_configs[player_id]
            threshold = self.player_scores[player_id].get("threshold", 0)
            
            score_message = f"{config['agent_name']} final score: {score} points (threshold: {threshold})"
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=player_id,
                message=score_message,
                observation_type=ta.ObservationType.GAME_ADMIN
            )
        
        # Determine winners (players who met their threshold)
        winners = []
        for player_id, score in final_scores.items():
            threshold = self.player_scores[player_id].get("threshold", 0)
            if score >= threshold:
                winners.append(player_id)
        
        if winners:
            # Find the highest scorer among those who met threshold
            best_score = max(final_scores[pid] for pid in winners)
            best_players = [pid for pid in winners if final_scores[pid] == best_score]
            
            if len(best_players) == 1:
                # Set winner info
                for pid in range(self.state.num_players):
                    self.state.game_info[pid]["winner"] = pid in best_players
                self.state.step_info["winner_reason"] = f"Highest score ({best_score}) among players meeting threshold"
            else:
                # Set draw
                for pid in range(self.state.num_players):
                    self.state.game_info[pid]["winner"] = False
                self.state.step_info["draw_reason"] = f"Tie with score {best_score} among players meeting threshold"
        else:
            # Set draw - no one met threshold
            for pid in range(self.state.num_players):
                self.state.game_info[pid]["winner"] = False
            self.state.step_info["draw_reason"] = "No players met their minimum threshold"
        
        # Set rewards based on scores
        rewards = {}
        max_possible_score = max(final_scores.values()) if final_scores else 1
        for player_id, score in final_scores.items():
            # Normalize score to 0-100 range
            normalized_score = int((score / max_possible_score) * 100) if max_possible_score > 0 else 0
            rewards[player_id] = max(0, normalized_score)  # Ensure non-negative
        
        self.state.rewards = rewards
    
    def _handle_no_deal(self):
        """Handle case where no deal was reached."""
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message="NO DEAL REACHED - Negotiation failed",
            observation_type=ta.ObservationType.GAME_ADMIN
        )
        
        # All players get 0 reward for failed negotiation
        self.state.rewards = {pid: 0 for pid in range(self.state.num_players)}
        # Set draw info
        for pid in range(self.state.num_players):
            self.state.game_info[pid]["winner"] = False
        self.state.step_info["draw_reason"] = "No agreement reached within time limit"
    
    def _calculate_player_score(self, player_id: int, deal: Dict[str, str]) -> int:
        """Calculate a player's score for a given deal."""
        total_score = 0
        player_scores = self.player_scores[player_id]
        
        for issue_key, option in deal.items():
            if issue_key in player_scores and option in player_scores[issue_key]:
                total_score += player_scores[issue_key][option]
        
        return total_score
    
    def get_observation(self):
        """Get observation for current player."""
        player_id = self.state.current_player_id
        observation = self.state.get_current_player_observation()
        
        # Add current game state information
        if self.current_deal:
            deal_summary = render_current_deal(self.current_deal, self.issues)
            observation.append((ta.GAME_ID, deal_summary, ta.ObservationType.GAME_BOARD))
        
        # Add negotiation summary
        summary = render_negotiation_summary(
            self.negotiation_history, self.current_deal, 
            self.state.turn + 1, self.max_rounds
        )
        observation.append((ta.GAME_ID, summary, ta.ObservationType.GAME_MESSAGE))
        
        return player_id, observation
