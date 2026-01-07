from __future__ import annotations

from typing import Sequence

import plotly.graph_objects as go
from plotly.io import to_html


def build_grid_animation(grid: dict, paths: Sequence[Sequence[tuple[int, int]]], accepts: Sequence[bool], accent: str):
    if not paths:
        return {"plot_html": ""}

    width = grid["width"]
    height = grid["height"]
    obstacles = set(map(tuple, grid.get("obstacles", [])))
    start = tuple(grid["start"])
    goal = tuple(grid["goal"])

    # Base grid points
    xs = []
    ys = []
    colors = []
    for x in range(width):
        for y in range(height):
            xs.append(x)
            ys.append(y)
            if (x, y) == start:
                colors.append("#22c55e")
            elif (x, y) == goal:
                colors.append("#f97316")
            elif (x, y) in obstacles:
                colors.append("#0f172a")
            else:
                colors.append("#e2e8f0")
    grid_trace = go.Scatter(
        x=xs,
        y=ys,
        mode="markers",
        marker=dict(size=10, color=colors, symbol="square"),
        hoverinfo="none",
        showlegend=False,
    )

    frames = []
    slider_steps = []
    for idx, path in enumerate(paths):
        px = [p[0] for p in path]
        py = [p[1] for p in path]
        path_trace = go.Scatter(
            x=px,
            y=py,
            mode="lines+markers",
            line=dict(color=accent, width=4),
            marker=dict(size=10, color=accent),
            hoverinfo="none",
            showlegend=False,
        )
        accepted = accepts[idx] if idx < len(accepts) else False
        frames.append(go.Frame(data=[grid_trace, path_trace], name=f"step-{idx}", layout=dict(title=f"Step {idx} ({'accepted' if accepted else 'rejected'})")))
        slider_steps.append(
            dict(
                method="animate",
                args=[[f"step-{idx}"], {"frame": {"duration": 200, "redraw": True}, "mode": "immediate"}],
                label=str(idx),
            )
        )

    initial_path = paths[0]
    fig = go.Figure(
        data=[
            grid_trace,
            go.Scatter(
                x=[p[0] for p in initial_path],
                y=[p[1] for p in initial_path],
                mode="lines+markers",
                line=dict(color=accent, width=4),
                marker=dict(size=10, color=accent),
                hoverinfo="none",
                showlegend=False,
            ),
        ],
        frames=frames,
    )
    fig.update_layout(
        template="plotly_white",
        title="Metropolis–Hastings path samples",
        xaxis=dict(range=[-0.05, width - 0.95], dtick=1, tick0=0, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-1, height], dtick=1, tick0=0, zeroline=False, scaleanchor="x", scaleratio=1, showticklabels=False),
        height=420,
        margin=dict(l=20, r=20, t=80, b=40),
        showlegend=False,
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                pad=dict(r=10, t=10),
                x=0.0,
                xanchor="left",
                y=-0.2,
                bgcolor=accent,
                bordercolor=accent,
                font=dict(color="#ffffff"),
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 200, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}],
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


def build_length_trace(lengths: Sequence[int], accepts: Sequence[bool], accent: str):
    if not lengths:
        return {"plot_html": ""}
    steps = list(range(len(lengths)))
    colors = ["#22c55e" if (i < len(accepts) and accepts[i]) else "#ef4444" for i in steps]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=steps,
                y=lengths,
                mode="lines+markers",
                line=dict(color=accent, width=3),
                marker=dict(color=colors, size=8),
                hovertemplate="Step %{x}<br>Length %{y}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        template="plotly_white",
        title="Path length over MH steps",
        xaxis=dict(title="Step"),
        yaxis=dict(title="Path length"),
        margin=dict(l=40, r=20, t=50, b=40),
        height=320,
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
