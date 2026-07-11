[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-FF6B6B)](https://xgboost.ai)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://fraud-detection.streamlit.app)   <!-- Ganti dengan URL setelah deploy -->

# 💳 Credit Card Fraud Detection with XGBoost & SMOTE

> **Portfolio Project #7** – Imbalanced classification to detect fraudulent transactions.

This project tackles the extreme class imbalance problem (only 0.17% fraud) using **SMOTE** oversampling and **XGBoost** classifier. It includes a training pipeline, a FastAPI endpoint, and an interactive Streamlit dashboard.

## 📊 Key Results (on test set)

| Metric | Value |
|--------|-------|
| **Recall (fraud)** | 0.88 |
| **Precision (fraud)** | 0.09 |
| **F2‑Score** | 0.35 |
| **AUC‑ROC** | 0.97 |

> 🎯 *Recall is prioritised because missing a fraudulent transaction is more costly than a false alarm (F2‑score confirms this business logic).*

## 🗂️ Repository Structure

```
fraud-detection/
├── data/                  # creditcard.csv (ignored by git)
├── src/
│   └── train.py           # data loading, SMOTE, XGBoost training
├── api/
│   └── main.py            # FastAPI prediction endpoint
├── dashboard/
│   └── app.py             # Streamlit dashboard
├── models/                # trained model & scaler (joblib)
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/afiqandico13/fraud-detection.git
cd fraud-detection
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Download the dataset
- Go to [Kaggle Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- Download `creditcard.csv` and place it in the `data/` folder.

### 4️⃣ Train the model
```bash
python src/train.py
```
This will:
- Load and split the data
- Apply SMOTE to balance the classes
- Train an XGBoost classifier
- Save the model and scaler to `models/`

### 5️⃣ Run the FastAPI (optional)
```bash
uvicorn api.main:app --reload
```
Test with `curl`:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [0.5, -1.2, 0.3, ... (30 numbers)]}'
```

### 6️⃣ Launch the Streamlit dashboard
```bash
streamlit run dashboard/app.py
```
Upload a CSV file with 30 features (the model will auto‑remove the `Class` column if present).

## 📈 How It Works

1. **Exploratory data analysis** – check class distribution, scale features.
2. **SMOTE** – synthetic minority oversampling to balance the training set.
3. **XGBoost** – gradient boosting with `scale_pos_weight` for extra imbalance handling.
4. **Evaluation** – focus on **recall** (fraction of frauds caught) and **precision**.
5. **Deployment** – model saved as `joblib` and loaded by FastAPI + Streamlit.

## 🌐 Live Demo (Streamlit Cloud)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://fraud-detection.streamlit.app)  
*Note: The demo uses a pre‑trained model; the dataset is not uploaded due to size.*

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file.

## 🙏 Acknowledgements

- **Dataset:** [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) by ULB Machine Learning Group.
- **Libraries:** `xgboost`, `imbalanced-learn`, `scikit-learn`, `streamlit`, `fastapi`.

---

## 📧 Contact & Portfolio

**Afiq Andico**  
[![GitHub](https://img.shields.io/badge/GitHub-afiqandico13-181717)](https://github.com/afiqandico13) 
[![Email](https://img.shields.io/badge/Email-afiqandico13%40gmail.com-D14836)](mailto:afiqandico13@gmail.com)

---

*“Consistency over intensity – 2 days, 2 hours, forever.”*
```
