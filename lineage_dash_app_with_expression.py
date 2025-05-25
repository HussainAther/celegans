import dash
from dash import html, dcc, Input, Output
import dash_cytoscape as cyto
import networkx as nx
import pandas as pd
import json
from dash_extensions import Download
from dash_extensions.snippets import send_string

from build_initial_lineage import build_lineage_tree, add_random_syncytial_cells
from fate_utils import assign_cell_fates

# Expression data
expression_df = pd.DataFrame([
    {"cell": "ABa", "hlh-1": 0.89, "end-1": 0.85, "pal-1": 0.81},
    {"cell": "ABp", "hlh-1": 0.39, "end-1": 0.57, "pal-1": 0.23},
    {"cell": "EMS", "hlh-1": 0.98, "end-1": 0.08, "pal-1": 0.23},
    {"cell": "P2",  "hlh-1": 0.37, "end-1": 0.30, "pal-1": 0.03},
    {"cell": "MS",  "hlh-1": 0.40, "end-1": 0.89, "pal-1": 0.09},
    {"cell": "E",   "hlh-1": 0.50, "end-1": 0.93, "pal-1": 0.85},
    {"cell": "C",   "hlh-1": 0.59, "end-1": 0.08, "pal-1": 0.75},
    {"cell": "P3",  "hlh-1": 0.34, "end-1": 0.91, "pal-1": 0.80},
    {"cell": "D",   "hlh-1": 0.96, "end-1": 0.68, "pal-1": 0.32},
    {"cell": "P4",  "hlh-1": 0.40, "end-1": 0.82, "pal-1": 0.32},
    {"cell": "Z2",  "hlh-1": 0.42, "end-1": 0.47, "pal-1": 0.22},
    {"cell": "Z3",  "hlh-1": 0.11, "end-1": 0.65, "pal-1": 0.34}
])

FATE_COLORS = {
    "neuron": "purple", "muscle": "red", "skin": "tan", "gut": "green",
    "germline": "blue", "progenitor": "lightblue", "undifferentiated": "gray", None: "lightgray"
}

def get_expression_color(val):
    if val is None:
        return "lightgray"
    r = int(255 * (1 - val))
    g = int(255 * (1 - abs(0.5 - val)))
    b = int(255 * val)
    return f"rgb({r},{g},{b})"

G = build_lineage_tree()
add_random_syncytial_cells(G, num_cells=10)
assign_cell_fates(G)

for _, row in expression_df.iterrows():
    if row["cell"] in G.nodes:
        G.nodes[row["cell"]]["expression"] = row.drop("cell").to_dict()

def nx_to_cytoscape(G, time_cutoff=None, fate_filter=None, gene=None):
    elements = []
    for node in G.nodes:
        div_time = G.nodes[node].get("division_time", 999)
        if time_cutoff is not None and div_time > time_cutoff:
            continue
        if fate_filter and G.nodes[node].get("fate") != fate_filter:
            continue

        sync = G.nodes[node].get("syncytial", False)
        shape = "rectangle" if sync else "ellipse"

        if gene:
            expr_val = G.nodes[node].get("expression", {}).get(gene)
            color = get_expression_color(expr_val)
        else:
            fate = G.nodes[node].get("fate", "unknown")
            color = FATE_COLORS.get(fate, "lightgray")

        elements.append({
            'data': {'id': node, 'label': node},
            'style': {'shape': shape, 'background-color': color, 'label': node}
        })

    for source, target in G.edges:
        if time_cutoff:
            if G.nodes[source].get("division_time", 999) > time_cutoff:
                continue
            if G.nodes[target].get("division_time", 999) > time_cutoff:
                continue
        elements.append({'data': {'source': source, 'target': target}})
    return elements

app = dash.Dash(__name__)
app.title = "🧬 Lineage Tree with Gene Expression"

app.layout = html.Div([
    html.H2("🧬 Lineage Tree with Gene Expression Overlay"),

    html.Div([
        html.Label("Color by Gene Expression:"),
        dcc.Dropdown(
            id="gene-selector",
            options=[{"label": gene, "value": gene} for gene in ["hlh-1", "end-1", "pal-1"]],
            placeholder="None (Use Fate Colors)",
            style={'width': '300px'}
        )
    ], style={'margin': '10px'}),

    html.Div([
        html.Label("Expression Level Legend:"),
        html.Img(src="https://i.imgur.com/Zc5ChbE.png", style={"width": "300px"})
    ], id="legend-div", style={'margin': '10px', 'display': 'none'}),

    dcc.Slider(
        id='time-slider',
        min=0,
        max=max(nx.get_node_attributes(G, "division_time").values()),
        value=0,
        marks={i: f"{i} min" for i in range(0, 65, 5)},
        tooltip={"placement": "bottom"}
    ),

    cyto.Cytoscape(
        id='cytoscape-lineage',
        layout={'name': 'breadthfirst', 'roots': ['Zygote']},
        style={'width': '100%', 'height': '700px'},
        elements=nx_to_cytoscape(G, time_cutoff=0),
        stylesheet=[
            {'selector': 'node', 'style': {
                'width': '50px', 'height': '50px',
                'text-valign': 'center', 'text-halign': 'center',
                'color': 'black', 'font-size': '10px'
            }},
            {'selector': 'edge', 'style': {'line-color': '#ccc', 'width': 2}},
        ],
        userZoomingEnabled=True,
        userPanningEnabled=True
    ),

    html.Div(id="hover-tooltip", style={"marginTop": "10px", "fontSize": "16px"}),
    html.Button("⬇️ Download JSON", id="btn-download-json"),
    Download(id="download-json")
])

@app.callback(
    Output("cytoscape-lineage", "elements"),
    Input("time-slider", "value"),
    Input("gene-selector", "value")
)
def update_tree(time_val, gene_val):
    return nx_to_cytoscape(G, time_cutoff=time_val, gene=gene_val)

@app.callback(
    Output("hover-tooltip", "children"),
    Input("cytoscape-lineage", "mouseoverNodeData"),
    Input("gene-selector", "value")
)
def show_hover_expression(node_data, gene):
    if not node_data or not gene:
        return "Hover on a node to see expression value."
    node_id = node_data.get("id")
    value = G.nodes[node_id].get("expression", {}).get(gene)
    if value is not None:
        return f"🧬 {node_id} – {gene}: {value:.2f}"
    return f"{node_id} has no expression data for {gene}."

@app.callback(
    Output("legend-div", "style"),
    Input("gene-selector", "value")
)
def toggle_legend(gene):
    if gene:
        return {'margin': '10px', 'display': 'block'}
    return {'display': 'none'}

@app.callback(
    Output("download-json", "data"),
    Input("btn-download-json", "n_clicks"),
    Input("time-slider", "value"),
    Input("gene-selector", "value"),
    prevent_initial_call=True
)
def download_json(n_clicks, time_val, gene_val):
    elements = nx_to_cytoscape(G, time_cutoff=time_val, gene=gene_val)
    return send_string(json.dumps(elements, indent=2), filename="lineage_visible.json")

if __name__ == "__main__":
    app.run_server(debug=True)

