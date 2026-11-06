"""Tetris visualization module."""
from typing import List, Tuple, Dict, Union, Any, Optional
import time

try:
    from tetris_evolution.tetris.constants import (
        SHAPE_SEQUENCE, SHAPES, SHAPE_COLORS, ROWS, COLS, CELL_SIZE
    )
    from tetris_evolution.tetris.game import Board, legal_x
except ImportError:
    from .constants import (
        SHAPE_SEQUENCE, SHAPES, SHAPE_COLORS, ROWS, COLS, CELL_SIZE
    )
    from .game import Board, legal_x


def visualize(agent_or_plan: Any,
              seq: List[str] = SHAPE_SEQUENCE,
              cell: int = CELL_SIZE,
              delay: float = 0.0) -> None:
    """
    Show the plan in a Pygame window.
    Accepts an Agent OR a raw placements list.

    Args:
        agent_or_plan: Agent object or list of placements
        seq: Sequence of shapes to visualize
        cell: Size of each cell in pixels
        delay: Delay between piece drops (for slower visualization)
    """
    try:
        import pygame
        import sys
    except ImportError:
        print("Error: pygame is required for visualization. Install it with 'pip install pygame'.")
        return

    plan = agent_or_plan() if hasattr(agent_or_plan, '__call__') else agent_or_plan

    def draw_board(_screen, _board, extra=None, current_shape=None):
        _screen.fill((230, 230, 230))
        for pos, shape_type in _board.filled_shapes.items():
            x, y = pos
            if 0 <= y < ROWS:
                color = SHAPE_COLORS.get(shape_type, (80, 80, 80))
                pygame.draw.rect(_screen, color,
                                 (x*cell+1, y*cell+1, cell-2, cell-2))
        if extra and current_shape:
            color = SHAPE_COLORS.get(current_shape, (0, 180, 220))
            for x, y in extra:
                if 0 <= y < ROWS:
                    pygame.draw.rect(_screen, color,
                                     (x*cell+1, y*cell+1, cell-2, cell-2))
        for c in range(COLS+1):
            pygame.draw.line(_screen, (60, 60, 60),
                             (c*cell, 0), (c*cell, ROWS*cell))
        for r in range(ROWS+1):
            pygame.draw.line(_screen, (60, 60, 60),
                             (0, r*cell), (COLS*cell, r*cell))

        if _board.game_over:
            font = pygame.font.SysFont('Arial', 36, True)
            text = font.render('GAME OVER', True, (0, 0, 0))
            text_rect = text.get_rect(
                center=(_screen.get_width()/2, _screen.get_height()/2))
            _screen.blit(text, text_rect)

        pygame.display.flip()

    pygame.init()
    screen = pygame.display.set_mode((COLS*cell, ROWS*cell))
    pygame.display.set_caption("Tetris Evolution - Visualizer")
    clock = pygame.time.Clock()

    class ColorBoard(Board):
        def __init__(self, cols=COLS, rows=ROWS):
            super().__init__(cols, rows)
            self.filled_shapes: Dict[Tuple[int, int], str] = {}

        def drop(self, shape: str, rot: int, ox: int) -> None:
            if not legal_x(shape, rot, ox, self.cols) or self.game_over:
                return
            y = -2
            while self._fits(shape, rot, ox, y + 1):
                y += 1
            for dx, dy in SHAPES[shape][rot]:
                pos = (ox + dx, y + dy)
                self.filled.add(pos)
                self.filled_shapes[pos] = shape
                if y + dy <= 0:
                    self.game_over = True

    board = ColorBoard()

    for (rot, x_pos), shp in zip(plan, seq):
        if board.game_over:
            draw_board(screen, board)
            pygame.time.wait(3000)
            break

        rot = rot % len(SHAPES[shp])
        if not legal_x(shp, rot, x_pos):
            continue

        if any((x_pos + dx, dy) in board.filled for dx, dy in SHAPES[shp][rot] if dy <= 0):
            board.game_over = True
            draw_board(screen, board)
            pygame.time.wait(500)
            break

        y = 0
        while board._fits(shp, rot, x_pos, y + 1):
            y += 1
            fall_coords = [(x_pos + dx, y + dy) for dx, dy in SHAPES[shp][rot]]
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            draw_board(screen, board, fall_coords, shp)
            clock.tick(60)

            if delay > 0:
                time.sleep(delay)

        board.drop(shp, rot, x_pos)

        if y == 0:
            board.game_over = True

        draw_board(screen, board)

        pygame.time.wait(100)

    while True:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)
