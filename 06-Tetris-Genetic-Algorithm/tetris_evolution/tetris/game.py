"""Core Tetris game logic."""
from typing import List, Tuple, Set, Optional

try:
    from tetris_evolution.tetris.constants import SHAPES, COLS, ROWS, SHAPE_SEQUENCE
except ImportError:
    from .constants import SHAPES, COLS, ROWS, SHAPE_SEQUENCE


def legal_x(shape: str, rot: int, x_off: int, cols: int = COLS) -> bool:
    """
    True if every square of (shape, rot) lies in 0 … cols-1 after x_off.
    """
    for dx, _ in SHAPES[shape][rot]:
        if not (0 <= x_off + dx < cols):
            return False
    return True


class Board:
    """Represents a Tetris game board."""

    def __init__(self, cols: int = COLS, rows: int = ROWS):
        """Initialize a new game board with given dimensions."""
        self.cols: int = cols
        self.rows: int = rows
        self.filled: Set[Tuple[int, int]] = set()
        self.game_over: bool = False

    def _fits(self, shape: str, rot: int, ox: int, oy: int) -> bool:
        """True if piece is within walls/floor and not colliding."""
        for dx, dy in SHAPES[shape][rot]:
            x, y = dx + ox, dy + oy
            if x < 0 or x >= self.cols:
                return False
            if y >= self.rows:
                return False
            if (x, y) in self.filled:
                return False
        return True

    def drop(self, shape: str, rot: int, ox: int) -> None:
        """Drop the piece straight down until blocked, then lock it."""
        if not legal_x(shape, rot, ox, self.cols) or self.game_over:
            return
        y = -5
        while self._fits(shape, rot, ox, y + 1):
            y += 1
        for dx, dy in SHAPES[shape][rot]:
            pos = (ox + dx, y + dy)
            self.filled.add(pos)
            if y + dy <= 0:
                self.game_over = True

    def score(self) -> int:
        score = 0
        rows, cols = self.rows, self.cols

        # Count how many blocks in each row
        row_counts = [0] * rows
        for (x, y) in self.filled:
            if 0 <= y < rows:
                row_counts[y] += 1

        # Completed rows - reward deeper clears much more
        full_rows = 0
        depth_bonus = 0
        for y in range(rows):
            if row_counts[y] == cols:
                full_rows += 1
                if y >= rows - 8:
                    # Bottom 6 rows : very strong reward
                    depth_bonus += (abs(y + 1) ** 5)
                else:
                    # Other rows get depth-based reward
                    depth_bonus += (abs(y + 1) ** 2)


        # Column heights
        heights = [0] * cols
        for (x, y) in self.filled:
            heights[x] = max(heights[x], y + 1)
        total_height = sum(heights)

        # Well depth penalty
        well_penalty = 0
        for x in range(1, cols - 1):
            left = heights[x - 1]
            right = heights[x + 1]
            center = heights[x]
            if center < left and center < right:
                well_depth = min(left, right) - center
                well_penalty += well_depth ** 2  # Penalize deeper wells more

        # Count holes - weighted more if they are lower
        holes = 0
        full = 0
        holes_depth = 0
        for x in range(cols):
            block_seen = False
            for y in range(rows):
                if (x, y) in self.filled:
                    block_seen = True
                    depth_weight1 = (rows - y) ** 2  # Lower y  => higher score
                    full += depth_weight1

                # elif block_seen:
                else:
                    depth_weight = (y) ** 6  # Lower y  => higher penalty
                    holes += 1
                    holes_depth += depth_weight

        # Bumpiness (height difference between adjacent columns)
        bumpiness = 0
        for i in range(cols - 1):
            bumpiness += abs(heights[i] - heights[i + 1])

        # Final score calculation
        score += full_rows  * 400                 # Base reward per cleared row
        score += depth_bonus * 1100                 # Reward depth of full rows
        # score += full * 50                        # reward for full entries
        # score -= holes * 250 
        score -= holes_depth * 800                  # Penalize deeper holes more
        score -= (total_height ** 2) * 5               # Penalize high stacks
        score -= well_penalty * 30
        score -= bumpiness * 60                   # Penalize uneven surface

        print(f"Score: rows={full_rows}, holes={holes}, height={total_height}, bumpiness={bumpiness}, total={score}")
        return score


    def play_sequence(self,
                      placements: List[Tuple[int, int]],
                      seq: List[str] = SHAPE_SEQUENCE) -> int:
        """Return score after dropping every (rot,x) on the shape list."""
        b = Board(self.cols, self.rows)
        for (rot, x), shp in zip(placements, seq):
            if b.game_over:
                break
            b.drop(shp, rot % len(SHAPES[shp]), x)
        return b.score()
