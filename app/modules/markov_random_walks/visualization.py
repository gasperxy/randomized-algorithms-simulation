from __future__ import annotations

import math
from typing import Iterable, Sequence, Tuple

import numpy as np
import plotly.graph_objects as go
from plotly.io import to_html


def _path_positions(n: int) -> dict:
    return {i: (i * 1.2, 0.0) for i in range(n)}


def _circular_positions(n: int, radius: float = 2.0) -> dict:
    pos = {}
    for i in range(n):
        angle = 2 * math.pi * i / n
        pos[i] = (radius * math.cos(angle), radius * math.sin(angle))
    return pos


def _lollipop_positions(n: int) -> dict:
    n_path = max(2, n // 2)
    n_clique = n - n_path
    pos = {}
    # Path along x-axis.
    for i in range(n_path):
        pos[i] = (i * 1.2, 0.0)
    if n_clique == 0:
        return pos
    center_x = (n_path - 1) * 1.2 + 2.5
    center_y = 0.0
    for idx, node in enumerate(range(n_path, n)):
        angle = 2 * math.pi * idx / n_clique
        pos[node] = (
            center_x + 1.3 * math.cos(angle),
            center_y + 1.3 * math.sin(angle),
        )
    return pos


def _positions(graph_type: str, n: int) -> dict:
    if graph_type in ("path", "path_endpoint"):
        return _path_positions(n)
    if graph_type == "complete":
        return _circular_positions(n)
    if graph_type in ("lollipop_free", "lollipop_bridge"):
        return _lollipop_positions(n)
    return _circular_positions(n)


def _edge_traces(edges: Iterable[Tuple[int, int]], positions: dict) -> go.Scatter:
    xs = []
    ys = []
    for u, v in edges:
        xs.extend([positions[u][0], positions[v][0], None])
        ys.extend([positions[u][1], positions[v][1], None])
    return go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#cbd5e1", width=1.5), hoverinfo="none", showlegend=False)


def build_graph_animation(
    graph_type: str,
    edges: Sequence[Tuple[int, int]],
    path: Sequence[int],
    first_hit: Sequence[int | None],
    n: int,
    accent: str,
):
    if not path:
        return {"plot_html": ""}

    positions = _positions(graph_type, n)
    edge_trace = _edge_traces(edges, positions)

    # Precompute visited sets for frames
    frames = []
    slider_steps = []
    visited = set()
    for idx, node in enumerate(path):
        visited.add(node)
        colors = []
        hover = []
        for i in range(n):
            if i == node:
                colors.append(accent)
            elif i in visited:
                colors.append("#22c55e")
            else:
                colors.append("#0f172a")
            hit = first_hit[i]
            hover.append(f"v{i+1}<br>First hit: {hit if hit is not None else '—'}")
        node_trace = go.Scatter(
            x=[positions[i][0] for i in range(n)],
            y=[positions[i][1] for i in range(n)],
            mode="markers+text",
            text=[str(i + 1) for i in range(n)],
            textposition="middle center",
            marker=dict(size=24, color=colors, line=dict(color="#0f172a", width=1.5)),
            hoverinfo="text",
            hovertext=hover,
            showlegend=False,
        )
        frame_name = f"step-{idx}"
        frames.append(go.Frame(data=[edge_trace, node_trace], name=frame_name))
        slider_steps.append(
            dict(
                method="animate",
                args=[[frame_name], {"frame": {"duration": 300, "redraw": True}, "mode": "immediate"}],
                label=str(idx),
            )
        )

    # Initial nodes (step 0)
    initial_colors = []
    initial_hover = []
    visited_init = {path[0]}
    for i in range(n):
        if i == path[0]:
            initial_colors.append(accent)
        elif i in visited_init:
            initial_colors.append("#22c55e")
        else:
            initial_colors.append("#0f172a")
        hit = first_hit[i]
        initial_hover.append(f"v{i+1}<br>First hit: {hit if hit is not None else '—'}")

    node_start = go.Scatter(
        x=[positions[i][0] for i in range(n)],
        y=[positions[i][1] for i in range(n)],
        mode="markers+text",
        text=[str(i + 1) for i in range(n)],
        textposition="middle center",
        marker=dict(size=24, color=initial_colors, line=dict(color="#0f172a", width=1.5)),
        hoverinfo="text",
        hovertext=initial_hover,
        showlegend=False,
    )

    fig = go.Figure(data=[edge_trace, node_start], frames=frames)
    fig.update_layout(
        template="plotly_white",
        title="Random walk on the graph",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=50, b=40),
        height=450,
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
                        args=[None, {"frame": {"duration": 300, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}],
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


def build_cover_growth(
    graph_type: str,
    sizes: Sequence[int],
    means: Sequence[float],
    stdevs: Sequence[float],
    fit: dict,
    accent: str,
):
    if not sizes:
        return {"plot_html": ""}

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sizes,
            y=means,
            mode="lines+markers",
            error_y=dict(type="data", array=stdevs, visible=True, color="rgba(15,23,42,0.4)"),
            line=dict(color=accent, width=3),
            marker=dict(color=accent),
            name="Average cover time",
        )
    )

    if fit and fit.get("predicted"):
        fig.add_trace(
            go.Scatter(
                x=sizes,
                y=fit["predicted"],
                mode="lines",
                line=dict(color="#0f172a", dash="dash"),
                name="Fit",
            )
        )

    subtitle = {
        "path": "Expected Θ(n²)",
        "complete": "Expected Θ(n log n)",
        "lollipop": "Expected Θ(n·m)",
    }.get(graph_type, "")

    fig.update_layout(
        template="plotly_white",
        title=f"Cover time vs graph size ({subtitle})",
        xaxis=dict(title="Number of vertices"),
        yaxis=dict(title="Average cover steps", rangemode="tozero"),
        margin=dict(l=50, r=20, t=60, b=40),
        height=420,
        showlegend=True,
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
