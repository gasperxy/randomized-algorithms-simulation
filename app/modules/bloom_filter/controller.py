from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Tuple

from . import simulation, visualization


@dataclass
class BloomForm:
    m: int = 128
    k: int = 4
    n_inserts: int = 200
    n_queries: int = 200
    hash_family: str = "multiply_shift"
    playback_speed_ms: int = 250
    seed: int | None = None


def default_parameters() -> Dict:
    return asdict(BloomForm())


def _parse_int(value: str, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def parse_form(data: Mapping[str, str]) -> Tuple[BloomForm, Dict[str, str]]:
    defaults = BloomForm()
    errors: Dict[str, str] = {}

    m = max(16, min(2048, _parse_int(data.get("m", ""), defaults.m)))
    k = max(1, min(12, _parse_int(data.get("k", ""), defaults.k)))
    n_inserts = max(1, min(2000, _parse_int(data.get("n_inserts", ""), defaults.n_inserts)))
    n_queries = max(10, min(2000, _parse_int(data.get("n_queries", ""), defaults.n_queries)))
    playback_speed_ms = max(100, min(1000, _parse_int(data.get("playback_speed_ms", ""), defaults.playback_speed_ms)))

    hash_family = data.get("hash_family", defaults.hash_family)
    if hash_family not in ("multiply_shift", "mod_prime", "biased"):
        hash_family = defaults.hash_family

    if k > m:
        errors["k"] = "k must be <= m."

    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = BloomForm(
        m=m,
        k=k,
        n_inserts=n_inserts,
        n_queries=n_queries,
        hash_family=hash_family,
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
        "fp_html": "",
        "summary": {},
    }
    if errors:
        return response

    sim_params = simulation.SimulationParameters(
        m=params.m,
        k=params.k,
        n_inserts=params.n_inserts,
        n_queries=params.n_queries,
        hash_family=params.hash_family,
        seed=params.seed,
    )
    result = simulation.run(sim_params)

    animation_states = result["states"][:100]
    animation = visualization.build_bit_animation(
        animation_states,
        m=params.m,
        accent_color=accent_color,
        frame_duration_ms=params.playback_speed_ms,
    )
    fp_chart = visualization.build_false_positive_chart(
        result["states"],
        m=params.m,
        k=params.k,
        accent_color=accent_color,
    )

    response.update(
        {
            "animation_html": animation["plot_html"],
            "fp_html": fp_chart["plot_html"],
            "summary": result["summary"],
        }
    )
    return response
