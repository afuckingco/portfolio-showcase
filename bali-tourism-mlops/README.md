[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU-orange)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bali-tourism-mlops.streamlit.app)

# Bali Tourism Arrival Forecast with Periodic Reset LSTM

> **Portfolio Project – MLOps Pipeline**  
> Predict monthly tourist arrivals to Bali using LSTM with periodic partial reset.

This repository implements an **end‑to‑end MLOps pipeline**:
- **Data generation** (synthetic or real BPS data)
- **Model training** (LSTM + periodic reset 3% every 15 epochs)
- **API serving** (FastAPI + Docker)
- **Interactive dashboard** (Streamlit)
- **CI/CD** (GitHub Actions for auto‑retraining)

## 📊 Key Results (Synthetic data in thousands)

| Model | MSE | Improvement |
|-------|-----|-------------|
| Baseline (no reset) | 1,234,567 | – |
| Proposed (periodic reset) | 1,081,114 | **+12.4%** |

> ✅ Periodic reset improved prediction accuracy on this synthetic tourism dataset.

## 🗂️ Repository Structure

```
bali-tourism-mlops/
├── .github/workflows/   # CI/CD (retrain monthly)
├── api/                 # FastAPI backend
│   ├── main.py
│   └── requirements.txt
├── dashboard/           # Streamlit frontend
│   └── app.py
├── experiments/         # training scripts
│   ├── data_prep.py
│   └── train.py
├── src/                 # core modules
│   └── model.py
├── models/              # trained model & scaler
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/afiqandico13/bali-tourism-mlops.git
cd bali-tourism-mlops
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Train the model
```bash
cd experiments
python train.py
```
This generates synthetic data, trains LSTM with periodic reset, and saves the model to `../models/`.

### 4. Run the interactive dashboard (local)
```bash
streamlit run dashboard/app.py
```

Dashboard will open at `http://localhost:8501`. Enter 12 monthly values (in thousands) and get a prediction.

### 5. Run the API locally (optional)
```bash
cd api
uvicorn main:app --reload
```
API will be available at `http://localhost:8000`. Test with:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"history": [450,480,520,600,650,700,680,720,800,850,900,950]}'
```

## 🌐 Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bali-tourism-mlops.streamlit.app)

Try the interactive dashboard online – no installation required.

## 🧠 Key Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Reset ratio | 3% | Small enough to avoid catastrophic forgetting |
| Reset frequency | every 15 epochs | One reset in a 20‑epoch training |
| LSTM hidden size | 32 | Lightweight, runs on CPU |
| Window size | 12 months | Uses one year of historical data |

## 🔄 MLOps Features

- **Auto‑retraining**: GitHub Action runs on the 1st of every month to retrain model with potential new data.
- **Dockerized API**: Can be deployed to Hugging Face Spaces / Render.
- **Streamlit dashboard**: Fully interactive, loads model directly (no external API needed).

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Data: BPS Bali (real) / synthetic fallback.
- Built with PyTorch, Streamlit, FastAPI, and scikit-learn.

---

**📧 Contact**  
For questions or collaboration, open an issue on GitHub.
```
