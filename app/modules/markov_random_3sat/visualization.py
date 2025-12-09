from __future__ import annotations

from typing import Iterable, Sequence

import plotly.graph_objects as go
from plotly.io import to_html


def build_clause_heatmap(
    clause_satisfaction: Sequence[Sequence[int]] | Sequence[int],
    clause_labels: Iterable[str],
    accent: str,
    clause_count: int | None = None,
    restart_boundaries: Sequence[int] | None = None,
    condensed: bool = False,
):
    if not clause_satisfaction:
        return {"plot_html": ""}

    first = clause_satisfaction[0]
    if isinstance(first, (int, float)):
        satisfied_counts = list(clause_satisfaction)  # type: ignore[arg-type]
        clause_count = clause_count or max(satisfied_counts + [0])
    else:
        clause_count = clause_count or len(first)
        satisfied_counts = [sum(row) for row in clause_satisfaction]  # type: ignore[arg-type]
    steps = len(satisfied_counts)
    unsatisfied_counts = [clause_count - count for count in satisfied_counts]

    x_values = list(range(1, steps + 1)) if condensed else list(range(steps))
    bars = [
        go.Bar(
            x=x_values,
            y=satisfied_counts,
            name="Satisfied",
            marker_color="#86efac",
            hovertemplate="Step %{x}<br>Satisfied %{y}<extra></extra>",
            offsetgroup="s",
        ),
        go.Bar(
            x=x_values,
            y=unsatisfied_counts,
            name="Unsatisfied",
            marker_color="#fca5a5",
            hovertemplate="Step %{x}<br>Unsatisfied %{y}<extra></extra>",
            offsetgroup="u",
        ),
    ]
    restart_markers = []
    if restart_boundaries:
        marker_x = [b for b in restart_boundaries if 0 <= b < steps]
        if marker_x:
            restart_markers.append(
                go.Scatter(
                    x=marker_x,
                    y=[clause_count] * len(marker_x),
                    mode="markers",
                    marker=dict(symbol="triangle-down", size=8, color="#0f172a"),
                    hoverinfo="text",
                    hovertext=[f"Restart {idx + 1}" for idx, _ in enumerate(marker_x)],
                    showlegend=False,
                )
            )

    fig = go.Figure(data=[*bars, *restart_markers])
    shapes = []
    if restart_boundaries:
        for boundary in restart_boundaries:
            if boundary <= 0 or boundary >= steps:
                continue
            shapes.append(
                dict(
                    type="line",
                    x0=boundary - 0.5,
                    x1=boundary - 0.5,
                    y0=0,
                    y1=clause_count,
                    line=dict(color="#cbd5e1", dash="dot", width=1),
                    layer="below",
                )
            )
    fig.update_layout(
        template="plotly_white",
        height=340,
        title="Clause satisfaction over time",
        barmode="stack",
        bargap=0,
        bargroupgap=0,
        xaxis=dict(title="Restart" if condensed else "Step", showgrid=False, zeroline=False),
        yaxis=dict(title="# Clauses", automargin=True, rangemode="tozero", showgrid=False, zeroline=False),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        shapes=shapes,
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
