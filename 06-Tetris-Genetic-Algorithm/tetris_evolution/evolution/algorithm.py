"""Evolutionary algorithm implementation for Tetris optimization."""
from tetris.constants import SHAPE_SEQUENCE, SHAPES, COLS
from tetris.agent import Agent
from typing import List, Tuple, Callable, Optional, Any, Dict, Union
import random
import time
from abc import ABC, abstractmethod
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Import using absolute paths


class Selection(ABC):
    """Base class for selection operators."""

    @abstractmethod
    def select(self, population: List[Agent], fitnesses: List[int]) -> List[Agent]:
        """
        Select individuals from the population based on their fitness.

        Args:
            population: List of agents
            fitnesses: List of fitness values corresponding to each agent

        Returns:
            Selected individuals
        """
        pass


class TournamentSelection(Selection):
    """Tournament selection implementation."""

    def __init__(self, tournament_size: int = 3):
        """
        Initialize tournament selection.

        Args:
            tournament_size: Number of individuals in each tournament
        """
        self.tournament_size = tournament_size

    def select(self, population: List[Agent], fitnesses: List[int]) -> List[Agent]:
        """
        TODO: Student implementation in the implementation.py file

        Implement tournament selection:
        1. Randomly select tournament_size individuals from the population
        2. Choose the one with the highest fitness
        3. Repeat until you have selected the same number as the original population

        Return the selected individuals.
        """
        pass


class RouletteWheelSelection(Selection):
    """Roulette wheel (fitness proportionate) selection implementation."""

    def select(self, population: List[Agent], fitnesses: List[int]) -> List[Agent]:
        """
        TODO: Student implementation in the implementation.py file

        Implement roulette wheel selection:
        1. Calculate the sum of all fitness values
        2. Select individuals with probability proportional to their fitness
        3. Repeat until you have selected the same number as the original population

        Return the selected individuals.
        """
        pass


class Crossover(ABC):
    """Base class for crossover operators."""

    @abstractmethod
    def crossover(self, parent1: Agent, parent2: Agent) -> Tuple[Agent, Agent]:
        """
        Perform crossover between two parents to produce two offspring.

        Args:
            parent1: First parent agent
            parent2: Second parent agent

        Returns:
            Two offspring agents
        """
        pass


class SinglePointCrossover(Crossover):
    """Single point crossover implementation."""

    def crossover(self, parent1: Agent, parent2: Agent) -> Tuple[Agent, Agent]:
        """
        TODO: Student implementation in the implementation.py file

        Implement single point crossover:
        1. Choose a random crossover point
        2. Create two children by swapping parts of the parents' placements
        3. Return the two new agents

        Note: Make sure the sequence is the same for both parents and children.
        """
        pass


class UniformCrossover(Crossover):
    """Uniform crossover implementation."""

    def __init__(self, swap_probability: float = 0.5):
        """
        Initialize uniform crossover.

        Args:
            swap_probability: Probability of swapping each gene
        """
        self.swap_probability = swap_probability

    def crossover(self, parent1: Agent, parent2: Agent) -> Tuple[Agent, Agent]:
        """
        TODO: Student implementation in the implementation.py file

        Implement uniform crossover:
        1. For each position in the genome, swap the genes with probability swap_probability
        2. Create two children with the resulting genomes
        3. Return the two new agents

        Note: Make sure the sequence is the same for both parents and children.
        """
        pass


class Mutation(ABC):
    """Base class for mutation operators."""

    @abstractmethod
    def mutate(self, agent: Agent) -> Agent:
        """
        Mutate an agent's genome.

        Args:
            agent: Agent to mutate

        Returns:
            Mutated agent
        """
        pass


class RandomMutation(Mutation):
    """Random mutation implementation."""

    def __init__(self, mutation_rate: float = 0.1):
        """
        Initialize random mutation.

        Args:
            mutation_rate: Probability of mutating each gene
        """
        self.mutation_rate = mutation_rate

    def mutate(self, agent: Agent) -> Agent:
        """
        TODO: Student implementation in the implementation.py file

        Implement random mutation:
        1. For each placement in the agent's genome:
           a. With probability mutation_rate, replace it with a random valid placement
           b. Otherwise, keep it unchanged
        2. Return a new agent with the mutated genome

        Note: For each shape, you need to ensure the rotation is valid and the
        x-position is within the board width.
        """
        pass


class GeneticAlgorithm:
    """Genetic algorithm implementation for Tetris optimization."""

    def __init__(self,
                 population_size: int = 50,
                 selection: Selection = None,
                 crossover: Crossover = None,
                 mutation: Mutation = None,
                 elitism_count: int = 2,
                 seq: List[str] = SHAPE_SEQUENCE):
        """
        Initialize the genetic algorithm.

        Args:
            population_size: Number of individuals in the population
            selection: Selection operator
            crossover: Crossover operator
            mutation: Mutation operator
            elitism_count: Number of best individuals to keep unchanged
            seq: Sequence of Tetris shapes to optimize for
        """
        self.population_size = population_size
        self.selection = selection or TournamentSelection()
        self.crossover = crossover or SinglePointCrossover()
        self.mutation = mutation or RandomMutation()
        self.elitism_count = elitism_count
        self.seq = seq

        # Initialize population
        self.population = [Agent(seq=seq) for _ in range(population_size)]
        self.best_agent = None
        self.best_fitness = 0

    def evaluate_population(self) -> List[int]:
        """
        Calculate fitness for each individual in the population.

        Returns:
            List of fitness values
        """
        return [agent.fitness() for agent in self.population]

    def run_generation(self) -> Tuple[Agent, int]:
        """
        Run one generation of the genetic algorithm.

        TODO: Student implementation in the implementation.py file

        Implement a single generation of the genetic algorithm:
        1. Evaluate the fitness of the population
        2. Select parents using the selection operator
        3. Create offspring using crossover and mutation
        4. Apply elitism (keep the best individuals)
        5. Replace the old population with the new one
        6. Return the best agent and its fitness

        Returns:
            Tuple of (best_agent, best_fitness)
        """
        pass

    def run(self,
            max_generations: int = 100,
            target_fitness: Optional[int] = None,
            verbose: bool = True,
            log_interval: int = 10) -> Agent:
        """
        Run the genetic algorithm for multiple generations.

        Args:
            max_generations: Maximum number of generations to run
            target_fitness: Stop if this fitness is reached
            verbose: Whether to print progress
            log_interval: How often to print progress

        Returns:
            Best agent found
        """
        start_time = time.time()

        for generation in range(max_generations):
            best_agent, best_fitness = self.run_generation()

            # Update overall best
            if self.best_agent is None or best_fitness > self.best_fitness:
                self.best_agent = best_agent
                self.best_fitness = best_fitness

            # Print progress
            if verbose and generation % log_interval == 0:
                elapsed = time.time() - start_time
                print(f"Generation {generation}/{max_generations} | "
                      f"Best Fitness: {self.best_fitness} | "
                      f"Time: {elapsed:.2f}s")

            # Check if target fitness reached
            if target_fitness is not None and self.best_fitness >= target_fitness:
                if verbose:
                    print(
                        f"Target fitness {target_fitness} reached at generation {generation}")
                break

        return self.best_agent

    def save_best_agent(self, filename: str) -> None:
        """Save the best agent to a file."""
        if self.best_agent is not None:
            self.best_agent.save(filename)
        else:
            raise ValueError("No best agent to save")
