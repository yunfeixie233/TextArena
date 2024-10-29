from typing import Any, Dict, Optional, Tuple
import random
import re
import textarena as ta

import nltk
from nltk.corpus import words
from nltk import pos_tag

nltk.download("words")
nltk.download("averaged_perceptron_tagger_eng")

class TwentyQuestionsEnv(ta.Env):
    """
    Twenty Questions game environment.
    """

    def __init__(
        self, 
        hardcore: Optional[bool] = False,
        gamemaster_class: ta.JudgeVote = ta.game_makers.GPTGamemasterAction,
    ):
        """
        Initialize the environment.
        
        Args:
            gamemaster_class: The gamemaster class to use
        """
        self.environment_name = "TwentyQuestions"
        self.hardcore = hardcore

        ## intitialise the game state
        self.state = ta.State(
            num_players=1,
            render_keys=["rendered_text"],
            max_turns=21
        )

        ## init the gamemaster
        self.gamemaster = gamemaster_class(
            options=["Yes", "No", "I don't know"],
        )

        ## load the word list
        if self.hardcore:
            self.word_list = self._load_word_list(words.words("en"))
        else:
            self.word_list = self._load_word_list(words.words("en-basic"))
        

    def reset(
        self,
        seed: Optional[int] = None,
    ) -> Optional[ta.Observations]:
        """
        Reset the environment.

        Args:
            seed: Random seed for the environment.

        Returns:
            Observations: Initial observations.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        ## load the game word
        self.game_word = random.choice(self.word_list)

        ## update the gamemaster
        initial_context = (
            f"You are the gamemaster for the game of '20 Questions'.\n"
            f"You will provide responses to the players' questions that guides them into guessing the target word: {self.game_word}\n"
        )
        self.gamemaster.set_initial_context(initial_context=initial_context)
        
        ## reset the game state
        return self.state.reset(
            game_state={
                "target_word": self.game_word,
                "rendered_text": self._render_text() ## TODO: Implement this function
            },
            player_prompt_function=self._generate_player_prompt
        )
    
    def _generate_player_prompt(
        self,
        player_id: int,
    ) -> str:
        """
        Generate the initial prompt for a player.
        
        Args:
            player_id: The player's ID (0 or 1).
            
        Returns:
            str: The initial prompt for the player.
        """
        prompt = (
            f"You are Player {player_id}. You are playing 20 Questions ({'Hardcore' if self.hardcore else 'Basic'}).\n"
            "The gamemaster has chosen one word. You have to guess that word by asking yes-or-no questions.\n"
            "The game will last for a maximum of 20 questions. After 20 questions, the gamemaster will prompt you to make a guess.\n"
            "You may ask your question in any manner.\n"
            "But, to make your final word guess, ensure that you wrap it with square brackets, e.g. [plane].\n"
            "As you play, the history of your questions and gamemaster's responses will be displayed."
        )

        return prompt
    
    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[ta.Observations],
        Optional[ta.Rewards],
        bool,
        bool,
        ta.Info
    ]:
        """
        Take a step in the environment.
        
        Args:
            player_id: The player's ID.
            action: The action taken by the player.
            
        Returns:
            Tuple: Observations, rewards, truncated, terminated, and info.
        """

        ## update the observation
        self.state.add_observation(
            from_id=player_id,
            to_id=-1,
            message=action,
            for_logging=True
        )

        ## validate the action
        action_search_pattern = re.compile(r"\[([a-zA-Z]+)\]") # e.g. [plane]
        action_match = action_search_pattern.search(action)

        if not action_match:
            ## if the action is not a guess, then it is a question
            gamemaster_response = self._generate_gamemaster_response(action)
            if self.state.turn == self.state.max_turns-2:
                gamemaster_response += "\nYou have run out of questions. What is your final guess?"
            self.state.add_observation(
                from_id=-1,
                to_id=player_id,
                message=gamemaster_response,
                for_logging=True
            )

        else:
            ## if the action is a guess
            action_text = action_match.group(1).lower()
            if action_text == self.game_word:
                self.state.set_winners(
                    player_ids=[player_id],
                    reason=f"Congratulations! Player {player_id} guessed the word."
                )
            else:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"Invalid guess. Player {player_id} guessed incorrectly."]
                    )

            self.state.game_state["rendered_text"] = self._render_text() ## TODO: Implement this function

        return self.state.step()

    def _generate_gamemaster_response(self, question: str) -> str:
        """
        Generate a response from the gamemaster to a player's question.
        
        Args:
            question: The question asked by the player.
            
        Returns:
            str: The response from the gamemaster.
        """
        ## generate a random response
        responses = self.gamemaster.respond_to_action(question)

        return responses
    
    def _render_text(self) -> str:
        """
        Render the game state.
        
        Returns:
            str: The rendered game state.
        """
        return f"Game word: {self.game_word}"
    
    def render(self):
        """
        Render the game state.
        """
        print(self.state.game_state["rendered_text"])

    def _load_word_list(self, word_list: list) -> list:
        """
        Load the word list for the game.

        Args:
            word_list: The word list to load.

        Returns:
            list: The loaded word list.
        """
        # NN: Noun
        return [word for word in word_list if pos_tag([word])[0][1] in ["NN"]]

