from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple


@dataclass
class Rectangle:
    x: float
    y: float
    width: float
    height: float

    @property
    def x2(self) -> float:
        return self.x + self.width

    @property
    def y2(self) -> float:
        return self.y + self.height

    @property
    def area(self) -> float:
        return self.width * self.height

    def contains_cell(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        return self.x <= x1 and self.y <= y1 and self.x2 >= x2 and self.y2 >= y2

    def contains_point(self, px: float, py: float) -> bool:
        return self.x <= px <= self.x2 and self.y <= py <= self.y2


@dataclass
class SimulationParameters:
    n_rectangles: int
    size_range: Tuple[float, float]
    bounds: Tuple[float, float, float, float]
    samples: int
    seed: int | None = None


def generate_rectangles(params: SimulationParameters) -> List[Rectangle]:
    rng = random.Random(params.seed)
    x_min, x_max, y_min, y_max = params.bounds
    min_size, max_size = params.size_range
    rectangles: List[Rectangle] = []
    for _ in range(params.n_rectangles):
        width = rng.uniform(min_size, max_size)
        height = rng.uniform(min_size, max_size)
        x = rng.uniform(x_min, x_max - width)
        y = rng.uniform(y_min, y_max - height)
        rectangles.append(Rectangle(x, y, width, height))
    return rectangles


def _grid_coordinates(rectangles: Sequence[Rectangle]) -> Tuple[List[float], List[float]]:
    xs = sorted({rect.x for rect in rectangles} | {rect.x2 for rect in rectangles})
    ys = sorted({rect.y for rect in rectangles} | {rect.y2 for rect in rectangles})
    return xs, ys


def decompose_disjoint(rectangles: Sequence[Rectangle]) -> Tuple[List[List[Rectangle]], float]:
    xs, ys = _grid_coordinates(rectangles)
    components: List[List[Rectangle]] = [[] for _ in rectangles]
    total_area = 0.0

    for ix in range(len(xs) - 1):
        for iy in range(len(ys) - 1):
            x1, x2 = xs[ix], xs[ix + 1]
            y1, y2 = ys[iy], ys[iy + 1]
            width = x2 - x1
            height = y2 - y1
            if width <= 0 or height <= 0:
                continue
            for idx, rect in enumerate(rectangles):
                if rect.contains_cell(x1, y1, x2, y2):
                    cell_rect = Rectangle(x1, y1, width, height)
                    components[idx].append(cell_rect)
                    total_area += cell_rect.area
                    break
    return components, total_area


def sample_point_in_rect(rect: Rectangle, rng: random.Random) -> Tuple[float, float]:
    return rng.uniform(rect.x, rect.x2), rng.uniform(rect.y, rect.y2)


def run(params: SimulationParameters):
    rectangles = generate_rectangles(params)
    b_components, union_area = decompose_disjoint(rectangles)
    total_rect_area = sum(rect.area for rect in rectangles)
    rng = random.Random((params.seed or 0) + 1337)

    states = []
    hits = 0

    hits_by_rect = [0 for _ in rectangles]
    misses_by_rect = [0 for _ in rectangles]

    for step in range(1, params.samples + 1):
        weights = [rect.area for rect in rectangles]
        choice = rng.choices(range(len(rectangles)), weights=weights, k=1)[0]
        rect = rectangles[choice]
        px, py = sample_point_in_rect(rect, rng)
        is_hit = any(comp.contains_point(px, py) for comp in b_components[choice])
        if is_hit:
            hits += 1
            hits_by_rect[choice] += 1
        else:
            misses_by_rect[choice] += 1
        estimate = (hits / step) * total_rect_area if step > 0 else 0.0
        states.append(
            {
                "step": step,
                "rect_index": choice,
                "point": (px, py),
                "is_hit": is_hit,
                "hits": hits,
                "estimate": estimate,
                "hit_ratio": hits / step,
            }
        )

    return {
        "rectangles": rectangles,
        "components": b_components,
        "union_area": union_area,
        "total_rect_area": total_rect_area,
        "states": states,
        "per_rect_stats": [
            {
                "hits": hits_by_rect[i],
                "misses": misses_by_rect[i],
            }
            for i in range(len(rectangles))
        ],
    }
