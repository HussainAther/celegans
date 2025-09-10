import json 
import base64
import io
import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_cytoscape as cyto
from dash_extensions.enrich import DashProxy, MultiplexerTransform
from dash.exceptions import PreventUpdate
import networkx as nx
import pandas as pd
import numpy as np
from dash_extensions import Download
from dash_extensions.snippets import send_string

# Sample lineage tree
G = nx.DiGraph()
G.add_edges_from([
    ("Zygote", "AB"),
    ("Zygote", "P1"),
    ("AB", "ABa"),
    ("AB", "ABp"),
    ("P1", "EMS"),
    ("P1", "P2"),
    ("EMS", "MS"),
    ("EMS", "E"),
    ("P2", "C"),
    ("P2", "P3"),
    ("P3", "D"),
    ("P3", "P4"),
    ("P4", "Z2"),
    ("P4", "Z3")
])

# Add sample metadata
fates = {
    "ABa": "neuron", "ABp": "neuron", "EMS": "gut", "P2": "germline",
    "MS": "muscle", "E": "gut", "C": "muscle", "P3": "germline",
    "D": "muscle", "P4": "germline", "Z2": "germline", "Z3": "germline"
}

expression_df = pd.DataFrame([
    {"cell": "ABa", "hlh-1": 0.8, "end-1": 0.2, "pal-1": 0.1},
    {"cell": "ABp", "hlh-1": 0.6, "end-1": 0.3, "pal-1": 0.2},
    {"cell": "EMS", "hlh-1": 0.3, "end-1": 0.9, "pal-1": 0.2},
    {"cell": "P2", "hlh-1": 0.1, "end-1": 0.2, "pal-1": 0.8},
])
expression_df.set_index("cell", inplace=True)

for node in G.nodes:
    G.nodes[node]["fate"] = fates.get(node, "undiff")
    G.nodes[node]["expression"] = expression_df.loc[node].to_dict() if node in expression_df.index else {}

# Map fates to colors
fate_colors = {
    "neuron": "#1f77b4",
    "muscle": "#2ca02c",
    "gut": "#ff7f0e",
    "germline": "#d62728",
    "undiff": "#bbbbbb"
}

def nx_to_cytoscape(G, gene=None):
    nodes = []
    edges = []
    for node in G.nodes:
        meta = G.nodes[node]
        expr = meta.get("expression", {})
        color = fate_colors.get(meta.get("fate", "undiff"), "#bbbbbb")
        if gene and gene in expr:
            val = expr[gene]
            color = f"rgba(255, 0, 0, {val})"  # red intensity
        nodes.append({"data": {"id": node, "label": node}, "style": {"background-color": color}})
    for u, v in G.edges:
        edges.append({"data": {"source": u, "target": v}})
    return nodes + edges

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])

app.layout = html.Div([
    html.H1("🧬 C. elegans Lineage Explorer"),
    html.Div([
        html.Label("Gene Expression Overlay:"),
        dcc.Dropdown(
            id="gene-selector",
            options=[{"label": gene, "value": gene} for gene in expression_df.columns],
            value=None,
            placeholder="Select a gene to color nodes",
            style={"width": "300px"}
        ),
        html.Br(),
        html.Label("Search Cell by Name:"),
        dcc.Input(id="cell-search", type="text", placeholder="e.g., EMS", debounce=True),
        html.Br(),
        html.Label("Layout:"),
        dcc.Dropdown(
            id="layout-selector",
            options=[
                {"label": "Tree (Breadthfirst)", "value": "breadthfirst"},
                {"label": "Radial (Circle)", "value": "circle"}
            ],
            value="breadthfirst",
            style={"width": "300px"}
        ),
        html.Br(),
        html.Label("Theme:"),
        dcc.Dropdown(
            id="theme-selector",
            options=[
                {"label": "Light", "value": "light"},
                {"label": "Dark", "value": "dark"}
            ],
            value="light",
            style={"width": "200px"}
        ),
        html.Div(id="hover-tooltip", style={"marginTop": "10px"})
    ]),
    cyto.Cytoscape(
        id="cytoscape-lineage",
        elements=nx_to_cytoscape(G),
        layout={"name": "breadthfirst"},
        style={"width": "100%", "height": "600px"},
    ),
    html.Div([
        html.Button("⬇️ Download JSON", id="btn-download-json"),
        Download(id="download-json"),
        html.Br(), html.Br(),
        html.Button("📷 Download PNG", id="btn-download-png", n_clicks=0),
        dcc.Store(id="trigger-png"),
        html.Br(), html.Br(),
        html.Button("🖼️ Download SVG", id="btn-download-svg", n_clicks=0),
        dcc.Store(id="trigger-svg"),
    ])
])

@app.callback(
    Output("cytoscape-lineage", "elements"),
    Input("gene-selector", "value")
)
def update_elements(gene):
    return nx_to_cytoscape(G, gene)

@app.callback(
    Output("hover-tooltip", "children"),
    Input("cytoscape-lineage", "mouseoverNodeData"),
    Input("gene-selector", "value")
)
def show_hover(node_data, gene):
    if not node_data:
        return "Hover over a node."
    if gene:
        val = G.nodes[node_data["id"]].get("expression", {}).get(gene, None)
        if val is not None:
            return f"{node_data['id']} – {gene}: {val:.2f}"
    return f"{node_data['id']}"

@app.callback(
    Output("cytoscape-lineage", "zoom"),
    Output("cytoscape-lineage", "pan"),
    Input("cell-search", "value"),
    State("cytoscape-lineage", "elements")
)
def center_on_node(cell_name, elements):
    if not cell_name:
        raise PreventUpdate
    for el in elements:
        if el.get("data", {}).get("id") == cell_name:
            return 2, {"x": 0, "y": 0}
    return dash.no_update, dash.no_update

@app.callback(
    Output("cytoscape-lineage", "layout"),
    Input("layout-selector", "value")
)
def update_layout(layout_name):
    return {"name": layout_name}

@app.callback(
    Output("cytoscape-lineage", "stylesheet"),
    Input("theme-selector", "value")
)
def update_theme(theme):
    base_stylesheet = [
        {"selector": "node", "style": {"label": "data(label)"}}
    ]
    if theme == "dark":
        return base_stylesheet + [
            {"selector": "node", "style": {"color": "white", "background-color": "#888"}},
            {"selector": "edge", "style": {"line-color": "#999"}},
            {"selector": "core", "style": {"background-color": "#111"}}
        ]
    else:
        return base_stylesheet + [
            {"selector": "node", "style": {"color": "black", "background-color": "#ccc"}},
            {"selector": "edge", "style": {"line-color": "#666"}},
            {"selector": "core", "style": {"background-color": "#fff"}}
        ]

@app.callback(
    Output("download-json", "data"),
    Input("btn-download-json", "n_clicks"),
    prevent_initial_call=True
)
def download_json(n):
    lineage_json = nx.node_link_data(G)
    return send_string(json.dumps(lineage_json, indent=2), "lineage.json")

app.clientside_callback(
    """
    function(n_clicks) {
        let cy = window.cyto_cytoscape_lineage;
        if (cy && n_clicks > 0) {
            let pngContent = cy.png({ full: true, scale: 2 });
            let a = document.createElement("a");
            a.href = pngContent;
            a.download = "lineage_tree.png";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
        return "";
    }
    """,
    Output("trigger-png", "data"),
    Input("btn-download-png", "n_clicks")
)

app.clientside_callback(
    """
    function(n_clicks) {
        let cy = window.cyto_cytoscape_lineage;
        if (cy && n_clicks > 0) {
            let svgContent = cy.svg({ full: true, scale: 1 });
            let blob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' });
            let url = URL.createObjectURL(blob);
            let a = document.createElement("a");
            a.href = url;
            a.download = "lineage_tree.svg";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        return "";
    }
    """,
    Output("trigger-svg", "data"),
    Input("btn-download-svg", "n_clicks")
)

if __name__ == "__main__":
    app.run_server(debug=True)

