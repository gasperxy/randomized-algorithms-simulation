# Module Guide: Bloom Filters

## Summary
Simulate a Bloom filter as items are inserted, visualize the bit array updates, and track the false-positive rate over time. Compare a good hash family against a deliberately biased one.

## Concept
A Bloom filter is a space-efficient probabilistic set representation:
- Insert item `x`: set `k` bit positions `h_1(x), ..., h_k(x)` to 1.
- Query `x`: if all `k` bits are 1, return "maybe"; if any is 0, return "no".
This yields false positives (never false negatives).

## Parameters
| Field | Default | Notes |
| --- | --- | --- |
| `m` | 128 | Number of bits in the array. |
| `k` | 4 | Number of hash functions. |
| `n_inserts` | 200 | How many items to insert. |
| `n_queries` | 200 | Random queries to estimate false positives. |
| `hash_family` | multiply_shift / biased | Choice of hash family. |
| `seed` | None | RNG seed for reproducibility. |
| `playback_speed_ms` | 250 | Animation frame duration. |

## Hash Families
- **Multiply-shift (good-ish):**
  $$
    h_i(x) = \left( (a_i x + b_i) \bmod 2^{64} \right) \gg \left(64 - \log_2 m\right)
  $$
  with random odd \(a_i\) and random \(b_i\) per hash function.
- **Biased (bad):**
  $$
    h_i(x) = (x + i) \bmod m \quad \text{or} \quad h_i(x) = (c x + i) \bmod m
  $$
  for small \(c\).

## Visualization Plan
Two charts displayed side by side:

### Left: Bit Array Animation
- Horizontal strip of `m` bits (0/1).
- Each insertion highlights the `k` hash positions, then turns them on.
- The current item and its hash indices are shown in a small caption.

### Right: False-Positive Rate
- Line chart of empirical false-positive rate vs number of inserted items.
- Overlay theoretical curve: \( (1 - e^{-kn/m})^k \).
- Optional badge for fill ratio (fraction of 1 bits).

## Outputs / Metrics
- Final fill ratio (bits set / m).
- Empirical false-positive rate after `n_inserts`.
- Theoretical false-positive rate at `n_inserts`.

## Implementation Notes
- Use integer keys sampled uniformly from a large range.
- Ensure `m` is a power of two for the multiply-shift trick; if not, fall back to modulo.
- Keep bit array visualization light: render as a single scatter row or small rectangle grid.
