import networkx as nx
import random

def build_lineage_tree():
    """
    Build the initial C. elegans lineage tree with annotated division times
    and known cell relationships.
    Returns a directed graph (DiGraph).
    """
    lineage_tree = nx.DiGraph()

    # Known early embryonic lineage from literature
    known_lineage = {
        "Zygote": ["AB", "P1"],
        "AB": ["ABa", "ABp"],
        "P1": ["EMS", "P2"],
        "EMS": ["MS", "E"],
        "P2": ["C", "P3"],
        "P3": ["D", "P4"],
        "P4": ["Z2", "Z3"]
    }

    # Add edges and initialize nodes
    for parent, children in known_lineage.items():
        for child in children:
            lineage_tree.add_edge(parent, child)

    # Assign division times based on tree depth
    assign_division_times(lineage_tree)
    
    return lineage_tree


def assign_division_times(tree, root="Zygote"):
    """Assign approximate division times to all nodes based on depth."""
    def dfs(node, depth):
        tree.nodes[node]["division_time"] = depth * 5  # 5 mins per division step
        for child in tree.successors(node):
            dfs(child, depth + 1)
    dfs(root, 0)


def annotate_syncytial_cell(tree, node):
    """Mark a node in the tree as syncytial with metadata."""
    tree.nodes[node]["syncytial"] = True
    tree.nodes[node]["nuclei_count"] = random.randint(2, 8)
    tree.nodes[node]["shared_cytoplasm"] = True
    if "division_time" not in tree.nodes[node]:
        tree.nodes[node]["division_time"] = random.randint(20, 60)


def add_random_syncytial_cells(tree, num_cells=5):
    """Randomly insert and annotate syncytial cells."""
    for _ in range(num_cells):
        parent = random.choice(list(tree.nodes))
        new_cell = f"Sync_{random.randint(1000, 9999)}"
        tree.add_edge(parent, new_cell)
        annotate_syncytial_cell(tree, new_cell)


if __name__ == "__main__":
    # For testing this module directly
    tree = build_lineage_tree()
    add_random_syncytial_cells(tree, num_cells=5)

    print("Nodes with division times and syncytial annotations:")
    for node, data in tree.nodes(data=True):
        print(f"{node}: {data}")

