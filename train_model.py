import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import joblib
import os

# Load data
df = pd.read_csv('data/processed_data.csv')
pit_stops = pd.read_csv('data/pit_stops.csv')
circuits = pd.read_csv('data/circuits.csv')

print(f"📊 Dataset: {df.shape[0]} rows")

# ── Extra feature: avg pit stops per driver per race ──────────
pit_counts = pit_stops.groupby(['raceId', 'driverId'])['stop'].max().reset_index()
pit_counts.columns = ['raceId', 'driverId', 'pit_stop_count']

races = pd.read_csv('data/races.csv')
results_raw = pd.read_csv('data/results.csv')
pit_counts = pit_counts.merge(results_raw[['raceId','driverId']], on=['raceId','driverId'], how='left')
df = df.merge(pit_counts, on=['raceId'], how='left')

# ── Extra feature: circuit info (country/location type) ───────
circuits['is_street'] = circuits['name'].str.contains(
    'Monaco|Singapore|Baku|Melbourne|Adelaide', case=False).astype(int)
df = df.merge(circuits[['circuitId', 'is_street', 'lat', 'lng']],
              on='circuitId', how='left')

# ── Extra feature: driver's recent form (avg finish last 3 races) ──
df = df.sort_values(['driverRef', 'year', 'round'])
df['recent_avg_finish'] = (
    df.groupby('driverRef')['positionOrder']
    .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
)

# ── Extra feature: constructor's recent form ──────────────────
df['constructor_recent_form'] = (
    df.groupby('constructorRef')['points']
    .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
)

# ── Extra feature: driver's historical wins at this circuit (no leakage) ──
df = df.sort_values(['year', 'round'])
df['circuit_wins'] = df.groupby(['driverRef', 'circuitId'])['won_race'].transform(
    lambda x: x.shift(1).cumsum().fillna(0)
)

# ── Encode categoricals ───────────────────────────────────────
le_driver      = LabelEncoder()
le_constructor = LabelEncoder()
le_circuit     = LabelEncoder()

df['driver_enc']      = le_driver.fit_transform(df['driverRef'])
df['constructor_enc'] = le_constructor.fit_transform(df['constructorRef'])
df['circuit_enc']     = le_circuit.fit_transform(df['circuitId'].astype(str))

# ── Feature list (expanded) ───────────────────────────────────
FEATURES = [
    'grid',
    'quali_position',
    'driver_champ_points',
    'driver_champ_pos',
    'constructor_champ_points',
    'constructor_champ_pos',
    'driver_enc',
    'constructor_enc',
    'circuit_enc',
    'round',
    'year',
    'recent_avg_finish',
    'constructor_recent_form',
    'circuit_wins',
    'is_street',
    'lat',
    'lng',
]

df_clean = df.dropna(subset=['grid', 'positionOrder', 'quali_position'])
df_clean = df_clean.fillna(df_clean.median(numeric_only=True))

# ── Train/test split ──────────────────────────────────────────
train = df_clean[df_clean['year'] <= 2022]
test  = df_clean[df_clean['year'] >= 2023]

X_train = train[FEATURES]
X_test  = test[FEATURES]

# ── Tuned hyperparameters ─────────────────────────────────────
WINNER_PARAMS = {
    'n_estimators': 500,
    'max_depth': 6,
    'learning_rate': 0.03,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'min_child_weight': 5,
    'scale_pos_weight': 20,
    'eval_metric': 'logloss',
    'random_state': 42,
}

PODIUM_PARAMS = {
    'n_estimators': 500,
    'max_depth': 6,
    'learning_rate': 0.03,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'min_child_weight': 3,
    'scale_pos_weight': 6,
    'eval_metric': 'logloss',
    'random_state': 42,
}

# ── Model 1: Race Winner ──────────────────────────────────────
print("\n🏆 Training Race Winner model...")
y_train_win = train['won_race']
y_test_win  = test['won_race']

model_winner = xgb.XGBClassifier(**WINNER_PARAMS)
model_winner.fit(
    X_train, y_train_win,
    eval_set=[(X_test, y_test_win)],
    verbose=False
)
pred_win  = model_winner.predict(X_test)
print(f"  ✅ Accuracy: {accuracy_score(y_test_win, pred_win):.3f}")
print(classification_report(y_test_win, pred_win, target_names=['No Win', 'Win']))

# ── Model 2: Podium ───────────────────────────────────────────
print("\n🥉 Training Podium model...")
y_train_pod = train['podium']
y_test_pod  = test['podium']

model_podium = xgb.XGBClassifier(**PODIUM_PARAMS)
model_podium.fit(
    X_train, y_train_pod,
    eval_set=[(X_test, y_test_pod)],
    verbose=False
)
pred_pod = model_podium.predict(X_test)
print(f"  ✅ Accuracy: {accuracy_score(y_test_pod, pred_pod):.3f}")
print(classification_report(y_test_pod, pred_pod, target_names=['No Podium', 'Podium']))

# ── Save everything ───────────────────────────────────────────
os.makedirs('models', exist_ok=True)
joblib.dump(model_winner,   'models/model_winner.pkl')
joblib.dump(model_podium,   'models/model_podium.pkl')
joblib.dump(le_driver,      'models/le_driver.pkl')
joblib.dump(le_constructor, 'models/le_constructor.pkl')
joblib.dump(le_circuit,     'models/le_circuit.pkl')
joblib.dump(FEATURES,       'models/features.pkl')

print("\n✅ All improved models saved!")

# ── Feature importance ────────────────────────────────────────
print("\n📈 Top features for predicting race winner:")
importance = pd.Series(model_winner.feature_importances_, index=FEATURES)
print(importance.sort_values(ascending=False).to_string())