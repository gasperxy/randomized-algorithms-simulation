from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Tuple

from . import simulation, visualization


GRAPH_TYPES = {"path", "complete", "lollipop_free", "lollipop_bridge"}


@dataclass
class RandomWalkForm:
    graph_type: str = "path"
    n_small: int = 12
    steps_demo: int = 400
    start_vertex: int = 1
    n_min: int = 10
    n_max: int = 200
    n_step: int = 10
    runs_per_n: int = 5
    seed: int | None = None


def default_parameters() -> Dict:
    return asdict(RandomWalkForm())


def _parse_int(value, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def parse_form(data: Mapping[str, str]) -> Tuple[RandomWalkForm, Dict[str, str]]:
    defaults = RandomWalkForm()
    errors: Dict[str, str] = {}

    graph_type = data.get("graph_type", defaults.graph_type)
    if graph_type not in GRAPH_TYPES:
        errors["graph_type"] = "Unknown graph type."
        graph_type = defaults.graph_type

    n_small = max(4, min(_parse_int(data.get("n_small", ""), defaults.n_small), 20))
    steps_demo = max(50, min(_parse_int(data.get("steps_demo", ""), defaults.steps_demo), 1000))

    n_min = max(4, _parse_int(data.get("n_min", ""), defaults.n_min))
    n_max = max(n_min, _parse_int(data.get("n_max", ""), defaults.n_max))
    n_step = max(1, _parse_int(data.get("n_step", ""), defaults.n_step))
    runs_per_n = max(1, min(_parse_int(data.get("runs_per_n", ""), defaults.runs_per_n), 20))

    start_vertex = _parse_int(data.get("start_vertex", ""), defaults.start_vertex)
    if start_vertex < 1:
        start_vertex = 1
    if start_vertex > n_small:
        errors["start_vertex"] = "Adjusted start vertex to fit current graph size."
        start_vertex = n_small

    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = RandomWalkForm(
        graph_type=graph_type,
        n_small=n_small,
        steps_demo=steps_demo,
        start_vertex=start_vertex,
        n_min=n_min,
        n_max=n_max,
        n_step=n_step,
        runs_per_n=runs_per_n,
        seed=seed,
    )
    return form, errors


def run_module(form_data: Mapping[str, str], accent_color: str) -> Dict:
    params, errors = parse_form(form_data)
    response = {
        "errors": errors,
        "parameters": asdict(params),
        "graph_html": "",
        "cover_html": "",
        "fit": {},
        "cover_sizes": [],
        "cover_means": [],
        "cover_stdevs": [],
    }
    if errors:
        return response

    sim_params = simulation.SimulationParameters(**asdict(params))
    sim_result = simulation.run(sim_params)

    graph_plot = visualization.build_graph_animation(
        sim_result["graph_type"],
        sim_result["demo_edges"],
        sim_result["demo_path"],
        sim_result["demo_first_hit"],
        sim_result["stats_demo"]["n"],
        accent_color,
    )
    cover_plot = visualization.build_cover_growth(
        sim_result["graph_type"],
        sim_result["cover_sizes"],
        sim_result["cover_means"],
        sim_result["cover_stdevs"],
        sim_result["fit"],
        accent_color,
    )

    response.update(
        {
          "graph_html": graph_plot["plot_html"],
          "cover_html": cover_plot["plot_html"],
          "fit": sim_result["fit"],
          "cover_sizes": sim_result["cover_sizes"],
          "cover_means": sim_result["cover_means"],
          "cover_stdevs": sim_result["cover_stdevs"],
        }
    )
    return response
