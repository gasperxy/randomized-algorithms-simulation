from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Tuple

from . import simulation, visualization


@dataclass
class Ln2Form:
    """Default Monte Carlo settings so the page loads with a run."""
    samples: int = 500
    seed: int | None = None


def default_parameters() -> Dict:
    return asdict(Ln2Form())


def _parse_int(value: str, fallback: int) -> int:
    """Parse integers defensively for form inputs."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def parse_form(data: Mapping[str, str]) -> Tuple[Ln2Form, Dict[str, str]]:
    """Normalize sample count + seed while clamping unsafe values."""
    defaults = Ln2Form()
    errors: Dict[str, str] = {}

    samples = max(10, min(100000, _parse_int(data.get("samples", ""), defaults.samples)))
    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = Ln2Form(samples=samples, seed=seed)
    return form, errors


def run_module(form_data: Mapping[str, str], accent_color: str) -> Dict:
    params, errors = parse_form(form_data)
    response = {
        "errors": errors,
        "parameters": asdict(params),
        "plot_html": "",
        "timeline": [],
        "true_value": 0.0,
        "final_estimate": 0.0,
        "absolute_error": 0.0,
    }
    if errors:
        return response

    sim_params = simulation.SimulationParameters(samples=params.samples, seed=params.seed)
    result = simulation.run(sim_params)
    viz = visualization.build_chart(result["states"], result["true_value"], accent_color)

    response.update(
        {
            "plot_html": viz["plot_html"],
            "timeline": result["states"],
            "true_value": result["true_value"],
            "final_estimate": result["states"][-1]["estimate"],
            "absolute_error": abs(result["states"][-1]["estimate"] - result["true_value"]),
        }
    )
    return response
