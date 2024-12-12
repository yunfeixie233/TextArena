import textarena as ta 

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import PeftModel, PeftConfig
from unsloth import FastLanguageModel
import os
from typing import Optional
import torch 


class LoRAConnectFourAgent(ta.Agent):
    """
    Agent class for the fine-tuned LoRA Connect Four model.
    """
    def __init__(
        self,
        base_model_name: str = "meta-llama/Llama-3.2-1B",
        adapter_path: str = "connect4_20241122_160901",
        quantize: bool = True
    ):
        """
        Initialize the LoRA Connect Four agent.
        """
        super().__init__()
        
        # Set the Hugging Face access token
        # access_token = os.getenv("HF_ACCESS_TOKEN")
        # if not access_token:
            # raise ValueError("Hugging Face access token not found. Please set the HF_ACCESS_TOKEN environment variable.")
        
        # Load the base model and tokenizer with Unsloth
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=base_model_name,
            max_seq_length=2048,
            load_in_4bit=quantize,
            # token=access_token,
            dtype=torch.float16
        )
        
        # Load the LoRA adapter
        config = PeftConfig.from_pretrained(adapter_path)
        self.model = PeftModel.from_pretrained(
            self.model,
            adapter_path,
            # token=access_token
        )
        
        # Prepare model for inference
        self.model = FastLanguageModel.for_inference(self.model)
        
        # Set the model to evaluation mode
        self.model.eval()
        
    def format_observation(self, observation: str) -> str:
        """Format the observation for the model."""
        # return observation
        return f"""### Instruction: Play Connect Four optimally.

### Input: {observation}

### Response:"""
    
    def __call__(
        self,
        observation: str,
        temperature: float = 1.0
    ) -> str:
        """
        Process the observation and return the action.
        """
        try:
            # Format the input
            formatted_input = self.format_observation(observation)
            
            # Tokenize the input
            inputs = self.tokenizer(
                formatted_input,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=2048
            ).to(self.model.device)
            
            # Generate with the model directly
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=50,
                    num_return_sequences=1,
                    temperature=temperature,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode the output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the response part
            response_text = generated_text.split("### Response:")[1] #.strip()
            return response_text
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return "3"  # 




model_name = "Llama-sft 1B new2" # has to be unique
model_desc = "Llama 3.2 1B finetuned for three minutes."
email = "leon002@e.ntu.edu.sg"

# register the model
model_token = ta.register_online_model(
    model_name=model_name, 
    model_description=model_desc,
    email=email
)



# build agent
# agent = ta.basic_agents.OpenRouterAgent(model_name="GPT-4o")

agent = LoRAConnectFourAgent(
        # base_model_name="NousResearch/Llama-2-1b-hf",
        # adapter_path=f"final_model/connect4_{timestamp}",
        quantize=True
    )


for _ in range(50):
    # make the online environment
    env = ta.make_online(
        env_id="ConnectFour-v0",
        model_name=model_name,
        model_token=model_token,
    )

    # wrap for easy LLM use
    env = ta.LLMObservationWrapper(env=env)
    # env = ta.ClipWordsActionWrapper(env=env)

    # reset and get initial observations
    observations = env.reset()

    truncated, terminated = False, False
    while not (truncated or terminated):
        # get the current player id 
        player_id = env.get_current_player_id()

        # get agent action
        action = agent(observations[player_id])
        print(action)
        # step
        observations, _, truncated, terminated, _ = env.step(player_id, action)


    # print the game outcome and change in elo
    env.close()
    print(observations[player_id])