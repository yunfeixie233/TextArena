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
        """
        Wait until it's the player's turn to act.

        Returns:
            Dict[str, Any]: Observations from the game environment and done status.
        """
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
            print(f"Turn status: {turn_status}")
            if status == "Your turn":
                observations = turn_status.get("observations")
                # process to return int key
                observations = {int(k): v for k, v in observations.items()}
                self.done = turn_status.get("done", False)
                self.most_recent_observations = observations[self.player_id]
                return {"observations": observations, "done": self.done}
            elif status == "Not your turn":
                print(f"Waiting for turn...({time.time()-start_time:.0f}s)", end="\r")
                time.sleep(1)  # Wait before checking again
            elif status == "Game concluded":
                print(f"\nGame has concluded.")
                observations = turn_status.get("observations")
                # process to return int key
                observations = {int(k): v for k, v in observations.items()}
                self.done = turn_status["done"]
                return {"observations": observations, "done": self.done}

            else:
                # Handle unexpected statuses
                raise Exception(f"Unexpected turn status: {status}")

    def reset(self, seed: Optional[int] = None) -> Optional[Dict[int, Tuple[int, str]]]:
        """
        Reset the environment. No seed should be provided for online environments.

        Args:
            seed (Optional[int], optional): Seed value. Should be None. Defaults to None.

        Returns:
            Optional[Dict[int, Tuple[int, str]]]: Initial observations after reset.
        """
        if seed is not None:
            warnings.warn("No seed should be provided when using the online environment.")
            # Proceed without using the seed

        # Wait until it's the player's turn to start
        result = self._wait_until_player_turn()

        return result["observations"]

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[Dict[int, Tuple[int, str]]],  # Observations
        Optional[Dict[int, int]],               # Rewards
        bool,                                    # Truncated
        bool,                                    # Terminated
        Optional[Dict[str, Any]]                # Info
    ]:  
        """
        Submit an action to the environment and wait for the next turn.

        Args:
            action (str): Action text to submit.

        Returns:
            Tuple[
                Optional[Dict[int, Tuple[int, str]]],
                Optional[Dict[int, int]],
                bool,
                bool,
                Optional[Dict[str, Any]]
            ]: Tuple containing observations, rewards, truncated, terminated, and info.
        """
        # Ensure the correct player is making the action
        assert self.player_id is not None, "Player ID is not set."

        if self.done:
            return None, None, self.done, self.done, None 
        
        # Submit the action to the server
        result = ta.api.submit_step(
            env_id=self.env_id,
            model_name=self.model_name,
            model_token=self.model_token,
            game_id=self.game_id,
            action_text=action
        )
        print(result["message"])
        if result["done"]:
            self.done = True
            return None, None, True, True, None

        # Wait until it's the player's turn again
        result = self._wait_until_player_turn()
        observations = result["observations"]
        self.done = result["done"]

        # for rendering
        # self.most_recent_action = action

        # Return the observations and done flags. Rewards and info are not handled here.
        return observations, None, self.done, self.done, None

    def print_results(self):
        """ TODO """
        if not self.done:
            raise Exception(f"You can't check the results before the game has concluded.")

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


    def render(self):
        """ TODO """
        for from_id, obs in self.most_recent_observations:
            print(f"\n[{self.ID_TO_STR_DICT[from_id]}] {obs}")
        
        
