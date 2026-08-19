import torch
import torch.nn.functional as F
from build_initial_lineage import add_random_syncytial_cells, build_lineage_tree
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 1. Build lineage graph
G = build_lineage_tree()  #[cite: 11]
add_random_syncytial_cells(G, num_cells=20)  #[cite: 11]

node_map = {node: i for i, node in enumerate(G.nodes())}

# Feature matrix: [division_time, is_syncytial, nuclei_count]
features = []
labels = []
for node, attr in G.nodes(data=True):
    div_time = float(attr.get("division_time", 0))
    is_sync = 1.0 if attr.get("syncytial", False) else 0.0
    nuclei = float(attr.get("nuclei_count", 1 if not is_sync else 2))

    features.append([div_time, is_sync, nuclei])
    labels.append(1 if is_sync else 0)

x = torch.tensor(features, dtype=torch.float, device=DEVICE)
y = torch.tensor(labels, dtype=torch.long, device=DEVICE)

# 2. Extract edge indices directly into GPU memory
edges = [[node_map[u], node_map[v]] for u, v in G.edges()]
edge_index = torch.tensor(edges, dtype=torch.long, device=DEVICE).t().contiguous()

data = Data(x=x, edge_index=edge_index, y=y)


# 3. GCN Model
class LineageGCN(torch.nn.Module):

    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(3, 16)
        self.conv2 = GCNConv(16, 2)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        return self.conv2(x, edge_index)


print(f"Training Lineage GCN on: {torch.cuda.get_device_name(0)}")
model = LineageGCN().to(DEVICE)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = torch.nn.CrossEntropyLoss()

for epoch in range(1, 101):
    model.train()
    optimizer.zero_grad()
    out = model(data.x, data.edge_index)
    loss = loss_fn(out, data.y)
    loss.backward()
    optimizer.step()

    if epoch % 20 == 0:
        pred = out.argmax(dim=1)
        acc = (pred == data.y).float().mean().item()
        print(
            f"Epoch {epoch:03d} | Loss: {loss.item():.4f} | Syncytial Detection Acc: {acc*100:.1f}%"
        )