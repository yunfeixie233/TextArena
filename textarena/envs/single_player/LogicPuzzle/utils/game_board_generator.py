from openai import OpenAI
import os
import json
import re


client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

## Game board solutions to generate clues for
solutions = [
    {
        "people":["Alice", "Bob", "Charlie"],
        "locations":["home", "work", "park"],
        "times":["morning", "afternoon", "evening"],
    },
    {
        "people":["Alice", "Bob", "Charlie"],
        "car":["red", "blue", "green"],
        "fuel":["gasoline", "diesel", "electric"],
    },
    {
        "people":["Alice", "Bob", "Charlie"],
        "food":["pizza", "burger", "salad"],
        "drink":["water", "soda", "beer"],
    },
    {
        "people":["Alice", "Bob", "Charlie"],
        "sport":["soccer", "basketball", "tennis"],
        "day":["wednesday", "monday", "tuesday"],
    }
]

def get_all_combinations(entry):
    return list(zip(*entry.values()))


def get_clue_examples(solution: dict) -> list:
    """
    Get 10 clue examples for the specified word from OpenRouter.
    
    Args:
        word (str): The word for which to get the clues.
    
    Returns:
        list: A list of 10 distinct clues for the word.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"I am designing a logic puzzle with a unique solution format.\n"
                        f"Each category (such as {', '.join(solution.keys())}) has specific values assigned to unique index positions, representing the correct solution.\n"
                        "\n"
                        "For example, the solution structure given is:\n"
                        f"{get_all_combinations(solution)}\n"
                        "where each tuple in the list matches the correct combination that you have to create clues for.\n"
                        "\n"
                        "Please create 5 sets of 5 clues each for this solution in 'easy' and 'hard' difficulty levels. This means there should be 5 sets of clues for each difficulty.\n"
                        "\nFor the **easy clues:**\n"
                        "- Provide direct assignments or straightforward eliminations that guide players towards identifying correct category pairings.\n"
                        # "\nFor the **medium clues:**\n"
                        # "- Provide partial hints or multi-step eliminations that require some logical connections without being overly complex. These clues may involve simple conditional logic or comparisons that are not immediately obvious but can be deduced without advanced reasoning.\n"
                        "\nFor the **hard clues:**\n"
                        "- Use conditional, relational, or sequential reasoning, adding challenge by indirectly referencing the solution relationships.\n"
                        "Each set should support the unique solution derived from the input structure provided above.\n"
                        "Your response should be in a JSON format, where the keys are the difficulty levels ('easy', 'hard') and the values are lists of 5 clues for each difficulty level."
                    )
                }
            ],
            temperature=0.7,
        )
        
        # Extract the assistant's reply and use regex to isolate JSON content
        clues_text = response.choices[0].message.content.strip()
        json_match = re.search(r"```json\n({.*?})\n```", clues_text, re.DOTALL)

        if json_match:
            json_data = json.loads(json_match.group(1))
            return json_data
        else:
            return "No JSON data found in the response."
        
    except Exception as e:
        return [f"An error occurred: {e}"]

with open("game_board_clues.jsonl", "w") as f:
    for solution in solutions:
        res = get_clue_examples(solution)
        for difficulty in res.keys():
            for clue in res[difficulty]:
                json_line = json.dumps({"solution": solution, "difficulty": difficulty, "clue": clue})
                f.write(json_line + "\n")