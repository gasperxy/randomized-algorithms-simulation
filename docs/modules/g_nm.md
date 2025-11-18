# Module Guide: Random Graph Edge Process (G(n, m))

## Summary
Constructs an Erdős–Rényi G(n, m) graph by shuffling the \(\binom{n}{2}\) edge list and revealing edges one at a time. Shows how discrete edge counts track the equivalent G(n, p) probability thresholds.

## Parameters
| Name | Default | Description |
| --- | --- | --- |
| `n_vertices` | 30 | Number of vertices n. |
| `edge_count` | 80 | Target number of edges m (capped at \(\binom{n}{2}\)). |
| `playback_speed_ms` | 400 | Animation speed. |
| `seed` | `None` | Optional RNG seed for reproducible shuffles/layouts. |

## Outputs
- Plotly animation with base edges + highlighted newest edge.
- Timeline table per step showing edge count, p estimate (= edges / \(\binom{n}{2}\)), and graph stats.
- Phase-transition markers vs observed events (same logic as G(n, p)).

## Implementation Notes
- Edge sequence is generated once via `random.shuffle` of all possible edges.
- Layout positions are recomputed per step via `simulation.compute_layouts`, seeding each spring layout with the previous positions for smoother motion.
- Controller caps `edge_count` when the user exceeds \(\binom{n}{2}\) and surfaces an inline validation error.

## Future Enhancements
- Option to reuse the exact same edge order between runs for better visual comparison.
- Provide dual-view (edge additions vs probability sweep) simultaneously.
- Allow exporting the edge sequence for external analysis.
