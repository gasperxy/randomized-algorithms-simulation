# Module Guide: Markov Chains — Basics

## Summary
Generates a small random ergodic Markov chain, visualizes its transition graph, walks a sample trajectory from a chosen start state, and compares empirical visitation frequencies to the stationary distribution. Also reports first hitting times and the transition matrix.

## Parameters
| Name | Default | Description |
| --- | --- | --- |
| `n_states` | 6 | Number of states (clamped to 4–10). |
| `steps` | 500 | Length of the sampled trajectory. |
| `start_state` | 2 | Initial state (clamped to available states). |
| `seed` | `None` | RNG seed for reproducible chains and paths. |

## Outputs
- Transition graph: edge thickness encodes probabilities; node size encodes stationary mass.
- Bar chart: empirical visitation frequency vs stationary distribution.
- Variation-distance line: \(\tfrac12 \sum_i |\hat{\pi}_i - \pi_i|\) over steps to show convergence toward stationarity.
- Hitting times: first hit from start state to each state (or “not visited”).
- Transition matrix table and sample path (first 300 steps).
- Summary stats: unique states visited, variation distance between empirical and stationary.

## Implementation Notes
- Transition matrix sampled from positive weights then smoothed with a small uniform mix to ensure ergodicity.
- Stationary distribution solved via linear system \((P^T - I)\pi = 0\) with \(\sum \pi = 1\).
- Empirical frequencies come from the sampled path; hitting times are recorded on first visit per state.
