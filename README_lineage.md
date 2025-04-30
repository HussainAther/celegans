# 🧬 C. elegans Lineage Toolkit

A Python toolkit and command-line interface (CLI) for modeling, visualizing, animating, and exporting the full embryonic cell lineage of *Caenorhabditis elegans*, including support for syncytial cells, fate annotations, and more.

![screenshot](https://user-images.githubusercontent.com/example/demo.png)

---

## 📦 Features

- ✅ Build and extend the full *C. elegans* lineage tree
- 🧠 Annotate cells with fates (e.g., neuron, muscle, germline)
- 🔶 Support for syncytial cells (shared cytoplasm, multi-nucleated)
- 🎨 Visualize lineage trees with shape + color coding
- 📤 Export to GraphML and JSON for analysis
- 🎞️ Animate development over division time
- 💻 Installable as a CLI tool: `lineage-cli`

---

## 🚀 Installation

```bash
# Clone this repo
git clone https://github.com/yourusername/c_elegans_lineage.git
cd c_elegans_lineage

# Install the CLI tool
pip install .
```

---

## 🧪 Usage

### Visualize and Save Lineage Tree
```bash
lineage-cli visualize --fate --save tree.png
```

### Animate Development Over Time
```bash
lineage-cli animate --output dev.gif
```

### Export for Cytoscape or Gephi
```bash
lineage-cli export --format graphml --output lineage.graphml
```

---

## 📁 CLI Overview

| Command        | Description                           |
|----------------|---------------------------------------|
| `visualize`    | Visualize tree as image (with fates, shapes) |
| `export`       | Export to `.graphml` or `.json`       |
| `animate`      | Create a GIF of lineage progression   |

Use `--help` with any command:
```bash
lineage-cli visualize --help
```

---

## 🧬 Biology Background

*C. elegans* has a fully mapped embryonic lineage tree from zygote to all 959 somatic cells. This tool supports:
- Syncytial cells like those in the germline
- Fate mapping (e.g., AB → neurons, P lineage → germline)
- Future support for gene expression overlays and simulation

---

## 🛠️ Developer Info

### Folder Structure

```
c_elegans_lineage/
├── c_elegans_lineage/
│   ├── lineage_cli.py
│   ├── build_initial_lineage.py
│   ├── lineage_visualizer.py
│   ├── animate_lineage.py
│   └── ...
├── setup.py
├── README.md
└── requirements.txt
```

### Run Locally

```bash
python c_elegans_lineage/lineage_cli.py visualize --fate --show
```

---

## 👩‍🔬 Citation / Acknowledgments

Built using:
- [`networkx`](https://networkx.org/)
- [`matplotlib`](https://matplotlib.org/)
- Cell lineage data inspired by [WormAtlas](https://www.wormatlas.org/) and [WormBase](https://wormbase.org/)

---

## 📄 License

MIT License © Your Name, 2025

---

## 🧠 Future Ideas

- [ ] Gene expression overlays (marker heatmaps)
- [ ] Interactive web UI with Dash or Streamlit
- [ ] Real lineage dataset integration
