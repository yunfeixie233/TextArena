""" Truth and Deception Game Environment """

import os
import re
import json 
import random  
from typing import Optional, Tuple, Dict, Any

import textarena as ta 

class TruthAndDeceptionEnv(ta.Env):
    """ Environment for Truth and Deception Game """
    def __init__(self, max_turns: Optional[int]=5, data_path: Optional[str]=None):
        """
        Initialize the Truth and Deception game.

        Roles:
            - Player 0 is the deceiver
            - Player 1 is the guesser

        Args:
            max_turns (int): Maximum number of conversation turns.
            data_path (str): Path to the JSON file containing the facts.
        """
        # Enforce even number of turns
        assert max_turns%2==0, \
            f"Please use an even number of max turns. Current max_turns: {max_turns}"


        # load facts
        self._load_facts(data_path=data_path)


        # Initialize game state 
        self.state = ta.State(
            num_players=2, 
            max_turns=max_turns,
            check_truncated=False,
            role_mapping={0: "Deceiver", 1: "Guesser"}
        )


        # Define regex patterns
        self.guess_fact1_pattern = re.compile(r"\[Fact 1\]", re.IGNORECASE)
        self.guess_fact2_pattern = re.compile(r"\[Fact 2\]", re.IGNORECASE)

        self.board_state_render = ta.envs.two_player.TruthAndDeception.render.GameStateRender


    def _load_facts(self, data_path: Optional[str]) -> None:
        """Load the facts from the specified JSON file.

        Args:
            data_path (str): Path to the JSON file containing the facts.
        """
        if data_path is None:
            data_path = os.path.join(
                "textarena", "envs", "two_player", "TruthAndDeception", "facts.json"
            )

        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Facts data file not found at: {data_path}")

        with open(data_path, "r", encoding="utf-8") as file:
            self.facts_data = json.load(file)



    def reset(self, seed: Optional[int]=None) -> Optional[ta.Observations]:
        """Reset the game to its initial state.

        Args:
            seed (Optional[int]): Seed for random number generator to ensure reproducibility.

        Returns:
            ta.Observations: Initial prompts for both players.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        # Select a random set of facts
        selected_facts = random.choice(self.facts_data)

        # Randomize the order in which the facts are presented
        facts = [
            (selected_facts["facts"]["fact1"], selected_facts["correct_fact"]=="fact1"),
            (selected_facts["facts"]["fact2"], selected_facts["correct_fact"]=="fact2"),
        ]
        random.shuffle(facts)

        return self.state.reset(
            game_state={
                "fact1": {"fact": facts[0][0], "is_correct": facts[0][1]},
                "fact2": {"fact": facts[1][0], "is_correct": facts[1][1]},
                # set the gamestate facts for rendering
                "correct_fact": facts[0][0] if facts[0][1] else facts[1][0],
                "wrong_fact": facts[0][0] if facts[1][1] else facts[1][0]
            },
            player_prompt_function=self._generate_player_prompt
        )

    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        """Generate the initial prompt for a player.

        Args:
            player_id (int): The ID of the player (0 for Deceiver, 1 for Guesser).
            game_state (Dict[int, Any]): The current game state containing facts.

        Returns:
            str: The initial prompt message for the player.
        """
        prompt = f"You are Player {player_id}, and you are the {self.state.role_mapping[player_id]} in the 'Truth and Deception' game.\n"

        if self.state.role_mapping[player_id] == "Deceiver":
            prompt += (
                f"You know which of the following two facts is correct:\n"
                f"Fact 1: {game_state['fact1']['fact']} ({'correct' if game_state['fact1']['is_correct'] else 'wrong'})\n"
                f"Fact 2: {game_state['fact2']['fact']} ({'correct' if game_state['fact2']['is_correct'] else 'wrong'})\n"
                "Your goal is to convince the other player to choose the incorrect fact.\n"
                f"You will have a conversation for {self.state.max_turns} turns.\n"
                "After that, the other player will make their guess.\n"
                "On your turn, simply type your message."
            )

        elif self.state.role_mapping[player_id] == "Guesser":
            prompt += (
                f"You need to determine which of the following two facts is correct:\n"
                f"Fact 1: {game_state['fact1']['fact']}\n"
                f"Fact 2: {game_state['fact2']['fact']}\n"
                f"You will have a conversation with the other player for {self.state.max_turns} turns.\n"
                "After that, you will make your guess.\n"
                "On your turn, simply type your message."
            )

        else:
            # unexpected
            raise ValueError(f"Unexpected role mapping: {self.state.role_mapping[player_id]}. Expected 'Deceiver' or 'Guesser'.")

        return prompt 

    def get_current_player_id(self):
        return self.state.current_player

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[ta.Observations], # Observations: Dict[int, Tuple[int, str]]
        Optional[ta.Rewards], # Rewards: Dict[int, int]
        bool, # Truncated
        bool, # Terminated
        ta.Info, # Info: Optional[Dict[str, Any]]
    ]:
        """
        Process the player's action.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The player's move (column number).

        Returns:
            tuple: (observations, rewards, truncated, terminated, info)
        """
        # check the player_id and action fromat
        self.state.check_action_format(
            action=action,
            player_id=player_id
        )

        # update the observations and log the action
        self.state.add_observation(
            from_id=player_id,
            to_id=-1, # Broadcast to all
            message=action,
            for_logging=True
        )

        # check if the guessing phase has started
        if self.state.turn == self.state.max_turns-2:
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1, # Broadcast to all
                message="Now guess which of the two facts are correct by returning [Fact 1] or [Fact 2].",
                for_logging=True,
            )

        elif self.state.turn == self.state.max_turns-1:
            if self.guess_fact1_pattern.search(action) or self.guess_fact2_pattern.search(action):
                # evaluate guess
                if (
                    self.guess_fact1_pattern.search(action)
                    and self.state.game_state["fact1"]["is_correct"]
                ) or (
                    self.guess_fact2_pattern.search(action)
                    and self.state.game_state["fact2"]["is_correct"]
                ):
                    # correct guess
                    self.state.set_winners(
                        player_ids=[player_id],
                        reason=f"Player {player_id} guessed correct fact."
                    )
                else:
                    # wrong guess
                    self.state.set_winners(
                        player_ids=[1-player_id],
                        reason=f"Player {player_id} guessed the wrong fact."
                    )
            else:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"Player {player_id} did not make their guess in the correct format."]
                )

        return self.state.step()

    def render(self):
        """
        Render the current game state.
        """
        print(f"Turn: {self.state.turn}/{self.state.max_turns}")
        print("Game Logs:")
        for sender_id, message in self.state.logs:
            if sender_id == -1:
                print(f"[GAME]: {message}")
            else:
                print(f"Player {sender_id}: {message}")
        print("\n")


            