from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

import plotly.graph_objects as go
from plotly.io import to_html


def build_state_animation(
    states: Sequence[Dict],
    clause_count: int,
    accent: str,
    frame_duration_ms: int = 400,
):
    if not states:
        return {"plot_html": ""}

    positions = list(range(clause_count + 1))
    base_nodes = go.Scatter(
        x=positions,
        y=[0] * len(positions),
        mode="markers+text",
        text=[str(value) for value in positions],
        textposition="top center",
        marker=dict(
            color="#cbd5f5",
            size=14,
            line=dict(width=1, color="#1f2937"),
        ),
        hoverinfo="text",
        hovertext=[f"{value} satisfied clauses" for value in positions],
    )

    def highlight_trace(state):
        trend = state.get("trend")
        colors = {
            "improved": accent,
            "regressed": "#f97316",
            "steady": "#64748b",
            "initial": accent,
        }
        color = colors.get(trend, accent)
        return go.Scatter(
            x=[state["satisfied_count"]],
            y=[0],
            mode="markers",
            marker=dict(
                color=color,
                size=28,
                line=dict(width=2, color="#0f172a"),
            ),
            hoverinfo="text",
            hovertext=[
                f"Step {state['step']}<br>Satisfied {state['satisfied_count']} / {clause_count}"
            ],
        )

    frames = []
    slider_steps = []
    for state in states:
        frame_name = f"step-{state['step']}"
        frames.append(go.Frame(data=[base_nodes, highlight_trace(state)], name=frame_name))
        slider_steps.append(
            dict(
                method="animate",
                args=[[frame_name], {"frame": {"duration": frame_duration_ms, "redraw": True}, "mode": "immediate"}],
                label=str(state["step"]),
            )
        )

    fig = go.Figure(data=[base_nodes, highlight_trace(states[0])], frames=frames)
    fig.update_layout(
        template="plotly_white",
        title="Satisfied Clauses Markov Chain",
        showlegend=False,
        xaxis=dict(
            title="Satisfied clauses",
            tickmode="array",
            tickvals=positions,
            range=[-0.5, clause_count + 0.5],
        ),
        yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-1, 1]),
        height=380,
        margin=dict(l=20, r=20, t=60, b=20),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                pad=dict(r=10, t=10),
                x=0.0,
                xanchor="left",
                y=-0.3,
                bgcolor="#0d6efd",
                bordercolor="#0d6efd",
                font=dict(color="#ffffff"),
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
                        args=[[None], {"frame": {"duration": 0, "redraw": False}}],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                active=0,
                pad=dict(t=20),
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


def build_clause_heatmap(
    clause_satisfaction: Sequence[Sequence[int]],
    clause_labels: Iterable[str],
    accent: str,
):
    if not clause_satisfaction:
        return {"plot_html": ""}

    steps = len(clause_satisfaction)
    clause_count = len(clause_satisfaction[0])
    # Transpose to clause-major ordering.
    matrix = [[row[idx] for row in clause_satisfaction] for idx in range(clause_count)]
    labels = list(clause_labels)
    if len(labels) < clause_count:
        labels = [f"C{idx + 1}" for idx in range(clause_count)]

    heatmap = go.Heatmap(
        z=matrix,
        x=list(range(steps)),
        y=labels,
        colorscale=[(0, "#fee2e2"), (1, accent)],
        showscale=False,
    )
    fig = go.Figure(data=[heatmap])
    fig.update_layout(
        template="plotly_white",
        height=400,
        title="Clause satisfaction over time",
        xaxis=dict(title="Step"),
        yaxis=dict(title="Clause", automargin=True),
        margin=dict(l=50, r=20, t=50, b=40),
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
