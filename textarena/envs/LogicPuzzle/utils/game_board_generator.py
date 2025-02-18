from openai import OpenAI
import os
import json
import re
import tqdm

# Initialize OpenAI client with API key
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

# Define game board solutions to generate clues for
solutions = [
    {
        "people": ["Alice", "Bob", "Charlie"],
        "locations": ["home", "work", "park"],
        "times": ["morning", "afternoon", "evening"],
    },
    {
        "people": ["Alice", "Bob", "Charlie"],
        "car": ["red", "blue", "green"],
        "fuel": ["gasoline", "diesel", "electric"],
    },
    {
        "people": ["Alice", "Bob", "Charlie"],
        "food": ["pizza", "burger", "salad"],
        "drink": ["water", "soda", "beer"],
    },
    {
        "people": ["Alice", "Bob", "Charlie"],
        "sport": ["soccer", "basketball", "tennis"],
        "day": ["wednesday", "monday", "tuesday"],
    }
]

def get_all_combinations(entry):
    """Returns all possible combinations for a solution entry."""
    return list(zip(*entry.values()))

def get_clue_examples(solution: dict) -> dict:
    """
    Generate clue examples for the provided solution from OpenRouter.
    
    Args:
        solution (dict): Dictionary with category-value pairs to generate clues.
    
    Returns:
        dict: A dictionary with 'easy' and 'hard' clues, each containing 5 sets of clues.
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
        
        # Extract the assistant's reply and parse JSON content if available
        clues_text = response.choices[0].message.content.strip()
        json_match = re.search(r"```json\n({.*?})\n```", clues_text, re.DOTALL)
        
        if json_match:
            json_data = json.loads(json_match.group(1))
            return json_data
        else:
            print("Warning: No JSON data found in the response.")
            return {"easy": [], "hard": []}  # Return empty lists if no JSON data is found
        
    except Exception as e:
        print(f"Error while generating clues: {e}")
        return {"easy": [], "hard": []}

def main():
    """Main function to generate clues for each solution and write to a JSONL file."""
    output_file = "textarena/envs/single_player/LogicPuzzle/game_board_clues.jsonl"
    
    with open(output_file, "w") as f:
        for solution in tqdm.tqdm(solutions, desc="Generating clues"):
            res = get_clue_examples(solution)
            for difficulty, clues in res.items():
                for clue in clues:
                    json_line = json.dumps({"solution": solution, "difficulty": difficulty, "clue": clue})
                    f.write(json_line + "\n")
    
    print("Clues generation completed and saved to:", output_file)

# Execute main function when the script is run directly
if __name__ == "__main__":
    main()
