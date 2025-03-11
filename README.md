# C. elegans Lineage Tree Simulation

## Overview
This project simulates the **lineage tree of C. elegans**, incorporating **syncytial cells** to improve our understanding of differentiation and cell fate transitions. By using **network-based modeling**, we can visualize the lineage and analyze potential missing connections.

## Features
- **Constructs a base lineage tree** with known divisions.
- **Dynamically adds syncytial cells** to test hypotheses.
- **Visualizes the lineage structure** using NetworkX & Matplotlib.
- **Exports data** in GraphML format for further analysis.

## Installation
Clone this repository and install dependencies:
```bash
git clone https://github.com/yourusername/c-elegans-lineage.git
cd c-elegans-lineage
pip install -r requirements.txt
```

## Usage
Run the simulation with:
```bash
python c_elegans_lineage.py
```

This will:
1. Generate a **C. elegans lineage tree**.
2. **Randomly insert syncytial cells** into the lineage.
3. **Display the lineage graph**.
4. **Export the lineage** to a GraphML file (`c_elegans_lineage.graphml`).

## Dependencies
- `networkx` (Graph-based modeling)
- `matplotlib` (Visualization)

Install dependencies with:
```bash
pip install -r requirements.txt
```

## Future Improvements
- **Integration with real lineage datasets**.
- **Machine learning-based prediction of missing connections**.
- **Interactive visualization for exploring lineage evolution**.

## Contribution
Feel free to fork the repo, submit PRs, or reach out with suggestions!

## License
MIT License

