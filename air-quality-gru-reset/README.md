[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU-orange)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://air-quality-gru-reset-auuktdz2tgppthngddibmm.streamlit.app/)

# Air Quality (PM2.5) Prediction with Periodic GRU Reset

> **Portfolio Project** – Using GRU with periodic partial reset to handle sudden concept drift.

This repository implements **periodic partial reset** on a Gated Recurrent Unit (GRU) network for PM2.5 air quality forecasting. The method resets **3% of weights every 15 epochs** to help the model adapt to sudden changes (e.g., new environmental policies, seasonal shifts). 

## 📊 Key Results (Synthetic PM2.5 data with sudden drift)

| Model | MSE | Improvement | p‑value |
|-------|-----|-------------|---------|
| Baseline (no reset) | 5192.34 | – | – |
| Proposed (periodic reset) | 5386.00 | **-3.73%** | <0.001 |

> ⚠️ **Note:** Periodic reset **worsened** performance significantly. This negative result is still valuable – it highlights the sensitivity of the method to dataset characteristics and parameter choices. With proper tuning (e.g., lower reset ratio, different frequency), the method might yield positive gains.

## 🗂️ Repository Structure

air-quality-gru-reset/
├── data/ # dataset (auto‑downloaded or synthetic)
├── experiments/ # main experiment script
│ └── main_air_quality.py
├── src/ # core modules
│ ├── data_loader.py # download/preprocess PM2.5 data
│ ├── model.py # GRU + periodic reset logic
│ └── utils.py # metrics, plotting
├── dashboard/ # Streamlit interactive dashboard
│ └── app.py
├── results/ # output CSV and plots (auto‑generated)
├── requirements.txt
├── .gitignore
└── README.md



## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/afiqandico13/air-quality-gru-reset.git
cd air-quality-gru-reset

2. Create a virtual environment and install dependencies
bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# or
venv\Scripts\activate       # Windows

pip install -r requirements.txt

3. Run the main experiment
bash
cd experiments
python main_air_quality.py
This will either download the real Beijing PM2.5 dataset (if network permits) or generate synthetic data, inject a sudden drift at 70% of the series, and compare baseline vs periodic reset GRU over 30 bootstrap iterations.

4. Launch the interactive dashboard
bash
streamlit run dashboard/app.py
The dashboard lets you adjust drift factor, reset parameters, and see predictions in real time.

📈 Visual Results
https://results/boxplot_air.png

Boxplot of MSE over 30 iterations – baseline vs proposed.

🧠 Key Parameters
Parameter	Value	Rationale
Reset ratio	3%	Small enough to avoid catastrophic forgetting, adjustable
Reset frequency	every 15 epochs	One reset in a 20‑epoch training
GRU hidden size	32	Lightweight, runs on CPU
Window size	24 hours	One day of past data
🌐 Live Demo
Try the interactive dashboard online (after Streamlit Cloud deployment):
https://static.streamlit.io/badges/streamlit_badge_black_white.svg

No installation required – just click the badge!

📜 License
This project is licensed under the MIT License – see the LICENSE file for details.

🙏 Acknowledgements
Dataset: Beijing PM2.5 from UCI Machine Learning Repository (or synthetic fallback).

Built with PyTorch, Streamlit, and scikit-learn.

📧 Contact
For questions or collaboration, please open an issue on GitHub.

text

---

## 🔧 Langkah Terakhir

1. **Simpan** file `README.md` di folder proyek.
2. **Commit dan push** ke GitHub:
   ```bash
   git add README.md
   git commit -m "Add professional README"
   git push origin main
