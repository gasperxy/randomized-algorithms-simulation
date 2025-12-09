# Module Guide: Markov Random 3-SAT Walk

## Summary
Randomized local search with restarts for 3-SAT. For each restart, begin with a random assignment, then for up to \(3n\) steps pick an unsatisfied clause uniformly and flip a random variable inside it. If all clauses become satisfied, stop; otherwise restart with a fresh assignment.

## Parameters
| Name | Default | Description |
| --- | --- | --- |
| `n_variables` | 10 | Number of boolean variables \(n\). |
| `n_clauses` | 43 | Number of 3-clauses \(m\) (literals and signs drawn uniformly). |
| `error_probability` | 1.0 | Repeat factor \(r\); restarts computed as \(m = \lceil 2 r \sqrt{n} (4/3)^n \rceil\) (capped). Failure probability ≤ \(2^{-r}\). |
| `restarts` | computed | Display only; derived from \(r\) and \(n\). |
| `seed` | `None` | RNG seed for reproducible clauses and walks. |

## Outputs
- Stacked bar chart per step showing satisfied vs unsatisfied clauses; restart boundaries marked.
- Timeline table (step, restart index, satisfied count, delta, trend, and clause flipped).
- Restart outcomes table (steps taken, satisfied at end, success flag) plus summary stats (best satisfied, solved_at, rates of improvement/regression).
- Empirical transition counts between satisfied-clause levels.

## Notes
- Each restart runs at most \(3n\) steps; early exit on satisfaction.
- Clauses prefer distinct variables when possible; literal signs are uniform.
- Restart count is capped to keep runs interactive; users can override manually.
