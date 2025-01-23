import re 

from typing import Optional, Any, List, Tuple 
from e2b_code_interpreter import Sandbox, Logs

import textarena as ta 


__all__ = [
    "ThoughtAgentWrapper",
    "InterpreterAgentWrapper",
    "ChainAgentWrapper"
]

class ThoughtAgentWrapper(ta.AgentWrapper):
    """ Agent that uses a hidden chain of thought to plan out actions """

    def __init__(
        self, 
        agent: ta.Agent,
        system_prompt: Optional[str] = None,
        debugging: bool = False 
        ):
        """ TODO """
        super().__init__(agent)
        if system_prompt is None:
            system_prompt = (
            "\nWhen responding, first think extensively within a <thought/> tag to plan out your actions. "
            "Everything written in <thought> tags will be hidden from other players. "
            "Everything written outside of <thought> tags will be submitted to the game and displayed to the other player."
        )
        # set the system prompt 
        self.agent.system_prompt = system_prompt
        self.thought_blocks: List[List[str]] = []

        self.debugging = debugging

    def __call__(self, observation: str) -> str:
        out_text = self.agent(observation)

        if self.debugging:
            print("REASON", out_text)

        thought_blocks = re.findall(
            r"<thought>(.*?)</thought>", out_text, flags=re.DOTALL
        )
        self.thought_blocks.append(thought_blocks)

        # Replace thought tags with empty string
        out_text = re.sub(r"<thought>.*?</thought>", "", out_text, flags=re.DOTALL)
        out_text = out_text.strip().replace("\n\n", "")
        assert "<thought>" not in out_text, f"Thought tags still present: {out_text}"

        return out_text


class ActorCriticAgentWrapper(ta.AgentWrapper):
    """ TODO """
    def __init__(
        self,
        agent: ta.Agent,
        actor_system_prompt: Optional[str] = None,
        critic_system_prompt: Optional[str] = None,
        final_reply_system_prompt: Optional[str] = None,
        debugging: bool = False
    ):
        """ TODO """
        super().__init__(agent)

        # Initialize prompts
        self.actor_system_prompt = (
            actor_system_prompt or 
                "You are an expert player in a competitive game environment. Your goal is to play optimally, "
                "adhering strictly to the game's rules and format requirements.\n\n"
                "Evaluate the current game state carefully and decide your next move strategically. "
                "Always ensure your response is:\n"
                "1. In the correct format as specified by the game rules.\n"
                "2. Focused on maximizing your chances of winning while minimizing risks.\n\n"
                "Respond only with your chosen move in the required format."
            )
        self.critic_system_prompt = (
            critic_system_prompt or
                "You are a critical observer and rule enforcer for a competitive game. Your task is to:\n"
                "1. Review the provided action to ensure it complies with the game's rules and format requirements.\n"
                "2. Critique the action for strategic effectiveness, identifying any potential improvements. "
                "[esp. pointing out if this action will give the opponent a chance to win in the next move]\n"
                "3. Highlight specific reasons if the action is invalid or suboptimal.\n\n"
                "Provide your analysis clearly and concisely. Never trading is not a good strategy! Accept trades that seem good!"
            )
        self.final_reply_system_prompt = (
            final_reply_system_prompt or
                "You are an expert game strategist tasked with synthesizing a final move. Based on the initial action and the critique, "
                "generate a revised action that:\n"
                "1. Adheres strictly to the game's rules and format.\n"
                "2. Incorporates the improvements or corrections suggested in the critique.\n"
                "3. Optimizes strategic effectiveness to maximize the chances of success.\n\n"
                "Respond only with the final corrected action in the required format. Try not to make new offers every single move."
            )

        self.debugging = debugging

    def __call__(self, observation: str) -> str:
        """ TODO """

        # set first system prompt 
        self.agent.system_prompt = self.actor_system_prompt

        # first forward 
        initial_out = self.agent(observation)
        if self.debugging:
            print(f"Initial Agent output: {initial_out}")

        # set second system prompt 
        self.agent.system_prompt = self.critic_system_prompt

        # second forward
        second_out = self.agent(f"Observation: {observation}. \nCurrent Strategy: {initial_out}")
        if self.debugging:
            print(f"Critic Agent output: {second_out}")

        # set third system prompt 
        self.agent.system_prompt = self.final_reply_system_prompt

        # third forward
        final_out = self.agent(
            f"Observation: {observation}. \nInitial Strategy: {initial_out}. \nCriticism: {second_out} "
        )
        if self.debugging:
            print(f"Final Agent output: {final_out}\n\n")


        return final_out 
           



class InterpreterAgentWrapper(ta.AgentWrapper):
    """ Agent that uses a code interpreter to make decisions """
    def __init__(
        self, 
        agent: ta.Agent,
        code_instruction_prompt: Optional[str] = None,
        first_code_prompt: Optional[str] = None,
        cont_code_prompt: Optional[str] = None,
        prompt_max_chars: Optional[int] = 1024*10,
        out_max_chars: Optional[int] = 1024*4,
        debugging: Optional[bool] = False
    ):
        super().__init__(agent)
        self.sbx = Sandbox()

        # overwrite prompts if provided
        if code_instruction_prompt is None:
            code_instruction_prompt = (
                "You are a competitive game player. "
                "Your goal is plan and compute the right information "
                "to help with decision making for the following game. "
                "You have access a code interpreter via ```python and ending with ```.\n"
            )

        if first_code_prompt is None:
            first_code_prompt = (
                "You will write a set of concise, modular and reusable functions to assist with the game decision making. "
                "Your code should be setup so you can easily update variables when you encounter future game states, allowing "
                "changes in game states to be updated in a few lines. Don't print out the entire game state. "
                "You will only be able to view the stdout/stderr of the interpreter logs to make your decision, "
                "so clearly print any labeled information and the best decision in the required format."
            )

        if cont_code_prompt is None:
            cont_code_prompt = (
                "Reference variables and reuse functions previously executed in the interpreter. Be concise and don't repeat "
                "previously defined code. Update only game states that have changed. Don't print out the entire game state. "
                "You will only be able to view the stdout/stderr of the interpreter logs to make your decision, so clearly "
                "print any labeled information and the best decision in the required format."
            )



        # build the prompts
        self.init_prompt = code_instruction_prompt + first_code_prompt
        self.continue_prompt = code_instruction_prompt + cont_code_prompt

        # All code blocks the model has written and executed
        self.executed_code: List[Tuple[str, Logs]] = []

        self.prompt_max_chars = prompt_max_chars
        self.out_max_chars = out_max_chars

        self.debugging = debugging

    def prompt_log(self, log: Logs) -> str:
        stdout = "".join(log.stdout).strip()
        stderr = "".join(log.stderr).strip()
        text = ""
        if stdout:
            text += f"<stdout>\n{stdout}\n</stdout>"
        if stderr:
            text += f"<stderr>\n{stderr}\n</stderr>"
        return text

    def prompt_executed_code(self, executed_code: List[Tuple[str, Any]]) -> str:
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

        if self.debugging:
            print(executed_code)

        observation += (
            "---\n"
            "Previously executed code in interpreter:\n"
            "```python\n"
            f"{executed_code}\n"
            "```\n\n"
            "Your code:\n"
        ) if len(self.executed_code) == 0 else "\nYour code:"
        

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

       

class ChainAgentWrapper(ta.Agent):
    """
    Chains several agents and pipes the output of each agent to the next
    """
    def __init__(self, agents: List[ta.Agent], delimiter: str = "\n"):
        super().__init__()
        self.agents = agents
        self.delimiter = delimiter

    def __call__(self, observation: str) -> str:
        current_observation: str = f"Observation: {observation}\n"
        for i, agent in enumerate(self.agents):
            if i == len(self.agents)-1:
                out_text = agent(current_observation+"\nFinal Output: ")
            else:
                out_text = agent(current_observation)
                current_observation += f"Step {i+1} Output:{out_text}\n"
        return out_text
