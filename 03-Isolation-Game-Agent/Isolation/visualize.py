import json
import os
import webbrowser
from isolation import Board
from sample_players import RandomPlayer, GreedyPlayer
# You can also import your custom AI player:
from game_agent import MinimaxPlayer, AlphaBetaPlayer, custom_score, custom_score_2, custom_score_3

# --- 1. Setup players ---
player1 = AlphaBetaPlayer(score_fn=custom_score, search_depth=3) #my best aget based on test res
player2 = RandomPlayer()

# --- 2. Play the game and get move history ---
game = Board(player1, player2)
winner, history, outcome = game.play()
print(f"🏆 Game finished! Winner: {winner}")

# --- 3. Save history to JSON ---
output_dir = "isoviz"
output_path = os.path.join(output_dir, "match.json")
os.makedirs(output_dir, exist_ok=True)

with open(output_path, "w") as f:
    json.dump(history, f)
print(f"✅ Match saved to {output_path}")

# --- 4. Open visualization in browser ---
html_path = os.path.abspath(os.path.join(output_dir, "display.html"))
webbrowser.open(f"file://{html_path}")
print("🌐 Opening visualization in your default browser...")
