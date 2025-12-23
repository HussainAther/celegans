# syncytial_lineage_dataset_builder.py

import pandas as pd

# --- Cell lineage structure ---
# Simplified to start. We can expand with literature data.
lineage = [
    {"cell": "Zygote", "parent": None, "fate": "undiff", "syncytial_unit": "Zygote", "division_time": 0},
    {"cell": "AB", "parent": "Zygote", "fate": "ectoderm", "syncytial_unit": "AB", "division_time": 20},
    {"cell": "P1", "parent": "Zygote", "fate": "germline", "syncytial_unit": "P1", "division_time": 20},
    {"cell": "ABa", "parent": "AB", "fate": "neuron", "syncytial_unit": "AB", "division_time": 40},
    {"cell": "ABp", "parent": "AB", "fate": "neuron", "syncytial_unit": "AB", "division_time": 40},
    {"cell": "EMS", "parent": "P1", "fate": "gut precursor", "syncytial_unit": "P1", "division_time": 40},
    {"cell": "P2", "parent": "P1", "fate": "germline", "syncytial_unit": "P2", "division_time": 40},
    # Add more rows as needed (full 44 syncytial units)
]

# Optional: Add dummy expression data
expression_data = {
    "ABa": {"hlh-1": 0.7, "end-1": 0.2, "pal-1": 0.1},
    "ABp": {"hlh-1": 0.6, "end-1": 0.3, "pal-1": 0.2},
    "EMS": {"hlh-1": 0.2, "end-1": 0.9, "pal-1": 0.2},
    "P2": {"hlh-1": 0.1, "end-1": 0.2, "pal-1": 0.8},
}

# Convert to DataFrame
df = pd.DataFrame(lineage)

# Merge expression data
expr_df = pd.DataFrame(expression_data).T.reset_index().rename(columns={"index": "cell"})
df = df.merge(expr_df, on="cell", how="left")

# Save
df.to_csv("syncytial_lineage.csv", index=False)
print("✅ Dataset saved as syncytial_lineage.csv")

