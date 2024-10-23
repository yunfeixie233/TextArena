""" Debate Environment """
import textarena as ta 

import os, json, random
from typing import Optional, Dict, Tuple


class DebateEnv(ta.Env):
    """ Environment for the Debate game. """
    def __init__(
        self,
        max_turns: Optional[int] = 4,
        judge_class: ta.JudgeVote = ta.game_makers.GPTJudgeVote,
        num_judges: Optional[int] = 11,
        topics_path: Optional[str] = None,
    ):
        """
        Initialize the Debate game.

        Args:
            max_turns (int): Number of turns per player.
            judge_class (ta.JudgeVote): The judge object.
            num_judges (int): Number of judges evaluating the debate.
            topics_path (str): Path to the JSON file containing debate topics.
        """
        assert max_turns%2==0, \
            f"Please use an even number of max turns. Current max_turns: {max_turns}"

        self.environment_name = "Debate"

        # Load debate topics
        self._load_topics(topics_path)

        # initialize judges
        self.judge = judge_class(
            num_judges=num_judges,
            options=["Affirmative", "Negative"]
        )

        # Initialize game state
        self.state = ta.State(
            num_players=2,
            max_turns=max_turns,
            render_keys=["topic", "sides", "votes"]
        )

    def _load_topics(self, topics_path: Optional[str]):
        """
        Load debate topics from the JSON file.

        Args:
            topics_path (str): Path to the JSON file containing debate topics.
        """
        if topics_path is None:
            topics_path = os.path.join(
                "textarena", "envs", "two_player", "Debate", "topics.json"
            )

        if not os.path.exists(topics_path):
            raise FileNotFoundError(f"Debate topics file not found at {topics_path}")

        with open(topics_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "topics" not in data or not isinstance(data["topics"], list):
            raise ValueError(
                "Invalid format for debate topics JSON. Expected a key 'topics' with a list of topics."
            )

        self.topics = data["topics"]
        if not self.topics:
            raise ValueError("Debate topics list is empty.")
    
    def reset(
        self, seed: Optional[int] = None
    ) -> Optional[ta.Observations]:
        """
        Reset the Debate game to its initial state.

        Args:
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.

        Returns:
            Optional[ta.Observation]: Initial observations for both players as a dictionary.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        # Assign sides randomly
        affirmative_player_id = random.choice([0, 1])
        game_state = {
            "arguments": {0: [], 1:[]},
            "topic": random.choice(self.topics), # pick a random topic
            "sides": {
                affirmative_player_id: "Affirmative", 
                1-affirmative_player_id: "Negative"
            },
            "votes": {
                "pre-debate": {"Affirmative": 0, "Negative": 0},
                "post-debate": {"Affirmative": 0, "Negative": 0}
            }
        }

        game_state["votes"]["pre-debate"] = self._evaluate_debate(
            topic=game_state["topic"],
            debate_transcript=None,
        )

        return self.state.reset(
            game_state=game_state,
            player_prompt_function=self._generate_player_prompt,
        )


    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the initial prompt for a player based on their side.

        Args:
            player_id (int): The player's ID (0 or 1).

        Returns:
            str: The initial prompt for the player.
        """
        prompt = (
            f"You are Player {player_id} in the Debate game.\n"
            f"Topic: {self.state.game_state['topic']}\n"
            f"Your position: {self.state.game_state['sides'][player_id]}\n"
            f"You will have {self.state.max_turns} turns to present your arguments.\n"
            "On your turn, simply type your argument."
        )
        return prompt 

    def _evaluate_debate(
        self, 
        topic: str, 
        debate_transcript: Optional[str]=None
    ) -> Dict[str, int]:
        """
        Conduct evaluation by simulated judges.

        Args:
            debate_transcript (str): The transcript of the debate. If None, judges evaluate based on the topic only.

        Returns:
            Dict[str, int]: A dictionary with sides as keys and their corresponding (normalized) vote counts.
        """
        prompt = f"Debate Topic: {topic}\n"
        if debate_transcript:
            prompt += f"Debate Transcript:\n{debate_transcript}\n"
            prompt += "Based on the debate, please vote for either 'Affirmative' or 'Negative'. Provide only the side you vote for."
        else:
            prompt += "No debate has occurred yet. Please vote for either 'Affirmative' or 'Negative' based solely on the topic. Provide only the side you vote for."

        votes = self.judge.evaluate(
            context=prompt
        )
        return votes

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

        # record the debate argument
        self.state.game_state["arguments"][player_id].append(action)


        # Check if the debate is over
        if self.state.turn >= self.state.max_turns-1: # evaluate before turn limit
            winner_id = self._determine_debate_winner()
            if winner_id is None:
                # draw
                self.state.set_draw(reason="The judges' opinions did not change.")
            else:
                self.state.set_winners(
                    player_ids=[winner_id],
                    reason=f"Player {winner_id} wins by convincing the judges."
                )

        return self.state.step()

    def _determine_debate_winner(self) -> Optional[int]:
        """
        Determine the winner of the debate based on judge evaluations.

        Returns:
            Optional[int]: The player ID of the winner, or None if it's a draw.
        """
        # Compile the debate transcript for the judges
        debate_transcript = ""
        for i in range(len(self.state.game_state["arguments"][0])):
            if i < len(self.state.game_state["arguments"][0]):
                debate_transcript += f"Player 0 ({self.state.game_state['sides'][0]}): {self.state.game_state['arguments'][0][i]}\n"
            if i < len(self.state.game_state["arguments"][1]):
                debate_transcript += f"Player 1 ({self.state.game_state['sides'][1]}): {self.state.game_state['arguments'][1][i]}\n"

        # Conduct post-debate voting
        self.state.game_state["votes"]["post-debate"] = self._evaluate_debate(
            topic=self.state.game_state["topic"],
            debate_transcript=debate_transcript
        )

        # Calculate gains
        gain_affirmative = (
            self.state.game_state["votes"]["post-debate"]["Affirmative"]
            - self.state.game_state["votes"]["pre-debate"]["Affirmative"]
        )
        gain_negative = (
            self.state.game_state["votes"]["post-debate"]["Negative"]
            - self.state.game_state["votes"]["pre-debate"]["Negative"]
        )

        # Determine the winner
        if gain_affirmative > gain_negative:
            winner_side = "Affirmative"
        elif gain_negative > gain_affirmative:
            winner_side = "Negative"
        else:
            winner_side = None  # It's a tie

        if winner_side:
            winner_id = [
                pid
                for pid, side in self.state.game_state["sides"].items()
                if side == winner_side
            ][0]
        else:
            winner_id = None 

        return winner_id 

    def render(self):
        """
        Render the current game state to the console.
        """
        print(f"Turn: {self.state.turn}/{self.max_turns * 2}")
        print(f"Topic: {self.state.game_state['topic']}")
        print(f"Player Sides: {self.state.game_state['sides']}")
        print("\nGame Logs:")
        for sender_id, message in self.state.logs:
            if sender_id == ta.GAME_ID:
                print(f"[GAME]: {message}")
            else:
                print(f"[Player {sender_id}]: {message}")
        print("\n")
