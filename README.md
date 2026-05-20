# 🏎️ F1 Race Predictor

> Predicting Formula 1 race winners & podium finishers using machine learning — wrapped in a real-time web interface.

---

## 🏁 What It Does

Enter any F1 driver lineup with qualifying positions, championship standings, and constructor data — the model instantly predicts:

- 🏆 **Race Winner** probability for each driver
- 🥉 **Podium** probability for each driver
- 📊 Ranked results with animated F1-themed visualization

The model is trained on **75 years of F1 race data (1950–2024)** covering 305+ races and 6,400+ driver entries.

---

## 🧠 How It Works

| Layer | Tech | Purpose |
|---|---|---|
| Data | Kaggle + FastF1 | Historical F1 data (1950–2024) |
| Model | XGBoost | Predicts winner & podium |
| Backend | FastAPI | Serves predictions via REST API |
| Frontend | React + Vite | Interactive race predictor UI |
| Styling | CSS + Framer Motion | F1-themed animations |

### 📈 Model Accuracy
- 🏆 Race Winner Model — **99% accuracy**
- 🥉 Podium Model — **97.7% accuracy**

### 🔑 Key Features Used by the Model

```
Grid position (starting place on race day)
Qualifying position
Driver championship standing & points
Constructor championship standing & points
Driver recent form (avg finish last 3 races)
Constructor recent form (avg points last 3 races)
Circuit history wins (how many times driver won here)
Street circuit flag (Monaco, Baku, Singapore, etc.)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone the repository
```bash
git clone https://github.com/danishhhh05/F1-Predictor.git
cd F1-Predictor
```

### 2. Start the backend
```bash
cd f1-predictor
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn api:app --reload
```

### 3. Start the frontend
```bash
cd f1-frontend
npm install
npm run dev
```

### 4. Open the app
Visit `http://localhost:5173` in your browser 🏁

API docs available at `http://localhost:8000/docs`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/predict` | Get race predictions |
| GET | `/drivers` | List all known drivers |
| GET | `/constructors` | List all constructors |

### Sample `/predict` Response
```json
{
  "predictions": [
    {
      "driver": "verstappen",
      "constructor": "red_bull",
      "win_probability": 42.3,
      "podium_probability": 87.1
    },
    {
      "driver": "leclerc",
      "constructor": "ferrari",
      "win_probability": 28.7,
      "podium_probability": 74.2
    }
  ]
}
```

---

## 📁 Project Structure

```
F1-Predictor/
├── f1-predictor/               # Python backend
│   ├── api.py                  # FastAPI server
│   ├── train_model.py          # ML training pipeline
│   ├── prepare_data.py         # Data processing
│   ├── collect_data.py         # FastF1 data collection
│   ├── data/                   # CSV datasets
│   └── models/                 # Trained XGBoost models
│
└── f1-frontend/                # React frontend
    └── src/
        ├── App.jsx             # Main UI component
        └── App.css             # F1-themed styles
```

---

## 🗺️ System Architecture

```
User Input (Driver Grid)
        |
        ▼
React Frontend  ──►  FastAPI Backend  ──►  XGBoost Model
(localhost:5173)      (localhost:8000)      (models/*.pkl)
        |                   |
        ▼                   ▼
  Animated UI          Race Results
  (Framer Motion)      (Win % + Podium %)
```

---

## 👤 Author

**Danish** — AI/ML Engineer
GitHub: [@danishhhh05](https://github.com/danishhhh05)

---

*Built with 🏎️ and way too much F1 data.*
