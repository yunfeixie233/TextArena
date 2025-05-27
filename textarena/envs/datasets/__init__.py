""" Register all datasets environments """
from textarena.envs.registration import register 
from textarena.wrappers import SingleTurnObservationWrapper

# GSM8K - Grade School Math Word Problems
register(id="Dataset-GSM8K-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gsm8k/test.jsonl", n_samples=1)
register(id="Dataset-GSM8K-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gsm8k/test.jsonl", n_samples=None)

# AIME - American Invitational Mathematics Examination
register(id="Dataset-AIME24-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="aime24/test.jsonl", n_samples=1)
register(id="Dataset-AIME24-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="aime24/test.jsonl", n_samples=None)

register(id="Dataset-AIME23-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="aime23/test.jsonl", n_samples=1)
register(id="Dataset-AIME23-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="aime23/test.jsonl", n_samples=None)

# AQUA - Algebra Question Answering
register(id="Dataset-AQUA-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="aqua/test.jsonl", n_samples=1)
register(id="Dataset-AQUA-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="aqua/test.jsonl", n_samples=None)

# ASDIV - Arithmetic with diverse operations
register(id="Dataset-ASDIV-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="asdiv/test.jsonl", n_samples=1)
register(id="Dataset-ASDIV-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="asdiv/test.jsonl", n_samples=None)

# CARP - Complex Arithmetic Problems
register(id="Dataset-CARP_EN-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="carp_en/test.jsonl", n_samples=1)
register(id="Dataset-CARP_EN-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="carp_en/test.jsonl", n_samples=None)

# CMATH - College Mathematics
register(id="Dataset-CMATH-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="cmath/test.jsonl", n_samples=1)
register(id="Dataset-CMATH-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="cmath/test.jsonl", n_samples=None)

# Chinese Middle School Math
register(id="Dataset-CN_MIDDLE_SCHOOL-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="cn_middle_school/test.jsonl", n_samples=1)
register(id="Dataset-CN_MIDDLE_SCHOOL-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="cn_middle_school/test.jsonl", n_samples=None)

# College Math
register(id="Dataset-COLLEGE_MATH-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="college_math/test.jsonl", n_samples=1)
register(id="Dataset-COLLEGE_MATH-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="college_math/test.jsonl", n_samples=None)

# GAOKAO Math
register(id="Dataset-GAOKAO_MATH-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao_math/test.jsonl", n_samples=1)
register(id="Dataset-GAOKAO_MATH_QA-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao_math_qa/test.jsonl", n_samples=1)
register(id="Dataset-GAOKAO2023EN-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao2023en/test.jsonl", n_samples=1)
register(id="Dataset-GAOKAO2024_I-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao2024_I/test.jsonl", n_samples=1)
register(id="Dataset-GAOKAO2024_II-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao2024_II/test.jsonl", n_samples=1)
register(id="Dataset-GAOKAO2024_MCQ-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao2024_mcq/test.jsonl", n_samples=1)

register(id="Dataset-GAOKAO_MATH-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao_math/test.jsonl", n_samples=None)
register(id="Dataset-GAOKAO_MATH_QA-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao_math_qa/test.jsonl", n_samples=None)
register(id="Dataset-GAOKAO2023EN-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao2023en/test.jsonl", n_samples=None)
register(id="Dataset-GAOKAO2024_I-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao2024_I/test.jsonl", n_samples=None)
register(id="Dataset-GAOKAO2024_II-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao2024_II/test.jsonl", n_samples=None)
register(id="Dataset-GAOKAO2024_MCQ-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="gaokao2024_mcq/test.jsonl", n_samples=None)

# MATH
register(id="Dataset-MATH-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="math/test.jsonl", n_samples=1)
register(id="Dataset-MATH-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="math/test.jsonl", n_samples=None)

# MATH500
register(id="Dataset-MATH500-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="math500/test.jsonl", n_samples=1)
register(id="Dataset-MATH500-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="math500/test.jsonl", n_samples=None)

# MAWPS - Math Word Problems
register(id="Dataset-MAWPS-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="mawps/test.jsonl", n_samples=1)
register(id="Dataset-MAWPS-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="mawps/test.jsonl", n_samples=None)

# Minerva Math
register(id="Dataset-MINERVA_MATH-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="minerva_math/test.jsonl", n_samples=1)
register(id="Dataset-MINERVA_MATH-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="minerva_math/test.jsonl", n_samples=None)

# MMLU STEM
register(id="Dataset-MMLU_STEM-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="mmlu_stem/test.jsonl", n_samples=1)
register(id="Dataset-MMLU_STEM-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="mmlu_stem/test.jsonl", n_samples=None)

# Math Olympiad Benchmark
register(id="Dataset-OLYMPIADBENCH-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="olympiadbench/test.jsonl", n_samples=1)
register(id="Dataset-OLYMPIADBENCH-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="olympiadbench/test.jsonl", n_samples=None)

# SAT Math
register(id="Dataset-SAT_MATH-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="sat_math/test.jsonl", n_samples=1)
register(id="Dataset-SAT_MATH-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="sat_math/test.jsonl", n_samples=None)

# SVAMP
register(id="Dataset-SVAMP-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="svamp/test.jsonl", n_samples=1)
register(id="Dataset-SVAMP-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="svamp/test.jsonl", n_samples=None)

# TabMWP - Tabular Math Word Problems
register(id="Dataset-TABMWP-v0", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="tabmwp/test.jsonl", n_samples=1)
register(id="Dataset-TABMWP-v0-all", entry_point="textarena.envs.datasets.OpenEndedReasoningEvals.env:OpenEndedReasoningEvalsEnv", default_wrappers=[SingleTurnObservationWrapper], file_name="tabmwp/test.jsonl", n_samples=None)