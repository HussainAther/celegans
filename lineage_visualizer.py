import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Color palette for each fate category
FATE_COLORS = {
    "neuron": "purple",
    "muscle": "red",
    "skin": "tan",
    "gut": "green",
    "germline": "blue",
    "progenitor": "lightblue",
    "undifferentiated": "gray",
    None: "lightgray"  # fallback
}


def hierarchy_pos(G, root="Zygote", width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
    """
    Recursively compute a hierarchical layout for a directed tree.
    """
    if pos is None:
        pos = {root: (xcenter, vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)

    children = list(G.successors(root))
    if len(children) != 0:
        dx = width / len(children)
        next_x = xcenter - width / 2 - dx / 2
        for child in children:
            next_x += dx
            pos = hierarchy_pos(G, root=child, width=dx, vert_gap=vert_gap,
                                vert_loc=vert_loc - vert_gap, xcenter=next_x, pos=pos, parent=root)
    return pos


def visualize_lineage_tree(G, color_by_fate=True, title="C. elegans Lineage Tree (Hierarchical)"):
    """
    Visualize the lineage tree with:
    - Hierarchical layout
    - Color-coded fate
    - Shape-coded syncytial status
    """
    pos = hierarchy_pos(G, root="Zygote")

    # Separate nodes by shape
    circle_nodes = []
    square_nodes = []
    circle_colors = []
    square_colors = []

    for node in G.nodes:
        color = FATE_COLORS.get(G.nodes[node].get("fate"), "lightgray")
        if G.nodes[node].get("syncytial"):
            square_nodes.append(node)
            square_colors.append(color)
        else:
            circle_nodes.append(node)
            circle_colors.append(color)

    plt.figure(figsize=(14, 10))

    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray')

    # Draw nodes by shape
    nx.draw_networkx_nodes(G, pos, nodelist=circle_nodes, node_color=circle_colors,
                           node_shape='o', node_size=2500)
    nx.draw_networkx_nodes(G, pos, nodelist=square_nodes, node_color=square_colors,
                           node_shape='s', node_size=2500)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=9)

    # Title & layout
    plt.title(title)
    plt.axis('off')

    # Legends
    fate_legend = [
        Patch(facecolor=color, edgecolor='black', label=fate.capitalize() if fate else "Unknown")
        for fate, color in FATE_COLORS.items() if fate is not None
    ]
    shape_legend = [
        Line2D([0], [0], marker='o', color='w', label='Normal Cell',
               markerfacecolor='gray', markersize=12, markeredgecolor='black'),
        Line2D([0], [0], marker='s', color='w', label='Syncytial Cell',
               markerfacecolor='gray', markersize=12, markeredgecolor='black'),
    ]

    plt.legend(handles=fate_legend + shape_legend,
               title="Legend", loc='lower left', bbox_to_anchor=(1, 0.5))

    plt.tight_layout()
    plt.show()

