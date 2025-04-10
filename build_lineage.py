import networkx as nx
import matplotlib.pyplot as plt
import random
import json

class C_ElegansLineage:
    def __init__(self):
        self.lineage_tree = nx.DiGraph()
        self.build_initial_lineage()
    
    def build_initial_lineage(self):
        """Initialize a base lineage tree with known cell divisions."""
        known_lineage = {
            "Zygote": ["AB", "P1"],
            "AB": ["ABa", "ABp"],
            "P1": ["EMS", "P2"],
            "EMS": ["MS", "E"],
            "P2": ["C", "P3"],
            "P3": ["D", "P4"],
            "P4": ["Z2", "Z3"]
        }
        for parent, children in known_lineage.items():
            for child in children:
                self.lineage_tree.add_edge(parent, child)
    
    def add_syncytial_cells(self, num_cells=5):
        """Randomly insert syncytial cells into the lineage tree."""
        for _ in range(num_cells):
            parent = random.choice(list(self.lineage_tree.nodes))
            new_cell = f"Sync_{random.randint(1, 1000)}"
            self.lineage_tree.add_edge(parent, new_cell)
    
    def visualize_lineage(self):
        """Display the lineage tree graphically."""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.lineage_tree, seed=42)
        nx.draw(self.lineage_tree, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10)
        plt.title("C. elegans Lineage Tree with Syncytial Cells")
        plt.show()
    
    def export_lineage(self, filename="c_elegans_lineage.graphml"):
        """Save the lineage tree in GraphML format for further analysis."""
        nx.write_graphml(self.lineage_tree, filename)
        print(f"Lineage tree saved as {filename}")
    
    def export_json(self, filename="c_elegans_lineage.json"):
        """Save the lineage tree as a JSON file."""
        lineage_dict = nx.node_link_data(self.lineage_tree)
        with open(filename, 'w') as f:
            json.dump(lineage_dict, f, indent=4)
        print(f"Lineage tree saved as {filename}")
    
    def get_lineage_depth(self, node="Zygote"):
        """Calculate depth of lineage tree from a given node."""
        depths = {}
        def dfs(n, depth):
            depths[n] = depth
            for child in self.lineage_tree.successors(n):
                dfs(child, depth + 1)
        dfs(node, 0)
        return depths

    def annotate_syncytial_cell(self, node):
        """Mark a node as syncytial with metadata."""
        self.lineage_tree.nodes[node]["syncytial"] = True
        self.lineage_tree.nodes[node]["nuclei_count"] = random.randint(2, 8)  # Example: # of nuclei
        self.lineage_tree.nodes[node]["shared_cytoplasm"] = True

    def add_syncytial_cells(self, num_cells=5):
        """Randomly insert syncytial cells into the lineage tree with annotations."""
        for _ in range(num_cells):
            parent = random.choice(list(self.lineage_tree.nodes))
            new_cell = f"Sync_{random.randint(1, 1000)}"
            self.lineage_tree.add_edge(parent, new_cell)
            self.annotate_syncytial_cell(new_cell)

    def get_syncytial_cells(self):
        """Return a list of syncytial cells in the tree."""
        return [n for n, attr in self.lineage_tree.nodes(data=True) if attr.get("syncytial", False)]

    def visualize_lineage(self):
        """Display the lineage tree graphically, highlighting syncytial cells."""
        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(self.lineage_tree, seed=42)
        
        sync_cells = self.get_syncytial_cells()
        normal_cells = [n for n in self.lineage_tree.nodes if n not in sync_cells]

        nx.draw_networkx_nodes(self.lineage_tree, pos, nodelist=normal_cells, node_color='lightblue', node_size=2500)
        nx.draw_networkx_nodes(self.lineage_tree, pos, nodelist=sync_cells, node_color='orange', node_size=2800)
        nx.draw_networkx_edges(self.lineage_tree, pos, edge_color='gray')
        nx.draw_networkx_labels(self.lineage_tree, pos, font_size=10)
        
        plt.title("C. elegans Lineage Tree (Syncytial Cells in Orange)")
        plt.axis('off')
        plt.show()

    def print_lineage(self):
        """Print lineage tree in a structured format."""
        depths = self.get_lineage_depth()
        for node, depth in sorted(depths.items(), key=lambda x: x[1]):
            print("  " * depth + node)

if __name__ == "__main__":
    lineage_model = C_ElegansLineage()
    lineage_model.add_syncytial_cells(num_cells=10)
    lineage_model.visualize_lineage()
    lineage_model.export_lineage()
    lineage_model.export_json()
    lineage_model.print_lineage()

