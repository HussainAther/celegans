import dash
from dash import html, dcc, Input, Output
import dash_cytoscape as cyto
import networkx as nx
from build_initial_lineage import build_lineage_tree, add_random_syncytial_cells
from fate_utils import assign_cell_fates

# Initialize data
G = build_lineage_tree()
add_random_syncytial_cells(G, num_cells=10)
assign_cell_fates(G)

# Convert NetworkX to Cytoscape format
def nx_to_cytoscape(G, time_cutoff=None):
    elements = []
    for node in G.nodes:
        div_time = G.nodes[node].get("division_time", 999)
        if time_cutoff is not None and div_time > time_cutoff:
            continue

        fate = G.nodes[node].get("fate", "unknown")
        sync = G.nodes[node].get("syncytial", False)
        shape = "rectangle" if sync else "ellipse"
        color = {
            "neuron": "purple",
            "muscle": "red",
            "gut": "green",
            "skin": "tan",
            "germline": "blue",
            "progenitor": "lightblue",
            "undifferentiated": "gray"
        }.get(fate, "lightgray")

        elements.append({
            'data': {'id': node, 'label': node},
            'position': {},
            'classes': fate,
            'style': {
                'shape': shape,
                'background-color': color,
                'label': node
            }
        })

    for source, target in G.edges:
        if source in G.nodes and target in G.nodes:
            stime = G.nodes[source].get("division_time", 999)
            ttime = G.nodes[target].get("division_time", 999)
            if time_cutoff is None or (stime <= time_cutoff and ttime <= time_cutoff):
                elements.append({
                    'data': {'source': source, 'target': target}
                })
    return elements

# Dash app
app = dash.Dash(__name__)
app.title = "🧬 C. elegans Lineage Viewer"

app.layout = html.Div([
    html.H2("C. elegans Lineage Tree"),
    html.Div([
        dcc.Slider(
            id='time-slider',
            min=0,
            max=max(nx.get_node_attributes(G, "division_time").values()),
            value=0,
            marks={i: f"{i} min" for i in range(0, 60, 5)},
            tooltip={"placement": "bottom"}
        ),
    ], style={'margin': '20px'}),

    cyto.Cytoscape(
        id='cytoscape-lineage',
        layout={'name': 'breadthfirst', 'roots': ['Zygote']},
        style={'width': '100%', 'height': '800px'},
        elements=nx_to_cytoscape(G, time_cutoff=0),
        stylesheet=[
            {'selector': 'node', 'style': {
                'width': '50px',
                'height': '50px',
                'text-valign': 'center',
                'text-halign': 'center',
                'color': 'black',
                'font-size': '10px'
            }},
            {'selector': 'edge', 'style': {
                'line-color': '#ccc',
                'width': 2
            }},
        ],
        userZoomingEnabled=True,
        userPanningEnabled=True
    ),
    html.Div(id='hover-data', style={'marginTop': '20px', 'fontSize': '16px'})
])

@app.callback(
    Output('cytoscape-lineage', 'elements'),
    Input('time-slider', 'value')
)
def update_elements(time_value):
    return nx_to_cytoscape(G, time_cutoff=time_value)

if __name__ == '__main__':
    app.run_server(debug=True)

