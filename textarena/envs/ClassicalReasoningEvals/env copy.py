import re, random
import importlib.resources
from typing import Any, Dict, List, Tuple, Optional, Callable, Union

import textarena as ta

try:
    import latex2sympy2
except ImportError:
    raise ImportError(
        "latex2sympy2 required for the ClassicalReasoningEvals environment. "
        "Install it with: pip install latex2sympy2"
    )


class ClassicalReasoningEvalsEnv(ta.Env):
    """ TODO """
    
    def __init__(
        self, 
        file_name: str,
        n_samples: Optional[int] = None
    ):
        self.file_name = file_name 
        self.n_sample = n_samples

        # load the dataset
        self._load_dataset()

        print(self.dataset[0].keys()) ## 'question', 'answer', 'idx'


    def _load_dataset(self):
        """
        Load dataset from the specified file in the textarena package's data directory.
        If n_sample is specified, randomly select that many samples from the dataset.
        """
        try:
            # Split the file path correctly
            path_parts = self.file_name.split('/')
            dataset_dir = path_parts[0]
            file_name = '/'.join(path_parts[1:])
            
            # Get the base package path
            package_path = "textarena.envs.ClassicalReasoningEvals.data"
            
            # Use importlib.resources to access the file
            data_pkg = importlib.import_module(f"{package_path}.{dataset_dir}")
            resource_path = importlib.resources.files(data_pkg) / file_name
            
            with open(resource_path, 'r') as f:
                # Parse the file based on extension
                if file_name.endswith('.jsonl'):
                    import json
                    dataset = [json.loads(line) for line in f if line.strip()]
                elif file_name.endswith('.json'):
                    import json
                    dataset = json.load(f)
                else:
                    # Default case: read as text
                    dataset = f.readlines()
            
            # If n_sample is specified, randomly select that many samples
            if self.n_sample is not None and self.n_sample < len(dataset):
                dataset = random.sample(dataset, self.n_sample)
            
            # turn it into an iterator
            self.total_questions = len(dataset)
            self.questions_seen = 0
            self.dataset_iter = iter(dataset)

        except Exception as e:
            raise ValueError(f"Failed to load dataset from {self.file_name}: {e}")

    def reset(self, num_players: int, seed: Optional[int]=None):
        """ TODO """
        self.state = ta.State(num_players=num_players, min_players=1, max_players=1, seed=seed)
        self.state.reset(seed=seed, game_state={"correct": 0, "count": 0})

        # set the first question
        self._show_next_question()

    def _show_next_question(self):
        """ TODO """
        if self.questions_seen >= self.total_questions:
            # return rewards 
            accuracy = self.state.game_state["correct"] / self.state.game_state["count"] if self.state.game_state["count"] > 0 else 0
            reason = f"Completed all questions with accuracy: {accuracy:.2f}"
            self.state.set_custom_game_outcome(player_reward_dict={0: accuracy}, reason=reason)
            return

         try:
            # Get next item from dataset
            item = next(self.dataset_iter)
            # Extract question and answer from the dictionary
            self.question = item['question']
            self.answer = item['answer']
            self.questions_seen += 1
            
            # Add question to state
            self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=self.question)
            return True
        except StopIteration:
            # Handle unexpected end of iterator
            self.questions_seen = self.total_questions
            return self._show_next_question()  # Recursively call to handle the end case


    def _check_answer(self, submitted_answer: str) -> bool:
        """
        Check if the submitted answer is correct.
        This can be extended to use more sophisticated matching from the LLM harness.
        """
        # Basic exact match
        if submitted_answer.strip() == self.answer.strip():
            return True
        
        # Basic numeric answer extraction and comparison
        # This handles cases where the answer is a number within text
        try:
            # Extract numbers from both answers
            submitted_numbers = re.findall(r'-?\d+\.?\d*', submitted_answer)
            correct_numbers = re.findall(r'-?\d+\.?\d*', self.answer)
            
            if submitted_numbers and correct_numbers:
                # Compare the first extracted number
                return float(submitted_numbers[0]) == float(correct_numbers[0])
        except:
            pass
        
        # Add more sophisticated matching here if needed
        
        return False


    def step(self, action: str) -> Tuple[bool, ta.Info]:
        # match action to answer
        correct = self._check_answer(submitted_answer=action)

        # log the results
        self.state.info["correct"] = correct 
        self.state.game_state["correct"] += int(correct)
        self.state.game_state["count"] += 1
        self.state.info["current_accuracy"] = self.state.game_state["correct"] / self.state.game_state["count"]


        # get mext question
        self._show_next_question()
        
        return self.state.step()