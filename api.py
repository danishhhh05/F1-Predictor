from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models and encoders
model_winner   = joblib.load('models/model_winner.pkl')
model_podium   = joblib.load('models/model_podium.pkl')
le_driver      = joblib.load('models/le_driver.pkl')
le_constructor = joblib.load('models/le_constructor.pkl')
le_circuit     = joblib.load('models/le_circuit.pkl')
FEATURES       = joblib.load('models/features.pkl')

class DriverEntry(BaseModel):
    driver: str
    constructor: str
    grid: int
    quali_position: int
    driver_champ_points: float
    driver_champ_pos: int
    constructor_champ_points: float
    constructor_champ_pos: int
    circuit_id: str
    round: int
    year: int

class RaceRequest(BaseModel):
    drivers: list[DriverEntry]

def encode_safe(encoder, value):
    if value in encoder.classes_:
        return encoder.transform([value])[0]
    return 0  # unknown → 0

@app.get("/")
def root():
    return {"status": "F1 Predictor API is running 🏎️"}

@app.post("/predict")
def predict(request: RaceRequest):
    results = []

    for entry in request.drivers:
        features = {
            'grid': entry.grid,
            'quali_position': entry.quali_position,
            'driver_champ_points': entry.driver_champ_points,
            'driver_champ_pos': entry.driver_champ_pos,
            'constructor_champ_points': entry.constructor_champ_points,
            'constructor_champ_pos': entry.constructor_champ_pos,
            'driver_enc': encode_safe(le_driver, entry.driver),
            'constructor_enc': encode_safe(le_constructor, entry.constructor),
            'circuit_enc': encode_safe(le_circuit, entry.circuit_id),
            'round': entry.round,
            'year': entry.year,
            'recent_avg_finish': entry.grid,        # approximation
            'constructor_recent_form': entry.constructor_champ_points / 10 if entry.constructor_champ_points else 5,
            'circuit_wins': 0,                       # unknown for future races
            'is_street': 0,                          # default
            'lat': 0.0,
            'lng': 0.0,
        }

        X = pd.DataFrame([features])[FEATURES]

        win_prob    = model_winner.predict_proba(X)[0][1]
        podium_prob = model_podium.predict_proba(X)[0][1]

        results.append({
            'driver': entry.driver,
            'constructor': entry.constructor,
            'win_probability': round(float(win_prob) * 100, 1),
            'podium_probability': round(float(podium_prob) * 100, 1),
        })

    results.sort(key=lambda x: x['win_probability'], reverse=True)
    return {"predictions": results}

@app.get("/drivers")
def get_drivers():
    return {"drivers": list(le_driver.classes_)}

@app.get("/constructors")
def get_constructors():
    return {"constructors": list(le_constructor.classes_)}