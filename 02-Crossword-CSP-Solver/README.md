# Crossword Puzzle Solver (CSP) 🧩

An automated solver for crossword puzzles, modeled as a **Constraint Satisfaction Problem (CSP)**. This project efficiently assigns words from a dictionary to a grid while satisfying all overlapping and length constraints.

## 🧠 Core Concepts & Logic
The solver treats each blank sequence in the grid as a **Variable**. The goal is to select a word for each variable from a provided **Domain** (word list) such that:
1.  [cite_start]**Unary Constraints:** The word length matches the number of cells in the variable[cite: 412, 413].
2.  [cite_start]**Binary Constraints:** Intersecting variables must have the same character at their point of overlap[cite: 413].

## 🚀 Implemented Algorithms
To solve the puzzle efficiently, the following AI techniques were utilized:

### 1. Consistency Enforcement
* [cite_start]**Node Consistency:** Pre-processing the domain to ensure every word fits the variable's required length[cite: 407, 426].
* [cite_start]**Arc Consistency (AC-3):** Iteratively reducing domains by ensuring that for every word in a variable's domain, there exists a consistent word in all neighboring variables[cite: 407, 427].

### 2. Backtracking Search
[cite_start]A recursive search algorithm that assigns values to variables one by one[cite: 408, 428]. If a conflict arises, it "backtracks" to try a different path.

### 3. Optimization Heuristics
To minimize the search space, the following heuristics are used to decide *which* variable to assign next and in *what* order:
* [cite_start]**MRV (Minimum Remaining Values):** Selects the variable with the fewest remaining words in its domain to fail early if no solution exists[cite: 409, 429].
* [cite_start]**Degree Heuristic:** Acts as a tie-breaker by picking the variable that has the most intersections with others[cite: 429].
* [cite_start]**LCV (Least Constraining Value):** Orders the words in a domain by how much flexibility they leave for neighboring variables[cite: 409, 430].

## 🛠️ Project Structure
* [cite_start]`crossword.py`: Defines the `Variable` and `Crossword` classes representing the grid structure[cite: 417, 418].
* [cite_start]`creator.py`: The main engine containing the CSP logic, AC-3, and backtracking search[cite: 424, 425].
* [cite_start]`main.py`: The entry point for running the solver via command line[cite: 431, 432].

## 🏃 How to Run
Run the solver by specifying a puzzle structure and a word list:
```bash
python main.py puzzles/p1.txt 