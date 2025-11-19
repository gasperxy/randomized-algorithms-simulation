from __future__ import annotations

import math
from typing import Dict, List, Sequence

import plotly.graph_objects as go
from plotly.io import to_html


def _fallback_positions(graph) -> Dict[int, List[float]]:
    n = max(1, graph.number_of_nodes())
    return {
        node: [math.cos(2 * math.pi * idx / n), math.sin(2 * math.pi * idx / n)]
        for idx, node in enumerate(graph.nodes())
    }


def _ensure_positions(graph, positions):
    lookup = dict(positions)
    if not lookup or len(lookup) < graph.number_of_nodes():
        fallback = _fallback_positions(graph)
        fallback.update(lookup)
        lookup = fallback
    return lookup


def _edge_coordinates(edges, positions):
    edge_x: List[float] = []
    edge_y: List[float] = []
    for u, v in edges:
        x0, y0 = positions[u]
        x1, y1 = positions[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    return edge_x, edge_y


def _node_colors(graph, node_order, accent_color):
    return [accent_color if graph.degree(node) > 0 else "#e5e7eb" for node in node_order]


def build_animation(states: Sequence[Dict], positions_per_state: Sequence[Dict], accent_color, frame_duration_ms: int):
    """Render the edge-addition animation and attach slider metadata."""
    if not states:
        return {"plot_html": ""}

    positions = positions_per_state or [{} for _ in states]

    def get_positions(index: int):
        raw = positions[min(index, len(positions) - 1)]
        return _ensure_positions(states[index]["graph"], raw)

    initial_positions = get_positions(0)
    node_order = list(states[0]["graph"].nodes())
    node_x = [initial_positions[node][0] for node in node_order]
    node_y = [initial_positions[node][1] for node in node_order]
    node_text = [f"Node {node}" for node in node_order]

    initial_edges_x, initial_edges_y = _edge_coordinates(
        list(states[0]["graph"].edges()), initial_positions
    )
    initial_node_colors = _node_colors(states[0]["graph"], node_order, accent_color)
    initial_new_edge_x, initial_new_edge_y = _edge_coordinates(
        [states[0]["new_edge"]] if states[0].get("new_edge") else [], initial_positions
    )

    fig = go.Figure(
        data=[
            go.Scatter(
                x=initial_edges_x,
                y=initial_edges_y,
                mode="lines",
                line=dict(width=1.5, color=accent_color),
                hoverinfo="none",
            ),
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers",
                hoverinfo="text",
                text=node_text,
                marker=dict(size=7, color=initial_node_colors, line=dict(width=1, color="#111827")),
            ),
            go.Scatter(
                x=initial_new_edge_x,
                y=initial_new_edge_y,
                mode="lines",
                line=dict(width=3, color=accent_color),
                hoverinfo="none",
            ),
        ]
    )

    frames = []
    slider_steps = []
    for index, state in enumerate(states):
        current_positions = get_positions(index)
        edges_x, edges_y = _edge_coordinates(list(state["graph"].edges()), current_positions)
        node_colors = _node_colors(state["graph"], node_order, accent_color)
        node_x = [current_positions[node][0] for node in node_order]
        node_y = [current_positions[node][1] for node in node_order]
        node_text = [f"Node {node}<br>Degree {state['graph'].degree(node)}" for node in node_order]
        new_edge_coords = (
            _edge_coordinates([state["new_edge"]], current_positions)
            if state.get("new_edge")
            else ([], [])
        )
        frame_name = f"m={state['edges_used']}"
        frames.append(
            go.Frame(
                data=[
                    dict(x=edges_x, y=edges_y),
                    dict(x=node_x, y=node_y, text=node_text, marker=dict(color=node_colors)),
                    dict(x=new_edge_coords[0], y=new_edge_coords[1]),
                ],
                name=frame_name,
                traces=[0, 1, 2],
            )
        )
        slider_steps.append(
            dict(
                method="animate",
                args=[[frame_name], {"frame": {"duration": frame_duration_ms, "redraw": True}, "mode": "immediate"}],
                label=f"{state['edges_used']}",
            )
        )

    fig.frames = frames
    fig.update_layout(
        template="plotly_white",
        title="Erdős–Rényi G(n, m) Edge Process",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        margin=dict(l=10, r=10, t=80, b=10),
        height=620,
        hovermode="closest",
        transition=dict(duration=0),
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
                                "mode": "immediate",
                                "fromcurrent": True,
                                "transition": {"duration": 0},
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
                currentvalue=dict(prefix="Edges added: "),
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
