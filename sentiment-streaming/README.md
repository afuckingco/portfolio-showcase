# Real-Time Sentiment Analysis Streaming

> **Portfolio Project #6** – Streaming komentar wisatawan, analisis sentimen real-time, dan dashboard interaktif.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Redis](https://img.shields.io/badge/Redis-3.0%2B-red)](https://redis.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🎯 Deskripsi Proyek

Sistem ini mensimulasikan **streaming komentar wisatawan** secara real-time menggunakan Redis sebagai antrian pesan. Komentar diproses oleh **consumer** yang melakukan analisis sentimen (positif, netral, negatif) dengan **TextBlob** (berbasis rule, mendukung bahasa Inggris). Hasilnya ditampilkan di **dashboard Streamlit** yang memperbarui setiap 2 detik.

Proyek ini menunjukkan kemampuan:
- **Real-time data streaming** dengan Redis
- **Natural Language Processing** (sentiment analysis)
- **Arsitektur producer‑consumer**
- **Visualisasi interaktif** dengan Plotly + Streamlit

## 🗂️ Struktur Proyek
sentiment-streaming/
├── data/ # CSV history (auto-generated)
├── dashboard/
│ └── app.py # Streamlit dashboard
├── consumer.py # Mendengar komentar dari Redis, analisis sentimen
├── producer.py # Menghasilkan komentar acak (positif/netral/negatif)
├── requirements.txt
├── .gitignore
└── README.md

text

## 🚀 Cara Menjalankan (Lokal)

### 1. Clone repositori
git clone https://github.com/afuckingco/sentiment-streaming.git
cd sentiment-streaming
### 2. Install dependencies
pip install -r requirements.txt
### 3. Jalankan Redis server
Windows: Download Redis for Windows lalu jalankan redis-server.exe.

Mac/Linux: sudo apt install redis-server lalu redis-server.

Pastikan Redis berjalan di localhost:6379.

### 4. Jalankan consumer (terminal 1)
bash
python consumer.py
Consumer akan menunggu komentar dari antrian comments_queue dan menyimpan hasil sentimen ke Redis hash sentiment_results serta file CSV.

### 5. Jalankan producer (terminal 2)
bash
python producer.py
Producer mengirim komentar acak (dalam bahasa Inggris) ke antrian Redis setiap 2 detik.

### 6. Jalankan dashboard (terminal 3)
bash
streamlit run dashboard/app.py
Dashboard akan terbuka di http://localhost:8501 dan memperbarui setiap 2 detik secara otomatis.

## 📊 Fitur Dashboard
Total komentar, jumlah positif, negatif, netral

Pie chart distribusi sentimen

Tabel komentar terbaru dengan skor kepercayaan

Grafik volume komentar per detik (real-time)

## 🧠 Teknologi yang Digunakan
Komponen	Tools/Library
Streaming	Redis (queue)
Sentimen	TextBlob (polarity threshold)
Dashboard	Streamlit + Plotly
Bahasa	Inggris (agar TextBlob optimal)
## 📈 Contoh Hasil
https://screenshot.png (screenshot opsional)

## 🔮 Pengembangan Lebih Lanjut
Ganti TextBlob dengan model transformer multilingual (IndoBERT) untuk dukungan bahasa Indonesia.

Gunakan Redis Cloud agar dashboard bisa di‑deploy sepenuhnya ke cloud.

Tambahkan visualisasi sentimen over time (line chart per jam/hari).

## 📜 Lisensi
MIT License – lihat file LICENSE.
