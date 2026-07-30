import pandas as pd
import numpy as np
df = pd.read_csv("data/gesture_data.csv")
feature_cols = [c for c in df.columns if c != "label"]
def normalize_row(row):
    coords = row[feature_cols].values.reshape(21, 3).astype(float)
    wrist = coords[0].copy()
    coords -= wrist  # wrist becomes origin
    scale = np.linalg.norm(coords[9])  # middle finger MCP distance
    if scale > 0:
        coords /= scale
    return pd.Series(coords.flatten(), index=feature_cols)
normalized = df.apply(normalize_row, axis=1)
normalized["label"] = df["label"]
normalized.to_csv("data/gesture_data_normalized.csv", index=False)
print("Saved normalized data to data/gesture_data_normalized.csv")
print(normalized.shape)