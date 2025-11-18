from __future__ import annotations

import math
import random
from collections import deque
from typing import Dict, Iterable, List, Optional, Set, Tuple

import networkx as nx


def generate_er_graph(
    n_vertices: int,
    probability: float,
    seed: Optional[int] = None,
) -> nx.Graph:
    """Generate an Erdős–Rényi G(n, p) graph."""
    rng_seed = seed if seed is not None else random.randint(0, 1_000_000)
    return nx.gnp_random_graph(n_vertices, probability, seed=rng_seed)


def bfs_components(graph: nx.Graph) -> List[Set[int]]:
    """Return connected components using BFS to keep logic reusable."""
    visited: Set[int] = set()
    components: List[Set[int]] = []

    for node in graph.nodes():
        if node in visited:
            continue
        queue: deque[int] = deque([node])
        component: Set[int] = set()
        visited.add(node)

        while queue:
            current = queue.popleft()
            component.add(current)
            for neighbor in graph.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        components.append(component)
    return components


def get_connected_components(graph: nx.Graph) -> List[Set[int]]:
    """Expose BFS-based components so experiments can reuse without Nx helpers."""
    return bfs_components(graph)


def count_components(graph: nx.Graph) -> int:
    return len(get_connected_components(graph))


def largest_component(graph: nx.Graph) -> Set[int]:
    comps = get_connected_components(graph)
    return max(comps, key=len) if comps else set()


def is_connected(graph: nx.Graph) -> bool:
    return count_components(graph) == 1 if graph.number_of_nodes() else True


def has_cycle(graph: nx.Graph) -> Tuple[bool, List[List[int]]]:
    cycles = nx.cycle_basis(graph)
    return (len(cycles) > 0, cycles)


def count_triangles(graph: nx.Graph) -> int:
    triangles = nx.triangles(graph)
    total = sum(triangles.values())
    return total // 3


def global_clustering_coefficient(graph: nx.Graph) -> float:
    if graph.number_of_nodes() < 3:
        return 0.0
    return nx.transitivity(graph)


def average_degree(graph: nx.Graph) -> float:
    n = graph.number_of_nodes()
    if n == 0:
        return 0.0
    return (2 * graph.number_of_edges()) / n


def compute_graph_statistics(graph: nx.Graph) -> Dict[str, float | int | bool]:
    components = get_connected_components(graph)
    largest = max((len(comp) for comp in components), default=0)
    has_cycle_flag, cycles = has_cycle(graph)

    stats = {
        "n_vertices": graph.number_of_nodes(),
        "n_edges": graph.number_of_edges(),
        "largest_component_size": largest,
        "component_count": len(components),
        "is_connected": len(components) == 1 if graph.number_of_nodes() else True,
        "has_cycle": has_cycle_flag,
        "cycle_count": len(cycles),
        "triangle_count": count_triangles(graph),
        "average_degree": round(average_degree(graph), 3),
        "clustering_coefficient": round(global_clustering_coefficient(graph), 3),
        "isolated_vertices": sum(1 for node in graph.nodes() if graph.degree(node) == 0),
    }
    stats["has_triangle"] = stats["triangle_count"] > 0
    stats["has_isolated_vertices"] = stats["isolated_vertices"] > 0
    return stats


def theoretical_phase_markers(n_vertices: int) -> List[Dict[str, float | str]]:
    """Return theoretical phase thresholds to overlay on the probability axis."""
    if n_vertices <= 0:
        return []

    triangle_threshold = 0.0
    if n_vertices >= 3:
        triangle_threshold = (
            6 / (n_vertices * (n_vertices - 1) * (n_vertices - 2))
        ) ** (1 / 3)

    log_over_n = math.log(n_vertices) / n_vertices
    markers = [
        ("first_cycle", 1 / n_vertices, "First cycle ~1/n"),
        ("connectivity", log_over_n, "Connectivity (log n / n)"),
        ("isolated_vertices", log_over_n, "Isolated vertices disappear (log n / n)"),
        ("triangles", triangle_threshold, "First triangle (p ≈ d/n, d ≈ 1.82)"),
        ("dense", 0.5, "Dense regime 0.5"),
    ]

    sanitized = []
    for key, value, label in markers:
        p = max(0.0, min(1.0, value))
        sanitized.append({"key": key, "p": round(p, 4), "label": label})
    sanitized.sort(key=lambda marker: marker["p"])
    return sanitized
