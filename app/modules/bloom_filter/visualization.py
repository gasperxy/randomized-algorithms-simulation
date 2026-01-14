from __future__ import annotations

import math
from typing import Dict, List, Sequence

import plotly.graph_objects as go
from plotly.io import to_html


def _bit_colors(bits: Sequence[int]) -> List[str]:
    return ["#0f172a" if bit else "#e2e8f0" for bit in bits]


def build_bit_animation(states: Sequence[Dict], m: int, accent_color: str, frame_duration_ms: int) -> Dict:
    if not states:
        return {"plot_html": ""}

    xs = list(range(m))
    ys = [0.6] * m
    first_state = states[0]
    highlight_x = first_state["indices"]
    highlight_y = [0.6] * len(highlight_x)

    fig = go.Figure(
        data=[
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers",
                marker=dict(size=16, color=_bit_colors(first_state["bits"]), symbol="square"),
                hovertemplate="Index %{x}<extra></extra>",
                showlegend=False,
            ),
            go.Scatter(
                x=highlight_x,
                y=highlight_y,
                mode="markers",
                marker=dict(size=20, color=accent_color, symbol="square"),
                hoverinfo="skip",
                showlegend=False,
            ),
        ],
        frames=[],
    )

    frames = []
    slider_steps = []
    for state in states:
        frame_name = str(state["step"])
        frames.append(
            go.Frame(
                data=[
                    go.Scatter(
                        x=xs,
                        y=ys,
                        mode="markers",
                        marker=dict(size=16, color=_bit_colors(state["bits"]), symbol="square"),
                    ),
                    go.Scatter(
                        x=state["indices"],
                        y=[0.6] * len(state["indices"]),
                        mode="markers",
                        marker=dict(size=20, color=accent_color, symbol="square"),
                    ),
                ],
                name=frame_name,
                layout=dict(title=f"Insert step {state['step']} (key {state['key']})"),
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
        title="Bloom filter insertions",
        xaxis=dict(range=[-1, m], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 1.6], showgrid=False, zeroline=False, showticklabels=False),
        height=240,
        margin=dict(l=20, r=20, t=50, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                pad=dict(r=10, t=10),
                x=0.0,
                xanchor="left",
                y=-1.2,
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


def build_false_positive_chart(states: Sequence[Dict], m: int, k: int, accent_color: str) -> Dict:
    if not states:
        return {"plot_html": ""}

    steps = [state["step"] + 1 for state in states]
    empirical = [state["false_positive_rate"] for state in states]
    theoretical = [(1 - math.exp(-(k * n) / m)) ** k for n in steps]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=steps,
                y=empirical,
                mode="lines+markers",
                line=dict(color=accent_color, width=3),
                marker=dict(size=7, color=accent_color),
                name="Empirical",
            ),
            go.Scatter(
                x=steps,
                y=theoretical,
                mode="lines",
                line=dict(color="#94a3b8", width=2, dash="dash"),
                name="Theoretical",
            ),
        ]
    )
    fig.update_layout(
        title="False-positive rate over time",
        xaxis=dict(title="Inserted items"),
        yaxis=dict(title="False-positive rate", rangemode="tozero"),
        height=320,
        margin=dict(l=40, r=20, t=50, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
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
