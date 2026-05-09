# Fundamentals of Artificial Intelligence 🧠✨

A comprehensive collection of classical and modern AI projects developed at **Amirkabir University of Technology (Tehran Polytechnic)**. This repository showcases a diverse range of AI implementations, from state-space search and constraint satisfaction to adversarial game theory, reinforcement learning, and probabilistic reasoning.

---

## 📂 Project Portfolio

### 1. 📦 [Sokoban Search Solver](./01-Sokoban-AI-Solver)
*  **Goal:** Solving a modified Sokoban puzzle with dynamic costs (Apples and Poisons).
*  **Algorithms:** BFS, DFS, UCS, Greedy Search, and **A***.
*  **Key Features:** Custom heuristic design with corner-deadlock detection for optimal pathfinding in complex grids.

### 2. 🧩 [Crossword CSP Solver](./02-Crossword-CSP-Solver)
* **Goal:** Automated crossword puzzle generation using **Constraint Satisfaction Problems (CSP)**.
* **Core Logic:** Implements **AC-3 (Arc Consistency)** to prune the domain and **Backtracking Search** for value assignment.
* **Optimizations:** Utilizes **MRV (Minimum Remaining Values)**, Degree Heuristics, and **LCV (Least Constraining Value)** to minimize search space.

### 3. ⚔️ [Adversarial Isolation Agent](./03-Isolation-Game-Agent)
*  **Goal:** An intelligent agent for the game "Isolation" featuring Knight-like movement.
*  **Algorithms:** **Minimax** and **Alpha-Beta Pruning** with **Iterative Deepening** to meet strict time constraints.
* **Heuristics:** Advanced evaluation functions focusing on board control and limiting opponent mobility.

### 4. 🚀 [RL LunarLander & MDP](./04-RL-LunarLander)
*  **Goal:** Mastering the `LunarLander-v2` environment and solving GridWorld MDPs.
* **Reinforcement Learning:** Implemented **Q-Learning** with state discretization (binning) to handle continuous state spaces.
* **Dynamic Programming:** Solves MDPs using **Value Iteration** and **Policy Iteration** based on Bellman Equations.

### 5. 📉 [Bayesian Networks & Inference](./05-Bayesian-Networks)
* **Goal:** Probabilistic reasoning in uncertain environments (Nuclear Plant Safety & Sports Prediction).
* **Methods:**
    * **Exact Inference:** Variable Elimination and Enumeration.
    * **Approximate Inference:** Rejection Sampling, **Likelihood Weighting**, and **Gibbs Sampling (MCMC)**.

---

## 🛠️ Tech Stack & Requirements
*  **Language:** Python 3.10+ [cite: 1010]
*  **Libraries:** `Pygame`, `NumPy`, `Pandas`, `Gymnasium`, `Matplotlib`, `Sci-kit Learn` 
*  **Documentation:** LaTeX (for technical reports) 

## 🚀 How to Run
1. Clone the repository: `git clone https://github.com/parand1khalili/Fundamentals-of-AI.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Navigate to any project folder and run the `main.py` or `.ipynb` file.

---
 *Developed by **Parand Khalili** as part of the B.S. in Computer Engineering at Amirkabir University of Technology.* 