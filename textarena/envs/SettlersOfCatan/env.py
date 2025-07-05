import re
from typing import Optional, Dict, Any, Tuple

import textarena as ta 
from textarena.envs.SettlersOfCatan.game_engine import Board, render_board



_NEGO_ACCEPT_RE = re.compile(r'\[accept\]', re.I)
_NEGO_DENY_RE   = re.compile(r'\[deny\]',   re.I)
_NEGO_DONE_RE   = re.compile(r'\[done\]',   re.I)
_NEGO_OFFER_RE  = re.compile(r'\[offer:?\s*(?:i\s+(?:give|offer)\s+)?([^\[\]]+?)\s*\]', re.I | re.S)
_RESOURCE_PAIR_RE = re.compile(r'(\d+)\s+([A-Za-z]+)', re.I)
_RESOURCE_CANON = {"Sheeps": "Sheep", "Woods": "Wood"}
_C2_RES_NAMES = ["Wheat", "Wood", "Sheep", "Brick", "Ore"]

def _parse_resource_list(text: str) -> Optional[Dict[str,int]]:
    """Turn '3 Sheep, 2 Ore' → {'Sheep':3, 'Ore':2}. Returns None on error."""
    pairs = _RESOURCE_PAIR_RE.findall(text)
    if not pairs:
        return None
    out: Dict[str,int] = {}
    for qty_s, raw in pairs:
        qty = int(qty_s)
        name = _RESOURCE_CANON.get(raw.title(), raw.title())
        if name not in _C2_RES_NAMES or qty <= 0:
            return None
        out[name] = out.get(name, 0) + qty
    return out


def _parse_offer_body(body: str) -> Optional[Dict[str,Dict[str,int]]]:
    """
    Split '[Offer: ...]' body at '->' and return
        {'offered_resources': {...}, 'requested_resources': {...}}
    or None if ill-formed.
    """
    body = ' '.join(body.split())               # squash whitespace / linebreaks
    body = re.sub(r'[.,!?]+$', '', body)        # trailing punctuation
    body = re.sub(r'^(i\s+(?:give|offer)\s+)', '', body, flags=re.I)
    parts = re.split(r'\s*->\s*', body)
    if len(parts) != 2:
        return None
    offered = _parse_resource_list(parts[0])
    requested = _parse_resource_list(parts[1])
    if not offered or not requested:
        return None
    return {"offered_resources": offered, "requested_resources": requested}


def _has_resources(player_inv: Dict[str,int], costs: Dict[str,int]) -> bool:
    return all(player_inv.get(r, 0) >= q for r, q in costs.items())



class SettlersOfCatanEnv(ta.Env):
    roles = {0: "Red", 1: "White", 2: "Blue", 3: "Orange"}
    pids_from_roles = {"red": 0, "white": 1, "blue": 2, "orange": 3}
    def __init__(self, player_move_allowance: int=10, max_turns: int=200):
        self.game_moves = None
        self.player_move_allowance = player_move_allowance
        self.max_turns = max_turns


    def reset(self, num_players: int, seed: Optional[int]=None):
        assert num_players == 4, f"Environment is hard-coded for exactly four players. Received {num_players} players on reset."
        self.state = ta.MinimalMultiPlayerState(num_players=num_players, max_turns=self.max_turns, seed=seed)
        self.board = Board.build_standard()
        game_state = {
            "eliminated_players": set(), "move_allowance": self.player_move_allowance, "move_count": 0, "turn_done": False, "turn_phase": "action",
            "negotiation_partner": None, "trade_offer": None
        }
        self.state.reset(game_state=game_state, role_mapping=self.roles, player_prompt_function=self._prompt)
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
        self.game_moves = self.board._viable_moves(player)
        len_game_moves = len(self.game_moves)
        self.game_moves += [(len_game_moves+1, f"Negotiate.", None), (len_game_moves+2, f"Nothing.", None)]
        move_block = "\n".join(f"'[{idx}]'\t-  {desc}" for idx, desc, _ in self.game_moves) 
        hand_cards = '\n\t'.join(f'{k.name.lower()}: {v}' for k,v in player.hand.items())
        remaining_turn_moves = self.state.game_state["move_allowance"] - self.state.game_state["move_count"]
        message = "\n".join([
            f"{'='*24}  {colour.name}  {'='*24}", "Scores\n───────", "\n".join(score_lines), "", "Board\n──────", render_board(self.board),
            "", f"Your hand cards are:\n\t{hand_cards}", "", "Viable moves\n────────────", move_block, "Please select on of the viable actions by returning '[idx]' as part of your action."
            f"You have {remaining_turn_moves} moves left in your turn."
        ])
        self.state.add_observation(to_id=cpid, message=message, observation_type=ta.ObservationType.GAME_BOARD)

    def _handle_invalid(self, reason):
        player_terminated = self.state.set_invalid_move(reason=reason)
        if player_terminated:
            pid = self.state.current_player_id
            self.state.add_observation(message=f"Player {pid} ({self.roles[pid]}) has been eliminated because of repeated invalid moves.", observation_type=ta.ObservationType.GAME_ADMIN)
            return True
        return False

    def _rotate_players(self, force: bool):
        # check for the next non eliminated player
        _next = lambda x: (x+1)%self.state.num_players
        next_pid = _next(self.state.current_player_id)
        while next_pid != self.state.current_player_id:
            if next_pid not in self.state.game_state["eliminated_players"]:
                self.state.manually_set_current_player_id(new_player_id=next_pid, force=force) # set next player
                self.state.game_state["turn_done"] = False; self.state.game_state["move_count"] = 1
                self.state.game_state["turn_phase"] = "action"
                return
            else: next_pid = _next(next_pid)
        # if we reach here, no more alive players. End game 
        self._determine_winner()
        return

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        # self.state.add_observation(from_id=self.state.current_player_id, to_id=self.state.current_player_id, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)
        colour = self.board.str_to_enum(color_str=self.roles[self.state.current_player_id])
        # if self.game_moves is not None:
        match self.state.game_state["turn_phase"]: 
            case "action":
                m = re.search(r'\[(\d+)\]', action)
                print(m)
                if m is None: self.state.set_invalid_move(reason=f"No action found."); return self.state.step()
                act = int(m.group(1))
                if act > len(self.game_moves) or act <=0: 
                    if self._handle_invalid(reason="Selected action index is out of bounds. Please select from the list."):
                        self._rotate_players(force=True)
                        return 
                    
                elif act == len(self.game_moves): # skip turn selected
                    self.state.add_observation(message=f"Player {self.state.current_player_id} ({self.roles[self.state.current_player_id]}) ends his turn.", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)
                    self.state.game_state["turn_done"] = True

                elif act == len(self.game_moves)-1: # player selectes negotiation
                    self.state.game_state["move_count"] += 1
                    self.state.game_state["turn_phase"] = "negotiation_start"
                    pid_options = ", ".join([f"'[{pid}]'/'[{self.roles[pid]}]'" for pid in range(self.state.num_players) if (pid not in self.state.game_state["eliminated_players"] and pid != self.state.current_player_id)])
                    print("OPTIONS", pid_options)
                    self.state.add_observation(to_id=self.state.current_player_id, message=f"You selected action [{len(self.game_moves)-1}] (Negotiation). Please select a player you would like to negotiation with. The options are: {pid_options}. Please select exactly one.", observation_type=ta.ObservationType.GAME_MESSAGE)
                    return self.state.step(rotate_player=False)
                
                else: # player selected a game action
                    selected = next(m for m in self.game_moves if m[0] == act)
                    ok, err = self.board.execute_action(colour, selected[2])
                    # TODO addd observation of what the player did
                    self._render_board_state()
                    self.state.game_state["move_count"] += 1

            case "negotiation_start":
                self._negotiation_partner_selection(action=action)
                # check if player submitted a valid option and handle invalid move otherwise
                # TODO evaluate the selection by the player of whom to negotiate with 
                pass 

            case "negotiation":
                # TODO actual communication and negotiation between the two players
                pass

        # rotate player, roll dice, show board
        # pid = self.state.next_alive_player()
        # self.state.manually_set_current_player_id(new_player_id=pid)
        if self.state.game_state["turn_done"]:
            self._roll_dice()
            self._render_board_state()

        return self.state.step(rotate_player=False)


    def _negotiation_partner_selection(self, action: str):
        # m = re.compile(r'(?i)(?:\[\s*([0123]|red|white|blue|orange)\s*]').search(action)
        m = re.compile(r'(?i)(?:\[\s*([0123]|red|white|blue|orange)\s*\])').search(action)
        print(m)
        print(m.group(1).lower())

        pid_options = [pid for pid in range(self.state.num_players) if (pid not in self.state.game_state["eliminated_players"] and pid != self.state.current_player_id)]

        if not m: pass; return False # none found  # TODO
        choice = m.group(1).lower()
        if choice in self.pids_from_roles.keys():
            choice = self.pids_from_roles[choice]
        try:
            choice = int(choice)
        except Exception as e:
            print(f"Exception, {e}")
        print(type(choice))
        colors = [self.roles[pid] for pid in pid_options]
        if choice not in pid_options+colors: pass ; return False # not a valid selection # TODO

        # convert to pid choice 
        if choice in colors: choice = self.pids_from_roles[choice]
        self.state.game_state["negotiation_partner"] = choice
        negotiation_explanation = "You can converse freely and make trade offers int he following format: '[Offer: 3 Sheep, 2 Ore -> 5 Brick, 2 Sheep]': [Offer: Offered Resources -> Requested Resources]. When you receive a trade offer you can '[accept]' or '[deny]' it."
        self.state.add_observation(to_id=self.state.current_player_id, message=f"You have selected Player {choice} ({self.roles[choice]}) to negotiation with. {negotiation_explanation}. When you are done negotiating, please include '[done]' your response. You may now send your first message.", observation_type=ta.ObservationType.GAME_MESSAGE)
        self.state.add_observation(to_id=choice, message=f"Player {self.state.current_player_id} ({self.roles[self.state.current_player_id]}) selected you to negotiate with. {negotiation_explanation}.", observation_type=ta.ObservationType.GAME_MESSAGE)


    def _negotiation_step(self, action: str):
        """ Handle chat / offers / accept / deny / done while in phase 'negotiation' """
        gs = self.state.game_state
        me = self.state.current_player_id
        opp = gs["negotiation_partner"]

        # 1) [Done] ends negotiation immediately for BOTH players
        if _NEGO_DONE_RE.search(action):
            gs["turn_phase"] = "action"
            gs["move_count"] += 1
            gs["negotiation_partner"] = None
            gs["current_offer"] = None
            self.state.add_observation(message="Negotiation finished.", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)
            return # TODO rotate to correct player and phase

        # 2) Accept / Deny an existing offer (if I'm the receiver)
        if gs.get("current_offer") and gs["current_offer"]["to_player"] == me:
            if _NEGO_ACCEPT_RE.search(action):
                self._execute_trade_accept()
                return
            elif _NEGO_DENY_RE.search(action):
                self.state.add_observation(message=f"Player {me} denied the trade offer.", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)
                gs["current_offer"] = None

        # 3) Look for a NEW offer (only one active at a time)
        if not gs.get("current_offer"):
            offer_m = _NEGO_OFFER_RE.search(action)
            if offer_m:
                body = offer_m.group(1)
                parsed = _parse_offer_body(body)
                if parsed and _has_resources(self.board.players[self.board.str_to_enum(self.roles[me])].hand, parsed["offered_resources"]):
                    gs["current_offer"] = {"from_player": me, "to_player": opp, **parsed}
                    self.state.add_observation(message=f"Player {me} offered to Player {opp}: {body}", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)
                else:
                    self._handle_invalid("Malformed or unaffordable offer.")
                    return
        # just chatting
        self.state.add_observation(from_id=me, to_id=opp, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)


    def _execute_trade_accept(self):
        """Called only when receiver sent [Accept]."""
        gs = self.state.game_state
        offer = gs["current_offer"]
        giver_pid = offer["from_player"]
        taker_pid = offer["to_player"]

        giver_c = self.board.str_to_enum(self.roles[giver_pid])
        taker_c = self.board.str_to_enum(self.roles[taker_pid])
        giver_pl = self.board.players[giver_c]
        taker_pl = self.board.players[taker_c]

        if not (_has_resources(taker_pl.hand, offer["requested_resources"]) and _has_resources(giver_pl.hand, offer["offered_resources"])):
            self._handle_invalid("Trade failed: resources missing.")
            gs["current_offer"] = None
            return

        # transfer resources
        for res, qty in offer["offered_resources"].items():
            giver_pl.hand[res]  -= qty
            taker_pl.hand[res]  += qty
        for res, qty in offer["requested_resources"].items():
            taker_pl.hand[res]  -= qty
            giver_pl.hand[res]  += qty

        self.state.add_observation(message=f"Trade executed: Player {giver_pid} → {taker_pid} (offered {offer['offered_resources']}  /  requested {offer['requested_resources']}).", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)
        gs["current_offer"] = None


