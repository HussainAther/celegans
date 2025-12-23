import dash
from dash import dcc, html, Input, Output
import dash_cytoscape as cyto
import pandas as pd
import hypernetx as hnx

# Load expression and syncytial timing data
expression_df = pd.DataFrame([
    {"cell": "ABa", "hlh-1": 0.8, "end-1": 0.2, "pal-1": 0.1, "time": 5},
    {"cell": "ABp", "hlh-1": 0.6, "end-1": 0.3, "pal-1": 0.2, "time": 7},
    {"cell": "EMS", "hlh-1": 0.3, "end-1": 0.9, "pal-1": 0.2, "time": 10},
    {"cell": "P2", "hlh-1": 0.1, "end-1": 0.2, "pal-1": 0.8, "time": 12},
    {"cell": "P3", "hlh-1": 0.2, "end-1": 0.1, "pal-1": 0.7, "time": 15},
])

# Convert to dict of sets to define hyperedges
cell_to_complex = {
    "AB": ["ABa", "ABp"],
    "P1": ["EMS", "P2"],
    "P2": ["P3", "C"],
    "P3": ["D", "P4"],
    "P4": ["Z2", "Z3"]
}

# Build Hypergraph
H = hnx.Hypergraph(cell_to_complex)

# Add metadata to nodes
for _, row in expression_df.iterrows():
    cell = row['cell']
    if cell in H.nodes:
        node_data = row.drop("cell").to_dict()
        H.nodes[cell].properties.update(node_data)

# Function to convert HNX Hypergraph to Cytoscape elements
def hypergraph_to_cytoscape(H, max_time=100, rgb_genes=None):
    elements = []
    rgb_genes = rgb_genes or {"R": None, "G": None, "B": None}

    for node in H.nodes:
        meta = H.nodes[node].properties
        time = meta.get("time", 0)
        if time > max_time:
            continue

        r = meta.get(rgb_genes["R"], 0) if rgb_genes["R"] else 0
        g = meta.get(rgb_genes["G"], 0) if rgb_genes["G"] else 0
        b = meta.get(rgb_genes["B"], 0) if rgb_genes["B"] else 0

        elements.append({
            "data": {"id": node, "label": node},
            "style": {"background-color": f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"}
        })

    for hedge, nodes in H.incidence_dict.items():
        nodes = list(nodes)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                source, target = nodes[i], nodes[j]
                if source in H.nodes and target in H.nodes:
                    elements.append({"data": {"source": source, "target": target}})

    return elements

# Dash app setup
app = dash.Dash(__name__)
app.title = "C. elegans Hypergraph Explorer"

app.layout = html.Div([
    html.H2("🧬 C. elegans Hypergraph Explorer"),

    html.Label("Select Red, Green, Blue Genes:"),
    dcc.Dropdown(expression_df.columns.drop("cell").drop("time"), id="gene-R", placeholder="Red Channel"),
    dcc.Dropdown(expression_df.columns.drop("cell").drop("time"), id="gene-G", placeholder="Green Channel"),
    dcc.Dropdown(expression_df.columns.drop("cell").drop("time"), id="gene-B", placeholder="Blue Channel"),
    html.Br(),

    html.Label("Max Time (slider):"),
    dcc.Slider(min=0, max=30, step=1, value=30, id="max-time-slider", marks={i: str(i) for i in range(0, 31)}),

    html.Br(),
    cyto.Cytoscape(
        id="cytoscape",
        layout={"name": "cose"},
        style={"width": "100%", "height": "600px"},
        elements=[]
    )
])

@app.callback(
    Output("cytoscape", "elements"),
    Input("gene-R", "value"),
    Input("gene-G", "value"),
    Input("gene-B", "value"),
    Input("max-time-slider", "value")
)
def update_graph(r, g, b, max_time):
    genes = {"R": r, "G": g, "B": b}
    return hypergraph_to_cytoscape(H, max_time=max_time, rgb_genes=genes)

if __name__ == "__main__":
    app.run(debug=True)

