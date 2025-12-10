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
        yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-1, 1], showline=False),
        height=320,
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
    clause_satisfaction: Sequence[Sequence[int]] | Sequence[int],
    clause_labels: Iterable[str],
    accent: str,
    clause_count: int | None = None,
):
    if not clause_satisfaction:
        return {"plot_html": ""}

    first = clause_satisfaction[0]
    if isinstance(first, (int, float)):
        satisfied_counts = list(clause_satisfaction)  # type: ignore[arg-type]
        clause_count = clause_count or max(satisfied_counts + [0])
    else:
        steps = len(clause_satisfaction)
        clause_count = clause_count or len(first)
        satisfied_counts = [sum(row) for row in clause_satisfaction]  # type: ignore[arg-type]
    steps = len(satisfied_counts)
    unsatisfied_counts = [clause_count - count for count in satisfied_counts]

    bars = [
        go.Bar(
            x=list(range(steps)),
            y=satisfied_counts,
            name="Satisfied",
            marker_color="#86efac",
            offsetgroup="s",
            hovertemplate="Step %{x}<br>Satisfied %{y}<extra></extra>",
        ),
        go.Bar(
            x=list(range(steps)),
            y=unsatisfied_counts,
            name="Unsatisfied",
            marker_color="#fca5a5",
            offsetgroup="u",
            hovertemplate="Step %{x}<br>Unsatisfied %{y}<extra></extra>",
        ),
    ]
    fig = go.Figure(data=bars)
    fig.update_layout(
        template="plotly_white",
        height=340,
        title="Clause satisfaction over time",
        barmode="stack",
        bargap=0,
        bargroupgap=0,
        xaxis=dict(title="Step", showgrid=False, zeroline=False),
        yaxis=dict(title="# Clauses", automargin=True, rangemode="tozero", showgrid=False, zeroline=False),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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
