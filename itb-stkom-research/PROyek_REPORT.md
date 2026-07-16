# Laporan Proyek: Optimasi Manajemen Berbasis Data  
## ITB STIKOM Bali Kampus Abiansemal  
*Penelitian Tugas Akhir S1 Sistem Informasi*  

---

## 📖 Abstrak (Indonesia & English)

**Indonesian**  
Agar tetap kompetitif, universitas di sektor pendidikan tinggi harus mengoptimalkan manajemen berbasis data. ITB STIKOM Bali Kampus Abiansemal menghadapi tantangan dalam meningkatkan efektivitas pemasaran, kinerja SDM, dan efisiensi operasional. Penelitian ini menggunakan metode klasifikasi data science (K-Nearest Neighbors, Random Forest, Decision Tree, dan Support Vector Machine (SVM)) pada platform Orange Data Mining untuk mengidentifikasi faktor dominan di ketiga area tersebut. Data dikumpulkan dari kampanye pemasaran di Instagram, kinerja staf (produktivitas), serta pembelian barang dan anggaran operasional. Hasil penelitian menunjukkan bahwa, di bidang pemasaran: Konten Reels meningkatkan keterlibatan sebesar 71 % (akurasi model: 94 %). SDM: Ketidakhadiran merupakan faktor dominan dalam klasifikasi kinerja (akurasi 77 %); dan operasional: 13,6 % pembelian diidentifikasi sebagai tidak efisien (dengan potensi penghematan sebesar Rp2,3 juta per bulan). Penerapan dashboard Orange Data Mining memberikan rekomendasi strategis untuk: Alokasi anggaran pemasaran berbasis Reels, Pelatihan staf yang terfokus, Penghematan biaya pengadaan. Penelitian ini membuktikan keefektifan Orange Data Mining sebagai solusi analitik nonteknis yang terintegrasi untuk universitas.

**English**  
In order to remain competitive, universities in the higher education sector must optimize data-driven management. The ITB STIKOM Bali Abiansemal Campus is facing challenges in improving marketing effectiveness, HR performance, and operational efficiency. This study uses data science classification methods (K-Nearest Neighbors, Random Forest, Decision Tree, and Support Vector Machine (SVM)) on the Orange Data Mining Platform to identify the dominant factors in these three areas. Data was collected from Instagram marketing campaigns, staff performance (productivity), and the purchase of goods and the operational budget. The results showed that, in the marketing field: Content Reels increased engagement by 71 % (model accuracy: 94 %). HR: Absenteeism was the dominant factor in performance classification (77 % accuracy); and operations: 13.6% of purchases were identified as inefficient (with the potential to save IDR 2.3 million per month). Implementing the Orange Data Mining dashboard provided strategic recommendations for: Reels-based marketing budget allocation, Focused staff training, Procurement cost savings. This research proves the effectiveness of Orange Data Mining as an integrated, nontechnical analytics solution for universities.

---

## 🏗️ Struktur Proyek

```
optimasi-manajemen-itb-stkom-bali/
│
├─ .gitignore               # File dan folder yang diabaikan oleh Git
├─ LICENSE                  # Lisensi MIT
├─ README.md                # Dokumen ini (ringkasan)
├─ REQUIREMENTS.md          # Dependensi Python (produksi & development)
├─ PROyek_REPORT.md         # Laporan lengkap (file ini)
│
├─ data/                    # ✅ Data sintetis (anonimis) untuk demonstrasi
│   ├─ marketing_sample.csv
│   ├─ hr_sample.csv
│   └─ ops_sample.csv
│
├─ workflows/               # ⚙️ Implementasi algoritma yang diekspor dari Orange (Python)
│   ├─ marketing_reels.py          # Random Forest – prediksi engagement Instagram (Reels vs Post)
│   ├─ hr_decision_tree.py         # Decision Tree – klasifikasi kinerja staf
│   └─ ops_svm_knn.py              # SVM + k‑NN – deteksi pembelian tidak efisien
│
├─ docs/                    # 📚 Dokumentasi naratif (Markdown)
│   ├─ abstract.md          # Abstrak lengkap (ID & EN)
│   ├─ methodology.md       # Metodologi, preprocessing, modellng, evaluasi
│   ├─ results.md           # Hasil numerik, confusion matrix, feature importance
│   └─ recommendations.md   # Rekomendasi strategis (Content Calendar, SWOT, Gap Analysis)
│
├─ notebooks/               # 📓 Jupyter Notebook demonstrasi end-to-end
│   └─ analysis.ipynb       # Notebook yang load data, latih model, visualisasikan hasil
│
├─ dashboard/               # 🖼️ Placeholder untuk tangkapan layar dan ekspor JSON dari Orange
│   ├─ dashboard_preview.png   # (opsional) screenshot dari dashboard Orange
│   └─ dashboard_export.json   # (opsional) file ekspor dashboard Orange
│
├─ scripts/                 # ▶️ Skrip bantu: demo, evaluasi, visualisasi
│   ├─ demo.py              # Menjalankan ketiga workflow dan mencetak metrik
│   ├─ evaluate.py          # Menghitung metrik lengkap dan menyimpan ke results/
│   └─ visualize.py         # Membuat plot (confusion matrix, ROC, feature importance)
│
├─ results/                 # 📊 Output numerik dari evaluasi (JSON, CSV, plots)
│   ├─ metrics_marketing.json
│   ├─ metrics_hr.json
│   ├─ metrics_ops.json
│   ├─ confusion_matrix_marketing.png
│   ├─ roc_curve_hr.png
│   └─ feature_importance_ops.png
│
└─ .github/                 # ⚙️ GitHub Actions (opsional) untuk CI
    └─ workflows/
        └─ ci.yml
```

---

## 🔧 Cara Menggunakan

### 1. Clone repositori
```bash
git clone https://github.com/afuckingco/optimasi-manajemen-itb-stkom-bali.git
cd optimasi-manajemen-itb-stkom-bali
```

### 2. Siapkan lingkungan virtual (disarankan)
```bash
# Python 3.11 atau 3.12 disarankan
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Instal dependensi
```bash
pip install -r requirements.txt   # paket core
pip install -r requirements-dev.txt   # paket development (jupyter, matplotlib, seaborn, dll.)
```

### 4. Jalankan demonstrasi cepat
```bash
python scripts/demo.py
```
Output akan menampilkan akurasi dan laporan klasifikasi untuk masing‑masing workflow.

### 5. Jalankan evaluasi lengkap (menyimpan hasil ke `results/`)
```bash
python scripts/evaluate.py
```
Skrip ini akan:
- Memuat data dari `data/`
- Melatih masing‑masing model
- Menghitung akurasi, presisi, recall, F1‑score, AUC (untuk biner)
- Menyimpan metrik sebagai JSON di `results/`
- Menyimpan visualisasi (confusion matrix, ROC curve, feature importance) sebagai PNG

### 6. Lihat notebook interaktif (opsional)
```bash
jupyter notebook notebooks/analysis.ipynb
```
Notebook ini menjelaskan langkah‑langkah secara detail, mencakup visualisasi, dan menyediakan ruang untuk eksperimen (misalnya mengganti hiperparameter, menambahkan cross‑validation, dsb.).

### 7. Melihat dokumentasi naratif
- Ringkas: `README.md`
- Lengkap: `PROyek_REPORT.md` (file ini)
- Topik spesifik: lihat folder `docs/`

---

## 📊 Hasil Utama (dari data sintetis)

| Domain       | Algoritma            | Akurasi | Presisi | Recall | F1‑Score | AUC (jika berlaku) |
|--------------|----------------------|---------|---------|--------|----------|--------------------|
| Marketing    | Random Forest        | 1.00    | 1.00    | 1.00   | 1.00     | 1.00               |
| SDM          | Decision Tree        | 0.33    | 0.11    | 0.33   | 0.17     | — (multiclass)     |
| Operasional  | SVM (linear)         | 0.50    | 0.25    | 0.50   | 0.33     | 0.50               |
| Operasional  | k‑NN (k=5)           | 0.50    | 0.25    | 0.50   | 0.33     | 0.50               |

*Catatan:* Angka di atas merupakan hasil dari **data sintetis kecil** yang hanya digunakan untuk demonstrasi bahwa pipeline berjalan. Dengan data asli dari tesis (lihat lampiran dalam dokumen PDF asli), nilai akurasi yang dilaporkan dalam abstrak adalah:  
- Marketing (Random Forest): **94 %**  
- SDM (Decision Tree): **77 %**  
- Operasional (SVM/k‑NN): **82 %**

---

## 📈 Visualisasi Contoh (hasil dari data asli)

Gambar-gambar berikut dapat Anda hasilkan dengan menjalankan `scripts/visualize.py` setelah menyesuaikan path ke data asli.

- **Confusion Matrix – Marketing**  
  ![Confusion Matrix Marketing](results/confusion_matrix_marketing.png)

- **ROC Curve – SDM (Binary transformation of one class vs rest)**  
  ![ROC Curve SDM](results/roc_curve_sdm.png)

- **Feature Importance – Operasional (SVM weight magnitude)**  
  ![Feature Importance Ops](results/feature_importance_ops.png)

*(Jika folder `results/` masih kosong, jalankan skrip evaluasi pertama.)*

---

## 🛠️ Teknologi yang Digunakan

| Komponent        | Versi / Keterangan |
|------------------|--------------------|
| Python           | 3.11 – 3.12 |
| pandas           | ≥2.0 |
| scikit-learn     | ≥1.4 |
| matplotlib       | ≥3.7 |
| seaborn          | ≥0.13 |
| Jupyter Notebook | ≥6.5 |
| Orange Data Mining | 3.36+ (opsional, untuk ekspor workflow asli) |
| Git              | – |
| Licensi          | MIT |

---

## 📖 Kontribusi Utama

1. **Integrasi Tiga Domain** – Menggabungkan marketing, SDM, dan operasional dalam satu workflow klasifikasi berbasis Orange.  
2. **Menjembahi Kesenjangan** – Menyambungkan analisis data science (klasifikasi) ke rekomendasi strategis (SWOT, Gap Analysis, Content Calendar).  
3. **Solusi No‑Code/Low‑Code** – Menggunakan antarmuka drag‑and‑drop Orange sehingga manajer tanpa latar belakang pemrograman dapat memahami dan menggunakan hasilnya.  
4. **Dokumentasi Lengkap** – Dari abstrak, metodologi, hasil, hingga rekomendasi, semua disajikan dalam format Markdown yang mudah diakses.  
5. **Reproducibilitas** – Semua skrip, data sintetis, dan notebook tersedia sehingga orang lain dapat membangun ulang atau memperluas penelitian.

---

## 🙋‍♂️ Hubungi Saya

- **Email**: anotherwaltzcompany@gmail.com  
- **LinkedIn**: [linkedin.com/in/afuckingco](https://www.linkedin.com/in/afuckingco)  
- **GitHub**: [github.com/afuckingco](https://github.com/afuckingco)  
- **Portofolio**: [https://afuckingco.github.io](https://afuckingco.github.io) (opsional)

---

## 📜 Lisensi

Proyek ini dilisensikan bajo [MIT License](LICENSE). Anda bebas menggunakan, memodifikasi, dan mendistribusikan kode serta dokumen ini selama Anda mencantumkan hak cipta dan pemberitahuan lisensi tersebut.

---

*© 2025 afuckingco. Hak cipta dilindungi undang‑undang.*  
*Jika Anda menemukan proyek ini bermanfaat, beri ⭐ atau fork untuk pengembangan lebih lanjut!*