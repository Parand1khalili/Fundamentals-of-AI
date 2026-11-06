"""Agent for playing Tetris."""
from typing import List, Tuple, Optional
import random

try:
    from tetris_evolution.tetris.constants import SHAPES, COLS, SHAPE_SEQUENCE
    from tetris_evolution.tetris.game import Board
except ImportError:
    from .constants import SHAPES, COLS, SHAPE_SEQUENCE
    from .game import Board


class Agent:
    """
    Represents a Tetris-playing agent with a genome of placements.
    Each placement is a (rotation, x-position) tuple for a specific piece.
    """

    def __init__(self,
                 placements: Optional[List[Tuple[int, int]]] = None,
                 cols: int = COLS,
                 seq: List[str] = SHAPE_SEQUENCE):
        """
        Initialize a Tetris agent with either provided or random placements.

        Args:
            placements: List of (rotation, x-position) tuples for each shape in sequence
            cols: Width of the game board
            seq: Sequence of shape names
        """
        self.seq = seq

        if placements is None:
            self.placements = []
            for shp in seq:
                rot = random.randrange(0, len(SHAPES[shp]))
                max_dx = max(dx for dx, _ in SHAPES[shp][rot])
                x = random.randrange(cols - max_dx)
                self.placements.append((rot, x))
        else:
            if len(placements) != len(seq):
                raise ValueError(
                    f"Genome length ≠ shape list length: {len(placements)} != {len(seq)}")
            self.placements = placements

    def __call__(self) -> List[Tuple[int, int]]:
        """Return the agent's genome (placements)."""
        return self.placements

    def fitness(self) -> int:
        """Calculate the fitness of this agent by playing the sequence."""
        return Board().play_sequence(self.placements, self.seq)
    
    '''#changed:
    def fitness(self) -> int:
        """Calculate the fitness of this agent by playing the sequence."""
        b = Board()
        b.play_sequence(self.placements, self.seq)
        return b.score() ' '''

    
    def save(self, filename: str = "best_agent.txt") -> None:
        """Save the agent's placements to a file."""
        with open(filename, "w") as f:
            for placement in self.placements:
                f.write(f"{placement[0]},{placement[1]}\n")

    @classmethod
    def load(cls, filename: str = "best_agent.txt", seq: List[str] = SHAPE_SEQUENCE) -> 'Agent':
        """Load an agent from a file."""
        with open(filename, "r") as f:
            lines = f.read().split("\n")

        placements = []
        for line in lines:
            if line.strip():
                parts = line.replace("(", "").replace(")", "").split(",")
                placements.append((int(parts[0]), int(parts[1])))

        return cls(placements=placements, seq=seq)
