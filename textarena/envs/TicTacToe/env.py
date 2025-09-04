import re
from typing import Optional, Dict, Tuple, Any

import textarena as ta
from textarena.envs.TicTacToe.renderer import create_board_str

class TicTacToeEnv(ta.Env):
    def __init__(self, prompt_template: str = "basic"):
        super().__init__()
        self.prompt_template = prompt_template
        self.cell_mapping = {i * 3 + j: (i, j) for i in range(3) for j in range(3)}

    def get_board_str(self): return create_board_str(board=self.state.game_state["board"])
    def _render_board(self): return "\n---+---+---\n".join("|".join(f" {self.state.game_state['board'][r][c]} " if self.state.game_state['board'][r][c] else f" {str(r * 3 + c)} " for c in range(3)) for r in range(3))
    
    def reset(self, num_players: int, seed: Optional[int]=None):
        self.state = ta.TwoPlayerState(num_players=num_players, seed=seed)
        self.state.reset(game_state={"board": [['' for _ in range(3)] for _ in range(3)]}, player_prompt_function=self._prompt)
        self._observer_current_state()

    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
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

    def _basic_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"You are Player {player_id} in Tic Tac Toe.\n"
            "Your goal is to win three in a row (horizontally, vertically, or diagonally) on the board.\n"
            "On your turn, you should select the square number (0-8) you want to put your mark in next.\n"
            "For example, '[4]' places your mark in the center cell of the board.\n\n"
            f"As Player {player_id}, you will be '{'X' if player_id == 1 else 'O'}', "
            f"while your opponent is '{'O' if player_id == 1 else 'X'}'.\n"
        )

    def _basic_prompt_variant_1(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"Welcome to the Tic Tac Toe Arena! You are competing as Player {player_id}.\n"
            "Victory is achieved by claiming three consecutive squares in any direction: horizontal, vertical, or diagonal.\n"
            "To make your move, choose a numbered position (0-8) on the grid and submit it in brackets.\n"
            "Example: '[7]' will claim the bottom-right corner of the board.\n\n"
            f"Your battle symbol is '{'X' if player_id == 1 else 'O'}', "
            f"while your opponent fights with '{'O' if player_id == 1 else 'X'}'.\n"
        )

    def _basic_prompt_variant_2(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"You are operating as Player {player_id} in this Strategic Tic Tac Toe engagement.\n"
            "Your objective is to establish a tactical line of three marks aligned horizontally, vertically, or diagonally.\n"
            "Execute your strategy by selecting any available cell position (numbered 0-8) using the specified format.\n"
            "Strategic example: '[0]' secures the top-left corner position.\n\n"
            f"Your tactical marker is '{'X' if player_id == 1 else 'O'}', "
            f"opposing the enemy's '{'O' if player_id == 1 else 'X'}' marker.\n"
        )

    def _basic_prompt_variant_3(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"Player {player_id}, you have entered the Classic Tic Tac Toe Challenge.\n"
            "Solve this puzzle by creating an unbroken sequence of three identical marks in a straight line.\n"
            "Place your mark by indicating the cell number (0-8) enclosed in square brackets.\n"
            "Challenge example: '[2]' positions your mark in the top-right square.\n\n"
            f"You control the '{'X' if player_id == 1 else 'O'}' symbol, "
            f"while your challenger uses '{'O' if player_id == 1 else 'X'}'.\n"
        )

    def _basic_prompt_variant_4(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"Hello Player {player_id}! Let's play a friendly game of Tic Tac Toe.\n"
            "The idea is simple: get three of your marks lined up in any row, column, or diagonal.\n"
            "Just pick which square you want (they're numbered 0 through 8) and put it in brackets.\n"
            "Like this: '[8]' puts your mark in the bottom-right spot.\n\n"
            f"You'll be playing with '{'X' if player_id == 1 else 'O'}' marks, "
            f"and your friend is using '{'O' if player_id == 1 else 'X'}' marks.\n"
        )

    def _basic_prompt_variant_5(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"Player {player_id}, prepare for battle in this Competitive Tic Tac Toe Match!\n"
            "Dominate the board by forming an unbreakable line of three marks in any direction.\n"
            "Strike at your chosen cell (numbered 0-8) by declaring your attack in the required format.\n"
            "Attack command: '[5]' launches your assault on the center position.\n\n"
            f"Your weapon of choice is '{'X' if player_id == 1 else 'O'}', "
            f"while your adversary wields '{'O' if player_id == 1 else 'X'}'.\n"
        )

    def _few_shot_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"You are Player {player_id} in Tic Tac Toe.\n"
            "Your goal is to win three in a row (horizontally, vertically, or diagonally) on the board.\n"
            "On your turn, you should select the square number (0-8) you want to put your mark in next.\n"
            f"As Player {player_id}, you will be '{'X' if player_id == 1 else 'O'}', "
            f"while your opponent is '{'O' if player_id == 1 else 'X'}'.\n\n"
            "Here are some examples of good Tic Tac Toe decisions:\n\n"
            "Example 1: Player sees opponent has two X's in the top row (positions 0 and 1). "
            "They immediately play '[2]' to block the winning move.\n\n"
            "Example 2: Player has two O's diagonally (positions 0 and 4). "
            "They play '[8]' to complete the diagonal and win the game.\n\n"
            "Example 3: Early in the game, player chooses '[4]' to take the center position, "
            "which gives the most strategic options for creating multiple winning threats.\n\n"
            "Example 4: Player sees opponent controls center and one corner. "
            "They take the opposite corner '[8]' to prevent opponent from creating a fork.\n\n"
            "Format your move as '[number]' where number is 0-8."
        )

    def _chain_of_thought_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"You are Player {player_id} in Tic Tac Toe.\n"
            "Your goal is to win three in a row (horizontally, vertically, or diagonally) on the board.\n"
            f"As Player {player_id}, you will be '{'X' if player_id == 1 else 'O'}', "
            f"while your opponent is '{'O' if player_id == 1 else 'X'}'.\n\n"
            "Before making your move, think step-by-step about your approach.\n\n"
            "Some possible directions to consider (but feel free to think about whatever is most relevant):\n"
            "- What is the current state of the board?\n"
            "- Do you have any immediate winning moves available?\n"
            "- Does your opponent have any winning moves you need to block?\n"
            "- What strategic positions should you prioritize (center, corners, edges)?\n"
            "- How can you set up multiple winning threats simultaneously?\n"
            "- What might your opponent be planning with their positioning?\n\n"
            "Work through your reasoning step by step, then make your decision.\n\n"
            "Format your move as '[number]' where number is 0-8."
        )

    def _tree_of_thoughts_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"You are Player {player_id} in Tic Tac Toe.\n"
            "Your goal is to win three in a row (horizontally, vertically, or diagonally) on the board.\n"
            f"As Player {player_id}, you will be '{'X' if player_id == 1 else 'O'}', "
            f"while your opponent is '{'O' if player_id == 1 else 'X'}'.\n\n"
            "Imagine three different Tic Tac Toe experts are advising you on this move.\n"
            "Each expert will write down one step of their thinking, then share it with the group.\n"
            "Then all experts will go on to the next step, and so on.\n"
            "If any expert realizes they're wrong at any point, they leave.\n\n"
            "Consider what types of experts would be most helpful for this Tic Tac Toe decision:\n"
            "- A defensive strategist who focuses on blocking opponent threats\n"
            "- An offensive tactician who prioritizes creating winning opportunities\n"
            "- A positional expert who understands board control and setup moves\n\n"
            "Have them analyze the current board position from their different perspectives.\n\n"
            "Format your move as '[number]' where number is 0-8."
        )

    def _generated_knowledge_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"You are Player {player_id} in Tic Tac Toe.\n"
            "Your goal is to win three in a row (horizontally, vertically, or diagonally) on the board.\n"
            f"As Player {player_id}, you will be '{'X' if player_id == 1 else 'O'}', "
            f"while your opponent is '{'O' if player_id == 1 else 'X'}'.\n\n"
            "Before making your move, first generate relevant knowledge about Tic Tac Toe strategy that applies to your current situation.\n\n"
            "Generate Knowledge: What key principles, strategies, or insights about Tic Tac Toe are most relevant to your current board position? "
            "Consider aspects like:\n"
            "- Opening strategy (center vs corners vs edges)\n"
            "- Defensive priorities (when and what to block)\n"
            "- Offensive patterns (how to create forks and multiple threats)\n"
            "- Endgame tactics (forcing wins or draws)\n\n"
            "After generating this knowledge, apply it to make your move decision.\n\n"
            "Format your move as '[number]' where number is 0-8."
        )

    def _observer_current_state(self):
        available_moves = [f"'[{str(r*3+c)}]'" for r in range(3) for c in range(3) if self.state.game_state["board"][r][c] == '']
        self.state.add_observation(message=f"Current Board:\n\n{self._render_board()}\n\nAvailable Moves: {', '.join(available_moves)}", observation_type=ta.ObservationType.GAME_BOARD)

    def step(self,action:str)->Tuple[bool,ta.Info]:
        self.current_player = 'X' if self.state.current_player_id == 1 else 'O'
        self.state.add_observation(from_id=self.state.current_player_id, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)
        match = re.compile(r"\[\s*(\d+)\s*\]").search(action)
        if match is None: # Invalid format
            self.state.set_invalid_move(reason="The submitted move does not follow the correct format.")
        else:
            cell = int(match.group(1))
            if cell not in self.cell_mapping: # Ensure the cell is within 0–8
                self.state.set_invalid_move(reason=f"{cell}. Must be between 0 and 8.")
            else:
                row, col = self.cell_mapping[cell]
                if self.state.game_state["board"][row][col] == '':
                    self.state.game_state["board"][row][col] = self.current_player # Make the move
                    self.state.add_observation(message=f"Player {self.state.current_player_id} placed their symbol ({self.current_player}) in cell {cell}.", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)
                    if self._check_winner(): # Check for winner or draw
                        self.state.set_winner(player_id=self.state.current_player_id, reason=f"Player {self.state.current_player_id} has won!")
                    elif all(cell != '' for row in self.state.game_state["board"] for cell in row):
                        self.state.set_draw(reason="The game is a draw!")
                else:
                    self.state.set_invalid_move(reason=f"cell {cell} is already occupied.")
        self._observer_current_state()
        return self.state.step()

    def _check_winner(self) -> bool:
        board = self.state.game_state["board"]
        for i in range(3):
            if (board[i][0] == board[i][1] == board[i][2] != '' or board[0][i] == board[1][i] == board[2][i] != ''):    return True
        if (board[0][0] == board[1][1] == board[2][2] != '' or board[0][2] == board[1][1] == board[2][0] != ''):        return True
        return False
 