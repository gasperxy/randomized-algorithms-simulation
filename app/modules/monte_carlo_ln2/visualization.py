from __future__ import annotations

from typing import Dict, List

import plotly.graph_objects as go
from plotly.io import to_html


def build_chart(states: List[Dict], true_value: float, accent_color: str):
    """Plot cumulative estimates alongside the true ln(2)."""
    if not states:
        return {"plot_html": ""}

    x = [state["step"] for state in states]
    estimates = [state["estimate"] for state in states]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=estimates,
            mode="lines",
            line=dict(color=accent_color, width=2),
            name="Estimate",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[x[0], x[-1]],
            y=[true_value, true_value],
            mode="lines",
            line=dict(color="#0f172a", width=1, dash="dash"),
            name="ln(2)",
        )
    )

    fig.update_layout(
        title="Monte Carlo estimate of ln(2)",
        xaxis_title="Samples",
        yaxis_title="Estimate",
        template="plotly_white",
        margin=dict(l=40, r=20, t=60, b=40),
        height=500,
    )

    return {
        "plot_html": to_html(fig, full_html=False, include_plotlyjs="cdn"),
    }
