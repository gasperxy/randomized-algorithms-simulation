from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Tuple

from ..common import graph_services as gs
from . import simulation, visualization


@dataclass
class PhaseTransitionForm:
    """Defaults used when the experiment auto-runs."""
    n_vertices: int = 30
    p_start: float = 0.0
    p_end: float = 0.1
    p_step: float = 0.001
    playback_speed_ms: int = 400
    seed: int | None = None


def default_parameters() -> Dict:
    return asdict(PhaseTransitionForm())


def _parse_int(value: str, fallback: int) -> int:
    """Parse integers from user input, falling back on invalid data."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _parse_float(value: str, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def parse_form(data: Mapping[str, str]) -> Tuple[PhaseTransitionForm, Dict[str, str]]:
    """Clamp and validate form data before the simulation runs."""
    defaults = PhaseTransitionForm()
    errors: Dict[str, str] = {}

    n_vertices = max(1, _parse_int(data.get("n_vertices", ""), defaults.n_vertices))
    if n_vertices > 500:
        errors["n_vertices"] = "Please keep vertex count below 500 for performance."

    p_start = _parse_float(data.get("p_start", ""), defaults.p_start)
    p_end = _parse_float(data.get("p_end", ""), defaults.p_end)
    p_step = max(0.001, _parse_float(data.get("p_step", ""), defaults.p_step))

    playback_speed_ms = max(100, _parse_int(data.get("playback_speed_ms", ""), defaults.playback_speed_ms))
    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = PhaseTransitionForm(
        n_vertices=n_vertices,
        p_start=p_start,
        p_end=p_end,
        p_step=p_step,
        playback_speed_ms=playback_speed_ms,
        seed=seed,
    )
    return form, errors


def _summarize_events(timeline, markers, total_vertices: int):
    marker_lookup = {marker.get("key"): marker for marker in markers}

    def observed_for(predicate):
        for state in timeline:
            if predicate(state):
                return state["p"]
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
    if errors:
        return response

    sim_params = simulation.SimulationParameters(
        n_vertices=params.n_vertices,
        p_start=params.p_start,
        p_end=params.p_end,
        p_step=params.p_step,
        seed=params.seed,
    )

    states = simulation.run(sim_params)
    positions = simulation.compute_layouts(states, params.seed)
    viz = visualization.build_animation(
        states, positions, accent_color, frame_duration_ms=params.playback_speed_ms
    )

    timeline = [{"p": state["p"], **state["stats"]} for state in states]
    markers = gs.theoretical_phase_markers(params.n_vertices)
    response.update(
        {
            "plot_html": viz["plot_html"],
            "timeline": timeline,
            "markers": markers,
            "event_estimates": _summarize_events(timeline, markers, params.n_vertices),
        }
    )
    return response
