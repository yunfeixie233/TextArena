import re
from typing import Optional, Dict, Any, Tuple

import textarena as ta 
from textarena.envs.SettlersOfCatan.game_engine import Board, render_board


class SettlersOfCatanEnv(ta.Env):
    roles = {0: "Red", 1: "White", 2: "Blue", 3: "Orange"}
    def __init__(self):
        self.game_moves = None


    def reset(self, num_players: int, seed: Optional[int]=None):
        assert num_players == 4, f"Environment is hard-coded for exactly four players. Received {num_players} players on reset."
        self.state = ta.FFAMultiPlayerState(num_players=num_players, seed=seed)
        self.board = Board.build_standard()
        self.state.reset(game_state={}, role_mapping=self.roles, player_prompt_function=self._prompt)
        self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        # self._roll_dice()
        print("dice rolled")
        self._render_board_state()

    
    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return f"You are playing SettlersOfCatan as {self.roles[player_id]}"
    

    def _roll_dice(self):
        roll_str, added_clean = self.board.roll_dice()
        if any([len(qty_dict)!=0 for color, qty_dict in added_clean.items()]):
            message = f"Player {self.state.current_player_id} ({self.roles[self.state.current_player_id]}) rolled: {roll_str}. Items received:"
            print(added_clean)
            for color, qty_dict in added_clean.items():
                if len(qty_dict) == 0: continue
                message += f"\n\t {color}: " + ', '.join([f"{terrain}: +{qty}" for terrain, qty in qty_dict.items()])
        else:
            message = f"Player {self.state.current_player_id} ({self.roles[self.state.current_player_id]}) rolled: {roll_str}. Nobody received anything."
        self.state.add_observation(message=message, observation_type=ta.ObservationType.GAME_MESSAGE)


    def _render_board_state(self):
        cpid = self.state.current_player_id
        colour = self.board.str_to_enum(color_str=self.roles[self.state.current_player_id])
        player = self.board.players[colour]
        scores = self.board.get_scores()

        score_lines = [f"{str(c):6} {rec['total']:>2} VP   (S:{rec['settlements']}  C:{rec['cities']}  R:{rec['roads']})" for c, rec in scores.items()]
       
        # print(player)
        self.game_moves = self.board._viable_moves(player)
        # input(moves)
        len_game_moves = len(self.game_moves)
        self.game_moves += [
            (len_game_moves+1, f"Negotiate.", None),
            (len_game_moves+2, f"Nothing.", None)
        ]
        move_block = "\n".join(f"'[{idx}]'\t-  {desc}" for idx, desc, _ in self.game_moves) 

        parts = [
            f"{'='*24}  {colour.name}  {'='*24}",
            "Scores\n───────",
            "\n".join(score_lines),
            "",
            "Board\n──────",
            render_board(self.board),
            "",
            f"Your hand cards are:\n\t{{{'\n\t'.join(f'{k.name.lower()}: {v}' for k,v in player.hand.items())}}}",
            "",
            "Viable moves\n────────────",
            move_block,
            "Please select on of the viable actions by returning '[idx]' as part of your action."
        ]
        message = "\n".join(parts)

        self.state.add_observation(to_id=cpid, message=message, observation_type=ta.ObservationType.GAME_BOARD)


    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(from_id=self.state.current_player_id, to_id=self.state.current_player_id, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)
        colour = self.board.str_to_enum(color_str=self.roles[self.state.current_player_id])
        if self.game_moves is not None:
            m = re.search(r'\[(\d+)\]', action)
            print(m)
            if m is None: self.state.set_invalid_move(reason=f"No action found."); return self.state.step()
            act = int(m.group(1))
            if act > len(self.game_moves) or act <=0: self.state.set_invalid_move(reason=f"Selected action index is out of bounds. Please select from the list."); return self.state.step()
            if act == len(self.game_moves) or act == len(self.game_moves)-1: # these are Negotiation and skip
                print("selected Negotiation or Skip")
            else:
                selected = next(m for m in self.game_moves if m[0] == act)
                ok, err = self.board.execute_action(colour, selected[2])


            
            # # actract action idx and execute action
            # # i.e. extract 1 from "hello [1], goodbye"
            # self.game_moves

        else:
            # exectue action and check when to off-rotate
            pass

        # rotate player, roll dice, show board
        pid = self.state.next_alive_player()
        self.state.manually_set_current_player_id(new_player_id=pid)

        self._roll_dice()
        self._render_board_state()

        return self.state.step(rotate_player=False)