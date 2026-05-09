from isolation import Board
from game_agent import AlphaBetaPlayer, MinimaxPlayer, custom_score, custom_score_2, custom_score_3
from sample_players import RandomPlayer, GreedyPlayer

def play_matches(player1, player2, num_matches, description):
    """
    Plays a set of matches between two players and reports statistics.
    """
    p1_wins = 0
    total_moves = 0
    
    print(f"\n--- Running: {description} ---")
    
    for i in range(num_matches):
        game = Board(player1, player2)
        
        # Play the game
        winner, history, outcome = game.play()
        
        # Calculate stats
        total_moves += len(history)
        
        if winner == player1:
            p1_wins += 1
            
    # Report results
    win_rate = (p1_wins / num_matches) * 100
    avg_moves = total_moves / num_matches
    
    print(f"Results for {num_matches} matches:")
    print(f" > P1 Win Rate: {win_rate:.1f}% ({p1_wins}/{num_matches})")
    print(f" > Avg Game Length: {avg_moves:.1f} moves")
    print("-" * 40)

def main():
    # Number of matches per test case (Higher = more accurate, but slower)
    # For final report, consider 20 or 50. For quick test, use 5.
    NUM_MATCHES = 10 
    
    # ///////////////////////////////////////////////
    # PART 1: Compare Heuristics (AlphaBeta vs Greedy)
    # ////////////////////////////////////////////////
    print("\n" + "/"*50)
    print("PART 1: Comparing Heuristics (AlphaBeta vs GreedyPlayer)")
    print("/"*50)
    
    # Test Heuristic 1
    p1_h1 = AlphaBetaPlayer(score_fn=custom_score, search_depth=3)
    play_matches(p1_h1, GreedyPlayer(), NUM_MATCHES, "AlphaBeta (Heuristic 1) vs Greedy")
    
    # Test Heuristic 2
    p1_h2 = AlphaBetaPlayer(score_fn=custom_score_2, search_depth=3)
    play_matches(p1_h2, GreedyPlayer(), NUM_MATCHES, "AlphaBeta (Heuristic 2) vs Greedy")
    
    # Test Heuristic 3
    p1_h3 = AlphaBetaPlayer(score_fn=custom_score_3, search_depth=3)
    play_matches(p1_h3, GreedyPlayer(), NUM_MATCHES, "AlphaBeta (Heuristic 3) vs Greedy")

    # /////////////////////////////////////////////////
    # PART 2: Compare Algorithms (Minimax vs AlphaBeta)
    # ////////////////////////////////////////////////
    print("\n" + "/"*50)
    print("PART 2: Comparing Algorithms (Minimax vs AlphaBeta)")
    print("Note: Minimax Depth = 2 vs AlphaBeta Depth = 3")
    print("/"*50)
    
    # Minimax Agent (Using best heuristic, e.g., score_3)
    p1_minimax = MinimaxPlayer(score_fn=custom_score_3, search_depth=2)
    play_matches(p1_minimax, GreedyPlayer(), NUM_MATCHES, "Minimax (Heuristic 3) vs Greedy")
    
    # AlphaBeta Agent (Using same heuristic)
    p1_alphabeta = AlphaBetaPlayer(score_fn=custom_score_3, search_depth=3)
    play_matches(p1_alphabeta, GreedyPlayer(), NUM_MATCHES, "AlphaBeta (Heuristic 3) vs Greedy")

    # /////////////////////////////////////////////////////
    # PART 3: Baseline Test (Agent vs Random)
    # /////////////////////////////////////////////////////
    print("\n" + "/"*50)
    print("PART 3: Baseline Test (Your Best Agent vs RandomPlayer)")
    print("/"*50)
    
    # Assuming AlphaBeta with Heuristic 3 is your best
    best_agent = AlphaBetaPlayer(score_fn=custom_score_3, search_depth=3)
    play_matches(best_agent, RandomPlayer(), NUM_MATCHES, "Best Agent vs Random")

if __name__ == "__main__":
    main()