from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SimulationParameters:
    """Normalized inputs for the ln(2) estimator."""
    samples: int
    seed: int | None = None


def run(params: SimulationParameters) -> Dict:
    """Draw samples and keep cumulative estimates plus per-step history."""
    rng = random.Random(params.seed or 1337)
    values: List[float] = []
    estimates: List[float] = []
    cumulative = 0.0

    for step in range(1, params.samples + 1):
        x = rng.uniform(1.0, 2.0)
        fx = 1 / x
        cumulative += fx
        estimate = cumulative / step * 1.0  # interval length is 1
        values.append(fx)
        estimates.append(estimate)

    states = [
        {
            "step": step,
            "value": values[step - 1],
            "estimate": estimates[step - 1],
        }
        for step in range(1, params.samples + 1)
    ]

    return {
        "states": states,
        "estimates": estimates,
        "values": values,
        "true_value": math.log(2),
    }
