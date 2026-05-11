import joblib
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "health_model.pkl"
model = joblib.load(MODEL_PATH)


def predict_health_risk(age: int, vaccinated: int, sterilized: int, size: int) -> int:
    X = np.array([[age, vaccinated, sterilized, size]])
    result = model.predict(X)
    return int(result[0])