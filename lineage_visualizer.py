import matplotlib.pyplot as plt
import networkx as nx

def hierarchy_pos(G, root="Zygote", width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
    """
    Recursive function to calculate hierarchical layout for a tree.
    Credit: Joel (StackOverflow) https://stackoverflow.com/a/29597209
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


def visualize_lineage_tree(G, syncytial_highlight=True, title="C. elegans Lineage Tree (Hierarchical)"):
    """
    Visualize the lineage tree with a hierarchical layout.
    
    Parameters:
        G: networkx.DiGraph
        syncytial_highlight: bool — if True, highlight syncytial cells in orange
        title: str — plot title
    """
    pos = hierarchy_pos(G, root="Zygote")

    # Partition nodes
    if syncytial_highlight:
        sync_cells = [n for n, d in G.nodes(data=True) if d.get("syncytial")]
        normal_cells = [n for n in G.nodes if n not in sync_cells]
    else:
        sync_cells = []
        normal_cells = list(G.nodes)

    # Plot
    plt.figure(figsize=(14, 10))
    nx.draw_networkx_nodes(G, pos, nodelist=normal_cells, node_color='lightblue', node_size=2500)
    nx.draw_networkx_nodes(G, pos, nodelist=sync_cells, node_color='orange', node_size=2800)
    nx.draw_networkx_edges(G, pos, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=10)

    plt.title(title)
    plt.axis('off')
    plt.show()

