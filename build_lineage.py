import networkx as nx
import matplotlib.pyplot as plt
import random

class C_ElegansLineage:
    def __init__(self):
        self.lineage_tree = nx.DiGraph()
        self.build_initial_lineage()
    
    def build_initial_lineage(self):
        """Initialize a base lineage tree with known cell divisions."""
        self.lineage_tree.add_edge("Zygote", "AB")
        self.lineage_tree.add_edge("Zygote", "P1")
        self.lineage_tree.add_edge("AB", "ABa")
        self.lineage_tree.add_edge("AB", "ABp")
        self.lineage_tree.add_edge("P1", "EMS")
        self.lineage_tree.add_edge("P1", "P2")
    
    def add_syncytial_cells(self, num_cells=5):
        """Randomly insert syncytial cells into the lineage tree."""
        for _ in range(num_cells):
            parent = random.choice(list(self.lineage_tree.nodes))
            new_cell = f"Sync_{random.randint(1, 1000)}"
            self.lineage_tree.add_edge(parent, new_cell)
    
    def visualize_lineage(self):
        """Display the lineage tree graphically."""
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(self.lineage_tree, seed=42)
        nx.draw(self.lineage_tree, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10)
        plt.title("C. elegans Lineage Tree with Syncytial Cells")
        plt.show()
    
    def export_lineage(self, filename="c_elegans_lineage.graphml"):
        """Save the lineage tree in GraphML format for further analysis."""
        nx.write_graphml(self.lineage_tree, filename)

if __name__ == "__main__":
    lineage_model = C_ElegansLineage()
    lineage_model.add_syncytial_cells(num_cells=10)
    lineage_model.visualize_lineage()
    lineage_model.export_lineage()

