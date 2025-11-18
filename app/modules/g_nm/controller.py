from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Tuple

from ..common import graph_services as gs
from . import simulation, visualization


@dataclass
class GnmForm:
    n_vertices: int = 30
    edge_count: int = 80
    playback_speed_ms: int = 400
    seed: int | None = None


def default_parameters() -> Dict:
    return asdict(GnmForm())


def _parse_int(value: str, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def parse_form(data: Mapping[str, str]) -> Tuple[GnmForm, Dict[str, str]]:
    defaults = GnmForm()
    errors: Dict[str, str] = {}

    n_vertices = max(1, _parse_int(data.get("n_vertices", ""), defaults.n_vertices))
    max_edges = max(0, n_vertices * (n_vertices - 1) // 2)
    edge_count = _parse_int(data.get("edge_count", ""), defaults.edge_count)
    if edge_count < 0:
        edge_count = 0
    if edge_count > max_edges:
        edge_count = max_edges
        errors["edge_count"] = f"Edge count capped at {max_edges} for n = {n_vertices}."

    playback_speed_ms = max(
        100, _parse_int(data.get("playback_speed_ms", ""), defaults.playback_speed_ms)
    )
    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = GnmForm(
        n_vertices=n_vertices,
        edge_count=edge_count,
        playback_speed_ms=playback_speed_ms,
        seed=seed,
    )
    return form, errors


def run_module(form_data: Mapping[str, str], accent_color: str) -> Dict:
    params, errors = parse_form(form_data)
    response = {
        "errors": errors,
        "parameters": asdict(params),
        "plot_html": "",
        "timeline": [],
        "markers": [],
        "event_estimates": [],
        "total_possible_edges": 0,
    }
    if params.edge_count == 0:
        return response

    sim_params = simulation.SimulationParameters(
        n_vertices=params.n_vertices,
        edge_count=params.edge_count,
        seed=params.seed,
    )
    sim_result = simulation.run(sim_params)
    states = sim_result["states"]
    if not states:
        return response

    markers = gs.theoretical_phase_markers(params.n_vertices)
    positions = simulation.compute_layouts(states, params.seed)
    viz = visualization.build_animation(
        states, positions, accent_color, frame_duration_ms=params.playback_speed_ms
    )

    timeline = []
    for state in states:
        timeline.append(
            {
                "step": state["step"],
                "edges_used": state["edges_used"],
                "p_estimate": state["p_estimate"],
                **state["stats"],
            }
        )

    response.update(
        {
            "plot_html": viz["plot_html"],
            "timeline": timeline,
            "markers": markers,
            "event_estimates": _summarize_events(timeline, markers, params.n_vertices),
            "total_possible_edges": sim_result["total_possible_edges"],
        }
    )
    return response


def _summarize_events(timeline, markers, total_vertices: int):
    marker_lookup = {marker.get("key"): marker for marker in markers}

    def observed_for(predicate):
        for state in timeline:
            if predicate(state):
                return state["p_estimate"]
        return None

    events = [
        ("first_cycle", "First cycle appears", lambda s: s["has_cycle"]),
        ("connectivity", "Graph becomes connected", lambda s: s["is_connected"]),
        (
            "isolated_vertices",
            "Isolated vertices disappear",
            lambda s: not s["has_isolated_vertices"],
        ),
        ("triangles", "Triangle appears", lambda s: s["triangle_count"] > 0),
        (
            "giant_component",
            "Giant component ≥ 50% nodes",
            lambda s: s["largest_component_size"] >= max(1, total_vertices) / 2,
        ),
    ]

    summary = []
    for key, label, predicate in events:
        theoretical = marker_lookup.get(key, {}).get("p")
        observed = observed_for(predicate)
        summary.append(
            {
                "key": key,
                "label": label,
                "theoretical_p": theoretical,
                "observed_p": observed,
            }
        )
    return summary
