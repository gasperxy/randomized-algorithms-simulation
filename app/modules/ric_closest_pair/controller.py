from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Tuple

from . import simulation, visualization


@dataclass
class RicClosestPairForm:
    n_points: int = 50
    x_min: float = 0.0
    x_max: float = 10.0
    y_min: float = 0.0
    y_max: float = 10.0
    playback_speed_ms: int = 250
    seed: int | None = None


def default_parameters() -> Dict:
    return asdict(RicClosestPairForm())


def _parse_int(value: str, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _parse_float(value: str, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def parse_form(data: Mapping[str, str]) -> Tuple[RicClosestPairForm, Dict[str, str]]:
    defaults = RicClosestPairForm()
    errors: Dict[str, str] = {}

    n_points = max(2, min(1000, _parse_int(data.get("n_points", ""), defaults.n_points)))
    x_min = _parse_float(data.get("x_min", ""), defaults.x_min)
    x_max = _parse_float(data.get("x_max", ""), defaults.x_max)
    y_min = _parse_float(data.get("y_min", ""), defaults.y_min)
    y_max = _parse_float(data.get("y_max", ""), defaults.y_max)
    playback_speed_ms = max(100, min(1000, _parse_int(data.get("playback_speed_ms", ""), defaults.playback_speed_ms)))

    if x_min >= x_max:
        errors["x_min"] = "x_min must be less than x_max."
    if y_min >= y_max:
        errors["y_min"] = "y_min must be less than y_max."

    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = RicClosestPairForm(
        n_points=n_points,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        playback_speed_ms=playback_speed_ms,
        seed=seed,
    )
    return form, errors


def run_module(form_data: Mapping[str, str], accent_color: str) -> Dict:
    params, errors = parse_form(form_data)
    response = {
        "errors": errors,
        "parameters": asdict(params),
        "animation_html": "",
        "final_html": "",
        "rebuild_html": "",
        "summary": {},
    }
    if errors:
        return response

    sim_params = simulation.SimulationParameters(
        n_points=params.n_points,
        x_min=params.x_min,
        x_max=params.x_max,
        y_min=params.y_min,
        y_max=params.y_max,
        seed=params.seed,
    )
    result = simulation.run(sim_params)

    animation = visualization.build_incremental_animation(
        result["states"],
        accent_color=accent_color,
        frame_duration_ms=params.playback_speed_ms,
        bounds=result["bounds"],
    )
    final_plot = visualization.build_final_plot(
        result["points"],
        result["summary"]["best_pair"],
        accent_color=accent_color,
        bounds=result["bounds"],
        cell_size=result["states"][-1]["cell_size"] if result["states"] else None,
    )
    rebuild_plot = visualization.build_rebuild_trace(result["states"], accent_color)

    response.update(
        {
            "animation_html": animation["plot_html"],
            "final_html": final_plot["plot_html"],
            "rebuild_html": rebuild_plot["plot_html"],
            "summary": result["summary"],
        }
    )
    return response
