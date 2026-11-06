"""Run the evolutionary algorithm with the completed implementations."""
from tetris.agent import Agent
from tetris.visualizer import visualize
from evolution.implementation import (
    CompletedGeneticAlgorithm,
    CompletedRandomMutation,
    CompletedRouletteWheelSelection,
    CompletedSinglePointCrossover,
    CompletedTournamentSelection,
    CompletedUniformCrossover
)
from evolution.algorithm import (
    TournamentSelection,
    RouletteWheelSelection,
    SinglePointCrossover,
    UniformCrossover,
    RandomMutation,
    GeneticAlgorithm
)
from typing import List, Tuple
import random
import os
import sys
import argparse
import time
import matplotlib.pyplot as plt

# Add the parent directory to the path to enable imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run Tetris Evolution")

    parser.add_argument("--generations", type=int, default=100,
                        help="Number of generations to run")
    parser.add_argument("--population", type=int, default=100,
                        help="Population size")
    parser.add_argument("--elitism", type=int, default=2,
                        help="Number of elite individuals to keep")
    parser.add_argument("--mutation-rate", type=float, default=0.1,
                        help="Mutation rate (0.0 to 1.0)")

    parser.add_argument("--selection", type=str, default="tournament",
                        choices=["tournament", "roulette"],
                        help="Selection method to use")
    parser.add_argument("--tournament-size", type=int, default=3,
                        help="Tournament size for tournament selection")

    parser.add_argument("--crossover", type=str, default="single-point",
                        choices=["single-point", "uniform"],
                        help="Crossover method to use")
    parser.add_argument("--swap-prob", type=float, default=0.5,
                        help="Swap probability for uniform crossover")

    parser.add_argument("--visualize", action="store_true",
                        help="Visualize the best agent after evolution")
    parser.add_argument("--delay", type=float, default=0.05,
                        help="Delay for visualization animation")

    parser.add_argument("--output", type=str, default="best_agent.txt",
                        help="File to save the best agent to")
    parser.add_argument("--plot", action="store_true",
                        help="Plot fitness over generations")

    return parser.parse_args()


def main():
    """Run the evolutionary algorithm with the specified parameters."""
    args = parse_args()

    if args.selection == "tournament":
        selection = CompletedTournamentSelection(
            tournament_size=args.tournament_size)
        selection_name = f"Tournament (size={args.tournament_size})"
    else:  # roulette
        selection = CompletedRouletteWheelSelection()
        selection_name = "Roulette Wheel"

    if args.crossover == "single-point":
        crossover = CompletedSinglePointCrossover()
        crossover_name = "Single Point"
    else:  # uniform
        crossover = CompletedUniformCrossover(swap_probability=args.swap_prob)
        crossover_name = f"Uniform (p={args.swap_prob})"

    mutation = CompletedRandomMutation(mutation_rate=args.mutation_rate)

    ga = CompletedGeneticAlgorithm(
        population_size=args.population,
        selection=selection,
        crossover=crossover,
        mutation=mutation,
        elitism_count=args.elitism
    )

    best_agent = Agent.load("hold.txt")
    for i in range(20):
        ga.population.append(best_agent)

    fitness_history = []
    best_fitness = 0

    print(f"Running evolutionary algorithm with:")
    print(f"  - Population size: {args.population}")
    print(f"  - Generations: {args.generations}")
    print(f"  - Selection: {selection_name}")
    print(f"  - Crossover: {crossover_name}")
    print(f"  - Mutation rate: {args.mutation_rate}")
    print(f"  - Elitism count: {args.elitism}")
    print()

    start_time = time.time()

    for generation in range(args.generations):
        _, fitness = ga.run_generation()
        fitness_history.append(fitness)

        if fitness > best_fitness:
            best_fitness = fitness

        if generation % 5 == 0 or generation == args.generations - 1:
            elapsed = time.time() - start_time
            print(f"Generation {generation+1}/{args.generations} | "
                  f"Current best: {fitness} | "
                  f"Overall best: {best_fitness} | "
                  f"Time: {elapsed:.2f}s")

    best_agent = ga.best_agent
    print(f"\nEvolution complete!")
    print(f"Best fitness: {best_agent.fitness()}")

    best_agent.save(args.output)
    print(f"Best agent saved to {args.output}")

    if args.plot:
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, args.generations + 1), fitness_history)
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.title("Fitness Evolution")
        plt.grid(True)
        plt.savefig("fitness_evolution.png")
        print("Fitness plot saved to fitness_evolution.png")
        plt.close()

    if args.visualize:
        print("\nVisualizing the best agent...")
        print("Close the window when done viewing.")
        try:
            visualize(best_agent, delay=args.delay)
        except ImportError:
            print("Error: pygame not installed. Install with 'pip install pygame'")

    print("\nDone!")


if __name__ == "__main__":
    main()
