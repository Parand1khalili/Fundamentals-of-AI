"""Tetris Evolutionary Algorithm Assignment Package."""

from tetris_evolution.tetris.constants import SHAPE_SEQUENCE
from tetris_evolution.tetris.game import Board
from tetris_evolution.tetris.agent import Agent
from tetris_evolution.tetris.visualizer import visualize
from tetris_evolution.evolution.algorithm import GeneticAlgorithm, Selection, Crossover, Mutation

__version__ = "1.0.0"
