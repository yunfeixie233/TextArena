""" Debate Environment """
import textarena as ta 

from typing import Optional, 
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
    