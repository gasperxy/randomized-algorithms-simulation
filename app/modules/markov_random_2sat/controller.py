from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Mapping, Tuple

from . import simulation, visualization


@dataclass
class Markov2SatForm:
    n_variables: int = 12
    n_clauses: int = 40
    max_steps: int = 400
    restart_threshold: int | None = None
    playback_speed_ms: int = 400
    seed: int | None = None


def default_parameters() -> Dict:
    return asdict(Markov2SatForm())


def _parse_int(value, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def parse_form(data: Mapping[str, str]) -> Tuple[Markov2SatForm, Dict[str, str]]:
    defaults = Markov2SatForm()
    errors: Dict[str, str] = {}

    n_variables = max(2, _parse_int(data.get("n_variables", ""), defaults.n_variables))
    if n_variables > 20:
        errors["n_variables"] = "Please stay at or below 20 variables to keep the state space explorable."
        n_variables = 20

    n_clauses = max(2, _parse_int(data.get("n_clauses", ""), defaults.n_clauses))
    if n_clauses > 80:
        errors["n_clauses"] = "Clause count capped at 80 for readability."
        n_clauses = 80

    max_steps = max(10, _parse_int(data.get("max_steps", ""), defaults.max_steps))
    if max_steps > 1000:
        errors["max_steps"] = "Limit iterations to 1,000 for manageable animations."
        max_steps = 1000

    restart_threshold_raw = data.get("restart_threshold")
    restart_threshold = None
    if restart_threshold_raw:
        restart_threshold = max(1, _parse_int(restart_threshold_raw, defaults.restart_threshold or 1))
        if restart_threshold > max_steps:
            errors["restart_threshold"] = "Restart threshold cannot exceed the number of steps."
            restart_threshold = max_steps

    playback_speed_ms = max(
        100, _parse_int(data.get("playback_speed_ms", ""), defaults.playback_speed_ms)
    )

    seed_input = data.get("seed")
    seed = _parse_int(seed_input, defaults.seed or 0) if seed_input else None

    form = Markov2SatForm(
        n_variables=n_variables,
        n_clauses=n_clauses,
        max_steps=max_steps,
        restart_threshold=restart_threshold,
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
        "plot_html": "",
        "heatmap_html": "",
        "state_sequence": [],
        "clauses": [],
        "transition_rows": [],
        "stats": {},
        "deterministic_assignment": [],
        "deterministic_satisfiable": None,
    }
    if errors:
        return response

    sim_params = simulation.SimulationParameters(
        n_variables=params.n_variables,
        n_clauses=params.n_clauses,
        max_steps=params.max_steps,
        restart_threshold=params.restart_threshold,
        seed=params.seed,
    )
    sim_result = simulation.run(sim_params)

    state_plot = visualization.build_state_animation(
        sim_result["states"],
        clause_count=sim_result["clause_count"],
        accent=accent_color,
        frame_duration_ms=params.playback_speed_ms,
    )
    heatmap_plot = visualization.build_clause_heatmap(
        sim_result["clause_satisfaction"],
        clause_labels=[clause["label"] for clause in sim_result["clauses"]],
        accent=accent_color,
    )

    response.update(
        {
            "plot_html": state_plot["plot_html"],
            "heatmap_html": heatmap_plot["plot_html"],
            "state_sequence": sim_result["states"],
            "clauses": sim_result["clauses"],
            "transition_rows": _format_transition_rows(sim_result["transition_counts"]),
            "stats": sim_result["stats"],
            "deterministic_assignment": sim_result["deterministic_assignment"],
            "deterministic_satisfiable": sim_result["deterministic_satisfiable"],
        }
    )
    return response
