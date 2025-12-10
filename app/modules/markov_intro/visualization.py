from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np
import plotly.graph_objects as go
from plotly.io import to_html


def _circular_positions(n: int, radius: float = 1.4):
    # Evenly space nodes on a circle; deterministic order keeps animations stable.
    positions = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        positions.append((radius * math.cos(angle), radius * math.sin(angle)))
    return positions


def _self_loop_points(x: float, y: float, radius: float = 0.1):
    theta = np.linspace(0, 2 * math.pi, 20)
    return x + radius * np.cos(theta), y + radius * np.sin(theta)


def _curved_edge(x0: float, y0: float, x1: float, y1: float, rad: float, sign: int = 1):
    """Quadratic curve control point offset perpendicular to the segment."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    dist = math.sqrt(dx * dx + dy * dy) or 1.0
    nx, ny = -dy / dist, dx / dist
    cx, cy = mx + sign * rad * nx * dist, my + sign * rad * ny * dist
    t_values = np.linspace(0, 1, 20)
    xs = []
    ys = []
    for t in t_values:
        xt = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t**2 * x1
        yt = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t**2 * y1
        xs.append(xt)
        ys.append(yt)
    return xs, ys


def build_transition_graph(matrix: Sequence[Sequence[float]], stationary: Sequence[float], accent: str):
    n = len(matrix)
    positions = _circular_positions(n)
    node_x, node_y, node_text, node_size = [], [], [], []
    for idx, (x, y) in enumerate(positions):
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"State {idx + 1}<br>π={stationary[idx]:.3f}")
        node_size.append(18 + 45 * stationary[idx])

    edge_traces = []
    max_weight = max(max(row) for row in matrix) if matrix else 0
    annotations = []
    for i, row in enumerate(matrix):
        for j, weight in enumerate(row):
            if weight <= 0:
                continue
            if i == j:
                continue
            x0, y0 = positions[i]
            x1, y1 = positions[j]
            vec_x, vec_y = x1 - x0, y1 - y0
            norm = math.sqrt(vec_x * vec_x + vec_y * vec_y) or 1.0
            margin = 0.15  # keep arrows from touching node centers
            sx = x0 + margin * vec_x / norm
            sy = y0 + margin * vec_y / norm
            ex = x1 - margin * vec_x / norm
            ey = y1 - margin * vec_y / norm
            sign = 1 if (i + j) % 2 == 0 else -1
            xs, ys = _curved_edge(sx, sy, ex, ey, rad=0.16, sign=sign)
            mid_idx = len(xs) // 2
            mid_x = xs[mid_idx]
            mid_y = ys[mid_idx]
            # approximate direction using curve neighbors
            prev_idx = max(mid_idx - 1, 0)
            next_idx = min(mid_idx + 1, len(xs) - 1)
            dx = xs[next_idx] - xs[prev_idx]
            dy = ys[next_idx] - ys[prev_idx]
            edge_traces.append(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    line=dict(
                        width=1 + 4 * (weight / max_weight if max_weight else 0),
                        color="rgba(59,130,246,0.5)",
                    ),
                    hoverinfo="text",
                    text=[f"P({i+1}->{j+1})={weight:.3f}"],
                    showlegend=False,
                )
            )
            arrow_ax = mid_x - 0.3 * dx
            arrow_ay = mid_y - 0.3 * dy
            # Use an annotation arrow so Plotly renders a visible head on curved segments.
            annotations.append(
                dict(
                    x=mid_x,
                    y=mid_y,
                    ax=arrow_ax,
                    ay=arrow_ay,
                    xref="x",
                    yref="y",
                    axref="x",
                    ayref="y",
                    showarrow=True,
                    arrowhead=3,
                    arrowsize=1.5,
                    arrowwidth=2,
                    arrowcolor=accent,
                    standoff=0,
                    text="",
                )
            )

    nodes = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[str(i + 1) for i in range(n)],
        textposition="middle center",
        hoverinfo="text",
        hovertext=node_text,
        marker=dict(
            size=node_size,
            color=[accent] * n,
            line=dict(width=1, color="#0f172a"),
            opacity=0.9,
        ),
        showlegend=False,
    )

    fig = go.Figure(data=[*edge_traces, nodes])
    fig.update_layout(
        template="plotly_white",
        title="Random Markov chain",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=40, b=10),
        height=420,
        annotations=annotations,
    )

    return {
        "plot_html": to_html(
            fig,
            full_html=False,
            include_plotlyjs="cdn",
            auto_play=False,
            config={"displayModeBar": False},
        )
    }


def build_frequency_comparison(empirical: Sequence[float], stationary: Sequence[float], accent: str):
    n = len(empirical)
    x = [f"S{i+1}" for i in range(n)]
    fig = go.Figure(
        data=[
            go.Bar(name="Empirical", x=x, y=empirical, marker_color=accent),
            go.Bar(name="Stationary", x=x, y=stationary, marker_color="#64748b"),
        ]
    )
    fig.update_layout(
        template="plotly_white",
        title="Empirical vs stationary distribution",
        barmode="group",
        bargap=0.15,
        bargroupgap=0.05,
        yaxis=dict(title="Probability", rangemode="tozero"),
        margin=dict(l=30, r=20, t=50, b=40),
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return {
        "plot_html": to_html(
            fig,
            full_html=False,
            include_plotlyjs=False,
            auto_play=False,
            config={"displayModeBar": False},
        )
    }


def build_walk_animation(
    matrix: Sequence[Sequence[float]],
    path_states: Sequence[int],
    stationary: Sequence[float],
    accent: str,
):
    if not path_states:
        return {"plot_html": ""}

    n = len(matrix)
    positions = _circular_positions(n)
    node_size = [18 + 45 * s for s in stationary]
    node_x = [p[0] for p in positions]
    node_y = [p[1] for p in positions]

    max_weight = max(max(row) for row in matrix) if matrix else 0
    edge_traces = []
    annotations = []
    for i, row in enumerate(matrix):
        for j, weight in enumerate(row):
            if weight <= 0:
                continue
            if i == j:
                continue
            x0, y0 = positions[i]
            x1, y1 = positions[j]
            vec_x, vec_y = x1 - x0, y1 - y0
            norm = math.sqrt(vec_x * vec_x + vec_y * vec_y) or 1.0
            margin = 0.15
            sx = x0 + margin * vec_x / norm
            sy = y0 + margin * vec_y / norm
            ex = x1 - margin * vec_x / norm
            ey = y1 - margin * vec_y / norm
            sign = 1 if (i + j) % 2 == 0 else -1
            xs, ys = _curved_edge(sx, sy, ex, ey, rad=0.16, sign=sign)
            mid_idx = len(xs) // 2
            mid_x = xs[mid_idx]
            mid_y = ys[mid_idx]
            prev_idx = max(mid_idx - 1, 0)
            next_idx = min(mid_idx + 1, len(xs) - 1)
            dx = xs[next_idx] - xs[prev_idx]
            dy = ys[next_idx] - ys[prev_idx]
            edge_traces.append(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    
                    line=dict(
                        width=1 + 4 * (weight / max_weight if max_weight else 0),
                        color="rgba(59,130,246,0.35)",
                    ),
                    hoverinfo="none",
                    showlegend=False,
                )
            )
            arrow_ax = mid_x - 0.3 * dx
            arrow_ay = mid_y - 0.3 * dy
            annotations.append(
                dict(
                    x=mid_x,
                    y=mid_y,
                    ax=arrow_ax,
                    ay=arrow_ay,
                    xref="x",
                    yref="y",
                    axref="x",
                    ayref="y",
                    showarrow=True,
                    arrowhead=3,
                    arrowsize=1.5,
                    arrowwidth=2,
                    arrowcolor=accent,
                    standoff=0,
                    text="",
                )
            )

    base_nodes = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[str(i + 1) for i in range(n)],
        textposition="middle center",
        hoverinfo="text",
        hovertext=[f"State {i + 1}<br>π={stationary[i]:.3f}" for i in range(n)],
        marker=dict(
            size=node_size,
            color="#e5e7eb",
            line=dict(width=1, color="#0f172a"),
            opacity=0.9,
        ),
        showlegend=False,
    )

    frames = []
    slider_steps = []
    for idx, state in enumerate(path_states):
        walker = go.Scatter(
            x=[positions[state][0]],
            y=[positions[state][1]],
            mode="markers+text",
            text=[str(state + 1)],
            textfont=dict(color="#0f172a", size=12, family="Arial"),
            textposition="middle center",
            marker=dict(size=32, color=accent, line=dict(width=2, color="#0f172a")),
            hoverinfo="text",
            hovertext=[f"Step {idx}<br>State {state + 1}"],
            showlegend=False,
        )
        frame_name = f"step-{idx}"
        frames.append(go.Frame(data=[*edge_traces, base_nodes, walker], name=frame_name))
        slider_steps.append(
            dict(
                method="animate",
                args=[[frame_name], {"frame": {"duration": 400, "redraw": True}, "mode": "immediate"}],
                label=str(idx),
            )
        )

    walker_start = go.Scatter(
        x=[positions[path_states[0]][0]],
        y=[positions[path_states[0]][1]],
        mode="markers",
        marker=dict(size=32, color=accent, line=dict(width=2, color="#0f172a")),
        hoverinfo="text",
        hovertext=[f"Step 0<br>State {path_states[0] + 1}"],
        showlegend=False,
    )

    fig = go.Figure(data=[*edge_traces, base_nodes, walker_start], frames=frames)
    fig.update_layout(
        template="plotly_white",
        title="Sample walk (first steps)",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=50, b=20),
        height=420,
        annotations=annotations,
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                pad=dict(r=10, t=10),
                x=0.0,
                xanchor="left",
                y=-0.35,
                bgcolor=accent,
                bordercolor=accent,
                font=dict(color="#ffffff"),
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 400, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                active=0,
                pad=dict(t=10),
                currentvalue=dict(prefix="Step "),
                steps=slider_steps,
            )
        ],
    )

    return {
        "plot_html": to_html(
            fig,
            full_html=False,
            include_plotlyjs="cdn",
            auto_play=False,
            config={"displayModeBar": False},
        )
    }


def build_variation_line(variation_over_time: Sequence[float], accent: str):
    if not variation_over_time:
        return {"plot_html": ""}

    x = list(range(1, len(variation_over_time) + 1))
    fig = go.Figure(
        data=[
            go.Scatter(
                x=x,
                y=variation_over_time,
                mode="lines",
                line=dict(color=accent, width=3),
                hovertemplate="Step %{x}<br>Variation distance=%{y:.3f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        template="plotly_white",
        title="Convergence to stationary (variation distance)",
        xaxis=dict(title="Step"),
        yaxis=dict(title="Variation distance", rangemode="tozero"),
        margin=dict(l=40, r=20, t=50, b=40),
        height=380,
        showlegend=False,
    )
    return {
        "plot_html": to_html(
            fig,
            full_html=False,
            include_plotlyjs=False,
            auto_play=False,
            config={"displayModeBar": False},
        )
    }
