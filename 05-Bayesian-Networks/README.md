# Bayesian Networks: Power Plant Safety & Sports Prediction 🧠📊

This repository contains a comprehensive implementation of **Bayesian Networks** for probabilistic reasoning, covering both Exact and Approximate Inference techniques. The project is divided into two main parts: a safety diagnostic system for a nuclear power plant and a sports outcome predictor.

## 🛠️ Key Implementations

### Part 1: Nuclear Power Plant Diagnostic Net
A causal model designed to monitor a nuclear reactor's temperature and the reliability of its sensors/alarms.
* **Variables:** Temperature (T), Faulty Alarm (Fa), Faulty Gauge (Fg), Gauge Reading (G), and Alarm Status (A).
* **Logic:** Models complex dependencies, such as the gauge being more likely to fail when the temperature is high.

### Part 2: Sports Outcome Prediction (Bayes Net)
A dynamic network to predict the outcome of matches between multiple teams based on their latent skill levels.
* **Structure:** Designed a directed acyclic graph (DAG) where match outcomes depend on the performance of competing teams.

## 🔬 Inference Methods
The project implements and compares four major inference algorithms:

1.  **Exact Inference (Enumeration):** Computing precise marginal and conditional probabilities by summing over hidden variables.
2.  **Rejection Sampling:** An approximate method that generates samples and rejects those that do not match the evidence.
3.  **Likelihood Weighting:** A more efficient sampling technique that uses importance weights to avoid the "rejection" problem.
4.  **Gibbs Sampling:** A Markov Chain Monte Carlo (MCMC) algorithm that transitions through states to reach a stationary distribution.

## 📈 Performance Analysis
The included `report.pdf` provides a detailed comparison of these methods, analyzing:
* **Convergence:** How sample size affects the accuracy of approximate methods.
* **Efficiency:** Why Likelihood Weighting outperforms Rejection Sampling in "rare event" scenarios.
* **Local Dependencies:** The effectiveness of Gibbs Sampling in locally structured networks.

## 📁 Project Structure
* `bayes_model.ipynb`: Core implementation of the network structures and inference algorithms.
* `utils/`: Helper functions for network visualization and probability table (CPT) management.
* `report.pdf`: Analytical results, error comparisons (Exact vs. Approximate), and visualization of the DAGs.

## 🚀 Quick Start
To run the simulations and see the inference in action:
```bash
pip install numpy matplotlib
jupyter notebook bayes_model.ipynb