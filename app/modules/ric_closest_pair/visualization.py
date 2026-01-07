from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple

import plotly.graph_objects as go
from plotly.io import to_html

Point = Tuple[float, float]


def _axis_range(bounds: Dict[str, float]) -> Tuple[List[float], List[float]]:
    x_min = bounds["x_min"]
    x_max = bounds["x_max"]
    y_min = bounds["y_min"]
    y_max = bounds["y_max"]
    y_pad = (y_max - y_min) * 0.06 or 1.0
    return [-1.0, x_max + 1.0], [y_min - y_pad, y_max + y_pad]


def _grid_trace(bounds: Dict[str, float], cell_size: float | None) -> go.Scatter:
    if cell_size is None or cell_size <= 0:
        return go.Scatter(x=[], y=[], mode="lines", line=dict(color="rgba(148,163,184,0.45)", width=1), showlegend=False)

    x_min = bounds["x_min"]
    x_max = bounds["x_max"]
    y_min = bounds["y_min"]
    y_max = bounds["y_max"]

    x_span = x_max - x_min
    y_span = y_max - y_min
    if x_span <= 0 or y_span <= 0:
        return go.Scatter(x=[], y=[], mode="lines", line=dict(color="rgba(148,163,184,0.45)", width=1), showlegend=False)

    x_spacing = cell_size
    y_spacing = cell_size

    xs: List[float] = []
    ys: List[float] = []

    x = x_min
    while x <= x_max + 1e-9:
        xs.extend([x, x, None])
        ys.extend([y_min, y_max, None])
        x += x_spacing

    y = y_min
    while y <= y_max + 1e-9:
        xs.extend([x_min, x_max, None])
        ys.extend([y, y, None])
        y += y_spacing

    return go.Scatter(
        x=xs,
        y=ys,
        mode="lines",
        line=dict(color="rgba(148,163,184,0.45)", width=1),
        hoverinfo="skip",
        showlegend=False,
    )


def _pair_trace(pair: Tuple[Point, Point] | None, color: str) -> go.Scatter:
    if not pair:
        return go.Scatter(x=[], y=[], mode="lines+markers", line=dict(color=color, width=3), showlegend=False)
    (ax, ay), (bx, by) = pair
    return go.Scatter(
        x=[ax, bx],
        y=[ay, by],
        mode="lines+markers",
        line=dict(color=color, width=3),
        marker=dict(color=color, size=9),
        showlegend=False,
        hoverinfo="skip",
    )


def build_incremental_animation(
    states: Sequence[Dict],
    accent_color: str,
    frame_duration_ms: int,
    bounds: Dict[str, float],
) -> Dict:
    if not states:
        return {"plot_html": ""}

    x_range, y_range = _axis_range(bounds)
    first_state = states[0]
    point_x = [p[0] for p in first_state["points"]]
    point_y = [p[1] for p in first_state["points"]]
    pair_trace = _pair_trace(first_state["best_pair"], accent_color)

    fig = go.Figure(
        data=[
            _grid_trace(bounds, first_state["cell_size"]),
            go.Scatter(
                x=point_x,
                y=point_y,
                mode="markers",
                marker=dict(color="#0f172a", size=7),
                showlegend=False,
            ),
            pair_trace,
        ],
        frames=[],
    )

    frames = []
    slider_steps = []
    for state in states:
        pts_x = [p[0] for p in state["points"]]
        pts_y = [p[1] for p in state["points"]]
        pair = _pair_trace(state["best_pair"], accent_color)
        frame_name = str(state["step"])
        frames.append(
            go.Frame(
                data=[
                    _grid_trace(bounds, state["cell_size"]),
                    go.Scatter(x=pts_x, y=pts_y, mode="markers"),
                    pair,
                ],
                name=frame_name,
            )
        )
        slider_steps.append(
            dict(
                method="animate",
                args=[[frame_name], {"frame": {"duration": frame_duration_ms, "redraw": True}, "mode": "immediate"}],
                label=frame_name,
            )
        )

    fig.frames = frames
    fig.update_layout(
        title="Incremental closest-pair updates",
        xaxis=dict(range=x_range, showgrid=False, zeroline=False, autorange=False, constrain="domain"),
        yaxis=dict(
            range=y_range,
            showgrid=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
            autorange=False,
            constrain="domain",
        ),
        height=420,
        margin=dict(l=20, r=20, t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                pad=dict(r=10, t=10),
                x=0.0,
                xanchor="left",
                y=-0.35,
                bgcolor="#0d6efd",
                bordercolor="#0d6efd",
                font=dict(color="#ffffff"),
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": frame_duration_ms, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": 0},
                            },
                        ],
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


def build_final_plot(
    points: Sequence[Point],
    best_pair: Tuple[Point, Point] | None,
    accent_color: str,
    bounds: Dict[str, float],
    cell_size: float | None,
) -> Dict:
    if not points:
        return {"plot_html": ""}

    x_range, y_range = _axis_range(bounds)
    pts_x = [p[0] for p in points]
    pts_y = [p[1] for p in points]

    fig = go.Figure(
        data=[
            _grid_trace(bounds, cell_size),
            go.Scatter(
                x=pts_x,
                y=pts_y,
                mode="markers",
                marker=dict(color="#0f172a", size=7),
                showlegend=False,
            ),
            _pair_trace(best_pair, accent_color),
        ]
    )
    fig.update_layout(
        title="Final closest pair",
        xaxis=dict(range=x_range, showgrid=False, zeroline=False, autorange=False, constrain="domain"),
        yaxis=dict(
            range=y_range,
            showgrid=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
            autorange=False,
            constrain="domain",
        ),
        height=420,
        margin=dict(l=20, r=20, t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
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


def build_rebuild_trace(states: Sequence[Dict], accent_color: str) -> Dict:
    if not states:
        return {"plot_html": ""}

    steps = [state["step"] for state in states]
    rebuild_flags = [1 if state.get("rebuild") else 0 for state in states]
    colors = [accent_color if flag else "#94a3b8" for flag in rebuild_flags]
    cumulative_work = []
    total = 0
    for state in states:
        total += 1
        if state.get("rebuild"):
            total += state["step"]
        cumulative_work.append(total)

    fig = go.Figure(
        data=[
            go.Scatter(
                x=steps,
                y=rebuild_flags,
                mode="lines+markers",
                line=dict(color="#cbd5f5", width=2),
                marker=dict(color=colors, size=7),
                hovertemplate="Step %{x}<br>Rebuild %{y}<extra></extra>",
                showlegend=False,
            ),
            go.Scatter(
                x=steps,
                y=cumulative_work,
                mode="lines",
                line=dict(color=accent_color, width=2),
                hovertemplate="Step %{x}<br>Work %{y}<extra></extra>",
                yaxis="y2",
                showlegend=False,
            )
        ]
    )
    fig.update_layout(
        title="Rebuild events and cumulative work",
        xaxis=dict(title="Step"),
        yaxis=dict(title="Rebuild", tickvals=[0, 1], ticktext=["No", "Yes"], range=[-0.1, 1.1]),
        yaxis2=dict(title="Work", overlaying="y", side="right", showgrid=False),
        height=260,
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
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
