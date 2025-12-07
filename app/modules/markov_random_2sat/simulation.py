from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple


Literal = Tuple[int, bool]  # (variable_index, is_negated)
Clause = Tuple[Literal, Literal]


@dataclass
class SimulationParameters:
    n_variables: int
    n_clauses: int
    max_steps: int
    restart_threshold: int | None = None
    seed: int | None = None


def _random_literal(rng: random.Random, n_variables: int) -> Literal:
    var_index = rng.randrange(n_variables)
    negated = bool(rng.getrandbits(1))
    return (var_index, negated)


def _random_clause(rng: random.Random, n_variables: int) -> Clause:
    first = _random_literal(rng, n_variables)
    second = _random_literal(rng, n_variables)
    # Ensure two distinct variables when possible to keep clauses varied.
    if n_variables > 1 and second[0] == first[0]:
        alt = rng.randrange(n_variables - 1)
        if alt >= first[0]:
            alt += 1
        second = (alt, second[1])
    return (first, second)


def _random_assignment(rng: random.Random, n_variables: int) -> List[bool]:
    return [bool(rng.getrandbits(1)) for _ in range(n_variables)]


def _literal_value(assignment: Sequence[bool], literal: Literal) -> bool:
    var_index, negated = literal
    value = assignment[var_index]
    return not value if negated else value


def _clause_satisfied(assignment: Sequence[bool], clause: Clause) -> bool:
    return _literal_value(assignment, clause[0]) or _literal_value(assignment, clause[1])


def _format_literal(literal: Literal) -> Dict[str, str | int]:
    var_index, negated = literal
    return {
        "variable": var_index + 1,
        "negated": negated,
        "text": f"{'~' if negated else ''}x{var_index + 1}",
    }


def _format_clause(clause: Clause, index: int) -> Dict:
    lit_a, lit_b = clause
    literal_texts = [_format_literal(lit_a), _format_literal(lit_b)]
    text = f"({literal_texts[0]['text']} OR {literal_texts[1]['text']})"
    return {
        "index": index + 1,
        "label": f"C{index + 1}",
        "text": text,
        "literals": literal_texts,
    }


def _literal_node(literal: Literal) -> int:
    var_index, negated = literal
    return 2 * var_index + (1 if negated else 0)


def _solve_2sat(n_variables: int, clauses: Sequence[Clause]) -> Tuple[bool, List[bool]]:
    node_count = max(1, 2 * n_variables)
    graph = [[] for _ in range(node_count)]
    reverse = [[] for _ in range(node_count)]

    def add_edge(u: int, v: int) -> None:
        graph[u].append(v)
        reverse[v].append(u)

    for clause in clauses:
        a_node = _literal_node(clause[0])
        b_node = _literal_node(clause[1])
        add_edge(a_node ^ 1, b_node)
        add_edge(b_node ^ 1, a_node)

    order: List[int] = []
    visited = [False] * node_count

    def dfs(node: int) -> None:
        visited[node] = True
        for nxt in graph[node]:
            if not visited[nxt]:
                dfs(nxt)
        order.append(node)

    for node in range(node_count):
        if not visited[node]:
            dfs(node)

    component = [-1] * node_count

    def assign(node: int, label: int) -> None:
        component[node] = label
        for nxt in reverse[node]:
            if component[nxt] == -1:
                assign(nxt, label)

    label = 0
    for node in reversed(order):
        if component[node] == -1:
            assign(node, label)
            label += 1

    assignment = [False] * n_variables
    for var in range(n_variables):
        pos = 2 * var
        neg = pos + 1
        if component[pos] == component[neg]:
            return False, []
        assignment[var] = component[pos] > component[neg]
    return True, assignment


def run(params: SimulationParameters) -> Dict:
    rng = random.Random(params.seed)
    clauses: List[Clause] = [
        _random_clause(rng, params.n_variables) for _ in range(params.n_clauses)
    ]
    clause_display = [_format_clause(clause, idx) for idx, clause in enumerate(clauses)]
    clause_texts = [clause["text"] for clause in clause_display]
    deterministic_sat, deterministic_assignment = _solve_2sat(params.n_variables, clauses)
    assignment_display = [
        {
            "variable": idx + 1,
            "value": value,
            "text": f"x{idx + 1} = {'True' if value else 'False'}",
        }
        for idx, value in enumerate(deterministic_assignment)
    ] if deterministic_sat else []

    assignment = _random_assignment(rng, params.n_variables)
    pending_action = {"label": "initial"}
    states: List[Dict] = []
    clause_satisfaction: List[List[int]] = []
    transition_counts: Dict[Tuple[int, int], int] = defaultdict(int)

    best_count = -1
    best_step = 0
    solved_at = None
    last_satisfied = None
    improvements = regressions = stagnations = 0
    transitions_total = 0
    restart_count = 0

    step = 0
    while step <= params.max_steps:
        mask = [_clause_satisfied(assignment, clause) for clause in clauses]
        satisfied_count = sum(mask)
        fraction = satisfied_count / params.n_clauses if params.n_clauses else 0.0
        delta = (satisfied_count - last_satisfied) if last_satisfied is not None else 0
        trend = "improved" if delta > 0 else "regressed" if delta < 0 else "steady"

        states.append(
            {
                "step": step,
                "satisfied_count": satisfied_count,
                "satisfied_fraction": fraction,
                "delta": delta if last_satisfied is not None else 0,
                "trend": trend if last_satisfied is not None else "initial",
                "action_label": pending_action.get("label"),
                "action_clause": pending_action.get("clause"),
                "action_clause_text": pending_action.get("clause_text"),
                "action_variable": pending_action.get("variable"),
                "restart_triggered": pending_action.get("label") == "restart",
                "unsatisfied_clauses": params.n_clauses - satisfied_count,
            }
        )
        clause_satisfaction.append([1 if sat else 0 for sat in mask])

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
            best_step = step
        if satisfied_count == params.n_clauses and solved_at is None:
            solved_at = step

        if satisfied_count == params.n_clauses or step >= params.max_steps:
            break

        last_satisfied = satisfied_count

        if params.restart_threshold and (step + 1) % params.restart_threshold == 0:
            assignment = _random_assignment(rng, params.n_variables)
            pending_action = {"label": "restart"}
            restart_count += 1
        else:
            unsatisfied = [idx for idx, sat in enumerate(mask) if not sat]
            if not unsatisfied:
                pending_action = {"label": "halt"}
                break
            clause_index = rng.choice(unsatisfied)
            literal_choice = rng.choice(clauses[clause_index])
            var_index = literal_choice[0]
            assignment[var_index] = not assignment[var_index]
            pending_action = {
                "label": "walk",
                "clause": clause_index + 1,
                "clause_text": clause_texts[clause_index],
                "variable": var_index + 1,
            }

        step += 1

    stats = {
        "clauses": params.n_clauses,
        "variables": params.n_variables,
        "steps_recorded": len(states),
        "best_satisfied": best_count,
        "best_step": best_step,
        "solved_at": solved_at,
        "improvement_rate": improvements / transitions_total if transitions_total else 0.0,
        "regression_rate": regressions / transitions_total if transitions_total else 0.0,
        "stagnation_rate": stagnations / transitions_total if transitions_total else 0.0,
        "restart_count": restart_count,
        "deterministic_satisfiable": deterministic_sat,
    }

    return {
        "clauses": clause_display,
        "states": states,
        "clause_satisfaction": clause_satisfaction,
        "transition_counts": dict(transition_counts),
        "stats": stats,
        "clause_count": params.n_clauses,
        "deterministic_satisfiable": deterministic_sat,
        "deterministic_assignment": assignment_display,
    }
