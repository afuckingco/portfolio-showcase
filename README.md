# Bali Tourism MLOps Pipeline

Predict tourist arrivals to Bali using LSTM with periodic partial reset.

## Deployment

- API: (Render URL)
- Dashboard: (Streamlit URL)

## Local Setup

```bash
git clone https://github.com/afiqandico13/bali-tourism-mlops.git
cd bali-tourism-mlops
pip install -r requirements.txt
cd experiments
python train.py
cd ../api
uvicorn main:app --reload
cd ../dashboard
streamlit run app.py