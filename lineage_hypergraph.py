# lineage_hypergraph_extended.py

import hypernetx as hnx
import matplotlib.pyplot as plt
import pandas as pd
import json
import numpy as np

# ---------------------------
# Node metadata (simplified)
# ---------------------------
metadata = pd.DataFrame([
    {"cell": "Zygote", "time": 0, "fate": "embryo", "syncytial": False},
    {"cell": "AB", "time": 10, "fate": "neuron", "syncytial": False},
    {"cell": "P1", "time": 10, "fate": "germline", "syncytial": False},
    {"cell": "ABa", "time": 20, "fate": "neuron", "syncytial": False},
    {"cell": "ABp", "time": 20, "fate": "neuron", "syncytial": False},
    {"cell": "P2", "time": 20, "fate": "germline", "syncytial": False},
    {"cell": "Sync_AB_P1", "time": 15, "fate": "syncytium", "syncytial": True},
])

# ---------------------------
# Add sample gene expression
# ---------------------------
np.random.seed(42)
for g in ["hlh-1", "end-1", "pal-1"]:
    metadata[g] = np.random.rand(len(metadata))

# ---------------------------
# Hyperedges
# ---------------------------
hyperedges = {
    "Div_Zygote_AB_P1": {"members": ["Zygote", "AB", "P1"]},
    "Div_AB_ABa_ABp": {"members": ["AB", "ABa", "ABp"]},
    "Div_P1_P2": {"members": ["P1", "P2"]},
    "Sync_AB_P1": {"members": ["AB", "P1", "Sync_AB_P1"]},
}

# ---------------------------
# Build Hypergraph
# ---------------------------
H = hnx.Hypergraph({k: v["members"] for k, v in hyperedges.items()})

# Attach node metadata
for _, row in metadata.iterrows():
    node = row["cell"]
    if node in H.nodes:
        H.nodes[node].data.update(row.to_dict())

# ---------------------------
# Color mapping (by fate)
# ---------------------------
fate_colors = {
    "neuron": "#1f77b4",
    "muscle": "#2ca02c",
    "gut": "#ff7f0e",
    "germline": "#d62728",
    "syncytium": "#9467bd",
    "embryo": "#8c564b"
}

# ---------------------------
# Visualization
# ---------------------------
fig, ax = plt.subplots(figsize=(9, 7))
node_colors = [fate_colors.get(H.nodes[n].data.get("fate"), "#999999") for n in H.nodes]
hnx.drawing.draw(H, with_node_labels=True, node_color=node_colors, ax=ax)
plt.title("C. elegans Hypergraph with Fate Coloring")
plt.show()

# ---------------------------
# Export JSON
# ---------------------------
export_data = {
    "nodes": [
        {**H.nodes[n].data, "id": n} for n in H.nodes
    ],
    "edges": {e: list(H.edges[e]) for e in H.edges}
}

with open("lineage_hypergraph_extended.json", "w") as f:
    json.dump(export_data, f, indent=2)

print("Saved lineage_hypergraph_extended.json")

