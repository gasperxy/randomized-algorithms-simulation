# Module Guide: Randomized Incremental Construction — Smallest Enclosing Circle

## Summary
Compute the smallest enclosing circle (SEC) of a set of 2D points using randomized incremental construction (RIC). The algorithm inserts points in random order and updates the circle only when a new point falls outside. The visualization shows the incremental process on the left and the final SEC on the right.

## Problem
Given points in the plane, find the smallest circle that contains all of them. The optimal circle is uniquely determined by either:
- Two points on a diameter, or
- Three points on the boundary (their circumcircle).

## Algorithm (RIC / iterative Welzl-style)
```text
RIC-Smallest-Enclosing-Circle(points):
    shuffle(points)
    C = empty_circle()
    for p in points:
        if inside(C, p):
            continue
        C = circle_centered_at(p)
        for q in points_before(p):
            if inside(C, q):
                continue
            C = diameter_circle(p, q)
            for r in points_before(q):
                if inside(C, r):
                    continue
                C = circumcircle(p, q, r)
    return C
```

### Why random order?
Random insertion ensures that expensive rebuilds are rare on average. Each point is unlikely to become a boundary point many times, yielding expected O(n) time.

## Visualization Plan
Two charts displayed side by side:

### Left: Incremental Animation
- Shows points as they are inserted one at a time.
- The current SEC is drawn after each insertion.
- On each update event (a new point added), the circle is recomputed using the RIC routine and the frame updates:
  - Points up to the current step are visible.
  - Boundary points (if known) can be highlighted to explain the defining set (2 or 3 points).

### Right: Final Snapshot
- Shows all points.
- Shows the final SEC circle computed after all insertions.
- This view is static and serves as a reference for the end state.

## Suggested Parameters
| Field | Default | Notes |
| --- | --- | --- |
| `n_points` | 40 | Number of points to sample. |
| `x_min` / `x_max` | 0 / 10 | Bounds for x coordinates. |
| `y_min` / `y_max` | 0 / 10 | Bounds for y coordinates. |
| `seed` | None | RNG seed for reproducibility. |
| `playback_speed_ms` | 250 | Animation frame duration. |

## Outputs
- Left Plotly animation: point set prefix + evolving SEC.
- Right Plotly plot: full point set + final SEC.
- Summary stats: final radius, circle center, boundary point count (2 or 3), and total points.

## Implementation Notes
- Use a small epsilon for inside checks to avoid floating-point jitter.
- Circumcircle computation should handle collinear points by falling back to the diameter circle of the farthest pair.
- Keep all geometry in plain floats; no external geometry libraries required.
