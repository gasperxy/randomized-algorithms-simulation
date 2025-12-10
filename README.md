# Randomized Experiments Lab

A modular Flask app for visualizing randomized algorithms. Each experiment lives in its own module with a consistent controller/simulation/visualization split.


Try it out:

[![Live Demo](https://img.shields.io/badge/Azure-Live%20App-blue?logo=microsoft-azure)](https://randomized-algorithm-simulator-ehbrb2c7fde0eqgr.germanywestcentral-01.azurewebsites.net/)

## Quick start

1. **Create virtual environment and install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run locally**
   ```bash
   flask --app app run --debug
   ```
3. **Docker**
   ```bash
   docker build -t randomized-lab .
   docker run -p 8000:8000 randomized-lab
   ```

## Current modules
- **Phase Transition (G(n, p))** – Sweeps edge probability to show Erdős–Rényi phase transitions and statistics.
- **Edge Process (G(n, m))** – Adds random edges one by one to map m onto the equivalent G(n, p) thresholds.
- **Monte Carlo Union of Rectangles** – Estimates the area of overlapping rectangles via sampling while displaying the disjoint \(B_i\) slices.
- **Monte Carlo ln(2)** – Samples \(x ∈ [1,2]\), averages \(1/x\), and plots convergence toward ln(2).
- **Markov Chains — Basics** – Generates a tiny random Markov chain, walks a sample trajectory, and compares empirical visitation to the stationary distribution.
- **Markov Random 2-SAT Walk** – Animates Papadimitriou's random walk on a random 2-SAT instance, showing the Markov chain over satisfied-clause counts.
- **Markov Random 3-SAT Walk** – Restart-based random walk for 3-SAT, flipping variables in unsatisfied clauses across repeated trials to target a desired failure probability.

## Module structure
Each experiment (e.g., `phase_transition`, `g_nm`, `monte_carlo_union`) contains:

- `simulation.py`: pure generation logic (graphs, statistics, Monte Carlo runs).
- `controller.py`: parses form inputs, orchestrates the simulation, prepares template context.
- `visualization.py`: builds Plotly figures (HTML/JS) rendered by the presentation layer.

Shared utilities (graph stats, module registry) live under `app/modules/common`. Templates under `app/presentation/templates` provide server-rendered views.

See `docs/modules/` for detailed module guides.
