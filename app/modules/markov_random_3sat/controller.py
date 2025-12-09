from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Dict, List, Mapping, Tuple

from . import simulation, visualization


@dataclass
class Markov3SatForm:
    n_variables: int = 10
    n_clauses: int = 43
    error_probability: float = 1.0  # repeat factor r
    restarts: int | None = None
    playback_speed_ms: int = 200
    seed: int | None = None


def default_parameters() -> Dict:
    base = Markov3SatForm()
    base.restarts = _suggest_restarts(base.n_variables, base.error_probability)
    return asdict(base)


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


def _suggest_restarts(n_variables: int, error_probability: float, max_cap: int = 500) -> int:
    suggested = math.ceil(2 * error_probability * math.sqrt(max(1, n_variables)) * ((4 / 3) ** n_variables))
    return max(1, min(suggested, max_cap))


def parse_form(data: Mapping[str, str]) -> Tuple[Markov3SatForm, Dict[str, str]]:
    defaults = Markov3SatForm()
    errors: Dict[str, str] = {}

    n_variables = max(3, _parse_int(data.get("n_variables", ""), defaults.n_variables))
    if n_variables > 20:
        errors["n_variables"] = "Please keep variable count at or below 20 to avoid runaway runtime."
        n_variables = 20

    n_clauses = max(n_variables, _parse_int(data.get("n_clauses", ""), defaults.n_clauses))
    if n_clauses > 5 * n_variables:
        errors["n_clauses"] = f"Clause count capped at {5 * n_variables} (5n) to keep runs responsive."
        n_clauses = 5 * n_variables

    error_probability = _parse_float(data.get("error_probability", ""), defaults.error_probability)
    if error_probability <= 0:
        errors["error_probability"] = "Repeat factor r must be positive."
        error_probability = defaults.error_probability

    restarts = _suggest_restarts(n_variables, error_probability)

    playback_speed_ms = max(
        50, _parse_int(data.get("playback_speed_ms", ""), defaults.playback_speed_ms)
    )

    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = Markov3SatForm(
        n_variables=n_variables,
        n_clauses=n_clauses,
        error_probability=error_probability,
        restarts=restarts,
        playback_speed_ms=playback_speed_ms,
        seed=seed,
    )
    return form, errors


def _format_transition_rows(transition_counts: Dict[Tuple[int, int], int]) -> List[Dict]:
    totals: Dict[int, int] = {}
    for (origin, _), count in transition_counts.items():
        totals[origin] = totals.get(origin, 0) + count

    rows = []
    for (origin, dest), count in sorted(transition_counts.items(), key=lambda item: item[1], reverse=True):
        total_from = totals.get(origin, 1)
        rows.append(
            {
                "from": origin,
                "to": dest,
                "count": count,
                "probability": count / total_from if total_from else 0.0,
            }
        )
    return rows[:15]


def run_module(form_data: Mapping[str, str], accent_color: str) -> Dict:
    params, errors = parse_form(form_data)
    response = {
        "errors": errors,
        "parameters": asdict(params),
        "heatmap_html": "",
        "state_sequence": [],
        "clauses": [],
        "transition_rows": [],
        "stats": {},
        "restart_outcomes": [],
    }
    if errors:
        return response

    sim_params = simulation.SimulationParameters(
        n_variables=params.n_variables,
        n_clauses=params.n_clauses,
        restarts=params.restarts or 1,
        steps_per_restart=3 * params.n_variables,
        seed=params.seed,
    )
    sim_result = simulation.run(sim_params)

    heatmap_plot = visualization.build_clause_heatmap(
        sim_result["satisfied_counts"],
        clause_labels=[clause["label"] for clause in sim_result["clauses"]],
        accent=accent_color,
        clause_count=sim_result["clause_count"],
        restart_boundaries=None if sim_result["condensed"] else sim_result["restart_boundaries"],
        condensed=sim_result["condensed"],
    )

    response.update(
        {
            "heatmap_html": heatmap_plot["plot_html"],
            "state_sequence": sim_result["states"],
            "clauses": sim_result["clauses"],
            "transition_rows": _format_transition_rows(sim_result["transition_counts"]),
            "stats": {**sim_result["stats"], "condensed": sim_result["condensed"]},
            "restart_outcomes": sim_result["restart_outcomes"],
        }
    )
    return response
