import requests
import time
import warnings
from typing import Optional, Tuple, List, Dict, Any
import textarena as ta  # Ensure textarena is properly imported


class OnlineState:
    """ 
    TODO 
    A minimal state to make the online env compatible with most wrappers
    """
    def __init__(
        self,
        num_players: int,
        max_turns: Optional[int] = None,
        render_keys: Optional[List[str]] = None,
        role_mapping: Optional[Dict[int, str]] = {}
    ):
        self.num_players = num_players
        self.role_mapping = role_mapping
        self.render_keys = render_keys



class OnlineEnv(ta.Env):
    """
    Represents an online game environment for a model.

    Attributes:
        env_id (str): Environment ID.
        model_name (str): Name of the model.
        model_token (str): Authentication token for the model.
        game_id (str): ID of the current game.
        player_id (int): Player ID within the game.
    """

    def __init__(
        self,
        env_id: str,
        model_name: str,
        model_token: str,
        player_id: int,
        game_id: int,
        num_players: int,
    ):
        self.env_id = env_id 
        self.model_name = model_name 
        self.model_token = model_token 
        self.player_id = player_id
        self.game_id = game_id 
        self.done = False 

        self.state = OnlineState(
            num_players=num_players,
        )

        self.ID_TO_STR_DICT = {
            -1: "GAME",
            self.player_id: "You"
        }
        for player_nr in range(self.state.num_players):
            if player_nr != self.player_id:
                self.ID_TO_STR_DICT[player_nr] = f"Opponent {len(self.ID_TO_STR_DICT)-1}"

        self.most_recent_observations = []

    def _wait_until_player_turn(self) -> Dict[str, Any]:
        start_time = time.time()
        while True:
            turn_status = ta.api.check_turn(
                env_id=self.env_id,
                model_name=self.model_name,
                model_token=self.model_token,
                game_id=self.game_id,
                player_id=self.player_id
            )

            status = turn_status.get("status")
            # print(f"Turn status: {turn_status}")
            if status == "Your turn":
                return {"observation": turn_status.get("observation"), "done": self.done}
            elif status == "Not your turn":
                print(f"Waiting for turn...({time.time()-start_time:.0f}s)", end="\r")
                time.sleep(1)  # Wait before checking again
            elif status == "Game concluded":
                print(f"\nGame has concluded.")
                return {"observation": turn_status.get("observation"), "done": self.done}
            else:
                # Handle unexpected statuses
                raise Exception(f"Unexpected turn status: {status}")

    def reset(self, seed: Optional[int] = None):
        if seed is not None:
            warnings.warn("No seed should be provided when using the online environment.")

        # Wait until it's the player's turn
        result = self._wait_until_player_turn()
        self.observation = result["observation"]
        self.done = result["done"]


    def get_observation(self) -> Tuple[int, List[Tuple[int, str]]]:
        return self.player_id, self.observation


    def step(self, action: str) -> Tuple[bool, Optional[Dict[str, Any]]]:  

        if self.done:
            return True, None
        
        # Submit the action to the server
        result = ta.api.submit_step(
            env_id=self.env_id,
            model_name=self.model_name,
            model_token=self.model_token,
            game_id=self.game_id,
            action_text=action
        )
        print(f"\nAction submitted.")

        if result["done"]:
            self.done = True
            return True, None

        # Wait until it's the player's turn again
        result = self._wait_until_player_turn()
        self.observation = result["observation"]
        self.done = result["done"]

        return self.done, None


    def close(self):
        """ TODO """
        if not self.done:
            raise Exception(f"Should not .close() and ongoing game.")

        # check the results via api call
        result_status = ta.api.get_results(
            game_id=self.game_id,
            model_name=self.model_name,
            env_id=self.env_id 
        )
        current_elo_score = result_status['current_elo_score']
        prev_elo_score = result_status['prev_elo_score']
        if prev_elo_score is None:
            prev_elo_score = 1_000

        elo_delt_symb = "+" if current_elo_score>prev_elo_score else "-"
        abs_elo_delta = abs(current_elo_score-prev_elo_score)

        print("\n\n\n")
        print("="*30, f"[{result_status['outcome']}]", "="*30)
        print(f"Environment:\t {self.env_id}")
        print(f"Model Name: \t {self.model_name}")
        print(f"Player Nr.: \t {self.player_id}")
        print(f"Opponent(s):\t {result_status['opponent_names']}")
        print(f"Reason(s):  \t {result_status['reason']}")
        print(f"Prev. Elo:  \t {prev_elo_score}")
        print(f"New Elo:    \t {current_elo_score}")
        print(f"Elo Delta:  \t {elo_delt_symb}{abs_elo_delta}")
        print("="*(62+len(f"[{result_status['outcome']}]")))

        return None