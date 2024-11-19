import re
from typing import Any
from .basic_agents import SystemPromptAgent, Agent

from e2b_code_interpreter import Sandbox, Logs


class ThoughtAgent(Agent):
    """
    Agent that uses a hidden chain of thought to plan out actions.
    """

    def __init__(self, agent: SystemPromptAgent):
        super().__init__()
        self.agent = agent
        self.agent.system_prompt += "\nWhen responding, first think extensively within a <thought/> tag to plan out your actions. Everything written in <thought> tags will be hidden from other players. Everything written outside of <thought> tags will be submitted to the game and displayed to the other player."
        self.thought_blocks: list[list[str]] = []

    def __call__(self, observation: str) -> str:
        out_text = self.agent(observation)

        thought_blocks = re.findall(
            r"<thought>(.*?)</thought>", out_text, flags=re.DOTALL
        )
        self.thought_blocks.append(thought_blocks)

        # Replace thought tags with empty string
        out_text = re.sub(r"<thought>.*?</thought>", "", out_text, flags=re.DOTALL)
        out_text = out_text.strip().replace("\n\n", "")
        assert "<thought>" not in out_text, f"Thought tags still present: {out_text}"

        return out_text


class InterpreterAgent(Agent):
    """
    Agent that uses a code interpreter to make decisions.
    """

    def __init__(self, agent: SystemPromptAgent):
        super().__init__()
        self.agent = agent
        self.sbx = Sandbox()

        # Prompt for init
        prompt_pre = "You are a competitive game player. Your goal is plan and compute the right information to help with decision making for the following game. You have access a code interpreter via ```python and ending with ```.\n"
        self.init_prompt = (
            prompt_pre
            + "You will write a set of concise, modular and reusable functions to assist with the game decision making. Your code should be setup so you can easily update variables when you encounter future game states, allowing changes in game states to be updated in a few lines. Don't print out the entire game state. You will only be able to view the stdout/stderr of the interpreter logs to make your decision, so clearly print any labeled information and the best decision in the required format."
        )

        # Prompt for continuing
        self.continue_prompt = (
            prompt_pre
            + "Reference variables and reuse functions previously executed in the interpreter. Be concise and don't repeat previously defined code. Update only game states that have changed. Don't print out the entire game state. You will only be able to view the stdout/stderr of the interpreter logs to make your decision, so clearly print any labeled information and the best decision in the required format."
        )
        # All code blocks the model has written and executed
        self.executed_code: list[tuple[str, Logs]] = []

        self.prompt_max_chars = 1024 * 10
        self.out_max_chars = 1024 * 4

    def prompt_log(self, log: Logs) -> str:
        stdout = "".join(log.stdout).strip()
        stderr = "".join(log.stderr).strip()
        text = ""
        if stdout:
            text += f"<stdout>\n{stdout}\n</stdout>"
        if stderr:
            text += f"<stderr>\n{stderr}\n</stderr>"
        return text

    def prompt_executed_code(self, executed_code: list[tuple[str, Any]]) -> str:
        text = ""
        for code_block, logs in executed_code:
            text += f"```python\n{code_block}\n```\n"
            text += self.prompt_log(logs)
        return text

    def __call__(self, observation: str) -> str:
        self.agent.system_prompt = (
            self.init_prompt if len(self.executed_code) == 0 else self.continue_prompt
        )

        # Append previous code and logs to the observation
        executed_code = "\n".join(code_block for code_block, _ in self.executed_code)[
            -self.prompt_max_chars :
        ]
        observation += (
            f"""
---
Previously executed code in interpreter:
```python
{executed_code}
```

Your code:
"""
            if len(self.executed_code) == 0
            else "\nYour code:"
        )

        out_text = self.agent(observation)
        code_blocks = re.findall(r"```python(.*?)```", out_text, flags=re.DOTALL)
        for code_block in code_blocks:
            try:
                execution = self.sbx.run_code(code_block, timeout=3)
            except Exception as e:
                print(f"Error executing code: {code_block}\n{e}")
                break
            self.executed_code.append((code_block, execution.logs))

        return "\n".join(self.prompt_log(logs) for _, logs in self.executed_code)[
            -self.out_max_chars :
        ]


class ChainAgent(Agent):
    """
    Chains several agents and pipes the output of each agent to the next.
    """

    def __init__(self, agents: list[Agent], delimiter: str = "\n"):
        super().__init__()
        self.agents = agents
        self.delimiter = delimiter

    def __call__(self, observation: str) -> str:
        out_text: str = ""
        for agent in self.agents:
            out_text = agent(observation)
            observation += f"{self.delimiter}{out_text}"
        return out_text
