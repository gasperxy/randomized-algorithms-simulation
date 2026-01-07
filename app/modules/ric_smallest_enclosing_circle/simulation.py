from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Dict, List, Sequence, Tuple

Point = Tuple[float, float]


@dataclass
class SimulationParameters:
    n_points: int
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    seed: int | None = None


def _dist_sq(a: Point, b: Point) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def _circle_from_two_points(a: Point, b: Point) -> Dict[str, float]:
    cx = (a[0] + b[0]) / 2.0
    cy = (a[1] + b[1]) / 2.0
    r = math.sqrt(_dist_sq(a, b)) / 2.0
    return {"cx": cx, "cy": cy, "r": r}


def _circle_from_three_points(a: Point, b: Point, c: Point) -> Dict[str, float]:
    ax, ay = a
    bx, by = b
    cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return _circle_from_farthest_pair(a, b, c)

    ax2ay2 = ax * ax + ay * ay
    bx2by2 = bx * bx + by * by
    cx2cy2 = cx * cx + cy * cy
    ux = (ax2ay2 * (by - cy) + bx2by2 * (cy - ay) + cx2cy2 * (ay - by)) / d
    uy = (ax2ay2 * (cx - bx) + bx2by2 * (ax - cx) + cx2cy2 * (bx - ax)) / d
    r = math.sqrt((ux - ax) ** 2 + (uy - ay) ** 2)
    return {"cx": ux, "cy": uy, "r": r}


def _circle_from_farthest_pair(a: Point, b: Point, c: Point) -> Dict[str, float]:
    pairs = [(a, b), (a, c), (b, c)]
    farthest = max(pairs, key=lambda pair: _dist_sq(pair[0], pair[1]))
    return _circle_from_two_points(farthest[0], farthest[1])


def _inside(circle: Dict[str, float], point: Point, eps: float = 1e-9) -> bool:
    return _dist_sq((circle["cx"], circle["cy"]), point) <= (circle["r"] + eps) ** 2


def _ric_circle_with_boundary(points: Sequence[Point], end_index: int, p: Point) -> Dict[str, float]:
    circle = {"cx": p[0], "cy": p[1], "r": 0.0}
    for j in range(end_index):
        q = points[j]
        if _inside(circle, q):
            continue
        circle = _circle_from_two_points(p, q)
        for k in range(j):
            r = points[k]
            if _inside(circle, r):
                continue
            circle = _circle_from_three_points(p, q, r)
    return circle


def _boundary_count(points: Sequence[Point], circle: Dict[str, float], eps: float = 1e-6) -> int:
    count = 0
    r = circle["r"]
    cx = circle["cx"]
    cy = circle["cy"]
    for point in points:
        dist = math.sqrt((point[0] - cx) ** 2 + (point[1] - cy) ** 2)
        if abs(dist - r) <= eps:
            count += 1
    return count


def run(params: SimulationParameters) -> Dict:
    rng = random.Random(params.seed)
    x_mid = (params.x_min + params.x_max) / 2.0
    y_mid = (params.y_min + params.y_max) / 2.0
    x_std = max((params.x_max - params.x_min) / 6.0, 1e-6)
    y_std = max((params.y_max - params.y_min) / 6.0, 1e-6)
    points: List[Point] = []
    while len(points) < params.n_points:
        x = rng.gauss(x_mid, x_std)
        y = rng.gauss(y_mid, y_std)
        if params.x_min <= x <= params.x_max and params.y_min <= y <= params.y_max:
            points.append((x, y))
    rng.shuffle(points)

    states: List[Dict] = []
    circle: Dict[str, float] | None = None
    rebuilds = 0
    for idx, point in enumerate(points):
        rebuilt = False
        if circle is None or not _inside(circle, point):
            circle = _ric_circle_with_boundary(points, idx, point)
            rebuilds += 1
            rebuilt = True
        states.append(
            {
                "step": idx,
                "point": point,
                "points": points[: idx + 1],
                "circle": circle,
                "rebuild": rebuilt,
            }
        )

    final_circle = circle or {"cx": 0.0, "cy": 0.0, "r": 0.0}
    summary = {
        "center": (final_circle["cx"], final_circle["cy"]),
        "radius": final_circle["r"],
        "boundary_points": _boundary_count(points, final_circle),
        "n_points": len(points),
        "rebuilds": rebuilds,
    }

    return {
        "points": points,
        "states": states,
        "final_circle": final_circle,
        "summary": summary,
        "bounds": {
            "x_min": params.x_min,
            "x_max": params.x_max,
            "y_min": params.y_min,
            "y_max": params.y_max,
        },
    }
