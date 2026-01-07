from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Tuple

from . import simulation, visualization


@dataclass
class MHPathsForm:
    width: int = 10
    height: int = 10
    steps: int = 200
    lam: float = 0.2
    obstacles: int = 10
    mode: str = "shortest"
    seed: int | None = None


def default_parameters() -> Dict:
    return asdict(MHPathsForm())


def _parse_int(value, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _parse_float(value, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def parse_form(data: Mapping[str, str]) -> Tuple[MHPathsForm, Dict[str, str]]:
    defaults = MHPathsForm()
    errors: Dict[str, str] = {}

    width = max(4, min(_parse_int(data.get("width", ""), defaults.width), 20))
    height = max(4, min(_parse_int(data.get("height", ""), defaults.height), 20))
    steps = max(20, min(_parse_int(data.get("steps", ""), defaults.steps), 800))
    lam = max(0.0, _parse_float(data.get("lam", ""), defaults.lam))
    obstacles = max(0, min(_parse_int(data.get("obstacles", ""), defaults.obstacles), width * height // 3))
    mode = data.get("mode", defaults.mode)
    if mode not in ("shortest", "longest"):
        errors["mode"] = "Unknown mode; using shortest."
        mode = "shortest"

    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = MHPathsForm(
        width=width,
        height=height,
        steps=steps,
        lam=lam,
        obstacles=obstacles,
        mode=mode,
        seed=seed,
    )
    return form, errors


def run_module(form_data: Mapping[str, str], accent_color: str) -> Dict:
    params, errors = parse_form(form_data)
    response = {
        "errors": errors,
        "parameters": asdict(params),
        "graph_html": "",
        "length_html": "",
        "warning": "",
    }
    if errors:
        return response

    sim_params = simulation.SimulationParameters(**asdict(params))
    sim_result = simulation.run(sim_params)
    if "error" in sim_result:
        response["warning"] = sim_result["error"]
        return response

    graph_plot = visualization.build_grid_animation(sim_result["grid"], sim_result["paths"], sim_result["accepts"], accent_color)
    length_plot = visualization.build_length_trace(sim_result["lengths"], sim_result["accepts"], accent_color)

    response.update(
        {
            "graph_html": graph_plot["plot_html"],
            "length_html": length_plot["plot_html"],
        }
    )
    return response
