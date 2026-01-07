from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple


Coord = Tuple[int, int]


@dataclass
class SimulationParameters:
    width: int
    height: int
    steps: int
    lam: float
    obstacles: int
    mode: str = "shortest"  # "shortest" or "longest"
    seed: int | None = None


def _neighbors(cell: Coord, width: int, height: int) -> List[Coord]:
    x, y = cell
    cand = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [(a, b) for a, b in cand if 0 <= a < width and 0 <= b < height]


def _manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _shortest_path(start: Coord, goal: Coord, width: int, height: int, blocked: set[Coord]) -> List[Coord]:
    from collections import deque

    q = deque([start])
    prev: Dict[Coord, Coord | None] = {start: None}
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for nb in _neighbors(cur, width, height):
            if nb in blocked or nb in prev:
                continue
            prev[nb] = cur
            q.append(nb)
    if goal not in prev:
        return []
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return list(reversed(path))


def _is_simple(path: Sequence[Coord], blocked: set[Coord], width: int | None = None, height: int | None = None) -> bool:
    seen = set()
    for p in path:
        if width is not None and height is not None and not _in_bounds(p, width, height):
            return False
        if p in seen or p in blocked:
            return False
        seen.add(p)
    return True


def _generate_obstacles(width: int, height: int, k: int, start: Coord, goal: Coord, rng: random.Random) -> set[Coord]:
    all_cells = [(x, y) for x in range(width) for y in range(height) if (x, y) not in (start, goal)]
    rng.shuffle(all_cells)
    return set(all_cells[: max(0, min(k, len(all_cells)))])


def _in_bounds(cell: Coord, width: int, height: int) -> bool:
    x, y = cell
    return 0 <= x < width and 0 <= y < height


def _candidate_corner_flip(path: List[Coord], blocked: set[Coord], width: int, height: int) -> List[List[Coord]]:
    cands = []
    for i in range(1, len(path) - 1):
        prev = path[i - 1]
        cur = path[i]
        nxt = path[i + 1]
        if _manhattan(prev, nxt) != 2:
            continue
        # For an L-turn, the intersection candidates are (prev.x, nxt.y) or (nxt.x, prev.y).
        candidates = [(prev[0], nxt[1]), (nxt[0], prev[1])]
        for new_node in candidates:
            if new_node == cur or new_node in blocked or not _in_bounds(new_node, width, height):
                continue
            new_path = path[:i] + [new_node] + path[i + 1 :]
            if _is_simple(new_path, blocked, width, height):
                cands.append(new_path)
    return cands


def _candidate_shortcut(path: List[Coord], blocked: set[Coord], width: int, height: int) -> List[List[Coord]]:
    cands = []
    for i in range(1, len(path) - 1):
        prev = path[i - 1]
        cur = path[i]
        nxt = path[i + 1]
        if _manhattan(prev, nxt) != 1:
            continue
        new_path = path[:i] + path[i + 1 :]
        if _is_simple(new_path, blocked, width, height):
            cands.append(new_path)
    return cands


def _candidate_detour(path: List[Coord], blocked: set[Coord], width: int, height: int) -> List[List[Coord]]:
    cands = []
    for i in range(len(path) - 1):
        a = path[i]
        c = path[i + 1]
        if _manhattan(a, c) != 1:
            continue
        # try perpendicular detours
        dx = c[0] - a[0]
        dy = c[1] - a[1]
        perp = [(dy, dx), (-dy, -dx)]
        for px, py in perp:
            b1 = (a[0] + px, a[1] + py)
            b2 = (c[0] + px, c[1] + py)
            if not (_in_bounds(b1, width, height) and _in_bounds(b2, width, height)):
                continue
            if b1 in blocked or b2 in blocked:
                continue
            new_path = path[: i + 1] + [b1, b2] + path[i + 1 :]
            if _is_simple(new_path, blocked, width, height):
                cands.append(new_path)
    return cands


def _candidate_reroute(path: List[Coord], blocked: set[Coord], width: int, height: int, mode: str) -> List[List[Coord]]:
    """Reconnect small subpaths via an alternate internal route; can shorten or lengthen depending on mode."""
    cands: List[List[Coord]] = []
    n = len(path)
    for i in range(n - 3):
        for window in range(3, min(6, n - i - 1) + 1):
            j = i + window
            if j >= n:
                continue
            a = path[i]
            c = path[j]
            segment = path[i : j + 1]
            current_len = len(segment)
            avoid = set(blocked)
            for p in path:
                if p not in (a, c) and p not in segment:
                    avoid.add(p)
            sp = _shortest_path(a, c, width, height, avoid)
            if not sp:
                continue
            if mode == "shortest" and len(sp) >= current_len:
                continue
            if mode == "longest" and len(sp) <= current_len:
                continue
            new_path = path[:i] + sp + path[j + 1 :]
            if _is_simple(new_path, blocked, width, height):
                cands.append(new_path)
    return cands


def _neighbors_of_path(path: List[Coord], blocked: set[Coord], width: int, height: int, mode: str) -> List[List[Coord]]:
    cands: List[List[Coord]] = []
    cands.extend(_candidate_corner_flip(path, blocked, width, height))
    cands.extend(_candidate_shortcut(path, blocked, width, height))
    cands.extend(_candidate_detour(path, blocked, width, height))
    cands.extend(_candidate_reroute(path, blocked, width, height, mode))
    # Deduplicate
    unique = []
    seen = set()
    for p in cands:
        key = tuple(p)
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def _energy(path: Sequence[Coord], lam: float, mode: str) -> float:
    length = max(0, len(path) - 1)
    sign = -1.0 if mode == "longest" else 1.0
    return sign * lam * length


def run(params: SimulationParameters) -> Dict:
    rng = random.Random(params.seed)
    start = (0, 0)
    goal = (params.width - 1, params.height - 1)
    blocked = _generate_obstacles(params.width, params.height, params.obstacles, start, goal, rng)
    base_path = _shortest_path(start, goal, params.width, params.height, blocked)
    if not base_path:
        return {"error": "No valid path found with given obstacles."}

    path = base_path
    paths: List[List[Coord]] = [path]
    lengths = [len(path) - 1]
    accepts = [True]

    for _ in range(params.steps):
        neigh_all = _neighbors_of_path(path, blocked, params.width, params.height, params.mode)
        neigh = [p for p in neigh_all if p and p[0] == start and p[-1] == goal]
        if not neigh:
            paths.append(path)
            lengths.append(len(path) - 1)
            accepts.append(False)
            continue
        proposal = rng.choice(neigh)
        e_cur = _energy(path, params.lam, params.mode)
        e_prop = _energy(proposal, params.lam, params.mode)
        q_cur = len(neigh)
        neigh_prop = _neighbors_of_path(proposal, blocked, params.width, params.height, params.mode)
        q_prop = max(1, len([p for p in neigh_prop if p and p[0] == start and p[-1] == goal]))
        ratio = math.exp(-(e_prop - e_cur)) * (q_cur / q_prop)
        alpha = min(1.0, ratio)
        if rng.random() < alpha:
            path = proposal
            accepted = True
        else:
            accepted = False
        paths.append(path)
        lengths.append(len(path) - 1)
        accepts.append(accepted)

    return {
        "grid": {"width": params.width, "height": params.height, "obstacles": list(blocked), "start": start, "goal": goal},
        "paths": paths,
        "lengths": lengths,
        "accepts": accepts,
    }
