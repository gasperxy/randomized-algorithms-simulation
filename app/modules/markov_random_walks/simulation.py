from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np


GraphType = str


@dataclass
class SimulationParameters:
    graph_type: GraphType
    n_small: int
    steps_demo: int
    start_vertex: int
    n_min: int
    n_max: int
    n_step: int
    runs_per_n: int
    seed: int | None = None


def _path_graph(n: int) -> Tuple[List[List[int]], int]:
    adj = [[] for _ in range(n)]
    for i in range(n - 1):
        adj[i].append(i + 1)
        adj[i + 1].append(i)
    m = sum(len(neigh) for neigh in adj) // 2
    return adj, m


def _complete_graph(n: int) -> Tuple[List[List[int]], int]:
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                adj[i].append(j)
    m = sum(len(neigh) for neigh in adj) // 2
    return adj, m


def _lollipop_graph(n: int) -> Tuple[List[List[int]], int]:
    # Path of n_path nodes with a clique of n_clique attached by a single edge.
    n_path = max(2, n // 2)
    n_clique = n - n_path
    adj = [[] for _ in range(n)]

    # Path edges
    for i in range(n_path - 1):
        adj[i].append(i + 1)
        adj[i + 1].append(i)

    # Clique edges
    clique_start = n_path
    for i in range(clique_start, n):
        for j in range(clique_start, n):
            if i != j:
                adj[i].append(j)

    # Attach path end to one clique node
    if n_clique > 0:
        adj[n_path - 1].append(clique_start)
        adj[clique_start].append(n_path - 1)

    m = sum(len(neigh) for neigh in adj) // 2
    return adj, m


def _build_graph(graph_type: GraphType, n: int) -> Tuple[List[List[int]], int]:
    if graph_type in ("path", "path_endpoint"):
        return _path_graph(n)
    if graph_type == "complete":
        return _complete_graph(n)
    if graph_type in ("lollipop_free", "lollipop_bridge"):
        return _lollipop_graph(n)
    raise ValueError(f"Unknown graph type: {graph_type}")


def _start_node_for_graph(graph_type: GraphType, n: int) -> int:
    if graph_type in ("path", "path_endpoint"):
        return 0  # endpoint
    if graph_type == "lollipop_free":
        return 0  # free end of the path
    if graph_type == "lollipop_bridge":
        # endpoint adjacent to the clique
        n_path = max(2, n // 2)
        return n_path - 1
    # default: random start elsewhere
    rng = random.Random()
    return rng.randrange(n)


def _cover_time(adj: Sequence[Sequence[int]], start: int, rng: random.Random, cap: int) -> int:
    n = len(adj)
    visited = [False] * n
    current = start
    visited[current] = True
    seen = 1
    steps = 0
    while seen < n and steps < cap:
        current = rng.choice(adj[current])
        steps += 1
        if not visited[current]:
            visited[current] = True
            seen += 1
    return steps


def _fit_curve(graph_type: GraphType, sizes: List[int], means: List[float], edges: List[int]) -> Dict:
    if not sizes:
        return {"coeffs": [], "predicted": [], "r2": None}

    X_rows = []
    for n, m in zip(sizes, edges):
        if graph_type in ("path", "path_endpoint"):
            X_rows.append([n * n, n, 1.0])
        elif graph_type == "complete":
            X_rows.append([n * math.log(max(n, 2)), n, 1.0])
        elif graph_type in ("lollipop_free", "lollipop_bridge"):
            X_rows.append([n**3, n * n, n, 1.0])
        else:
            X_rows.append([n, 1.0, 0.0])

    if not X_rows:
        return {"coeffs": [], "predicted": [], "r2": None}

    X = np.array(X_rows, dtype=float)
    y = np.array(means, dtype=float)

    coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    predicted = X @ coeffs
    ss_res = float(np.sum((y - predicted) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = None if ss_tot == 0 else 1 - ss_res / ss_tot
    return {
        "coeffs": [float(c) for c in np.atleast_1d(coeffs).flatten()],
        "predicted": [float(p) for p in np.atleast_1d(predicted).tolist()],
        "r2": r2,
    }


def _build_demo_path(adj: Sequence[Sequence[int]], steps: int, start: int, rng: random.Random) -> Dict:
    n = len(adj)
    current = start
    path = [current]
    visited = [False] * n
    visited[current] = True
    first_hit = [None] * n
    first_hit[current] = 0

    for step in range(1, steps):
        current = rng.choice(adj[current])
        path.append(current)
        if not visited[current]:
            visited[current] = True
            first_hit[current] = step
    return {"path": path, "first_hit": first_hit}


def run(params: SimulationParameters) -> Dict:
    rng = random.Random(params.seed)

    # Demo graph + sample path
    n_small = max(4, min(params.n_small, 20))
    adj_demo, m_demo = _build_graph(params.graph_type, n_small)
    # Demo start: honor graph-type conventions for lollipops; otherwise use form input.
    if params.graph_type == "lollipop_free":
        start_idx = 0
    elif params.graph_type == "lollipop_bridge":
        start_idx = max(0, max(2, n_small // 2) - 1)
    else:
        start_idx = max(0, min(params.start_vertex - 1, n_small - 1))
    demo = _build_demo_path(adj_demo, params.steps_demo, start_idx, rng)

    # Sweep cover times
    sizes: List[int] = []
    edges: List[int] = []
    samples: List[List[int]] = []
    means: List[float] = []
    stdevs: List[float] = []

    for n in range(params.n_min, params.n_max + 1, params.n_step):
        adj, m = _build_graph(params.graph_type, n)
        cap = max(params.steps_demo, 20 * n * m)
        runs: List[int] = []
        for run_idx in range(params.runs_per_n):
            run_seed = rng.randint(0, 1_000_000_000)
            run_rng = random.Random(run_seed)
            start_node = _start_node_for_graph(params.graph_type, n)
            steps_taken = _cover_time(adj, start_node, run_rng, cap)
            runs.append(steps_taken)
        mean_val = float(np.mean(runs))
        std_val = float(np.std(runs)) if len(runs) > 1 else 0.0
        sizes.append(n)
        edges.append(m)
        samples.append(runs)
        means.append(mean_val)
        stdevs.append(std_val)

    fit = _fit_curve(params.graph_type, sizes, means, edges)

    return {
        "graph_type": params.graph_type,
        "demo_adj": adj_demo,
        "demo_edges": [(i, j) for i, neigh in enumerate(adj_demo) for j in neigh if i < j],
        "demo_path": demo["path"],
        "demo_first_hit": demo["first_hit"],
        "stats_demo": {"n": n_small, "m": m_demo},
        "cover_sizes": sizes,
        "cover_means": means,
        "cover_stdevs": stdevs,
        "cover_samples": samples,
        "cover_edges": edges,
        "fit": fit,
    }
