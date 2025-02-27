import re, random
import importlib.resources
from typing import Any, Dict, List, Tuple, Optional, Callable, Union
import multiprocessing
from math import isclose
from collections import defaultdict

import textarena as ta

try:
    import sympy
    from sympy import simplify, N
    from sympy.parsing.sympy_parser import parse_expr
    from sympy.parsing.latex import parse_latex
    import latex2sympy2
    from latex2sympy2 import latex2sympy
except ImportError:
    raise ImportError(
        "sympy and latex2sympy2 required for the ClassicalReasoningEvals environment. "
        "Install it with: pip install sympy latex2sympy2"
    )


class ClassicalReasoningEvalsEnv(ta.Env):
    """ TODO """
    
    def __init__(self, file_name: str, n_samples: Optional[int] = None):
        self.file_name = file_name 
        self.n_sample = n_samples

        # load the dataset
        self._load_dataset()

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
                    self.dataset = [json.loads(line) for line in f if line.strip()]
                elif file_name.endswith('.json'):
                    import json
                    self.dataset = json.load(f)
                else:
                    # Default case: read as text
                    self.dataset = f.readlines()
            
            # If n_sample is specified, randomly select that many samples
            if self.n_sample is not None and self.n_sample < len(self.dataset):
                self.dataset = random.sample(self.dataset, self.n_sample)
            
            # turn it into an iterator
            self.total_questions = len(self.dataset)
            self.questions_seen = 0
            self.dataset = iter(self.dataset)

        except Exception as e:
            raise ValueError(f"Failed to load dataset from {self.file_name}: {e}")

    def reset(self, num_players: int, seed: Optional[int]=None):
        """ TODO """
        self.state = ta.State(num_players=num_players, min_players=1, max_players=1)
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
            return False

        try:
            # Get next item from dataset
            item = next(self.dataset)
            # Extract question and answer from the dictionary
            self.question = item['question']
            self.answer = item['answer']
            self.questions_seen += 1
            
            # Add question to state
            self.state.add_observation(from_id=ta.GAME_ID, to_id=self.state.current_player_id, message=str(self.question))
            return True
        except StopIteration:
            # Handle unexpected end of iterator
            self.questions_seen = self.total_questions
            return self._show_next_question()  # Recursively call to handle the end case


    def _check_answer(self, submitted_answer: str) -> bool:
        """
        Check if the submitted answer is correct using the math_eval function
        which handles various mathematical expression formats.
        """
        try:
            return math_eval(submitted_answer, self.answer)
        except Exception as e:
            # Fallback to basic comparison if math_eval fails
            print(f"Math evaluation failed: {e}")
            return submitted_answer.strip() == self.answer.strip()

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        # match action to answer
        correct = self._check_answer(submitted_answer=action)

        # log the results
        self.state.info["correct"] = correct 
        self.state.game_state["correct"] += int(correct)
        self.state.game_state["count"] += 1
        self.state.info["current_accuracy"] = self.state.game_state["correct"] / self.state.game_state["count"]

        # get next question
        self._show_next_question()
        
        return self.state.step()


def choice_answer_clean(pred: str):
    """Clean and standardize multiple choice answers."""
    pred = pred.strip("\n").rstrip(".").rstrip("/").strip(" ").lstrip(":")
    # Clean the answer based on the dataset
    tmp = re.findall(r"\b(A|B|C|D|E)\b", pred.upper())
    if tmp:
        pred = tmp
    else:
        pred = [pred.strip().strip(".")]
    pred = pred[-1]
    # Remove the period at the end, again!
    pred = pred.rstrip(".").rstrip("/")
    return pred


def parse_digits(num):
    """Parse string representations of numbers, including percentages."""
    num = re.sub(",", "", str(num))
    try:
        return float(num)
    except:
        if num.endswith("%"):
            num = num[:-1]
            if num.endswith("\\"):
                num = num[:-1]
            try:
                return float(num) / 100
            except:
                pass
    return None


def is_digit(num):
    """Check if a string can be parsed as a number."""
    return parse_digits(num) is not None


def str_to_pmatrix(input_str):
    """Convert a string matrix representation to LaTeX pmatrix format."""
    input_str = input_str.strip()
    matrix_str = re.findall(r"\{.*,.*\}", input_str)
    pmatrix_list = []

    for m in matrix_str:
        m = m.strip("{}")
        pmatrix = r"\begin{pmatrix}" + m.replace(",", "\\") + r"\end{pmatrix}"
        pmatrix_list.append(pmatrix)

    return ", ".join(pmatrix_list)


def symbolic_equal(a, b):
    """
    Check if two expressions are symbolically equal using sympy.
    Attempts multiple parsing methods.
    """
    def _parse(s):
        for f in [parse_latex, parse_expr, latex2sympy]:
            try:
                return f(s.replace("\\\\", "\\"))
            except:
                try:
                    return f(s)
                except:
                    pass
        return s

    a = _parse(a)
    b = _parse(b)

    # direct equal
    try:
        if str(a) == str(b) or a == b:
            return True
    except:
        pass

    # simplify equal
    try:
        if a.equals(b) or simplify(a - b) == 0:
            return True
    except:
        pass

    # equation equal
    try:
        if (abs(a.lhs - a.rhs)).equals(abs(b.lhs - b.rhs)):
            return True
    except:
        pass

    try:
        if numeric_equal(float(N(a)), float(N(b))):
            return True
    except:
        pass

    # matrix
    try:
        # if a and b are matrix
        if a.shape == b.shape:
            _a = a.applyfunc(lambda x: round(x, 3))
            _b = b.applyfunc(lambda x: round(x, 3))
            if _a.equals(_b):
                return True
    except:
        pass

    return False


def symbolic_equal_process(a, b, output_queue):
    """Helper function for timeout-based symbolic equality checking."""
    result = symbolic_equal(a, b)
    output_queue.put(result)


def call_with_timeout(func, *args, timeout=1, **kwargs):
    """Run a function with a timeout to prevent hanging."""
    output_queue = multiprocessing.Queue()
    process_args = args + (output_queue,)
    process = multiprocessing.Process(target=func, args=process_args, kwargs=kwargs)
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        return False

    return output_queue.get()


def numeric_equal(prediction: float, reference: float):
    """Compare numerical values with appropriate tolerance."""
    return isclose(reference, prediction, rel_tol=1e-4)


def math_eval(prediction: Union[bool, float, str], reference: Union[float, str], 
             include_percentage: bool = True, is_close: bool = True, 
             timeout: bool = True) -> bool:
    """
    Evaluate if a mathematical prediction is equal to a reference answer.
    
    This function supports various formats including:
    - Exact string matching
    - Multiple choice answers
    - Numerical equality with tolerance
    - Symbolic mathematical equality
    - Matrix and vector equality
    
    Take from: https://github.com/hkust-nlp/simpleRL-reason/blob/main/eval/grader.py

    Which is itself based on:
    - https://github.com/microsoft/ProphetNet/tree/master/CRITIC
    - https://github.com/openai/prm800k
    - https://github.com/microsoft/ToRA/blob/main/src/eval/grader.py
    - https://github.com/deepseek-ai/DeepSeek-Math/blob/main/evaluation/eval/eval_utils.py
    - 
    
    Args:
        prediction: The predicted answer to evaluate
        reference: The ground truth answer to compare against
        include_percentage: Whether to handle percentage values (e.g., 50% = 0.5 = 50)
        is_close: Whether to use approximate numeric equality
        timeout: Whether to apply a timeout for symbolic equality checking
        
    Returns:
        bool: True if the prediction is equal to the reference, False otherwise
    """
    # Handle None values
    if prediction is None or reference is None:
        return False
    
    # Exact string match
    if str(prediction.strip().lower()) == str(reference.strip().lower()):
        return True
    
    # Multiple choice handling
    if reference in ["A", "B", "C", "D", "E"] and choice_answer_clean(prediction) == reference:
        return True

    try:  # Numerical equality
        if is_digit(prediction) and is_digit(reference):
            prediction = parse_digits(prediction)
            reference = parse_digits(reference)
            # Handle percentage variants
            if include_percentage:
                gt_result = [reference / 100, reference, reference * 100]
            else:
                gt_result = [reference]
            
            for item in gt_result:
                try:
                    if is_close:
                        if numeric_equal(prediction, item):
                            return True
                    else:
                        if item == prediction:
                            return True
                except Exception:
                    continue
            return False
    except:
        pass

    # Handle empty predictions
    if not prediction and prediction not in [0, False]:
        return False

    # Prepare for symbolic comparison
    reference = str(reference).strip()
    prediction = str(prediction).strip()

    # Handle pmatrix format
    if "pmatrix" in prediction and not "pmatrix" in reference:
        reference = str_to_pmatrix(reference)

    # Handle basic bracket differences
    pred_str, ref_str = prediction, reference
    if (prediction.startswith("[") and prediction.endswith("]") and not reference.startswith("(")) or \
       (prediction.startswith("(") and prediction.endswith(")") and not reference.startswith("[")):
        pred_str = pred_str.strip("[]()")
        ref_str = ref_str.strip("[]()")
    
    # Strip braces for simple comparison
    for s in ["{", "}", "(", ")"]:
        ref_str = ref_str.replace(s, "")
        pred_str = pred_str.replace(s, "")
    if pred_str.lower() == ref_str.lower():
        return True

    # Handle arrays/vectors [a, b] vs. [c, d]
    if re.search(r"(\(|\[).+(\)|\])", prediction) is not None and \
       re.search(r"(\(|\[).+(\)|\])", reference) is not None:
        pred_parts = prediction[1:-1].split(",")
        ref_parts = reference[1:-1].split(",")
        if len(pred_parts) == len(ref_parts):
            if all([math_eval(pred_parts[i], ref_parts[i], include_percentage, is_close)
                   for i in range(len(pred_parts))]):
                return True
    
    # Handle matrices
    if ((prediction.startswith("\\begin{pmatrix}") or prediction.startswith("\\begin{bmatrix}")) and
        (prediction.endswith("\\end{pmatrix}") or prediction.endswith("\\end{bmatrix}")) and
        (reference.startswith("\\begin{pmatrix}") or reference.startswith("\\begin{bmatrix}")) and
        (reference.endswith("\\end{pmatrix}") or reference.endswith("\\end{bmatrix}"))):
        
        pred_begin = "\\begin{pmatrix}"
        pred_end = "\\end{pmatrix}"
        ref_begin = "\\begin{pmatrix}"
        ref_end = "\\end{pmatrix}"
        
        if "bmatrix" in prediction:
            pred_begin = "\\begin{bmatrix}"
            pred_end = "\\end{bmatrix}"
        if "bmatrix" in reference:
            ref_begin = "\\begin{bmatrix}"
            ref_end = "\\end{bmatrix}"
            
        pred_lines = [line.strip() for line in 
                      prediction[len(pred_begin):-len(pred_end)].split("\\\\") if line.strip()]
        ref_lines = [line.strip() for line in 
                     reference[len(ref_begin):-len(ref_end)].split("\\\\") if line.strip()]
        
        matched = True
        if len(pred_lines) == len(ref_lines):
            for pred_line, ref_line in zip(pred_lines, ref_lines):
                pred_parts = pred_line.split("&")
                ref_parts = ref_line.split("&")
                if len(pred_parts) == len(ref_parts):
                    if not all([math_eval(pred_parts[i], ref_parts[i], include_percentage, is_close)
                               for i in range(len(pred_parts))]):
                        matched = False
                        break
                else:
                    matched = False
                if not matched:
                    break
        else:
            matched = False
        if matched:
            return True

    # Handle equations with single equal sign
    if prediction.count("=") == 1 and reference.count("=") == 1:
        pred = prediction.split("=")
        pred = f"{pred[0].strip()} - ({pred[1].strip()})"
        ref = reference.split("=")
        ref = f"{ref[0].strip()} - ({ref[1].strip()})"
        if symbolic_equal(pred, ref) or symbolic_equal(f"-({pred})", ref):
            return True
    elif (prediction.count("=") == 1 and len(prediction.split("=")[0].strip()) <= 2 and 
          "=" not in reference):
        if math_eval(prediction.split("=")[1], reference, include_percentage, is_close):
            return True
    elif (reference.count("=") == 1 and len(reference.split("=")[0].strip()) <= 2 and 
          "=" not in prediction):
        if math_eval(prediction, reference.split("=")[1], include_percentage, is_close):
            return True

    # Full symbolic equality check with timeout option
    if timeout:
        if call_with_timeout(symbolic_equal_process, prediction, reference, timeout=3):
            return True
    else:
        if symbolic_equal(prediction, reference):
            return True

    return False