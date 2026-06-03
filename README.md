[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU-orange)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

# Energy Consumption Prediction with Periodic Partial Reset LSTM

> **Portfolio Project** – Adapting to sudden changes in household power usage.

This project implements **periodic partial reset** on LSTM to handle sudden concept drift in energy consumption forecasting. The method resets **3% of weights every 15 epochs**, helping the model adapt to regime changes.

## 📊 Key Results (Synthetic drift on UCI Household Power dataset)

| Model | MSE | Improvement |
|-------|-----|-------------|
| Baseline (no reset) | 1.7709 | – |
| Proposed (periodic reset) | 1.7693 | **+0.09%** |

> ⚠️ Periodic reset did **not** significantly improve performance (p = 0.842). This indicates that the method's effectiveness depends heavily on data characteristics.

## 🗂️ Repository Structure
energy-reset-lstm/
├── data/ # dataset (auto‑downloaded)
├── experiments/ # main_energy.py
├── src/ # data_loader, model, utils
├── dashboard/ # Streamlit app
├── results/ # boxplot and CSV
├── requirements.txt
└── README.md


## 🚀 Getting Started

```bash
git clone https://github.com/afiqandico13/energy-reset-lstm.git
cd energy-reset-lstm
pip install -r requirements.txt
python experiments/main_energy.py
streamlit run dashboard/app.py

📈 Visual Results
https://results/boxplot_energy.png

📜 License
MIT

