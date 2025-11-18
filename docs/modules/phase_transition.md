# Module Guide: Random Graph Phase Transitions (G(n, p))

## Summary
Animates Erdős–Rényi G(n, p) graphs as the edge probability sweeps from `p_start` to `p_end`, revealing phase transitions (first cycle, connectivity, triangles, giant component, etc.).

## Parameters
| Name | Default | Description |
| --- | --- | --- |
| `n_vertices` | 30 | Number of vertices n. |
| `p_start` / `p_end` / `p_step` | 0 → 0.1 step 0.001 | Probability range for the sweep. |
| `playback_speed_ms` | 400 | Animation frame duration. |
| `seed` | `None` | Optional RNG seed (added to base seed per frame). |

## Outputs
- Plotly animation with play/pause & slider (probability axis).
- Statistics table for each probability.
- Phase-transition summary comparing theoretical vs observed thresholds.

## Implementation Notes
- Simulation uses NetworkX `gnp_random_graph` per sweep step.
- Layout positions are stabilized by seeding the spring layout once and reusing positions, minimizing jitter.
- Theoretical markers come from `modules.common.graph_services.theoretical_phase_markers`.

## Future Enhancements
- Allow node/edge styling toggles (color by degree, component numbering, etc.).
- Add snapshot download for any frame.
- Expose more statistics (betweenness, spectral gap) when feasible.
