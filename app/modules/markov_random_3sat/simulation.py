from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple


Literal = Tuple[int, bool]  # (variable_index, is_negated)
Clause = Tuple[Literal, Literal, Literal]


@dataclass
class SimulationParameters:
    n_variables: int
    n_clauses: int
    restarts: int
    steps_per_restart: int
    seed: int | None = None


def _random_literal(rng: random.Random, n_variables: int) -> Literal:
    var_index = rng.randrange(n_variables)
    negated = bool(rng.getrandbits(1))
    return (var_index, negated)


def _random_clause(rng: random.Random, n_variables: int) -> Clause:
    # Try to keep literals distinct for a more interesting clause.
    indices = list(range(n_variables))
    rng.shuffle(indices)
    picks = indices[:3] if n_variables >= 3 else [rng.randrange(n_variables) for _ in range(3)]
    literals: List[Literal] = []
    for idx in picks:
        literals.append((idx, bool(rng.getrandbits(1))))
    return (literals[0], literals[1], literals[2])


def _random_assignment(rng: random.Random, n_variables: int) -> List[bool]:
    return [bool(rng.getrandbits(1)) for _ in range(n_variables)]


def _literal_value(assignment: Sequence[bool], literal: Literal) -> bool:
    var_index, negated = literal
    value = assignment[var_index]
    return not value if negated else value


def _clause_satisfied(assignment: Sequence[bool], clause: Clause) -> bool:
    return any(_literal_value(assignment, lit) for lit in clause)


def _format_literal(literal: Literal) -> Dict[str, str | int]:
    var_index, negated = literal
    math_text = f"{'\\lnot ' if negated else ''}x_{{{var_index + 1}}}"
    return {
        "variable": var_index + 1,
        "negated": negated,
        "text": f"{'~' if negated else ''}x{var_index + 1}",
        "math_text": math_text,
    }


def _format_clause(clause: Clause, index: int) -> Dict:
    literal_texts = [_format_literal(lit) for lit in clause]
    text = f"({literal_texts[0]['text']} OR {literal_texts[1]['text']} OR {literal_texts[2]['text']})"
    math_text = f"({literal_texts[0]['math_text']} \\lor {literal_texts[1]['math_text']} \\lor {literal_texts[2]['math_text']})"
    return {
        "index": index + 1,
        "label": f"C{index + 1}",
        "text": text,
        "math_text": math_text,
        "literals": literal_texts,
    }


def run(params: SimulationParameters) -> Dict:
    rng = random.Random(params.seed)
    clauses: List[Clause] = [_random_clause(rng, params.n_variables) for _ in range(params.n_clauses)]
    clause_display = [_format_clause(clause, idx) for idx, clause in enumerate(clauses)]
    clause_math_texts = [clause["math_text"] for clause in clause_display]

    states: List[Dict] = []
    satisfied_counts: List[int] = []
    transition_counts: Dict[Tuple[int, int], int] = defaultdict(int)
    restart_outcomes: List[Dict] = []

    best_count = -1
    best_step = 0
    solved_at = None
    improvements = regressions = stagnations = 0
    transitions_total = 0

    global_step = 0
    restart_boundaries: List[int] = []
    condense_threshold = max(1, 30 * params.n_variables)
    condensed = params.restarts * params.steps_per_restart > condense_threshold
    last_summary_satisfied = None
    total_steps_scheduled = params.restarts * params.steps_per_restart
    steps_executed = 0
    for restart_index in range(params.restarts):
        restart_boundaries.append(global_step)
        assignment = _random_assignment(rng, params.n_variables)
        last_satisfied = None
        restart_success = False
        steps_used = 0
        for step_in_restart in range(params.steps_per_restart):
            mask = [_clause_satisfied(assignment, clause) for clause in clauses]
            satisfied_count = sum(mask)
            delta = (satisfied_count - last_satisfied) if last_satisfied is not None else 0
            trend = "improved" if delta > 0 else "regressed" if delta < 0 else "steady"
            steps_executed += 1

            if not condensed:
                states.append(
                    {
                        "step": global_step,
                        "restart": restart_index + 1,
                        "step_in_restart": step_in_restart,
                        "satisfied_count": satisfied_count,
                        "unsatisfied_count": params.n_clauses - satisfied_count,
                        "delta": delta if last_satisfied is not None else 0,
                        "trend": trend if last_satisfied is not None else "initial",
                        "action_label": "initial" if last_satisfied is None else "walk",
                        "action_clause": None,
                        "action_clause_math": None,
                        "action_variable": None,
                    }
                )
                satisfied_counts.append(satisfied_count)

            if last_satisfied is not None:
                transitions_total += 1
                transition_counts[(last_satisfied, satisfied_count)] += 1
                if delta > 0:
                    improvements += 1
                elif delta < 0:
                    regressions += 1
                else:
                    stagnations += 1

            if satisfied_count > best_count:
                best_count = satisfied_count
                best_step = global_step
            if satisfied_count == params.n_clauses:
                solved_at = global_step
                restart_success = True
                steps_used = step_in_restart + 1
                break

            # Walk step
            unsatisfied = [idx for idx, sat in enumerate(mask) if not sat]
            if not unsatisfied:
                restart_success = True
                steps_used = step_in_restart + 1
                solved_at = solved_at or global_step
                break
            clause_index = rng.choice(unsatisfied)
            literal_choice = rng.choice(clauses[clause_index])
            var_index = literal_choice[0]
            assignment[var_index] = not assignment[var_index]

            # Update last and action metadata
            last_satisfied = satisfied_count
            if not condensed and states:
                states[-1]["action_clause"] = clause_index + 1
                states[-1]["action_clause_math"] = clause_math_texts[clause_index]
                states[-1]["action_variable"] = var_index + 1

            global_step += 1
            steps_used = step_in_restart + 1

        if condensed:
            summary_delta = (
                satisfied_count - last_summary_satisfied if last_summary_satisfied is not None else 0
            )
            summary_trend = (
                "improved" if summary_delta > 0 else "regressed" if summary_delta < 0 else "steady"
            )
            states.append(
                {
                    "step": global_step,
                    "restart": restart_index + 1,
                    "step_in_restart": step_in_restart,
                    "satisfied_count": satisfied_count,
                    "unsatisfied_count": params.n_clauses - satisfied_count,
                    "delta": summary_delta if last_summary_satisfied is not None else 0,
                    "trend": summary_trend if last_summary_satisfied is not None else "initial",
                    "action_label": "restart_summary",
                    "action_clause": None,
                    "action_clause_math": None,
                    "action_variable": None,
                }
            )
            satisfied_counts.append(satisfied_count)
            last_summary_satisfied = satisfied_count

        restart_outcomes.append(
            {
                "restart": restart_index + 1,
                "steps": steps_used or params.steps_per_restart,
                "satisfied_at_end": satisfied_counts[-1] if satisfied_counts else 0,
                "success": restart_success,
            }
        )
        if restart_success:
            break
        global_step += 1  # advance between restarts to keep unique step ids

    stats = {
        "clauses": params.n_clauses,
        "variables": params.n_variables,
        "steps_recorded": steps_executed,
        "steps_executed": steps_executed,
        "steps_scheduled": total_steps_scheduled,
        "best_satisfied": best_count,
        "best_step": best_step,
        "solved_at": solved_at,
        "improvement_rate": improvements / transitions_total if transitions_total else 0.0,
        "regression_rate": regressions / transitions_total if transitions_total else 0.0,
        "stagnation_rate": stagnations / transitions_total if transitions_total else 0.0,
        "restarts_attempted": len(restart_outcomes),
        "restarts_successful": sum(1 for r in restart_outcomes if r["success"]),
    }

    return {
        "clauses": clause_display,
        "states": states,
        "satisfied_counts": satisfied_counts,
        "transition_counts": dict(transition_counts),
        "stats": stats,
        "clause_count": params.n_clauses,
        "restart_outcomes": restart_outcomes,
        "restart_boundaries": restart_boundaries,
        "condensed": condensed,
    }
