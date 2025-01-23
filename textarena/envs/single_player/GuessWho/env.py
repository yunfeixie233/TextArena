from typing import Any, Dict, Optional, Tuple
import random
import re
import textarena as ta
import json

class GuessWhoEnv(ta.Env):
    """
    Guess Who game environment
    """
    
    def __init__(
        self,
        gamemaster_class: ta.JudgeVote = ta.game_makers.GPTGamemasterAction,
    ):
        """
        Initialise the environment.
        
        Args:
            gamemaster_class: The gamemaster class to use
        """
        self.environment_name = "GuessWho"
        
        ## initialise the game state
        self.state = ta.State(
            num_players=1,
            max_turns=40
        )

        ## init the gamemaster
        self.gamemaster = gamemaster_class(
            options=["Yes", "No", "I don't know"],
        )

        ## load the character list
        with open('textarena/envs/single_player/GuessWho/characters.json') as f:
            self.characters = json.load(f)

    @property
    def offline_renderer(self):
        pass

    @property
    def terminal_render_keys(self):
        return ["rendered_text"]

    def reset(
        self,
        seed: Optional[int] = None,
    ) -> Optional[ta.Observations]:
        """
        Reset the environment.
        
        Args:
            seed: Random seed for the environment.

        Returns:
            The initial observations
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()
        
        ## select a random character
        self.target_character = random.choice(self.characters)

        ## update the gamemaster
        initial_context = (
            f"You are the gamemaster for the game of 'Guess Who'.\n"
            f"You will provide responses to the player's questions that guides them into guessing the target character with the following name and traits: {self.target_character}.\n"
        )
        self.gamemaster.set_initial_context(initial_context=initial_context)

        ## reset the game state
        return self.state.reset(
            game_state={
                "target_character": self.target_character,
                "rendered_text": self._render_text()
            },
            player_prompt_function=self._generate_player_prompt
        )

    def _generate_player_prompt(
        self, 
        player_id: int,
        game_state: Dict[int, Any]
    ) -> str:
        """
        Generate the player prompt.
        
        Args:
            player_id: The player ID
        
        Returns:
            The player prompt
        """
        prompt = (
            f"You are Player {player_id}. You are playing Guess Who.\n"
            "The gamemaster has chosen one target character from the list of characters that you will be shown below.\n"
            "You have to guess the target character by asking yes-or-no questions about the target character's traits.\n"
            "You can ask questions like 'Is the character male?' or 'Does the character have a beard?'.\n"
            "You can also guess the name of the target character at any time by ensuring that you wrap their name in square brackets, e.g. [Zach].\n"
            "As you play, the history of your questions and gamemaster's responses will be displayed."
            "Here is the list of characters you can ask questions about:\n"
        )

        prompt += self._characters_to_string()

        return prompt
    
    def _characters_to_string(
        self
    ) -> str:
        """
        Render the text for the game.
        
        Returns:
            The rendered text
        """
        formatted_descriptions = []
        for i, char in enumerate(self.characters, start=1):
            # Format the description in a narrative style
            accessories = ", ".join(char["accessories"]) if char["accessories"] else "no accessories"
            description = (
                f"{i}. {char['name']} is a {char['age_range']} {char['gender']} with {char['hair_style']} "
                f"{char['hair_color']} hair and {char['eye_color']} eyes. {char['name']} has a {char['complexion']} complexion, "
                f"{char['skin_tone']} skin tone, and {char['smile_type']} smile. They wear {accessories}, "
                f"have {char['facial_hair']} facial hair, and their clothing style is {char['clothing_style']}. "
                f"{char['name']} has {char['hair_texture']} hair texture, {char['eyewear_style']} glasses style, "
                f"a {char['nose_shape']} nose, {char['ear_size']} ears, and {char['cheek_features']} on their cheeks."
            )
            formatted_descriptions.append(description)
        
        # Join all descriptions into a single text block
        return "\n\n".join(formatted_descriptions)
    
    def step(
        self,
        action: str,
    ) -> Tuple[
        Optional[ta.Observations],
        Optional[ta.Rewards],
        bool,
        bool,
        ta.Info
    ]:
        """
        Process the player's action and update the environment state.

        Args:
            player_id (int): The ID of the player making the move.
            action (str): The action taken by the player.

        Returns:
            Observations: Observations for the player after the action.
            Rewards: Rewards for the player after the action.
            bool: Whether the game was truncated.
            bool: Whether the game is terminated.
            Info: Additional information about the game state
        """
        player_id = self.state.current_player_id
        
        ## update the observation
        self.state.add_observation(
            from_id=player_id,
            to_id=-1,
            message=action,
            for_logging=True
        )

        ## validate the action
        action_search_pattern = re.compile(r"\[([a-zA-Z]+)\]") # e.g. [zach]
        action_match = action_search_pattern.search(action)

        if not action_match:
            ## if the action is not a guess, then it is a question
            gamemaster_response = self._generate_gamemaster_response(action)
            
            self.state.add_observation(
                from_id=-1,
                to_id=player_id,
                message=gamemaster_response,
                for_logging=True
            )
        
        else:
            ## if the action is a guess
            action_text = action_match.group(1).lower()
            if action_text == self.target_character["name"].lower():
                self.state.set_winners(
                    player_ids=[player_id],
                    reason=f"Congratulations! Player {player_id} guessed the target character."
                )
            else:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"Invalid guess. Player {player_id} guessed incorrectly."]
                    )
            
            self.state.game_state["rendered_text"] = self._render_text()
        
        return self.state.step()
    
    def _generate_gamemaster_response(
        self,
        question: str
    ) -> str:
        """
        Generate the gamemaster's response to the player's question.
        
        Args:
            question: The question asked by the player
        
        Returns:
            The gamemaster's response
        """
        response = self.gamemaster.respond_to_action(question)
        
        return response
    
    def _render_text(self) -> str:
        """
        Render the target character and their traits.
        
        Returns:
            string: The rendered text
        """
        res = ""
        for key, value in self.target_character.items():
            res += f"{key}: {value}\n"
        return res
    
    def render(self):
        """
        Render the game state.
        """
        print(self.state.game_state["rendered_text"])

    


