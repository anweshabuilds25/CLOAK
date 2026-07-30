import pickle
import numpy as np
import pandas as pd
from utils import normalize_landmarks

with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

FEATURE_COLUMNS = [f"{axis}{i}" for i in range(21) for axis in ["x", "y", "z"]]

def predict(landmarks):
    landmarks = normalize_landmarks(landmarks)
    df = pd.DataFrame([landmarks], columns=FEATURE_COLUMNS)
    return int(model.predict(df)[0])

def predict_proba(landmarks):
    landmarks = normalize_landmarks(landmarks)
    df = pd.DataFrame([landmarks], columns=FEATURE_COLUMNS)
    return model.predict_proba(df)[0][1]