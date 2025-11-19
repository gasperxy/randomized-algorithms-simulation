# Module Guide: Monte Carlo ln(2)

## Summary
Approximates \(\ln(2)\) by drawing uniform samples x ∈ [1, 2] and averaging 1/x. The estimator converges to the integral of 1/x over that interval.

## Parameters
| Name | Default | Description |
| --- | --- | --- |
| `samples` | 500 | Number of samples drawn. |
| `seed` | `None` | Optional RNG seed for reproducible sequences. |

## Outputs
- Line chart of the cumulative estimate vs sample count with a dashed horizontal line at ln(2).
- Table showing each sample value (1/x) and running estimate.

## Implementation Notes
- The simulation tracks cumulative sums of 1/x and stores each step.
- Visualization uses Plotly lines; there is no animation, but the graph updates whenever the form is submitted.

## Future Enhancements
- Surface confidence intervals (e.g., ±1.96 σ/√n) to illustrate variance.
- Support other integrals / functions by generalizing the sampler.
