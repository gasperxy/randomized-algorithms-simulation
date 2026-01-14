from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Callable, Dict, List, Sequence, Tuple


HashFn = Callable[[int], int]


@dataclass
class SimulationParameters:
    m: int
    k: int
    n_inserts: int
    n_queries: int
    hash_family: str
    seed: int | None = None


def _is_power_of_two(value: int) -> bool:
    return value > 0 and (value & (value - 1)) == 0


def _make_multiply_shift_hashes(m: int, k: int, rng: random.Random) -> List[HashFn]:
    mask = (1 << 64) - 1
    if _is_power_of_two(m):
        shift = 64 - int(math.log2(m))

        def _hash(a: int, b: int) -> HashFn:
            return lambda x: ((a * x + b) & mask) >> shift
    else:

        def _hash(a: int, b: int) -> HashFn:
            return lambda x: ((a * x + b) & mask) % m

    hashes = []
    for _ in range(k):
        a = rng.getrandbits(64) | 1
        b = rng.getrandbits(64)
        hashes.append(_hash(a, b))
    return hashes


def _make_mod_prime_hashes(m: int, k: int, rng: random.Random) -> List[HashFn]:
    p = 2305843009213693951  # 2^61 - 1 prime
    hashes = []
    for _ in range(k):
        a = rng.randrange(1, p - 1)
        b = rng.randrange(0, p - 1)

        def _hash(x: int, a=a, b=b) -> int:
            return ((a * x + b) % p) % m

        hashes.append(_hash)
    return hashes


def _make_biased_hashes(m: int, k: int) -> List[HashFn]:
    c = 3
    return [lambda x, i=i: (c * x + i) % m for i in range(k)]


def _make_hashes(m: int, k: int, family: str, rng: random.Random) -> List[HashFn]:
    if family == "biased":
        return _make_biased_hashes(m, k)
    if family == "mod_prime":
        return _make_mod_prime_hashes(m, k, rng)
    return _make_multiply_shift_hashes(m, k, rng)


def run(params: SimulationParameters) -> Dict:
    rng = random.Random(params.seed)
    hashes = _make_hashes(params.m, params.k, params.hash_family, rng)
    bit_array = [0] * params.m
    inserted: set[int] = set()

    states: List[Dict] = []
    fp_rates: List[float] = []
    fill_ratios: List[float] = []

    for step in range(params.n_inserts):
        key = rng.randrange(1 << 31)
        while key in inserted:
            key = rng.randrange(1 << 31)
        inserted.add(key)

        indices = [h(key) for h in hashes]
        for idx in indices:
            bit_array[idx] = 1

        bits_set = sum(bit_array)
        fill_ratio = bits_set / params.m

        false_positives = 0
        queries = 0
        while queries < params.n_queries:
            candidate = rng.randrange(1 << 31)
            if candidate in inserted:
                continue
            queries += 1
            if all(bit_array[h(candidate)] for h in hashes):
                false_positives += 1
        fp_rate = false_positives / max(1, queries)

        fp_rates.append(fp_rate)
        fill_ratios.append(fill_ratio)

        states.append(
            {
                "step": step,
                "key": key,
                "indices": indices,
                "bits": bit_array.copy(),
                "fill_ratio": fill_ratio,
                "false_positive_rate": fp_rate,
            }
        )

    summary = {
        "fill_ratio": fill_ratios[-1] if fill_ratios else 0.0,
        "false_positive_rate": fp_rates[-1] if fp_rates else 0.0,
        "theoretical_rate": _theoretical_rate(params.m, params.k, params.n_inserts),
        "optimal_k": (params.m / params.n_inserts) * math.log(2) if params.n_inserts else 0.0,
        "n_inserts": params.n_inserts,
        "n_queries": params.n_queries,
    }

    return {
        "states": states,
        "summary": summary,
    }


def _theoretical_rate(m: int, k: int, n: int) -> float:
    if m <= 0:
        return 0.0
    return (1 - math.exp(-(k * n) / m)) ** k
