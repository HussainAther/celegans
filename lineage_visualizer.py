import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

# Color palette for each fate category
FATE_COLORS = {
    "neuron": "purple",
    "muscle": "red",
    "skin": "tan",
    "gut": "green",
    "germline": "blue",
    "progenitor": "lightblue",
    "undifferentiated": "gray",
    None: "lightgray"  # fallback for missing fates
}


def hierarchy_pos(G, root="Zygote", width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
    """
    Recursively compute a hierarchical layout for a directed tree.
    Source: adapted from StackOverflow (Joel, https://stackoverflow.com/a/29597209)
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
    Visualize the lineage tree using a hierarchical layout.
    
    Parameters:
        G: networkx.DiGraph
        color_by_fate: bool — whether to color nodes by their fate annotation
        title: str — plot title
    """
    pos = hierarchy_pos(G, root="Zygote")
    node_colors = []
    for node in G.nodes:
        fate = G.nodes[node].get("fate") if color_by_fate else None
        color = FATE_COLORS.get(fate, "lightgray")
        node_colors.append(color)

    plt.figure(figsize=(14, 10))
    nx.draw(G, pos, with_labels=True, node_color=node_colors,
            edge_color='gray', node_size=2500, font_size=9)

    plt.title(title)
    plt.axis('off')

    if color_by_fate:
        legend_elements = [
            Patch(facecolor=color, edgecolor='black', label=fate.capitalize() if fate else "Unknown")
            for fate, color in FATE_COLORS.items() if fate is not None
        ]
        plt.legend(handles=legend_elements, title="Cell Fates", loc='lower left', bbox_to_anchor=(1, 0.5))

    plt.tight_layout()
    plt.show()

