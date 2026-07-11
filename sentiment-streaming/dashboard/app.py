import streamlit as st
import redis
import json
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Konfigurasi Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

st.set_page_config(page_title="Sentiment Analysis Dashboard", layout="wide")
st.title("🗣️ Real-time Sentiment Analysis (Komentar Wisatawan)")

# Auto-refresh setiap 5 detik
st_autorefresh(interval=5000, key="refresh")

# Ambil semua data sentimen dari Redis
sentiment_data = []
keys = r.hkeys("sentiment_results")
for key in keys:
    val = r.hget("sentiment_results", key)
    if val:
        try:
            record = json.loads(val)
            sentiment_data.append(record)
        except:
            pass

if sentiment_data:
    df = pd.DataFrame(sentiment_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df.sort_values('timestamp', ascending=False)
    
    # Metrik
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Komentar", len(df))
    col2.metric("Positif", len(df[df['sentiment'] == 'POSITIVE']))
    col3.metric("Negatif", len(df[df['sentiment'] == 'NEGATIVE']))
    
    # Grafik pie
    fig_pie = px.pie(df, names='sentiment', title='Distribusi Sentimen', color='sentiment',
                     color_discrete_map={'POSITIVE':'green','NEGATIVE':'red'})
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Tabel komentar terbaru
    st.subheader("📋 Komentar Terbaru")
    st.dataframe(df[['text', 'sentiment', 'confidence']].head(10))
    
    # Grafik waktu (opsional)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df_time = df.groupby(df['timestamp'].dt.floor('S')).size().reset_index(name='count')
    fig_line = px.line(df_time, x='timestamp', y='count', title='Volume Komentar per Detik')
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("Belum ada data sentimen. Tunggu producer mengirim komentar...")