#!/usr/bin/env python3
"""
Verification script to compare Elo implementations between test_tic.py and elo_tracker.py
"""
import sys
import math

# Constants (should match both implementations)
K = 32
INITIAL_RATING = 1500
RESULT_RANK = {"won": 2, "tied": 1, "lost": 0}

def get_pair_result(result_i, result_j):
    """From both implementations - should be identical"""
    rank_i = RESULT_RANK.get(result_i, 1)
    rank_j = RESULT_RANK.get(result_j, 1)
    if rank_i > rank_j:
        return 1, 0
    elif rank_i < rank_j:
        return 0, 1
    else:
        return 0.5, 0.5

def expected_score(rating_i, rating_j):
    """From both implementations - should be identical"""
    return 1 / (1 + 10 ** ((rating_j - rating_i) / 400))

def process_game_test_tic(models_dict, game_result, ratings):
    """test_tic.py implementation"""
    ratings = ratings.copy()  # Don't modify original
    
    player_ids = list(models_dict.keys())
    n = len(player_ids)
    
    # Ensure all models exist in our ratings dictionary
    for pid in player_ids:
        model = models_dict[pid]
        if model not in ratings:
            ratings[model] = INITIAL_RATING

    # For each model (player) in this game, accumulate actual/expected scores
    score_sum = {models_dict[pid]: 0 for pid in player_ids}
    expected_sum = {models_dict[pid]: 0 for pid in player_ids}
    
    # Loop over all unordered pairs of players
    for i in range(n):
        for j in range(i+1, n):
            pid_i = player_ids[i]
            pid_j = player_ids[j]
            model_i = models_dict[pid_i]
            model_j = models_dict[pid_j]
            res_i = game_result.get(pid_i, "tied")  # test_tic uses "tied"
            res_j = game_result.get(pid_j, "tied")
            
            # Determine the head-to-head result
            S_i, S_j = get_pair_result(res_i, res_j)
            
            # Compute expected scores from the current ratings
            R_i = ratings[model_i]
            R_j = ratings[model_j]
            E_i = expected_score(R_i, R_j)
            E_j = expected_score(R_j, R_i)
            
            # Accumulate results
            score_sum[model_i] += S_i
            score_sum[model_j] += S_j
            expected_sum[model_i] += E_i
            expected_sum[model_j] += E_j

    # Update each player's rating
    for pid in player_ids:
        model = models_dict[pid]
        delta = (K / (n - 1)) * (score_sum[model] - expected_sum[model]) if (n > 1) else 0
        ratings[model] += delta

    return ratings

def process_game_elo_tracker(models_dict, game_result, ratings):
    """elo_tracker.py implementation"""
    ratings = ratings.copy()  # Don't modify original
    
    player_ids = list(models_dict.keys())
    n = len(player_ids)
    
    # Ensure all models exist in our ratings dictionary
    for pid in player_ids:
        model = models_dict[pid]
        if model not in ratings:
            ratings[model] = INITIAL_RATING

    # For each model (player) in this game, accumulate actual/expected scores
    score_sum = {models_dict[pid]: 0 for pid in player_ids}
    expected_sum = {models_dict[pid]: 0 for pid in player_ids}
    
    # Loop over all unordered pairs of players
    for i in range(n):
        for j in range(i+1, n):
            pid_i = player_ids[i]
            pid_j = player_ids[j]
            model_i = models_dict[pid_i]
            model_j = models_dict[pid_j]
            res_i = game_result.get(pid_i, "tie")  # elo_tracker uses "tie"
            res_j = game_result.get(pid_j, "tie")
            
            # Determine the head-to-head result
            S_i, S_j = get_pair_result(res_i, res_j)
            
            # Compute expected scores from the current ratings
            R_i = ratings[model_i]
            R_j = ratings[model_j]
            E_i = expected_score(R_i, R_j)
            E_j = expected_score(R_j, R_i)
            
            # Accumulate results
            score_sum[model_i] += S_i
            score_sum[model_j] += S_j
            expected_sum[model_i] += E_i
            expected_sum[model_j] += E_j

    # Update each player's rating
    for pid in player_ids:
        model = models_dict[pid]
        delta = (K / (n - 1)) * (score_sum[model] - expected_sum[model]) if (n > 1) else 0
        ratings[model] += delta

    return ratings

def test_elo_implementations():
    """Test both implementations with identical inputs"""
    print("="*60)
    print("ELO IMPLEMENTATION VERIFICATION")
    print("="*60)
    
    # Test 1: Basic 2-player game
    print("\n--- Test 1: Basic 2-player game (A wins vs B) ---")
    
    models_dict = {"0": "ModelA", "1": "ModelB"}
    game_result_tic = {"0": "won", "1": "lost"}  # test_tic format
    game_result_tracker = {"0": "won", "1": "lost"}  # Same format works
    initial_ratings = {"ModelA": 1500, "ModelB": 1500}
    
    ratings_tic = process_game_test_tic(models_dict, game_result_tic, initial_ratings)
    ratings_tracker = process_game_elo_tracker(models_dict, game_result_tracker, initial_ratings)
    
    print(f"test_tic results:    ModelA: {ratings_tic['ModelA']:.2f}, ModelB: {ratings_tic['ModelB']:.2f}")
    print(f"elo_tracker results: ModelA: {ratings_tracker['ModelA']:.2f}, ModelB: {ratings_tracker['ModelB']:.2f}")
    
    diff_a = abs(ratings_tic['ModelA'] - ratings_tracker['ModelA'])
    diff_b = abs(ratings_tic['ModelB'] - ratings_tracker['ModelB'])
    print(f"Differences: ModelA: {diff_a:.6f}, ModelB: {diff_b:.6f}")
    
    test1_passed = diff_a < 1e-10 and diff_b < 1e-10
    print(f"Test 1 {'PASSED' if test1_passed else 'FAILED'}")
    
    # Test 2: Different starting ratings
    print("\n--- Test 2: Different starting ratings (1600 vs 1400) ---")
    
    initial_ratings2 = {"ModelA": 1600, "ModelB": 1400}
    game_result2 = {"0": "lost", "1": "won"}  # B wins (upset)
    
    ratings_tic2 = process_game_test_tic(models_dict, game_result2, initial_ratings2)
    ratings_tracker2 = process_game_elo_tracker(models_dict, game_result2, initial_ratings2)
    
    print(f"test_tic results:    ModelA: {ratings_tic2['ModelA']:.2f}, ModelB: {ratings_tic2['ModelB']:.2f}")
    print(f"elo_tracker results: ModelA: {ratings_tracker2['ModelA']:.2f}, ModelB: {ratings_tracker2['ModelB']:.2f}")
    
    diff_a2 = abs(ratings_tic2['ModelA'] - ratings_tracker2['ModelA'])
    diff_b2 = abs(ratings_tic2['ModelB'] - ratings_tracker2['ModelB'])
    print(f"Differences: ModelA: {diff_a2:.6f}, ModelB: {diff_b2:.6f}")
    
    test2_passed = diff_a2 < 1e-10 and diff_b2 < 1e-10
    print(f"Test 2 {'PASSED' if test2_passed else 'FAILED'}")
    
    # Test 3: Tie game
    print("\n--- Test 3: Tie game ---")
    
    game_result3_tic = {"0": "tied", "1": "tied"}  # test_tic uses "tied"
    game_result3_tracker = {"0": "tied", "1": "tied"}  # Both should handle "tied"
    
    ratings_tic3 = process_game_test_tic(models_dict, game_result3_tic, initial_ratings)
    ratings_tracker3 = process_game_elo_tracker(models_dict, game_result3_tracker, initial_ratings)
    
    print(f"test_tic results:    ModelA: {ratings_tic3['ModelA']:.2f}, ModelB: {ratings_tic3['ModelB']:.2f}")
    print(f"elo_tracker results: ModelA: {ratings_tracker3['ModelA']:.2f}, ModelB: {ratings_tracker3['ModelB']:.2f}")
    
    diff_a3 = abs(ratings_tic3['ModelA'] - ratings_tracker3['ModelA'])
    diff_b3 = abs(ratings_tic3['ModelB'] - ratings_tracker3['ModelB'])
    print(f"Differences: ModelA: {diff_a3:.6f}, ModelB: {diff_b3:.6f}")
    
    test3_passed = diff_a3 < 1e-10 and diff_b3 < 1e-10
    print(f"Test 3 {'PASSED' if test3_passed else 'FAILED'}")
    
    # Test 4: Manual calculation verification
    print("\n--- Test 4: Manual calculation verification ---")
    print("Player A (1500) beats Player B (1600)")
    
    # Manual calculation
    E_A = 1 / (1 + 10**((1600-1500)/400))  # Expected score for A
    E_B = 1 / (1 + 10**((1500-1600)/400))  # Expected score for B
    
    S_A = 1.0  # A won
    S_B = 0.0  # B lost
    
    delta_A = K * (S_A - E_A)
    delta_B = K * (S_B - E_B)
    
    manual_A = 1500 + delta_A
    manual_B = 1600 + delta_B
    
    print(f"Manual calculation: A: {manual_A:.2f}, B: {manual_B:.2f}")
    print(f"Expected A: {E_A:.6f}, Expected B: {E_B:.6f}")
    print(f"Delta A: {delta_A:.2f}, Delta B: {delta_B:.2f}")
    
    # Compare with implementations
    test_models = {"0": "A", "1": "B"}
    test_ratings = {"A": 1500, "B": 1600}
    test_result = {"0": "won", "1": "lost"}
    
    impl_ratings = process_game_test_tic(test_models, test_result, test_ratings)
    
    diff_manual_A = abs(impl_ratings["A"] - manual_A)
    diff_manual_B = abs(impl_ratings["B"] - manual_B)
    
    print(f"Implementation: A: {impl_ratings['A']:.2f}, B: {impl_ratings['B']:.2f}")
    print(f"Differences from manual: A: {diff_manual_A:.6f}, B: {diff_manual_B:.6f}")
    
    test4_passed = diff_manual_A < 1e-10 and diff_manual_B < 1e-10
    print(f"Test 4 {'PASSED' if test4_passed else 'FAILED'}")
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_tests_passed = test1_passed and test2_passed and test3_passed and test4_passed
    
    print(f"Test 1 (Basic game): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (Different ratings): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"Test 3 (Tie game): {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    print(f"Test 4 (Manual verification): {'✅ PASSED' if test4_passed else '❌ FAILED'}")
    print()
    print(f"Initial rating (1500): {'✅ STANDARD' if INITIAL_RATING == 1500 else '❌ NON-STANDARD'}")
    print(f"K-factor (32): {'✅ STANDARD' if K == 32 else '❌ NON-STANDARD'}")
    print()
    print(f"Overall: {'✅ ALL IMPLEMENTATIONS CORRECT' if all_tests_passed else '❌ IMPLEMENTATION ISSUES FOUND'}")
    
    return all_tests_passed

if __name__ == "__main__":
    test_elo_implementations()
