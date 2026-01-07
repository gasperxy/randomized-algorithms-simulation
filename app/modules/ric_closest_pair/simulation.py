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


def _distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _cell_key(point: Point, origin: Point, cell_size: float) -> Tuple[int, int]:
    x0, y0 = origin
    return (
        int(math.floor((point[0] - x0) / cell_size)),
        int(math.floor((point[1] - y0) / cell_size)),
    )


def _build_grid(points: Sequence[Point], origin: Point, cell_size: float) -> Dict[Tuple[int, int], List[Point]]:
    grid: Dict[Tuple[int, int], List[Point]] = {}
    for point in points:
        key = _cell_key(point, origin, cell_size)
        grid.setdefault(key, []).append(point)
    return grid


def _neighbor_points(
    grid: Dict[Tuple[int, int], List[Point]],
    key: Tuple[int, int],
) -> List[Point]:
    ix, iy = key
    candidates: List[Point] = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            candidates.extend(grid.get((ix + dx, iy + dy), []))
    return candidates


def _sample_points(params: SimulationParameters, rng: random.Random) -> List[Point]:
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
    return points


def run(params: SimulationParameters) -> Dict:
    rng = random.Random(params.seed)
    points = _sample_points(params, rng)
    rng.shuffle(points)

    origin = (params.x_min, params.y_min)
    processed: List[Point] = []
    grid: Dict[Tuple[int, int], List[Point]] = {}
    cell_size: float | None = None

    best_pair: Tuple[Point, Point] | None = None
    best_distance = math.inf
    rebuilds = 0
    states: List[Dict] = []

    for idx, point in enumerate(points):
        rebuilt = False

        if len(processed) >= 1 and math.isinf(best_distance):
            candidate = processed[0]
            best_distance = _distance(point, candidate)
            best_pair = (candidate, point)
            cell_size = max(best_distance, 1e-9)
            grid = _build_grid(processed + [point], origin, cell_size)
            rebuilds += 1
            rebuilt = True
        elif cell_size is not None:
            key = _cell_key(point, origin, cell_size)
            candidates = _neighbor_points(grid, key)
            new_distance = best_distance
            new_pair = best_pair
            for other in candidates:
                dist = _distance(point, other)
                if dist < new_distance:
                    new_distance = dist
                    new_pair = (point, other)
            if new_distance < best_distance:
                best_distance = new_distance
                best_pair = new_pair
                cell_size = max(best_distance, 1e-9)
                grid = _build_grid(processed + [point], origin, cell_size)
                rebuilds += 1
                rebuilt = True
            else:
                grid.setdefault(key, []).append(point)

        processed.append(point)

        states.append(
            {
                "step": idx,
                "point": point,
                "points": processed.copy(),
                "best_pair": best_pair,
                "best_distance": None if math.isinf(best_distance) else best_distance,
                "cell_size": cell_size,
                "rebuild": rebuilt,
            }
        )

    summary = {
        "n_points": len(points),
        "best_distance": None if math.isinf(best_distance) else best_distance,
        "best_pair": best_pair,
        "rebuilds": rebuilds,
    }

    return {
        "points": points,
        "states": states,
        "summary": summary,
        "bounds": {
            "x_min": params.x_min,
            "x_max": params.x_max,
            "y_min": params.y_min,
            "y_max": params.y_max,
        },
    }
