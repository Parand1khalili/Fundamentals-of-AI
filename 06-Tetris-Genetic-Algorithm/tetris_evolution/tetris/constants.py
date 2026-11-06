"""Constants for the Tetris game."""
from typing import List, Dict, Any
import os
import pkg_resources

COLS: int = 10
ROWS: int = 15
CELL_SIZE: int = 40

SHAPES: Dict[str, List[List[tuple]]] = {
    'I': [[(0, 0), (1, 0), (2, 0), (3, 0)],
          [(2, -1), (2, 0), (2, 1), (2, 2)]],
    'O': [[(0, 0), (1, 0), (0, 1), (1, 1)]],
    'T': [[(1, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (2, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (1, 2)],
          [(1, 0), (0, 1), (1, 1), (1, 2)]],
    'S': [[(1, 0), (2, 0), (0, 1), (1, 1)],
          [(1, 0), (1, 1), (2, 1), (2, 2)]],
    'Z': [[(0, 0), (1, 0), (1, 1), (2, 1)],
          [(2, 0), (1, 1), (2, 1), (1, 2)]],
    'L': [[(0, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (2, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (2, 2)],
          [(1, 0), (1, 1), (0, 2), (1, 2)]],
    'J': [[(2, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 2)],
          [(0, 1), (1, 1), (2, 1), (0, 2)],
          [(0, 0), (1, 0), (1, 1), (1, 2)]],
}

SHAPE_COLORS: Dict[str, tuple] = {
    'I': (205, 0, 0),
    'O': (0, 205, 0),
    'T': (0, 0, 205),
    'S': (205, 205, 0),
    'Z': (0, 205, 205),
    'L': (205, 0, 205),
    'J': (128-50, 128-50, 128-50),
}


def get_data_path(filename: str) -> str:
    """Get path to a data file, whether in development or installed package."""
    try:
        return pkg_resources.resource_filename('tetris_evolution', f'data/{filename}')
    except (ModuleNotFoundError, FileNotFoundError):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'data', filename)


def load_shape_sequence() -> List[str]:
    """Load the shape sequence from data file."""
    sequence_path = get_data_path('shape_sequence.txt')
    with open(sequence_path, "r") as f:
        return f.read().split()


try:
    SHAPE_SEQUENCE: List[str] = load_shape_sequence()
except FileNotFoundError:
    SHAPE_SEQUENCE = ['I', 'O', 'T', 'S', 'Z', 'L', 'J'] * 10
