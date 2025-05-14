import dash
from dash import html, dcc, Input, Output
import dash_cytoscape as cyto
import networkx as nx
import pandas as pd

from build_initial_lineage import build_lineage_tree, add_random_syncytial_cells
from fate_utils import assign_cell_fates

# Load or simulate gene expression data
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

# Color map for cell fates
FATE_COLORS = {
    "neuron": "purple", "muscle": "red", "skin": "tan", "gut": "green",
    "germline": "blue", "progenitor": "lightblue", "undifferentiated": "gray", None: "lightgray"
}

# Expression heatmap color scale
def get_expression_color(val):
    if val is None:
        return "lightgray"
    r = int(255 * (1 - val))
    g = int(255 * (1 - abs(0.5 - val)))
    b = int(255 * val)
    return f"rgb({r},{g},{b})"

# Build graph and attach metadata
G = build_lineage_tree()
add_random_syncytial_cells(G, num_cells=10)
assign_cell_fates(G)

# Attach expression to graph
for _, row in expression_df.iterrows():
    if row["cell"] in G.nodes:
        G.nodes[row["cell"]]["expression"] = row.drop("cell").to_dict()

# Graph to Cytoscape converter
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
            'style': {
                'shape': shape,
                'background-color': color,
                'label': node
            }
        })

    for source, target in G.edges:
        if time_cutoff:
            if G.nodes[source].get("division_time", 999) > time_cutoff:
                continue
            if G.nodes[target].get("division_time", 999) > time_cutoff:
                continue
        elements.append({'data': {'source': source, 'target': target}})
    return elements

# Build Dash app
app = dash.Dash(__name__)
app.title = "🧬 C. elegans Lineage + Gene Expression"

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
    )
])

@app.callback(
    Output("cytoscape-lineage", "elements"),
    Input("time-slider", "value"),
    Input("gene-selector", "value")
)
def update_tree(time_val, gene_val):
    return nx_to_cytoscape(G, time_cutoff=time_val, gene=gene_val)

if __name__ == "__main__":
    app.run_server(debug=True)

