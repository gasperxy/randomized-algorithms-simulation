# Design: Markov Chains — Random Walks on Graphs

## Goals
- New topic family “Random Walks in Graphs” under Markov Chains.
- For each graph family (path, complete, lollipop) provide:
  - Small interactive visualization + animated walk (10–15 vertices).
  - Empirical cover-time experiments as vertex count grows (10 → 200, step 10), averaged over 5 runs.
  - Comparison against known asymptotic cover-time bounds (fit overlay).

## Graph Families
- Path graph \(P_n\): cover time \(\Theta(n^2)\) (matches general \(O(nm)\)).
- Complete graph \(K_n\): cover time \(\Theta(n \log n)\) (coupon collector).
- Lollipop graph: \(P_{n/2}\) attached to \(K_{n/2}\); worst-case cover time \(\Theta(n m)\). We expose two starts: free path endpoint (≈ quadratic) and bridge-adjacent endpoint (≈ cubic, fit with \(a n^3 + b n^2 + c n + d\)).

## UI / Flow
- Module entry: “Random Walks in Graphs” (slug `markov_random_walks`), grouped with other Markov topics.
- Tabs or pills for graph type: Path, Complete, Lollipop.
- Layout per graph type:
  1) Row 1: graph visualization with animated walk (first 300–500 steps) + parameter card.
  2) Row 2: cover-time growth chart (avg over runs) with fitted curve overlay; stats table (mean, stdev, runs).
- Results cards: last cover time (small instance), bound label (e.g., \(O(n^2)\), \(O(n \log n)\), \(O(nm)\)), fitted coefficient/curve quality (R²).

## Parameters
| Field | Default | Notes |
| --- | --- | --- |
| `graph_type` | Path / Complete / Lollipop | UI tabs; not user-editable per run. |
| `n_small` | 12 | Vertex count for the animated demo (clamp 4–20). |
| `steps_demo` | 400 | Steps to animate (clamp 50–1000). |
| `start_vertex` | 1 | Starting vertex for demo (clamp to n). |
| `n_min` | 10 | Lower bound for sweep. |
| `n_max` | 200 | Upper bound for sweep. |
| `n_step` | 10 | Increment. |
| `runs_per_n` | 5 | Averaging runs per size. |
| `seed` | None | Optional seed for reproducibility. |

## Simulation Outline
- Graph generators:
  - Path: edges \((i,i+1)\).
  - Complete: edges between every pair.
  - Lollipop: path of \(n/2\) plus clique of \(n/2\) attached via a single bridge edge.
- Walk step: simple random walk (uniform over neighbors).
- Cover time experiment:
  - For each \(n\) in sweep: run `runs_per_n` independent walks until all vertices visited; record steps.
  - Return mean, stdev, raw samples.
- Demo animation:
  - Record first `steps_demo` steps (vertices visited) plus visit counts for highlighting.
  - Track time-to-first-visit per vertex for tooltips.

## Visualization Plan
- Graph view (Plotly + networkx layout):
  - Node colors indicate visitation: green = visited, gray/black = not yet visited, blue = current node; sizes stay uniform for clarity.
  - Edges simple lines; for complete graph use circular layout; path uses linear; lollipop uses hybrid layout (path line + clique circle).
  - Playback controls (play/pause/slider).
- Cover-time growth chart:
  - X: number of vertices.
  - Y: average cover time (log scale optional).
  - Overlay theoretical fit:
    - Path: fit \(a n^2 + b n + c\).
    - Complete: fit \(a n \log n + b n + c\).
    - Lollipop: fit \(a (n m) + b n + c\) (with \(m\) from the constructed graph).
  - Error bars for stdev.
- Stats table:
  - Latest demo cover time, mean cover time at largest \(n\), fitted coefficient, R² of fit vs observed.

## Implementation Notes
- Reuse module pattern (controller/simulation/visualization) with slug `markov_random_walks`.
- Simulation should short-circuit if cover time exceeds a safety cap (to avoid hangs on lollipop for large n).
- Keep payload small: only the demo walk stores per-step path; sweep runs return aggregated stats.
- Fit coefficients via least squares on transformed features (e.g., \(n^2\), \(n \log n\), \(nm\)).
- Keep all code ASCII; follow existing Markov module styling and math rendering (MathJax already enabled).
