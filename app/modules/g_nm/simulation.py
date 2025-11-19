from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from typing import Dict, List

import networkx as nx

from ..common import graph_services as gs


@dataclass
class SimulationParameters:
    n_vertices: int
    edge_count: int
    seed: int | None = None


def _generate_edge_sequence(n_vertices: int, seed: int | None = None) -> List[tuple[int, int]]:
    """Precompute all possible edges and shuffle them to obtain the m-order."""
    nodes = range(n_vertices)
    edges = list(itertools.combinations(nodes, 2))
    rng = random.Random(seed or 12345)
    rng.shuffle(edges)
    return edges


def run(params: SimulationParameters) -> Dict:
    """Simulate adding edges one at a time and capture state snapshots."""
    n = max(1, params.n_vertices)
    total_possible = n * (n - 1) // 2
    target_edges = min(max(0, params.edge_count), total_possible)

    sequence = []
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    edges_pool = _generate_edge_sequence(n, params.seed)

    for idx in range(target_edges):
        u, v = edges_pool[idx]
        graph.add_edge(u, v)
        stats = gs.compute_graph_statistics(graph)
        p_estimate = 0 if total_possible == 0 else (idx + 1) / total_possible
        sequence.append(
            {
                "step": idx + 1,
                "graph": graph.copy(),
                "stats": stats,
                "p_estimate": round(p_estimate, 4),
                "edges_used": idx + 1,
                "fraction": f"{idx + 1}/{total_possible}",
                "new_edge": (u, v),
            }
        )

    return {
        "states": sequence,
        "total_possible_edges": total_possible,
        "final_graph": graph,
    }


def layout_positions(final_graph: nx.Graph, seed: int | None = None) -> Dict[int, List[float]]:
    if final_graph.number_of_nodes() == 0:
        return {}
    return nx.spring_layout(final_graph, seed=seed or 42, k=0.4)


def compute_layouts(
    states: List[Dict], seed: int | None = None, iterations: int = 40
) -> List[Dict[int, List[float]]]:
    """Compute spring layouts for each state, seeding each with the previous layout."""
    layouts: List[Dict[int, List[float]]] = []
    previous_pos: Dict[int, List[float]] | None = None
    base_seed = seed or 42

    for idx, state in enumerate(states):
        graph: nx.Graph = state["graph"]
        if graph.number_of_nodes() == 0:
            layouts.append({})
            continue

        if previous_pos is None:
            pos = nx.spring_layout(graph, seed=base_seed, k=0.4)
        else:
            pos = nx.spring_layout(
                graph, seed=base_seed + idx, gravity=0.2, method="auto", pos=previous_pos, iterations=iterations
            )

        cleaned = {node: coords.tolist() for node, coords in pos.items()}
        layouts.append(cleaned)
        previous_pos = cleaned

    return layouts
