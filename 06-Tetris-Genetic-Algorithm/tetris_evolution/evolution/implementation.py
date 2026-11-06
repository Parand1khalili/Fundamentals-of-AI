"""
Implement the algorithm.py file here.
"""
from evolution.algorithm import (
    TournamentSelection,
    RouletteWheelSelection,
    SinglePointCrossover,
    UniformCrossover,
    RandomMutation,
    GeneticAlgorithm
)
from tetris.constants import SHAPES, COLS, SHAPE_SEQUENCE
from tetris.agent import Agent
import random
import sys
import os
from typing import List, Tuple

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class CompletedTournamentSelection(TournamentSelection):
    def select(self, population: List[Agent], fitnesses: List[int]) -> List[Agent]:

        """
        Implement tournament selection.

        1. Randomly select tournament_size individuals from the population
        2. Choose the one with the highest fitness
        3. Repeat until you have selected the same number as the original population
        """
        selected = []

        """ TODO: Student implementation """
        #randomly choose from population -> choose winner based on fitness untill we have chosen in the length of the first population
        while len(selected) < len(population): 
            #Randomly select tournament_size individuals from the population and sample
            candidates = random.sample(list(zip(population, fitnesses)), self.tournament_size)
            winner = max(candidates, key=lambda x: x[1])[0]  # Agent with highest fitness : the winnerr
            selected.append(winner)
        return selected


class CompletedRouletteWheelSelection(RouletteWheelSelection):
    def select(self, population: List[Agent], fitnesses: List[int]) -> List[Agent]:
        """
        Implement roulette wheel selection.

        1. Calculate the sum of all fitness values
        2. Select individuals with probability proportional to their fitness
        3. Repeat until you have selected the same number as the original population

        """
        selected = []

        """ TODO: Student implementation """
        total_fitness = sum(fitnesses)
        if total_fitness == 0:
            # fallback _ if total fitness is 0 -> chose without paying attention to the fitness and choose randomly
            return random.choices(population, k=len(population))
        probabilities = [f / total_fitness for f in fitnesses] #probability of choosing each agent
        selected = random.choices(population, weights=probabilities, k=len(population)) #it will choose randomly but fitness/total are weight

        return selected


class CompletedSinglePointCrossover(SinglePointCrossover):
    def crossover(self, parent1: Agent, parent2: Agent) -> Tuple[Agent, Agent]:
        """
        Implement single point crossover.

        1. Choose a random crossover point
        2. Create two children by swapping parts of the parents' placements
        3. Return the two new agents

        """

        """ TODO: Student implementation """
        crossover_point = random.randint(1, len(parent1.placements) - 1) #Choose a random crossover point
        child1 = Agent()
        child2 = Agent()
        #swapping parts of the parents for creating new agents (childs)
        child1.placements = parent1.placements[:crossover_point] + parent2.placements[crossover_point:]
        child2.placements = parent2.placements[:crossover_point] + parent1.placements[crossover_point:]

        return child1, child2


class CompletedUniformCrossover(UniformCrossover):
    def crossover(self, parent1: Agent, parent2: Agent) -> Tuple[Agent, Agent]:
        """
        Implement uniform crossover.

        1. For each position in the genome, swap the genes with probability swap_probability
        2. Create two children with the resulting genomes
        3. Return the two new agents'''
        
        """
        #make sure parents have the same genome length
        if len(parent1.placements) != len(parent2.placements):
            raise ValueError("Parents must have the same genome length")
        #create new childs
        child1 = Agent()
        child2 = Agent()
        child1.placements = []
        child2.placements = []

        """ TODO: Student implementation """ 
        #uniforn crossover
        for gene1, gene2 in zip(parent1.placements, parent2.placements):
            if random.random() < self.swap_probability:
                # With probability swap_probability -> perform the swap
                child1.placements.append(gene2)
                child2.placements.append(gene1)
            else:
                child1.placements.append(gene1)
                child2.placements.append(gene2)

        return child1, child2

class CompletedRandomMutation(RandomMutation):
    def mutate(self, agent: Agent) -> Agent:
        """
        Implement random mutation.

        1. For each placement in the agent's genome:
           a. With probability mutation_rate, replace it with a random valid placement
           b. Otherwise, keep it unchanged
        2. Return a new agent with the mutated genome
        """
        mutated = Agent()
        """ TODO: Student implementation """
        mutated.placements = []

         # iteerate placement in the parent genome
        for i, (rot, x) in enumerate(agent.placements):
            # With mutation_rate probability -> change this gene

            if random.random() < self.mutation_rate:

                shape = agent.seq[i]
                # random rotation index for the shape
                new_rot = random.randrange(0, len(SHAPES[shape]))
                # maximum x offset (width) the rotated shape can have
                max_dx = max(dx for dx, _ in SHAPES[shape][new_rot])
                # random x-position that fits on the board
                new_x = random.randrange(COLS - max_dx)
                # Append the new (rotation, x-position) as the mutated gene
                mutated.placements.append((new_rot, new_x))
            else:
                # No change needed
                mutated.placements.append((rot, x))
       
        return mutated

class CompletedGeneticAlgorithm(GeneticAlgorithm):
    def run_generation(self) -> Tuple[Agent, int]:
        """
        Run one generation of the genetic algorithm.

        Steps:
        1. Evaluate the fitness of the population
        2. Select parents using the selection operator
        3. Create offspring using crossover and mutation
        4. Apply elitism (keep the best individuals)
        5. Replace the old population with the new one
        6. Return the best agent and its fitness
        """

        # Calculate fitness of all in the population
        fitnesses = [agent.fitness() for agent in self.population]

        # Select parents based on fitness
        parents = self.selection.select(self.population, fitnesses)
        new_population = []

        # Perform crossover and mutation -> new offspring
        for i in range(0, len(parents) - 1, 2):
            parent1 = parents[i]
            parent2 = parents[i + 1]
            # Generate two children from the pair of parents
            child1, child2 = self.crossover.crossover(parent1, parent2)
            # mutation to each child and add them
            child1 = self.mutation.mutate(child1)
            child2 = self.mutation.mutate(child2)
            new_population.extend([child1, child2])

        # odd number of parents -> carry over the last one
        if len(parents) % 2 == 1:
            new_population.append(parents[-1])

        # Keep the best individuals (elitism)
        elitism_num = self.elitism_count
        sorted_population = [agent for _, agent in sorted(zip(fitnesses, self.population), key=lambda x: x[0], reverse=True)]
        elites = sorted_population[:elitism_num]

        # Replace the beginning of the new population with elites
        new_population[:elitism_num] = elites
        # change the population to original size
        self.population = new_population[:self.population_size]
        # Recalculate fitness -> find the best agent in the new generation
        fitnesses = [agent.fitness() for agent in self.population]
        best_idx = fitnesses.index(max(fitnesses))
        best_agent = self.population[best_idx]
        best_fitness = fitnesses[best_idx]

        # Storing
        self.best_agent = best_agent
        self.best_fitness = best_fitness

        return best_agent, best_fitness
    