# Module Guide: Markov Chain Playground (First Topic — Random 2-SAT Walk)

## Purpose
- Provide a dedicated space for Markov chain experiments, mirroring the modular interface used elsewhere in the lab.
- Share infrastructure (controllers, simulation core, visualization helpers) so additional topics like Metropolis–Hastings, random walks on graphs, or Glauber dynamics can plug in later.

## Module Layout
```
/modules/
  markov_random_2sat/      # First topic (Random 2-SAT Walk)
  markov_metropolis_/...   # Future topics live alongside with same conventions
```
- Every topic is a full module package (controller, simulation, visualization) just like `phase_transition` or `g_nm`.
- Home page groups these modules under a “Markov Chains” section, so visitors see a cohesive family even though each topic stands alone technically.
- Shared helpers (clause factories, RNG utilities, base Plotly components) live in `modules/common/markov/` to reduce duplication without forcing nested “topics” folders.

## Common Responsibilities
- **Module registry** (existing pattern) exposes `{slug, name, description, controller}`; each Markov topic registers independently but uses a shared naming convention (`markov_*`) so the presentation layer can group them on the home page.
- **Controllers** share a base mixin (optional) to normalize repeated parameters (e.g., number of steps, seed) and extend with topic-specific fields.
- **Simulation interface** returns
  ```
  {
    "states": [ { "step": int, "state": Any, "metadata": {...} }, ... ],
    "transitions": [ { "from": ..., "to": ..., "prob": float }, ... ],  # Optional static chain definition
    "stats": { ... },        # Topic-specific aggregates
    "topic_metadata": { ... }
  }
  ```
- **Visualization layer** receives the simulation payload and derives Plotly figures:
  - State timeline animation (current state moving along discrete positions).
  - Auxiliary view (e.g., clause satisfaction heat map, potential function).
  - Summary cards for convergence metrics / stopping conditions.

## Module: Markov Random 2-SAT Walk

### Concept
- Represent each assignment to variables \(x_1, \dots, x_n\) as a state summarized by the number of satisfied clauses (0 → m).
- Start from a random assignment, choose an unsatisfied clause, flip a random variable within it (Papadimitriou’s random-walk algorithm).
- Track the Markov chain over the coarse-grained state space “# satisfied clauses” to illustrate progress toward satisfying all clauses.

### Parameters
| Field | Default | Notes |
| --- | --- | --- |
| `topic` | `random_2sat` | Hidden drop-down for future topics. |
| `n_variables` | 12 | Number of boolean variables. |
| `n_clauses` | 40 | Clauses generated uniformly with literals sampled independently. |
| `max_steps` | 400 | Total random-walk iterations to simulate. |
| `restart_threshold` | `None` | Optional step count after which a new random assignment is sampled (mirrors restart heuristics). |
| `seed` | `None` | Seeds RNG for clause generation + walk sampling. |

### Simulation Outputs
- `clauses`: concrete clause list for display / validation.
- `state_sequence`: ordered list of steps with:
  - `step` index.
  - `satisfied_count` (0→m).
  - `current_assignment` snapshot (optional toggle for download to avoid heavy payloads).
  - `flipped_variable`, `chosen_clause`, and whether the step improved satisfaction.
- `best_state`: max satisfied clauses seen + step index.
- `absorbing_hit`: boolean indicating whether all clauses were satisfied, with step number.
- `transition_histogram`: counts of transitions between satisfied-clause levels to approximate the Markov chain probabilities empirically.

### Visualization Plan
1. **State Line Animation**
   - x-axis labeled `Satisfied Clauses (0 ... m)`.
   - Static nodes for each possible count; sizes convey empirical stationary weight.
   - Animated marker highlights the current state; color indicates improvement (green), neutral (blue), or regression (orange).
   - Playback slider follows step index (0...`max_steps`).
2. **Clause Satisfaction Heatmap**
   - Rows = clauses, columns = steps (sampled to keep width manageable).
   - Color encodes satisfied (1) vs unsatisfied (0).
   - Hover reveals clause literals and whether the flipped variable participates.
3. **Summary Cards**
   - “Peak satisfied clauses” vs total.
   - Steps to solution (if reached) or “not reached”.
   - Average improvement probability vs stagnation/regression.

### Extensibility Hooks
- Module registry already used by the home page can flag any `slug` prefixed with `markov_` to appear under the Markov Chains heading, so adding `markov_metropolis_grid`, `markov_glauber_colorings`, etc. requires no template changes.
- Visualization builder detects `topic_metadata.visual_layout` to choose the appropriate figure combination.
- Simulation core provides helpers:
  - RNG utilities (shared seeding with per-topic offsets).
  - Transition counter object for building empirical chain matrices.
  - Clause factory library for reproducible random formula generation.

### Future Enhancements
- Allow users to paste a custom CNF formula for deterministic runs.
- Surface theoretical runtime guidance (e.g., \(O(n^2)\) expected steps under satisfiable assumption).
- Add dual-view: assignment-level state graph (hypercube shortcuts) alongside coarse satisfied-count view.
- Export transition histogram as CSV for further Markov-chain analysis.

> Module guide: see `docs/modules/markov_random_3sat.md` for the 3-SAT variant.

## Module: Markov Random 3-SAT Walk

### Concept
- Randomized local search with restarts: start from a random assignment, repeat for up to \(3n\) steps—pick an unsatisfied 3-clause uniformly, flip a random variable within it, and check again. If not solved, restart with a fresh assignment.
- Run the restart loop \(m \approx 2 r \sqrt{n} (4/3)^n\) times (capped); with repeat factor \(r\), the probability of incorrectly returning “unsatisfied” when a solution exists is bounded by \(2^{-r}\).
- Surface how often restarts succeed, steps to solution, and how satisfied/unsatisfied counts evolve over time.

### Parameters
| Field | Default | Notes |
| --- | --- | --- |
| `n_variables` | 10 | Number of boolean variables. |
| `n_clauses` | 43 | Clauses generated uniformly with 3 literals each. |
| `error_probability` | 1.0 | Repeat factor \(r\); restarts \(m = \lceil 2 r \sqrt{n} (4/3)^n \rceil\) (capped), failure probability ≤ \(2^{-r}\). |
| `restarts` | computed | Display only; derived from \(r\) and \(n\). |
| `seed` | `None` | Seeds RNG for clause generation + walks. |

### Outputs
- Stacked bar chart of satisfied vs unsatisfied clauses per step across restarts.
- Timeline table per step with restart index, clause flipped, and trend (improved/steady/regressed).
- Restart outcomes table (steps taken, satisfied at end, success flag) plus summary stats.
- Transition histogram over satisfied-clause levels to approximate empirical chain moves.

### Implementation Notes
- Each restart runs exactly \(3n\) steps unless a satisfying assignment is found earlier.
- Clauses are generated with distinct variables when possible; literal signs are uniform.
- Restart count uses \(m = \lceil 2 r \sqrt{n} (4/3)^n \rceil\) but is capped to keep runs responsive; users can override `restarts` directly.

### Future Enhancements
- Optional per-restart plots (steps to solution distribution).
- Allow custom 3-CNF upload.
- Expose a hard cap/slider for restarts to explore runtime vs success trade-offs.

## Module: Markov Chains — Basics

### Concept
- Generate a small random, ergodic Markov chain and visualize its transition graph.
- Sample a trajectory from a chosen start state, compare empirical visitation to the stationary distribution, and report first hitting times.

### Parameters
| Field | Default | Notes |
| --- | --- | --- |
| `n_states` | 6 | Number of states (4–10). |
| `steps` | 500 | Length of the sampled trajectory. |
| `start_state` | 2 | Initial state (clamped to available states). |
| `seed` | `None` | RNG seed for reproducible chains and paths. |

### Outputs
- Transition graph with edge thickness by probability and node sizes by stationary mass.
- Bar chart comparing empirical visitation frequencies vs stationary distribution.
- Variation-distance line chart showing \(\tfrac12 \sum_i |\hat{\pi}_i - \pi_i|\) over steps (empirical vs stationary).
- Hitting-time table from the start state and the transition matrix for inspection.
- Sample path table (first 300 steps) and summary stats (unique states visited, variation distance).

### Implementation Notes
- Transition matrix rows are sampled from positive weights, then smoothed with a small uniform mix to ensure ergodicity.
- Stationary distribution solved via linear system \((P^T - I)\pi = 0\) with \(\sum \pi = 1\).
- Empirical frequencies come from the sampled path; hitting times are recorded on first visit per state.

## Module: Random Walks in Graphs

### Concept
- Simple random walks on graph families (path, complete, lollipop) to study cover time empirically and compare against known bounds.
- Small instance is animated; larger instances are swept (n = 10 → 200) with multiple runs averaged.

### Parameters
| Field | Default | Notes |
| --- | --- | --- |
| `graph_type` | path/complete/lollipop | Choose graph family. |
| `n_small` | 12 | Vertices in animated demo (4–20). |
| `steps_demo` | 400 | Steps captured for the animation. |
| `start_vertex` | 1 | Start node for demo. |
| `n_min` / `n_max` / `n_step` | 10 / 200 / 10 | Sweep range for cover-time experiments. |
| `runs_per_n` | 5 | Runs averaged per size. |
| `seed` | None | Optional seed. |

### Outputs
- Animated walk on the selected small graph, coloring visited vs unvisited nodes and highlighting the current node.
- Cover-time growth chart with mean + stdev bars and fitted curve:
  - Path: \(a n^2 + b n + c\).
  - Complete: \(a n \log n + b n + c\).
  - Lollipop: \(a (n m) + b n + c\) with \(m\) edges from the constructed graph.
- Fit summary (coefficients, \(R^2\)).

### Implementation Notes
- Graph generators: path edges \((i,i+1)\); complete connects all pairs; lollipop is a path of \(n/2\) nodes attached to a clique of \(n/2\) via a single edge.
- Cover-time runs stop when all vertices are visited or a generous safety cap \(O(nm)\) is reached.
- Fits solved by least squares on the chosen feature set for each graph family.
