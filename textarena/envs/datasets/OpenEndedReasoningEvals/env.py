import re, random, json
import importlib.resources
from typing import Any, Dict, List, Tuple, Optional, Callable, Union
import multiprocessing
from math import isclose
from collections import defaultdict, Counter

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
        "Install it with: 'pip install textarena[datasets]' OR 'pip install sympy latex2sympy2'"
    )


class OpenEndedReasoningEvalsEnv(ta.Env):
    def __init__(self, file_name: str, n_samples: Optional[int]=None):
        self.file_name = file_name 
        self.n_samples = n_samples

        # load the dataset
        self._load_dataset()

    def _load_dataset(self):
        """ Load dataset from the specified file in the textarena package's data directory If n_sample is specified, randomly select that many samples from the dataset """
        try:
            # Split the file path correctly
            path_parts = self.file_name.split('/')
            dataset_dir = path_parts[0]
            file_name = '/'.join(path_parts[1:])
            
            # Get the base package path
            package_path = "textarena.envs.datasets.OpenEndedReasoningEvals.data"
            
            # Use importlib.resources to access the file
            data_pkg = importlib.import_module(f"{package_path}.{dataset_dir}")
            resource_path = importlib.resources.files(data_pkg) / file_name
            
            with open(resource_path, 'r') as f:
                # Parse the file based on extension
                if file_name.endswith('.jsonl'):
                    self.dataset = [json.loads(line) for line in f if line.strip()]
                elif file_name.endswith('.json'):
                    self.dataset = json.load(f)
                else:
                    # Default case: read as text
                    self.dataset = f.readlines()

        except Exception as e:
            raise ValueError(f"Failed to load dataset from {self.file_name}: {e}")  

    def reset(self, num_players: int, seed: Optional[int]=None):
        self.state = ta.SinglePlayerState(num_players=num_players, seed=seed)
        # sample questions
        if self.n_samples is not None and self.n_samples < len(self.dataset):
            self.dataset_iter = iter(random.sample(self.dataset, self.n_samples))
        else:
            self.dataset_iter = iter(self.dataset.copy())
        self.state.reset(game_state={"questions_total": 0, "questions_correct": 0})
        self._show_next_question() # show first question

    def _show_next_question(self):
        """ Display the next question or finish the evaluation if done """
        try:
            next_item = next(self.dataset_iter)
            self.question = next_item["question"]
            self.answer = next_item["answer"]
            self.state.add_observation(message=str(self.question), observation_type=ta.ObservationType.GAME_BOARD) # Add question to state
            # return True
        except StopIteration:
            final_score = self.state.game_state["questions_correct"] / self.state.game_state["questions_total"]
            reason=f"Answered {self.state.game_state['questions_total']} questions with an accuracy of {final_score}"
            self.state.set_outcome(reward=final_score, reason=reason)
            # return False

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """Process the agent's answer and update the game state accordingly."""
        correct = self._check_answer(submitted_answer=action) # Check if the answer is correct
        self.state.info["correct"] = correct # Log the result
        self.state.info["correct_answer"] = f"The correct answer is: {self.answer}" 
        
        # Store the answer and correctness for various metrics
        self.state.game_state["questions_total"] += 1
        self.state.game_state["questions_correct"] += int(correct)
        self._show_next_question()
        return self.state.step()

    def _check_answer(self, submitted_answer: str) -> bool:
        sa = submitted_answer.strip().rstrip(".")
        # 1. boxed answers
        for match in re.findall(r"\\boxed\{([^}]*)\}", sa):
            if any(match.strip() == str(ans).strip() for ans in _ensure_list(self.answer)):
                return True

        # 2. direct string / regex match
        for ans in _ensure_list(self.answer):
            if re.search(re.escape(str(ans).strip()), sa, re.IGNORECASE):
                return True

        # 3. heavy-weight math check
        for ans in _ensure_list(self.answer):
            try:
                if math_eval(sa, ans):
                    return True
            except Exception:
                continue
        return False
    
def _ensure_list(x):
    return x if isinstance(x, list) else [x]

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