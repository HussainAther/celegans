import dash
from dash import html, dcc, Input, Output
import dash_cytoscape as cyto
import networkx as nx

from build_initial_lineage import build_lineage_tree, add_random_syncytial_cells
from fate_utils import assign_cell_fates

# Initialize lineage graph
G = build_lineage_tree()
add_random_syncytial_cells(G, num_cells=10)
assign_cell_fates(G)

# Fate → color map
FATE_COLORS = {
    "neuron": "purple",
    "muscle": "red",
    "skin": "tan",
    "gut": "green",
    "germline": "blue",
    "progenitor": "lightblue",
    "undifferentiated": "gray",
    None: "lightgray"
}

# Convert NetworkX to Cytoscape elements
def nx_to_cytoscape(G, time_cutoff=None, fate_filter=None):
    elements = []
    for node in G.nodes:
        div_time = G.nodes[node].get("division_time", 999)
        if time_cutoff is not None and div_time > time_cutoff:
            continue

        fate = G.nodes[node].get("fate", "unknown")
        if fate_filter and fate != fate_filter:
            continue

        sync = G.nodes[node].get("syncytial", False)
        shape = "rectangle" if sync else "ellipse"
        color = FATE_COLORS.get(fate, "lightgray")

        elements.append({
            'data': {'id': node, 'label': node},
            'classes': fate,
            'style': {
                'shape': shape,
                'background-color': color,
                'label': node
            }
        })

    for source, target in G.edges:
        stime = G.nodes[source].get("division_time", 999)
        ttime = G.nodes[target].get("division_time", 999)
        if time_cutoff is not None and (stime > time_cutoff or ttime > time_cutoff):
            continue
        if fate_filter and (G.nodes[target].get("fate") != fate_filter):
            continue
        elements.append({'data': {'source': source, 'target': target}})

    return elements

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "🧬 C. elegans Lineage Viewer"

# Layout
app.layout = html.Div([
    html.H2("C. elegans Lineage Tree Viewer"),

    html.Div([
        html.Label("Filter by Fate:"),
        dcc.Dropdown(
            id='fate-filter',
            options=[{'label': f.capitalize(), 'value': f} for f in FATE_COLORS.keys() if f],
            value=None,
            placeholder="Show all fates",
            clearable=True,
            style={'width': '300px'}
        )
    ], style={'margin': '20px'}),

    html.Div([
        dcc.Slider(
            id='time-slider',
            min=0,
            max=max(nx.get_node_attributes(G, "division_time").values()),
            value=0,
            marks={i: f"{i} min" for i in range(0, 65, 5)},
            tooltip={"placement": "bottom"}
        )
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

    html.Div(id='hover-data', style={'marginTop': '20px', 'fontSize': '16px'}),
    html.Hr(),
    html.Div(id='click-data', style={'marginTop': '20px', 'fontSize': '16px'})
])

# Update graph based on slider + dropdown
@app.callback(
    Output('cytoscape-lineage', 'elements'),
    Input('time-slider', 'value'),
    Input('fate-filter', 'value')
)
def update_elements(time_value, selected_fate):
    return nx_to_cytoscape(G, time_cutoff=time_value, fate_filter=selected_fate)

# Hover info
@app.callback(
    Output('hover-data', 'children'),
    Input('cytoscape-lineage', 'mouseoverNodeData')
)
def display_hover_metadata(node_data):
    if node_data is None:
        return "Hover over a cell to see metadata."

    node_id = node_data.get('id')
    node = G.nodes.get(node_id, {})

    return html.Div([
        html.Strong(f"🧬 {node_id}"),
        html.Br(),
        f"Fate: {node.get('fate', 'Unknown')}",
        html.Br(),
        f"Division time: {node.get('division_time', 'N/A')} min",
        html.Br(),
        f"Syncytial: {'Yes' if node.get('syncytial') else 'No'}",
        html.Br(),
        f"Nuclei: {node.get('nuclei_count', '-') if node.get('syncytial') else '-'}"
    ])

# Click info
@app.callback(
    Output('click-data', 'children'),
    Input('cytoscape-lineage', 'tapNodeData')
)
def display_click_metadata(node_data):
    if node_data is None:
        return "Click a cell to pin its info here."

    node_id = node_data.get('id')
    node = G.nodes.get(node_id, {})

    return html.Div([
        html.Strong(f"📌 Selected: {node_id}"),
        html.Br(),
        f"Fate: {node.get('fate', 'Unknown')}",
        html.Br(),
        f"Division time: {node.get('division_time', 'N/A')} min",
        html.Br(),
        f"Syncytial: {'Yes' if node.get('syncytial') else 'No'}",
        html.Br(),
        f"Nuclei: {node.get('nuclei_count', '-') if node.get('syncytial') else '-'}"
    ])

# Run server
if __name__ == '__main__':
    app.run_server(debug=True)

