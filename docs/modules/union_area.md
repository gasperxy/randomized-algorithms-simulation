# Module Guide: Monte Carlo Union of Rectangles

## Summary
Generates random axis-aligned rectangles, decomposes them into disjoint \(B_i\) slices, and estimates the union area using a Monte Carlo acceptance test (sample a rectangle proportional to its area, sample a point inside it, count it only if it belongs to the disjoint slice).

## Parameters
| Name | Default | Description |
| --- | --- | --- |
| `n_rectangles` | 6 | Number of rectangles to generate. |
| `min_size` / `max_size` | 1.0 / 3.0 | Side length range for randomly generated rectangles. |
| `x_max` / `y_max` | 10 / 10 | Canvas bounds; rectangles live in `[0, x_max] × [0, y_max]`. |
| `samples` | 200 | Number of Monte Carlo samples. |
| `speed_ms` | 300 | Frame speed for both animations. |
| `seed` | `None` | Optional RNG seed. |

## Outputs
- Main animation showing rectangles, shaded disjoint \(B_i\) regions, and sampled points (green hits, red misses).
- Rectangles overview grid with one subplot per rectangle, normalized to consistent axes and synchronized with the main slider.
- Timeline table, summary card (exact union vs estimate), and generated-rectangles table.

## Implementation Notes
- Exact union area and \(B_i\) decomposition use a grid constructed from all unique rectangle edges; each grid cell is assigned to the earliest rectangle that covers it.
- Sampling logic tracks per-rectangle hit/miss counts to feed the overview grid.
- Front-end JS keeps the overview grid animation in lockstep with the main slider via Plotly events, but the grid doesn’t auto-play until the user interacts.

## Future Enhancements
- Allow manual rectangle definitions (not just random generation).
- Expose epsilon/delta style controls (target accuracy, confidence) by adapting the sample count dynamically.
- Generalize to other shapes (convex polygons) given a membership predicate.
