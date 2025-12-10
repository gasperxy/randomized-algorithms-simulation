from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Sequence

import numpy as np


@dataclass
class SimulationParameters:
    n_states: int
    steps: int
    start_state: int
    seed: int | None = None


def _generate_transition_matrix(n_states: int, seed: int | None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = rng.random((n_states, n_states)) + 0.05  # keep every entry positive
    # De-emphasize self-loops to make animations more dynamic.
    np.fill_diagonal(base, base.diagonal() * 0.5)
    row_sums = base.sum(axis=1, keepdims=True)
    base = base / row_sums
    # Mix with uniform noise to guarantee ergodicity and avoid tiny rows.
    epsilon = 0.05
    uniform = np.full((n_states, n_states), 1.0 / n_states)
    return (1 - epsilon) * base + epsilon * uniform


def _stationary_distribution(P: np.ndarray) -> np.ndarray:
    # Solve (P^T - I) pi = 0 with the normalization sum pi = 1.
    n = P.shape[0]
    A = P.T - np.eye(n)
    A[-1, :] = 1.0
    b = np.zeros(n)
    b[-1] = 1.0
    pi = np.linalg.solve(A, b)
    # Clamp tiny negatives due to numerical noise.
    pi = np.clip(pi, 0, None)
    return pi / pi.sum()


def _sample_next(rng: random.Random, probs: Sequence[float]) -> int:
    # Simple inverse-CDF sampler to pick the next state.
    r = rng.random()
    cumulative = 0.0
    for idx, p in enumerate(probs):
        cumulative += p
        if r <= cumulative:
            return idx
    return len(probs) - 1


def run(params: SimulationParameters) -> Dict:
    matrix = _generate_transition_matrix(params.n_states, params.seed)
    stationary = _stationary_distribution(matrix)

    rng = random.Random(params.seed)
    current = max(0, min(params.start_state - 1, params.n_states - 1))
    counts = [0 for _ in range(params.n_states)]
    hitting_times = [None for _ in range(params.n_states)]
    path_states: List[int] = []
    variation_over_time: List[float] = []

    for step in range(params.steps):
        counts[current] += 1
        if hitting_times[current] is None:
            hitting_times[current] = step
        if step < 300:  # limit payload for playback to keep HTML light
            path_states.append(current)
        probs = matrix[current]
        total = sum(counts)
        if total:
            empirical_step = [c / total for c in counts]
            # Variation distance between empirical and stationary after this step.
            variation_over_time.append(
                0.5 * sum(abs(empirical_step[i] - stationary[i]) for i in range(params.n_states))
            )
        current = _sample_next(rng, probs)

    total = sum(counts) or 1
    empirical = [c / total for c in counts]
    variation = 0.5 * sum(abs(empirical[i] - stationary[i]) for i in range(params.n_states))
    unique_states = sum(1 for c in counts if c > 0)

    stats = {
        "states": params.n_states,
        "steps": params.steps,
        "start_state": params.start_state,
        "unique_states": unique_states,
        "variation_distance": variation,
    }

    return {
        "transition_matrix": matrix.tolist(),
        "empirical_probs": empirical,
        "stationary": stationary.tolist(),
        "hitting_times": hitting_times,
        "stats": stats,
        "path_states": path_states,
        "variation_over_time": variation_over_time,
    }
