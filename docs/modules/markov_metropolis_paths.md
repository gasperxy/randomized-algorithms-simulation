# Design: Markov Chains — Metropolis–Hastings for Grid Paths

## Goal
Sample simple paths on a 2D grid using a Metropolis–Hastings (MH) Markov chain that favors shorter paths (e.g., via an exponential energy/length penalty). This topic will live under the Markov Chains section alongside other MH-friendly examples.

## State Space
- States are *simple* paths on a rectangular grid between a fixed start and end cell (no self-intersections).
- Represent a path as an ordered list of grid coordinates $(x_i, y_i)$ with Manhattan-adjacent steps.
- Path length $L$ = number of edges (nodes $- 1$); energy $E(\text{path}) = \lambda \cdot L$ (or $L$ itself). Target distribution $\pi(\text{path}) \propto \exp(-E)$ to favor short paths.

## Proposal (Neighbors of a Path)
We need local moves that (a) keep paths simple, (b) allow exploration, and (c) are easy to sample. A few practical proposal moves:
1) **Corner Flip**: pick an internal node with distinct prev/next; if prev and next share a common neighbor that is not equal to current, replace current with that neighbor (flips a 90° turn).
2) **Edge Shortcut / Detour Swap**:
   - *Shortcut*: pick three consecutive nodes $A$–$B$–$C$ that are Manhattan distance 2 apart (a “zig-zag”); if $A$ and $C$ are adjacent and $A$–$C$ is not already used, replace $A$–$B$–$C$ with $A$–$C$.
   - *Detour*: inverse of shortcut—insert a two-step dogleg at an edge $A$–$C$ by picking a perpendicular detour $B$ such that $A$–$B$–$C$ is valid and simple.
3) **Endpoint Wiggle (extend/contract)**: at either endpoint, if there is a free neighbor not on the path, you can prepend/append it (extends length); if the second node has another neighbor that is free, you can drop the endpoint (contracts length).
4) **Segment Re-route (local reconnection)**: pick a small window (e.g., 4–6 nodes) and attempt to reconnect the ends via a shortest path within the bounding box if it stays simple. Keep only lightweight attempts to avoid heavy computation.

Practical proposal sampler:
- Precompute candidate moves for the current path:
  - Corner flips: iterate internal indices and test the perpendicular neighbor.
  - Shortcuts: scan triples $A$–$B$–$C$; if $\operatorname{dist}_1(A,C)=1$ and edge unused, propose removing $B$.
  - Detours: scan edges $A$–$C$; try the two perpendicular detours; keep those that are simple.
  - Endpoint wiggles: try adding/removing one step at each end.
- Collect all valid neighbor paths; pick one uniformly at random (or weighted per move type). If none exist, stay in place (self-loop).

### Visualizing Local Moves (ASCII sketches)
Corner flip (turn becomes turn in opposite corner):
```
Before:        After:
· A B ·        · A · ·
· · C ·        · B C ·
```

Shortcut (remove a zig-zag detour when $A$ and $C$ are already neighbors):
```
Before:           After:
· A B ·           · A · ·
· D C ·     ->    · D · ·
(A–B–C via D)     (collapsed to A–D)
```

Detour (reroute around a straight three-step run when $A$ and $C$ are two steps apart):
```
Before:        After:
· A · ·        D A · ·
· B · ·        E · · ·
· C · ·        F C · ·
```

More complex zig-zag or ladder patterns can appear; some proposals may momentarily create self-intersections or revisits. Those candidates must be rejected or simplified back to a simple path before being treated as valid neighbors.

Endpoint wiggle (extend endpoint; start/end remain fixed):
```
Before:        After:
N              N
|              |
S──P           S──P──N'
```

## Metropolis–Hastings Step
- Proposal $q(\text{path} \to \text{path}')$: uniform over the enumerated neighbor list.
- Target $\pi(\text{path}) \propto \exp(-\lambda \cdot L(\text{path}))$.
- Acceptance probability:
  $$
  \alpha = \min\left(1, \frac{\pi(\text{path}') \, q(\text{path}' \to \text{path})}{\pi(\text{path}) \, q(\text{path} \to \text{path}')}\right)
  = \min\left(1, e^{-\lambda(\ell' - \ell)} \cdot \frac{|N(\text{path})|}{|N(\text{path}')|}\right)
  $$
  where $|N(\cdot)|$ is the neighbor count used for uniform proposals.
- If proposal invalid (no neighbors), remain at current path.

## Parameters
| Field | Notes |
| --- | --- |
| Grid size ($W \times H$) | Keep small (e.g., 8–12) for visualization. |
| Start / End | Fixed grid cells. |
| \(\lambda\) | Inverse temperature; higher favors shorter paths (or longer if mode = “longest”). |
| Mode | `"shortest"` or `"longest"` to bias the target. |
| Steps | MH iterations to run (animation shows first ~300). |
| Seed | RNG seed for reproducibility. |

## Outputs / Visuals
- Animated path on the grid (Plotly): start/end pins; current path in blue; accepted proposals highlighted; rejected shown briefly in red/gray.
- Length trace over iterations.
- Histogram of visited lengths; mean/median length; acceptance rate.

## Edge Cases / Simplicity Checks
- Neighbor generation must enforce simplicity (no repeated vertices) and grid bounds.
- If a proposed path revisits a cell or uses out-of-bounds coordinates, discard.
- When no valid neighbors, self-loop (keeps chain aperiodic).

## Extensibility
- Swap the energy function (e.g., add turn penalties or obstacles).
- Alternative proposals: random “regrowth” of a suffix/prefix via simple random walk with self-avoidance, cropped at intersections.
- Could re-use the neighbor enumeration to visualize proposal distribution size \(|N(\text{path})|\) across states.
