# Module Guide: Randomized Incremental Construction — Closest Pair Distance

## Summary
Find the closest pair of points (minimum Euclidean distance) using a randomized incremental construction (RIC) with a grid bucketing structure. Points are inserted in random order, and the grid is rebuilt only when the current best distance shrinks. The visualization shows the evolving closest pair and the grid used for neighbor checks.

## Problem
Given points in the plane, compute the minimum distance between any two points, and optionally the pair itself.

## Algorithm (RIC with uniform grid)
```text
RIC-Closest-Pair(points):
    shuffle(points)
    d = +infinity
    best_pair = None
    grid = empty
    for p in points:
        if d is +infinity:
            insert p into grid
            if grid has any other point q:
                d = dist(p, q); best_pair = (p, q); rebuild grid with cell size d
            continue

        check all points in p's cell and 8 neighboring cells
        if any closer pair found:
            update d and best_pair
            rebuild grid with cell size d
        insert p into grid
    return (best_pair, d)
```

### Why a grid?
When grid cell size is proportional to the current best distance `d`, a point can only have a closer neighbor in its own cell or immediately adjacent cells. This keeps per-insertion checks constant on average.

### Expected performance
Random insertion ensures that the best distance shrinks only a few times on average, so grid rebuilds are rare. The expected runtime is near linear in the number of points.

## Visualization Plan
Two charts displayed side by side:

### Left: Incremental Animation + Grid
- Show points as they are inserted one at a time.
- Draw the current closest pair as a highlighted segment.
- Overlay the grid used for neighbor checks (thin lines).
- When a rebuild occurs (distance shrinks), update grid cell size and highlight the event.

### Right: Final Snapshot
- Show all points.
- Show the final closest pair segment and the final distance.
- Keep the same grid overlay as the last step for context (optional toggle).

## Suggested Parameters
| Field | Default | Notes |
| --- | --- | --- |
| `n_points` | 200 | Number of points to sample. |
| `x_min` / `x_max` | 0 / 10 | Bounds for x coordinates. |
| `y_min` / `y_max` | 0 / 10 | Bounds for y coordinates. |
| `seed` | None | RNG seed for reproducibility. |
| `playback_speed_ms` | 250 | Animation frame duration. |

## Outputs
- Left Plotly animation: points, grid, and current closest pair.
- Right Plotly plot: final closest pair and distance.
- Summary stats: final distance, closest pair coordinates, number of rebuilds.

## Implementation Notes
- Use a small epsilon to avoid precision issues when comparing distances.
- Grid cell size should be `d` (or `d / sqrt(2)`); use the same rule consistently in neighbor checks.
- If there are fewer than 2 points, return empty visuals.
