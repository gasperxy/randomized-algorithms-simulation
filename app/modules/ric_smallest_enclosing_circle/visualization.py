from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple

import plotly.graph_objects as go
from plotly.io import to_html

Point = Tuple[float, float]


def _circle_coords(circle: Dict[str, float], segments: int = 90) -> Tuple[List[float], List[float]]:
    cx = circle["cx"]
    cy = circle["cy"]
    r = circle["r"]
    if r <= 0:
        return [cx], [cy]
    angles = [2 * math.pi * i / segments for i in range(segments + 1)]
    xs = [cx + r * math.cos(angle) for angle in angles]
    ys = [cy + r * math.sin(angle) for angle in angles]
    return xs, ys


def _axis_range(bounds: Dict[str, float], circle: Dict[str, float] | None = None) -> Tuple[List[float], List[float]]:
    x_min = bounds["x_min"]
    x_max = bounds["x_max"]
    y_min = bounds["y_min"]
    y_max = bounds["y_max"]
    if circle is not None:
        cx = circle["cx"]
        cy = circle["cy"]
        r = circle["r"]
        x_min = min(x_min, cx - r)
        x_max = max(x_max, cx + r)
        y_min = min(y_min, cy - r)
        y_max = max(y_max, cy + r)
    x_pad = (x_max - x_min) * 0.06 or 1.0
    y_pad = (y_max - y_min) * 0.06 or 1.0
    return [x_min - x_pad, x_max + x_pad], [y_min - y_pad, y_max + y_pad]


def build_incremental_animation(
    states: Sequence[Dict],
    accent_color: str,
    frame_duration_ms: int,
    bounds: Dict[str, float],
) -> Dict:
    if not states:
        return {"plot_html": ""}

    first_state = states[0]
    final_state = states[-1]
    x_range, y_range = _axis_range(bounds, final_state["circle"])
    point_x = [p[0] for p in first_state["points"]]
    point_y = [p[1] for p in first_state["points"]]
    circle_x, circle_y = _circle_coords(first_state["circle"])

    fig = go.Figure(
        data=[
            go.Scatter(
                x=point_x,
                y=point_y,
                mode="markers",
                marker=dict(color="#0f172a", size=7),
                showlegend=False,
            ),
            go.Scatter(
                x=circle_x,
                y=circle_y,
                mode="lines",
                line=dict(color=accent_color, width=3),
                showlegend=False,
            ),
        ],
        frames=[],
    )

    frames = []
    slider_steps = []
    for state in states:
        pts_x = [p[0] for p in state["points"]]
        pts_y = [p[1] for p in state["points"]]
        c_x, c_y = _circle_coords(state["circle"])
        frame_name = str(state["step"])
        frames.append(
            go.Frame(
                data=[
                    go.Scatter(x=pts_x, y=pts_y, mode="markers"),
                    go.Scatter(x=c_x, y=c_y, mode="lines"),
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
        title="Incremental construction of the smallest enclosing circle",
        xaxis=dict(range=x_range, showgrid=False, zeroline=False),
        yaxis=dict(range=y_range, showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1),
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
                bgcolor=accent_color,
                bordercolor=accent_color,
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
    circle: Dict[str, float],
    accent_color: str,
    bounds: Dict[str, float],
) -> Dict:
    if not points:
        return {"plot_html": ""}

    x_range, y_range = _axis_range(bounds, circle)
    pts_x = [p[0] for p in points]
    pts_y = [p[1] for p in points]
    circle_x, circle_y = _circle_coords(circle)

    fig = go.Figure(
        data=[
            go.Scatter(
                x=pts_x,
                y=pts_y,
                mode="markers",
                marker=dict(color="#0f172a", size=7),
                showlegend=False,
            ),
            go.Scatter(
                x=circle_x,
                y=circle_y,
                mode="lines",
                line=dict(color=accent_color, width=3),
                showlegend=False,
            ),
        ]
    )
    fig.update_layout(
        title="Final smallest enclosing circle",
        xaxis=dict(range=x_range, showgrid=False, zeroline=False),
        yaxis=dict(range=y_range, showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1),
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
