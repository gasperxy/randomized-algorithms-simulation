from __future__ import annotations

from typing import Dict, List, Sequence

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.io import to_html

from .simulation import Rectangle


def _rect_shape(rect: Rectangle, color: str, opacity: float) -> Dict:
    return {
        "type": "rect",
        "xref": "x",
        "yref": "y",
        "x0": rect.x,
        "y0": rect.y,
        "x1": rect.x2,
        "y1": rect.y2,
        "line": {"color": color, "width": 1},
        "fillcolor": color,
        "opacity": opacity,
        "layer": "below",
    }


def _component_shapes(components: Sequence[List[Rectangle]], colors: List[str]) -> List[Dict]:
    shapes = []
    for idx, rects in enumerate(components):
        color = colors[idx % len(colors)]
        for rect in rects:
            shapes.append(_rect_shape(rect, color, 0.25))
    return shapes


def _rectangle_shapes(rectangles: Sequence[Rectangle]) -> List[Dict]:
    shapes = []
    for rect in rectangles:
        shapes.append(
            {
                "type": "rect",
                "xref": "x",
                "yref": "y",
                "x0": rect.x,
                "y0": rect.y,
                "x1": rect.x2,
                "y1": rect.y2,
                "line": {"color": "#0f172a", "width": 1},
                "fillcolor": "rgba(0,0,0,0)",
            }
        )
    return shapes


def _color_palette() -> List[str]:
    return [
        "rgba(16, 185, 129, 0.4)",
        "rgba(59, 130, 246, 0.4)",
        "rgba(236, 72, 153, 0.4)",
        "rgba(249, 115, 22, 0.4)",
        "rgba(139, 92, 246, 0.4)",
        "rgba(5, 150, 105, 0.4)",
    ]


def build_animation(rectangles, components, states, accent_color: str, frame_duration_ms: int = 250):
    if not rectangles:
        return {"plot_html": "", "grid_html": ""}

    palette = _color_palette()
    base_fig = go.Figure()
    base_fig.update_layout(
        shapes=_component_shapes(components, palette) + _rectangle_shapes(rectangles),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    hits_x: List[float] = []
    hits_y: List[float] = []
    misses_x: List[float] = []
    misses_y: List[float] = []

    base_fig.add_trace(
        go.Scatter(
            x=[],
            y=[],
            mode="markers",
            marker=dict(color="rgba(34,197,94,0.9)", size=7),
            name="Hit",
        )
    )
    base_fig.add_trace(
        go.Scatter(
            x=[],
            y=[],
            mode="markers",
            marker=dict(color="rgba(248,113,113,0.9)", size=7),
            name="Miss",
        )
    )
    base_fig.add_trace(
        go.Scatter(
            x=[(rect.x + rect.x2) / 2 for rect in rectangles],
            y=[(rect.y + rect.y2) / 2 for rect in rectangles],
            mode="text",
            text=[f"R{i+1}" for i in range(len(rectangles))],
            textfont=dict(color="#0f172a"),
            showlegend=False,
        )
    )

    frames = []
    slider_steps = []
    for state in states:
        px, py = state["point"]
        if state["is_hit"]:
            hits_x.append(px)
            hits_y.append(py)
        else:
            misses_x.append(px)
            misses_y.append(py)

        frame_name = f"{state['step']}"
        frames.append(
            go.Frame(
                data=[
                    go.Scatter(x=hits_x.copy(), y=hits_y.copy(), mode="markers"),
                    go.Scatter(x=misses_x.copy(), y=misses_y.copy(), mode="markers"),
                ],
                name=frame_name,
                traces=[0, 1],
            )
        )
        slider_steps.append(
            dict(
                method="animate",
                args=[[frame_name], {"frame": {"duration": frame_duration_ms, "redraw": True}, "mode": "immediate"}],
                label=frame_name,
                value=frame_name,
            )
        )

    base_fig.frames = frames
    base_fig.update_layout(
        title="Monte Carlo union area sampling",
        xaxis=dict(scaleanchor="y", scaleratio=1,  range=[0, max(rect.x2 for rect in rectangles) * 1.05]),
        yaxis=dict(range=[0, max(rect.y2 for rect in rectangles) * 1.05]),
        margin=dict(l=10, r=10, t=60, b=10),
        height=620,
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                pad=dict(r=10, t=10),
                 x=0.0,
                xanchor="left",
                y=-0.25,
                bgcolor="#0d6efd",
                bordercolor="#0d6efd",
                font=dict(color="#ffffff", family="system-ui, -apple-system"),
                active=-1,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": frame_duration_ms, "redraw": True},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                active=0,
                pad=dict(t=10),
                currentvalue=dict(prefix="Sample "),
                steps=slider_steps,
            )
        ],
        showlegend=True,
    )

    grid_html = _build_grid(rectangles, components, states, palette, frame_duration_ms)

    plot_html = to_html(
        base_fig,
        full_html=False,
        include_plotlyjs="cdn",
        auto_play=False,
        config={"displayModeBar": False},
        div_id="union-main-plot",
    )
    return {"plot_html": plot_html, "grid_html": grid_html}


def _build_grid(rectangles, components, states, palette, frame_duration_ms):
    if not rectangles:
        return ""

    cols = 3
    rows = (len(rectangles) + cols - 1) // cols
    max_width = max(rect.width for rect in rectangles)
    max_height = max(rect.height for rect in rectangles)
    titles = [f"R{i+1}" for i in range(len(rectangles))]
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=titles + [""] * (rows * cols - len(rectangles)),
        vertical_spacing=0.08,
        horizontal_spacing=0.05,
    )

    hits = [[[], []] for _ in rectangles]
    misses = [[[], []] for _ in rectangles]
    trace_order = []
    for i, rect in enumerate(rectangles):
        row = i // cols + 1
        col = i % cols + 1
        fig.add_shape(
            type="rect",
            x0=0,
            y0=0,
            x1=rect.width,
            y1=rect.height,
            line=dict(color="#0f172a", width=1),
            fillcolor="rgba(0,0,0,0)",
            row=row,
            col=col,
        )
        for cell in components[i]:
            color = palette[i % len(palette)]
            fig.add_shape(
                type="rect",
                x0=cell.x - rect.x,
                y0=cell.y - rect.y,
                x1=cell.x2 - rect.x,
                y1=cell.y2 - rect.y,
                fillcolor=color,
                opacity=0.4,
                line=dict(width=0),
                row=row,
                col=col,
            )
        fig.add_trace(
            go.Scatter(
                x=[],
                y=[],
                mode="markers",
                marker=dict(color="rgba(16,185,129,0.9)", size=5),
                showlegend=False,
            ),
            row=row,
            col=col,
        )
        hit_idx = len(fig.data) - 1
        fig.add_trace(
            go.Scatter(
                x=[],
                y=[],
                mode="markers",
                marker=dict(color="rgba(239,68,68,0.9)", size=5),
                showlegend=False,
            ),
            row=row,
            col=col,
        )
        miss_idx = len(fig.data) - 1
        trace_order.append((hit_idx, miss_idx))
        fig.update_xaxes(
            range=[0, max_width],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            row=row,
            col=col,
        )
        axis_idx = (row - 1) * cols + col
        xref = "x" if axis_idx == 1 else f"x{axis_idx}"
        fig.update_yaxes(
            range=[0, max_height],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            scaleanchor=xref,
            scaleratio=1,
            row=row,
            col=col,
        )

    if not states:
        fig.update_layout(
            height=260 * rows,
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        return to_html(fig, full_html=False, include_plotlyjs=False, div_id="union-grid-plot")

    frames = []
    for state in states:
        idx = state["rect_index"]
        rect = rectangles[idx]
        px, py = state["point"]
        local_x = px - rect.x
        local_y = py - rect.y
        target = hits[idx] if state["is_hit"] else misses[idx]
        target[0].append(local_x)
        target[1].append(local_y)

        frame_data = []
        for i in range(len(rectangles)):
            frame_data.append(
                go.Scatter(
                    x=hits[i][0],
                    y=hits[i][1],
                    mode="markers",
                )
            )
            frame_data.append(
                go.Scatter(
                    x=misses[i][0],
                    y=misses[i][1],
                    mode="markers",
                )
            )
        frame_name = f"{state['step']}"
        frames.append(
            go.Frame(
                data=frame_data,
                name=frame_name,
                traces=[idx for pair in trace_order for idx in pair],
            )
        )

    fig.frames = frames
    fig.update_layout(
        height=230 * rows,
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return to_html(
        fig,
        full_html=False,
        include_plotlyjs=False,
        auto_play=False,
        config={"displayModeBar": False},
        div_id="union-grid-plot",
    )
