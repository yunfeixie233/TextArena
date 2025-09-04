import re, chess 
from typing import Any, Dict, Optional, Tuple

import textarena as ta
from textarena.envs.Chess.renderer import create_board_str


class ChessEnv(ta.Env):
    def __init__(self, is_open: bool=True, max_turns: int=30, show_valid: bool=True, prompt_template: str="basic", max_retries: int=10):
        """
        Args:
            is_open (bool): If True, both players can see the current board state. If False, players receive minimal information.
            max_turns (int): Maximum number of turns before the game ends.
            show_valid (bool): If True, players can see a list of valid moves.
            prompt_template (str): Template name for prompts (e.g., basic, basic_variant_1, few_shot, chain_of_thought).
            max_retries (int): Maximum number of retries when invalid UCI moves are encountered.
        """
        self.max_turns = max_turns
        self.is_open = is_open 
        self.show_valid = show_valid
        self.prompt_template = prompt_template
        self.max_retries = max_retries 

    def get_board_str(self): return create_board_str(board=self.state.game_state["board"])

    def reset(self, num_players: int, seed: Optional[int]=None):
        self.state = ta.TwoPlayerState(num_players=num_players, max_turns=self.max_turns, seed=seed)
        board = chess.Board()
        valid_moves = ', '.join([f'[{move.uci()}]' for move in board.legal_moves])
        game_state = {
            "board": board, 
            "valid_moves": valid_moves,
            "retry_count": {0: 0, 1: 0},  # Track retries per player
            "last_error": {0: None, 1: None}  # Track last error per player
        }
        self.state.reset(game_state=game_state, player_prompt_function=self._prompt, role_mapping={0:"White", 1:"Black"})
        self._agument_observations()

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

    def _get_uci_instruction(self, player_id: int, game_state: Dict[int, Any]) -> str:
        """Generate UCI instruction and error feedback if applicable"""
        instruction = "Invalid moves include same-square moves (e.g. [e8e8]) and moves to squares you cannot reach. Always double-check your move format and ensure the move is legal in the current position."
        
        # Add error feedback if player has a previous error
        last_error = game_state.get("last_error", {}).get(player_id)
        if last_error:
            retry_count = game_state.get("retry_count", {}).get(player_id, 0)
            instruction = f"PREVIOUS ERROR (Retry {retry_count}/{self.max_retries}): {last_error}\n{instruction}"
        
        return instruction

    def _basic_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        uci_instruction = self._get_uci_instruction(player_id, game_state)
        return f"You are playing {'White' if player_id==0 else 'Black'} in a game of Chess.\nMake your moves in UCI format enclosed in square brackets (e.g., [e2e4]).\n\n{uci_instruction}"

    def _basic_prompt_variant_1(self, player_id: int, game_state: Dict[int, Any]) -> str:
        color = 'White' if player_id == 0 else 'Black'
        uci_instruction = self._get_uci_instruction(player_id, game_state)
        return (
            f"Welcome to the Chess Arena! You are commanding the {color} pieces in this strategic battle.\n"
            f"Your mission is to checkmate your opponent's king through tactical superiority.\n"
            f"Execute your strategic moves using UCI notation within square brackets.\n"
            f"Example: '[d2d4]' advances your pawn to establish central control.\n\n{uci_instruction}"
        )

    def _basic_prompt_variant_2(self, player_id: int, game_state: Dict[int, Any]) -> str:
        color = 'White' if player_id == 0 else 'Black'
        uci_instruction = self._get_uci_instruction(player_id, game_state)
        return (
            f"You are operating as the {color} player in this Chess engagement.\n"
            f"Your objective is to achieve victory through superior tactical planning and piece coordination.\n"
            f"Communicate your moves using the Universal Chess Interface format enclosed in brackets.\n"
            f"Move specification: '[g1f3]' develops your knight to a strong central square.\n\n{uci_instruction}"
        )

    def _basic_prompt_variant_3(self, player_id: int, game_state: Dict[int, Any]) -> str:
        color = 'White' if player_id == 0 else 'Black'
        uci_instruction = self._get_uci_instruction(player_id, game_state)
        return (
            f"Player {player_id}, you have entered the Classic Chess Challenge as {color}.\n"
            f"Master this ancient game by outmaneuvering your opponent to capture their king.\n"
            f"Submit your moves using the standard UCI format within square brackets.\n"
            f"Movement example: '[e1g1]' performs kingside castling for safety.\n\n{uci_instruction}"
        )

    def _basic_prompt_variant_4(self, player_id: int, game_state: Dict[int, Any]) -> str:
        color = 'White' if player_id == 0 else 'Black'
        uci_instruction = self._get_uci_instruction(player_id, game_state)
        return (
            f"Hello Player {player_id}! You're playing a friendly game of Chess with the {color} pieces.\n"
            f"The goal is simple: use strategy and tactics to checkmate your opponent's king.\n"
            f"Just specify your moves using UCI format in square brackets.\n"
            f"Like this: '[b1c3]' moves your knight to support the center.\n\n{uci_instruction}"
        )

    def _basic_prompt_variant_5(self, player_id: int, game_state: Dict[int, Any]) -> str:
        color = 'White' if player_id == 0 else 'Black'
        uci_instruction = self._get_uci_instruction(player_id, game_state)
        return (
            f"Player {player_id}, prepare for intellectual combat as {color} in this Chess duel!\n"
            f"Dominate the board through cunning strategy and precise calculation.\n"
            f"Declare your moves using UCI notation enclosed within brackets.\n"
            f"Combat command: '[f2f4]' launches an aggressive pawn storm against your adversary.\n\n{uci_instruction}"
        )

    def _few_shot_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        color = 'White' if player_id == 0 else 'Black'
        uci_instruction = self._get_uci_instruction(player_id, game_state)
        return (
            f"You are playing {color} in a game of Chess.\n"
            f"Your goal is to checkmate your opponent's king using tactical and strategic play.\n\n"
            f"Here are examples of good chess decision-making:\n\n"
            f"Example 1: Opening with '[e2e4]' controls the center and develops pieces quickly. "
            f"This is better than '[h2h3]' which wastes time on the edge.\n\n"
            f"Example 2: When your king is in danger, prioritize safety. "
            f"Castling with '[e1g1]' moves your king to safety behind pawns.\n\n"
            f"Example 3: Look for tactical opportunities. If opponent's queen is undefended, "
            f"move your knight with '[g1f3]' to attack it and gain material advantage.\n\n"
            f"Make your moves in UCI format enclosed in square brackets (e.g., [e2e4]).\n\n{uci_instruction}"
        )

    def _chain_of_thought_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        color = 'White' if player_id == 0 else 'Black'
        uci_instruction = self._get_uci_instruction(player_id, game_state)
        return (
            f"You are playing {color} in a game of Chess.\n"
            f"Your goal is to checkmate your opponent's king through strategic and tactical play.\n\n"
            f"Before making any move, think step-by-step about your approach.\n\n"
            f"Consider these questions in your analysis:\n"
            f"- What is the current position and what are my immediate threats?\n"
            f"- What are my opponent's threats and how should I respond?\n"
            f"- Which pieces need development or better placement?\n"
            f"- Are there any tactical opportunities (forks, pins, skewers)?\n"
            f"- How does this move fit into my overall strategy?\n\n"
            f"Work through your reasoning step by step, then make your decision.\n\n"
            f"Make your moves in UCI format enclosed in square brackets (e.g., [e2e4]).\n\n{uci_instruction}"
        )

    def _tree_of_thoughts_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        color = 'White' if player_id == 0 else 'Black'
        uci_instruction = self._get_uci_instruction(player_id, game_state)
        return (
            f"You are playing {color} in a game of Chess.\n"
            f"Your goal is to checkmate your opponent's king through superior strategic thinking.\n\n"
            f"Imagine three different chess experts are advising you on this move.\n"
            f"Each expert will analyze one aspect of the position, then share their insight.\n"
            f"Then all experts will collaborate on the next aspect of analysis.\n"
            f"If any expert realizes their analysis is flawed, they step back.\n\n"
            f"Consider what types of experts would be most helpful:\n"
            f"- A tactical expert focusing on immediate threats and combinations\n"
            f"- A positional expert evaluating long-term structural advantages\n"
            f"- An endgame expert considering how the position might resolve\n\n"
            f"Have them analyze the position from their different perspectives.\n\n"
            f"Make your moves in UCI format enclosed in square brackets (e.g., [e2e4]).\n\n{uci_instruction}"
        )

    def _generated_knowledge_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        color = 'White' if player_id == 0 else 'Black'
        uci_instruction = self._get_uci_instruction(player_id, game_state)
        return (
            f"You are playing {color} in a game of Chess.\n"
            f"Your goal is to checkmate your opponent's king through masterful play.\n\n"
            f"Before making a move, first generate relevant chess knowledge that applies to your current situation.\n\n"
            f"Generate Knowledge: What key chess principles, opening ideas, tactical patterns, "
            f"positional concepts, or endgame techniques are most relevant to your current position?\n\n"
            f"After generating this knowledge, apply it to evaluate your options and make your move.\n\n"
            f"Make your moves in UCI format enclosed in square brackets (e.g., [e2e4]).\n\n{uci_instruction}"
        )
    
    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(from_id=self.state.current_player_id, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)
        self._execute_player_move(action=action)
        self._check_gameover()
        self._agument_observations()
        return self.state.step()

    def _execute_player_move(self, action: str):
        match = re.compile(r"\[[a-h][1-8][a-h][1-8][qrbn]?\]", re.IGNORECASE).search(action.strip())
        current_player = self.state.current_player_id
        
        if match is None: 
            error_msg = "Wrong move format. Use UCI notation like [e2e4]."
            self._handle_invalid_move(current_player, error_msg)
        else:
            move_uci = match.group(0).lower().replace("[", "").replace("]", "") # Extract the move from within the brackets
            try:
                move = chess.Move.from_uci(move_uci) # Attempt to parse the move
                if move in self.state.game_state["board"].legal_moves:
                    # Valid move - execute it and reset retry count
                    self.state.game_state["board"].push(move)
                    self.state.game_state["retry_count"][current_player] = 0  # Reset retry count on success
                    self.state.game_state["last_error"][current_player] = None  # Clear error
                    self.state.add_observation(message=f"Player {current_player} made the following move: {move_uci}", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)
                else: 
                    error_msg = f"Illegal move: {move_uci}. This move is not legal in the current position."
                    self._handle_invalid_move(current_player, error_msg)
            except chess.InvalidMoveError:
                error_msg = f"Invalid UCI format: {move_uci}. Ensure you use proper format like [e2e4]."
                self._handle_invalid_move(current_player, error_msg)

    def _handle_invalid_move(self, player_id: int, error_msg: str):
        """Handle invalid moves with retry logic"""
        retry_count = self.state.game_state["retry_count"][player_id]
        
        if retry_count < self.max_retries:
            # Increment retry count and store error for next prompt
            self.state.game_state["retry_count"][player_id] += 1
            self.state.game_state["last_error"][player_id] = error_msg
            
            # Add observation about the error but don't end turn
            self.state.add_observation(
                message=f"Invalid move attempt {retry_count + 1}/{self.max_retries}: {error_msg} Please try again.",
                observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
            )
            
            # Mark as invalid move - the game will continue with retry logic
            self.state.set_invalid_move(reason=error_msg)
        else:
            # Exceeded max retries - end turn with invalid move
            self.state.game_state["retry_count"][player_id] = 0  # Reset for next time
            self.state.game_state["last_error"][player_id] = None
            self.state.set_invalid_move(reason=f"Exceeded {self.max_retries} retries. {error_msg}")

    def _check_gameover(self):
        if self.state.game_state["board"].is_game_over():
            outcome = self.state.game_state["board"].outcome().result()
            if outcome == "1/2-1/2": self.state.set_draw(reason=f"Game ended in a draw.") # check for draw
            else:
                winner_id = 0 if outcome == "1-0" else 1
                self.state.set_winner(player_id=winner_id, reason=f"Player {winner_id} wins the match.")

    def _agument_observations(self):
        message = ""
        if self.is_open: message+=f"Current board:\n{self._board_with_coords(self.state.game_state['board'])}" #f"Current board:\n{str(self.state.game_state["board"])}" # display the board state
        if self.show_valid: message+=f"\nValid moves: {', '.join([f'[{move.uci()}]' for move in self.state.game_state["board"].legal_moves])}"# show the valid moves
        self.state.add_observation(message=message, observation_type=ta.ObservationType.GAME_BOARD)

    @staticmethod
    def _board_with_coords(board: chess.Board) -> str:
        inner_width = len(str(board).splitlines()[0])
        top = bottom = f"   +{'-' * (inner_width + 2)}+"
        body = [f" {rank} | {row} |" for rank, row in zip(range(8, 0, -1), str(board).splitlines())]
        files = "   " + " ".join("a b c d e f g h".split()).center(inner_width + 2)
        return "\n".join([top, *body, bottom, files])