from __future__ import annotations

import math
from typing import Dict, List, Sequence

import plotly.graph_objects as go
from plotly.io import to_html

from ..common import graph_services as gs


def _fallback_positions(graph) -> Dict[int, List[float]]:
    positions = {}
    n = max(1, graph.number_of_nodes())
    for idx, node in enumerate(graph.nodes()):
        angle = (2 * math.pi * idx) / n
        positions[node] = [math.cos(angle), math.sin(angle)]
    return positions


def _build_edge_trace(edges, lookup, color, width):
    if not edges:
        return go.Scatter(
            x=[],
            y=[],
            line=dict(width=width, color=color),
            hoverinfo="none",
            mode="lines",
        )

    edge_x: List[float] = []
    edge_y: List[float] = []

    for edge in edges:
        x0, y0 = lookup[edge[0]]
        x1, y1 = lookup[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    return go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=width, color=color),
        hoverinfo="none",
        mode="lines",
    )


def _state_traces(graph, positions, accent_color: str):
    lookup = dict(positions)
    if not lookup or len(lookup) < graph.number_of_nodes():
        fallback = _fallback_positions(graph)
        fallback.update(lookup)
        lookup = fallback

    nodes_x = []
    nodes_y = []
    text = []
    colors = []
    comps = gs.get_connected_components(graph)
    largest = max(comps, key=len) if comps else set()

    largest_edges = []
    other_edges = []
    for edge in graph.edges():
        if edge[0] in largest and edge[1] in largest:
            largest_edges.append(edge)
        else:
            other_edges.append(edge)

    other_trace = _build_edge_trace(other_edges, lookup, "#94a3b8", 1.5)
    largest_trace = _build_edge_trace(largest_edges, lookup, accent_color, 2.5)

    for node in graph.nodes():
        x, y = lookup[node]
        nodes_x.append(x)
        nodes_y.append(y)
        degree = graph.degree(node)
        component_index = next(
            (idx for idx, comp in enumerate(comps) if node in comp), -1
        )
        text.append(f"Node {node}<br>Degree {degree}<br>Component {component_index}")
        colors.append(accent_color if node in largest else "#e5e7eb")

    node_trace = go.Scatter(
        x=nodes_x,
        y=nodes_y,
        mode="markers",
        hoverinfo="text",
        text=text,
        marker=dict(
            size=7,
            color=colors,
            line=dict(width=1, color="#111827"),
        ),
    )
    return (other_trace, largest_trace), node_trace


def build_animation(
    states: Sequence[Dict],
    positions_per_state: Sequence[Dict[int, List[float]]],
    accent: str,
    frame_duration_ms: int = 500,
):
    if not states:
        return {"plot_html": ""}

    if not positions_per_state:
        positions_per_state = [{} for _ in states]

    base_edges, base_nodes = _state_traces(states[0]["graph"], positions_per_state[0], accent)

    frames = []
    slider_steps = []
    for index, state in enumerate(states):
        positions = positions_per_state[min(index, len(positions_per_state) - 1)]
        edge_traces, nodes = _state_traces(state["graph"], positions, accent)
        frame_name = f"p={state['p']:.3f}"
        frames.append(go.Frame(data=[*edge_traces, nodes], name=frame_name))
        slider_steps.append(
            dict(
                method="animate",
                args=[[frame_name], {"frame": {"duration": frame_duration_ms, "redraw": False}, "mode": "immediate"}],
                label=f"{state['p']:.3f}",
            )
        )

    fig = go.Figure(data=[*base_edges, base_nodes], frames=frames)
    fig.update_layout(
        template="plotly_white",
        title="Erdős–Rényi Phase Transition",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="closest",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                pad=dict(r=10, t=10),
                x=0.02,
                xanchor="left",
                y=-0.8,
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
                                "mode": "immediate",
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
                pad=dict(t=70),
                currentvalue=dict(prefix="p = "),
                bgcolor="#f8f9fa",
                bordercolor="#dee2e6",
                activebgcolor="#0d6efd",
                font=dict(color="#0f172a", family="system-ui, -apple-system"),
                steps=slider_steps,
            )
        ],
    )

    plot_html = to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn",
        auto_play=False,
        config={"displayModeBar": False},
    )
    return {"plot_html": plot_html}
