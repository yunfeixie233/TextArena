from openai import OpenAI
import os

class CodenamesAgent:
    def __init__(self, api_key=os.getenv("OPENROUTER_API_KEY")):
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    
    def get_clue(self, prompt):
        print(prompt)
        response = self.client.completions.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=10,
            n=1,
            stop=None,
            temperature=0
        )
        clue = response.choices[0].text.lower().strip().split()
        if len(clue) >= 2:
            clue_word = clue[0]
            clue_number = int(clue[1])
            return clue_word, clue_number
        else:
            return "unknown", 1
    
    def guess_word(self, prompt):
        print(prompt)
        response = self.client.completions.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=10,
            n=1,
            stop=None,
            temperature=0
        )
        guess = response.choices[0].text.lower().strip()
        if guess:
            return guess
        else:
            return "unknown"