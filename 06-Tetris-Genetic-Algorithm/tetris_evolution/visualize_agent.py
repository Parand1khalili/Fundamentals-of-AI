"""Simple demonstration script for Tetris Evolution."""
from tetris.visualizer import visualize
from tetris.agent import Agent
from tetris.constants import SHAPE_SEQUENCE
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def main():
    """Create and visualize a random agent."""
    print(f"Loading agent from best_agent.txt")
    agent = Agent.load()
    print(f"Agent created with {len(agent.placements)} placements")
    print(f"Agent fitness: {agent.fitness()}")

    print("\nVisualizing the agent's gameplay...")
    print("Close the window when done viewing.")

    try:
        visualize(agent, delay=0.01, seq=SHAPE_SEQUENCE)
    except ImportError:
        print("Error: pygame not installed. Install with 'pip install pygame'")

    print("\nDone!")


if __name__ == "__main__":
    main()
