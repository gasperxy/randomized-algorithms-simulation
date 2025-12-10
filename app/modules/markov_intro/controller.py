from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Tuple

from . import simulation, visualization


@dataclass
class MarkovIntroForm:
    n_states: int = 4
    steps: int = 500
    start_state: int = 1
    seed: int | None = None


def default_parameters() -> Dict:
    return asdict(MarkovIntroForm())


def _parse_int(value, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def parse_form(data: Mapping[str, str]) -> Tuple[MarkovIntroForm, Dict[str, str]]:
    defaults = MarkovIntroForm()
    errors: Dict[str, str] = {}

    # Clamp to keep visuals readable and payloads light.
    n_states = max(2, _parse_int(data.get("n_states", ""), defaults.n_states))
    if n_states > 10:
        errors["n_states"] = "Please keep the chain to at most 10 states for readability."
        n_states = 10

    steps = max(10, _parse_int(data.get("steps", ""), defaults.steps))
    if steps > 5000:
        errors["steps"] = "Steps capped at 5000 to keep payloads manageable."
        steps = 5000

    start_state = _parse_int(data.get("start_state", ""), defaults.start_state)
    if start_state < 1:
        start_state = 1
    if start_state > n_states:
        errors["start_state"] = "Start state adjusted to fit within the number of states."
        start_state = n_states

    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = MarkovIntroForm(
        n_states=n_states,
        steps=steps,
        start_state=start_state,
        seed=seed,
    )
    return form, errors


def run_module(form_data: Mapping[str, str], accent_color: str) -> Dict:
    params, errors = parse_form(form_data)
    response = {
        "errors": errors,
        "parameters": asdict(params),
        "graph_html": "",
        "bar_html": "",
        "walk_html": "",
        "variation_html": "",
        "stats": {},
        "transition_matrix": [],
        "hitting_times": [],
    }
    if errors:
        return response

    # Compute simulation, then fan the outputs into the Plotly builders.
    sim_params = simulation.SimulationParameters(
        n_states=params.n_states,
        steps=params.steps,
        start_state=params.start_state,
        seed=params.seed,
    )
    sim_result = simulation.run(sim_params)

    graph_plot = visualization.build_transition_graph(
        sim_result["transition_matrix"], sim_result["stationary"], accent_color
    )
    bar_plot = visualization.build_frequency_comparison(
        sim_result["empirical_probs"],
        sim_result["stationary"],
        accent_color,
    )
    walk_plot = visualization.build_walk_animation(
        sim_result["transition_matrix"],
        sim_result["path_states"],
        sim_result["stationary"],
        accent_color,
    )
    variation_plot = visualization.build_variation_line(
        sim_result["variation_over_time"],
        accent_color,
    )

    response.update(
        {
            "graph_html": graph_plot["plot_html"],
            "bar_html": bar_plot["plot_html"],
            "walk_html": walk_plot["plot_html"],
            "variation_html": variation_plot["plot_html"],
            "stats": sim_result["stats"],
            "transition_matrix": sim_result["transition_matrix"],
            "hitting_times": sim_result["hitting_times"],
        }
    )
    return response
