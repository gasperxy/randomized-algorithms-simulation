from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Tuple

from . import simulation, visualization


@dataclass
class UnionAreaForm:
    n_rectangles: int = 6
    min_size: float = 1.0
    max_size: float = 3.0
    x_max: float = 10.0
    y_max: float = 10.0
    samples: int = 200
    speed_ms: int = 300
    seed: int | None = None


def default_parameters() -> Dict:
    return asdict(UnionAreaForm())


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


def parse_form(data: Mapping[str, str]) -> Tuple[UnionAreaForm, Dict[str, str]]:
    defaults = UnionAreaForm()
    errors: Dict[str, str] = {}

    n_rectangles = max(1, min(12, _parse_int(data.get("n_rectangles", ""), defaults.n_rectangles)))
    min_size = max(0.2, _parse_float(data.get("min_size", ""), defaults.min_size))
    max_size = max(min_size, _parse_float(data.get("max_size", ""), defaults.max_size))
    x_max = max(max_size + 1, _parse_float(data.get("x_max", ""), defaults.x_max))
    y_max = max(max_size + 1, _parse_float(data.get("y_max", ""), defaults.y_max))
    samples = max(10, min(2000, _parse_int(data.get("samples", ""), defaults.samples)))
    speed_ms = max(50, min(2000, _parse_int(data.get("speed_ms", ""), defaults.speed_ms)))
    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = UnionAreaForm(
        n_rectangles=n_rectangles,
        min_size=min_size,
        max_size=max_size,
        x_max=x_max,
        y_max=y_max,
        samples=samples,
        speed_ms=speed_ms,
        seed=seed,
    )
    return form, errors


def run_module(form_data: Mapping[str, str], accent_color: str) -> Dict:
    params, errors = parse_form(form_data)
    response = {
        "errors": errors,
        "parameters": asdict(params),
        "plot_html": "",
        "grid_html": "",
        "timeline": [],
        "rectangles": [],
        "components": [],
        "union_area": 0.0,
        "total_rect_area": 0.0,
        "per_rect_stats": [],
    }
    if errors:
        return response

    sim_params = simulation.SimulationParameters(
        n_rectangles=params.n_rectangles,
        size_range=(params.min_size, params.max_size),
        bounds=(0.0, params.x_max, 0.0, params.y_max),
        samples=params.samples,
        seed=params.seed,
    )
    result = simulation.run(sim_params)
    viz = visualization.build_animation(
        rectangles=result["rectangles"],
        components=result["components"],
        states=result["states"],
        accent_color=accent_color,
        frame_duration_ms=params.speed_ms,
    )

    response.update(
        {
            "plot_html": viz["plot_html"],
            "grid_html": viz["grid_html"],
            "timeline": [
                {
                    "step": state["step"],
                    "rect_index": state["rect_index"],
                    "is_hit": state["is_hit"],
                    "estimate": state["estimate"],
                    "hit_ratio": state["hit_ratio"],
                }
                for state in result["states"]
            ],
            "rectangles": result["rectangles"],
            "components": result["components"],
            "union_area": result["union_area"],
            "total_rect_area": result["total_rect_area"],
            "per_rect_stats": result["per_rect_stats"],
        }
    )
    return response
