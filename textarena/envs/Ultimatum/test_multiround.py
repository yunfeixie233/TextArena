"""
Test script for the Multi-Round Ultimatum Game environment.
This script simulates a complete 4-turn dialogue with history tracking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from spiral.envs.Ultimatum.env import UltimatumEnv


def simulate_4_turn_dialogue():
    """Simulate a complete 4-turn multi-round Ultimatum game."""
    
    print("=" * 80)
    print("      MULTI-ROUND ULTIMATUM GAME - 4-TURN SIMULATION")
    print("=" * 80)
    print("Game Setup: 4 turns = 2 rounds, $10 pool per round")
    print("Players alternate as Proposer/Responder each round")
    print("Winner determined by total accumulated money")
    print()

    # Create multi-round game
    env = UltimatumEnv(pool=10, max_turns=4)
    env.reset(num_players=2)
    
    # === TURN 1: Player 0 as Proposer (Round 1) ===
    print("🎯" + "=" * 78)
    print("TURN 1 - ROUND 1: Player 0 (Proposer)")
    print("=" * 80)
    
    # Get Player 0's prompt
    current_state = env.state.game_state
    prompt = env._generate_player_prompt(0, current_state)
    print("🎭 PLAYER 0 PROMPT:")
    print("-" * 40)
    print(prompt)
    print()
    
    # Player 0's response (making offer)
    player_0_response = "I'll start with a fair split since this is the first round. [Offer: $5]"
    print("💬 PLAYER 0 RESPONSE:")
    print(f'"{player_0_response}"')
    print()
    
    # Process the action
    done, info = env.step(player_0_response)
    print("🎮 GAME STATE AFTER TURN 1:")
    print(env.get_board_str())
    print(f"Game done: {done} | Info: {info}")
    print()
    
    # === TURN 2: Player 1 as Responder (Round 1) ===
    print("🎯" + "=" * 78)
    print("TURN 2 - ROUND 1: Player 1 (Responder)")
    print("=" * 80)
    
    # Get Player 1's prompt
    current_state = env.state.game_state
    prompt = env._generate_player_prompt(1, current_state)
    print("🎭 PLAYER 1 PROMPT:")
    print("-" * 40)
    print(prompt)
    print()
    
    # Player 1's response (accepting)
    player_1_response = "A 50-50 split sounds fair for the first round. Let's see how this plays out. [Accept]"
    print("💬 PLAYER 1 RESPONSE:")
    print(f'"{player_1_response}"')
    print()
    
    # Process the action
    done, info = env.step(player_1_response)
    print("🎮 GAME STATE AFTER TURN 2:")
    print(env.get_board_str())
    print(f"Game done: {done} | Info: {info}")
    print()
    
    # === TURN 3: Player 1 as Proposer (Round 2) ===
    print("🎯" + "=" * 78)
    print("TURN 3 - ROUND 2: Player 1 (Proposer)")
    print("=" * 80)
    
    # Get Player 1's prompt
    current_state = env.state.game_state
    prompt = env._generate_player_prompt(1, current_state)
    print("🎭 PLAYER 1 PROMPT:")
    print("-" * 40)
    print(prompt)
    print()
    
    # Player 1's response (being strategic)
    player_1_response = "Since we're tied and this is the final round, I need to be strategic. I'll keep a bit more for myself. [Offer: $4]"
    print("💬 PLAYER 1 RESPONSE:")
    print(f'"{player_1_response}"')
    print()
    
    # Process the action
    done, info = env.step(player_1_response)
    print("🎮 GAME STATE AFTER TURN 3:")
    print(env.get_board_str())
    print(f"Game done: {done} | Info: {info}")
    print()
    
    # === TURN 4: Player 0 as Responder (Round 2) ===
    print("🎯" + "=" * 78)
    print("TURN 4 - ROUND 2: Player 0 (Responder)")
    print("=" * 80)
    
    # Get Player 0's prompt
    current_state = env.state.game_state
    prompt = env._generate_player_prompt(0, current_state)
    print("🎭 PLAYER 0 PROMPT:")
    print("-" * 40)
    print(prompt)
    print()
    
    # Player 0's response (strategic decision)
    player_0_response = "Hmm, they gave me less than I gave them. But $4 is still better than $0 if I reject. I'll take it. [Accept]"
    print("💬 PLAYER 0 RESPONSE:")
    print(f'"{player_0_response}"')
    print()
    
    # Process the action
    done, info = env.step(player_0_response)
    print("🎮 FINAL GAME STATE:")
    print(env.get_board_str())
    print(f"Game done: {done} | Final result: {info}")
    print()
    
    # === GAME SUMMARY ===
    print("🏆" + "=" * 78)
    print("GAME SUMMARY")
    print("=" * 80)
    
    final_totals = env.state.game_state["player_totals"]
    history = env.state.game_state["round_history"]
    
    print("📊 Round-by-Round Breakdown:")
    for round_data in history:
        print(f"Round {round_data['round']}: P{round_data['proposer']} offered ${round_data['offer']} → {round_data['decision']}ed")
        print(f"   Gains: P{round_data['proposer']} +${round_data['proposer_gain']}, P{round_data['responder']} +${round_data['responder_gain']}")
    print()
    
    print(f"📈 Final Totals:")
    print(f"   Player 0: ${final_totals[0]}")
    print(f"   Player 1: ${final_totals[1]}")
    print()
    
    if final_totals[0] > final_totals[1]:
        winner = "Player 0"
        margin = final_totals[0] - final_totals[1]
    elif final_totals[1] > final_totals[0]:
        winner = "Player 1"
        margin = final_totals[1] - final_totals[0]
    else:
        winner = "Tie"
        margin = 0
    
    if winner != "Tie":
        print(f"🎉 Winner: {winner} (by ${margin})")
    else:
        print(f"🤝 Result: Tie game!")
    
    print()
    print("💡 Key Features Demonstrated:")
    print("✅ Multi-round gameplay with role switching")
    print("✅ History tracking and display in prompts")
    print("✅ Accumulated money across rounds")
    print("✅ Strategic considerations based on past behavior")
    print("✅ Dynamic prompts that update with game state")
    print("✅ Final winner determination based on total money")


def simulate_rejection_scenario():
    """Simulate a scenario with a rejection to show history tracking."""
    print("\n\n" + "🚫" + "=" * 78)
    print("BONUS SIMULATION: Rejection Scenario")
    print("=" * 80)
    
    env = UltimatumEnv(pool=10, max_turns=4)
    env.reset(num_players=2)
    
    # Round 1: Low offer gets rejected
    print("Round 1: Player 0 makes a greedy offer...")
    env.step("[Offer: $2]")  # Low offer
    done, info = env.step("That's way too low! [Reject]")  # Rejection
    
    print(f"After rejection - Totals: P0: ${env.state.game_state['player_totals'][0]}, P1: ${env.state.game_state['player_totals'][1]}")
    
    # Round 2: History affects decision
    print("\nRound 2: Player 1 now sees the history and responds...")
    current_state = env.state.game_state
    prompt = env._generate_player_prompt(1, current_state)
    
    print("🎭 PLAYER 1 PROMPT (showing history):")
    print("-" * 40)
    print(prompt)
    print()
    
    print("Notice how the prompt now includes:")
    print("• Previous round result (rejection)")
    print("• Current totals (both still at $0)")
    print("• Strategic context for decision-making")


if __name__ == "__main__":
    simulate_4_turn_dialogue()
    simulate_rejection_scenario() 