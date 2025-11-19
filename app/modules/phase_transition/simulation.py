from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

import networkx as nx

from ..common import graph_services as gs


@dataclass
class SimulationParameters:
    n_vertices: int
    p_start: float
    p_end: float
    p_step: float
    seed: int | None = None


def probability_sweep(params: SimulationParameters) -> List[float]:
    """Generate the discrete probability samples used by the animation."""
    start = max(0.0, min(1.0, params.p_start))
    end = max(0.0, min(1.0, params.p_end))
    step = max(0.001, abs(params.p_step))

    if end < start:
        start, end = end, start

    values: List[float] = []
    current = start
    while current <= end + 1e-9:
        values.append(round(min(1.0, current), 4))
        current += step

    # Ensure end included
    if values[-1] != round(end, 4):
        values.append(round(end, 4))
    return values


def run(params: SimulationParameters) -> List[Dict]:
    """Create a state per probability that includes the graph + stats."""
    sequence = []
    probabilities = probability_sweep(params)
    n = max(1, params.n_vertices)
    base_seed = params.seed or 12345

    for offset, probability in enumerate(probabilities):
        graph = gs.generate_er_graph(n, probability, seed=base_seed + offset)
        stats = gs.compute_graph_statistics(graph)
        sequence.append({"p": probability, "graph": graph, "stats": stats})
    return sequence


def compute_layouts(
    states: Sequence[Dict], seed: int | None = None, iterations: int = 40
) -> List[Dict[int, List[float]]]:
    """Generate smooth spring-layout positions per state to keep connected nodes close."""
    layouts: List[Dict[int, List[float]]] = []
    previous_pos: Dict[int, List[float]] | None = None
    base_seed = seed or 42

    for idx, state in enumerate(states):
        graph = state["graph"]
        if graph.number_of_nodes() == 0:
            layouts.append({})
            continue

        if previous_pos is None:
            computed = nx.spring_layout(graph, seed=base_seed)
        else:
            computed = nx.spring_layout(
                graph,
                seed=base_seed + idx,
                pos=previous_pos,
                iterations=iterations,
                gravity=0.2,
                method="auto"
            )

        cleaned = {node: coords.tolist() for node, coords in computed.items()}
        layouts.append(cleaned)
        previous_pos = cleaned

    return layouts
