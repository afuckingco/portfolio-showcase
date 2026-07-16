```markdown
```console
┌──(test㉿afuckingco)-[~/projects/portfolio-showcase]
└─$ cat README.md
```

# 📊 Portfolio Showcase

> A consolidated multi-discipline portfolio: Machine Learning, Data Science, Security, Web, Embedded Systems, and GIS projects. Demonstrating end-to-end pipelines — from data ingestion and model training to deployment and interactive dashboards.

<div align="center">

[![Status](https://img.shields.io/badge/STATUS-CONSOLIDATED-a6e3a1?style=for-the-badge&labelColor=1e1e2e)]()
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![C](https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-89b4fa?style=for-the-badge&labelColor=1e1e2e)](LICENSE)

</div>

---

```console
┌──(test㉿afuckingco)-[~/projects/portfolio-showcase]
└─$ ./run-pipeline.sh --all
```

```text
[Pipeline] Data Ingestion → Feature Engineering → Model Training (XGBoost/LSTM/GRU/Prophet) → Evaluation → Dashboard/API Deployment
Modules Active: 15 | Architecture: Modular Monorepo | Status: OPERATIONAL
```

---

```console
┌──(test㉿afuckingco)-[~/projects/portfolio-showcase]
└─$ htop --modules
```

## ⚙️ Core Subprojects

| Subproject | Domain | Stack | Use Case |
|------------|--------|-------|----------|
| **[fraud-detection](./fraud-detection)** | FinTech / Security | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat) | XGBoost classification with interactive Streamlit dashboard for real-time transaction scoring. |
| **[bali-tourism-mlops](./bali-tourism-mlops)** | Time-Series / MLOps | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat) ![LSTM](https://img.shields.io/badge/LSTM-0075ca?style=flat) | Deep learning forecasting for regional tourism arrival trends with automated retraining pipelines. |
| **[kopikita](./kopikita)** | Business Analytics | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat) ![Prophet](https://img.shields.io/badge/Prophet-1f77b4?style=flat) | Café sales forecasting and RFM customer segmentation. |
| **[air-quality-gru-reset](./air-quality-gru-reset)** | Environmental / Research | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat) ![GRU](https://img.shields.io/badge/GRU-0075ca?style=flat) | PM2.5 air quality prediction with GRU + adaptive reset. |
| **[sentiment-streaming](./sentiment-streaming)** | NLP / Real-time | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat) ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat) | Real-time sentiment analysis stream with message brokers. |
| **[dvwa-portfolio](./dvwa-portfolio)** | Security / Documentation | `Markdown` / `Python` | Comprehensive security research writeup for DVWA. |
| **[signbridge-ai](./signbridge-ai)** | CV / ML | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat) ![CV](https://img.shields.io/badge/CV-ff6b6b?style=flat) | BISINDO sign language translation using real-time computer vision. |
| **[itb-stkom-research](./itb-stkom-research)** | Data Science / Research | `Orange` / `Python` | Academic research: campus management optimization (Marketing, HR, Ops) with classification. |
| **[inji-cho](./inji-cho)** | Web / GIS | ![JS](https://img.shields.io/badge/JS-F7DF1E?style=flat) ![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=flat) | Hidden Shrine Catalog — vanilla JS + Leaflet + Vite. |
| **[2TUFF.wav](./2TUFF.wav)** | Embedded / Multimedia | `C` / `PSP` | PSP homebrew WAV player with bugfixes + features (shuffle, queue, crossfade). |

---

## 🌐 Web Projects

### Static Business Sites — HTML/CSS only (no build, no frameworks)

Five self-contained `index.html` sites under `restaurant/`, `coffee-shop/`, `minimarket/`, `apotek/`, `perusahaan/`. Open `small-business.html` for a navigation hub.

| Folder | Business | Type |
|--------|----------|------|
| [`restaurant/`](restaurant/index.html) | Warung Rasa Nusantara | Restoran |
| [`coffee-shop/`](coffee-shop/index.html) | Kopi Senja | Kedai Kopi |
| [`minimarket/`](minimarket/index.html) | Toko Kita | Minimarket |
| [`apotek/`](apotek/index.html) | Apotek Sehat Farma | Apotek |
| [`perusahaan/`](perusahaan/index.html) | PT. Cipta Solusi Nusantara | Perusahaan IT |

### Full-stack / GIS

| Folder | Business | Stack | Type |
|--------|----------|-------|------|
| [`kecap-manalagi-dewata/`](kecap-manalagi-dewata/) | Kecap Manalagi Dewata | Next.js | E-commerce |
| [`inji-cho/`](inji-cho/) | Inji-cho — Hidden Shrine Catalog | Vanilla JS + Leaflet + Vite | GIS / Maps |

---

```console
┌──(test㉿afuckingco)-[~/projects/portfolio-showcase]
└─$ htop --stack
```

## 🛠️ Technology Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Core Languages** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) 3.9+ · ![C](https://img.shields.io/badge/C-00599C?style=flat&logo=c&logoColor=white) · ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white) | Multi-paradigm: data science, embedded systems, and web. |
| **Data Manipulation** | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white) / ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white) | High-performance data wrangling and numerical computation. |
| **Machine Learning** | ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white) / ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white) | Robust classical ML algorithms and flexible deep learning architectures. |
| **Deployment / UI** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) / ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) / ![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=next.js&logoColor=white) | Rapid API development, interactive dashboards, and full-stack web. |
| **Infrastructure** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) / ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white) | Containerized reproducibility and high-speed in-memory data streaming. |

---

```console
┌──(test㉿afuckingco)-[~/projects/portfolio-showcase]
└─$ ./setup.sh
```

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/afuckingco/portfolio-showcase.git
cd portfolio-showcase

# 2. Navigate to a specific project (e.g., fraud-detection)
cd fraud-detection

# 3. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# 4. Install project-specific dependencies
pip install -r requirements.txt

# 5. Run the project
python app.py  # or streamlit run dashboard.py
```
> **⚠️ Note:** Datasets are either synthetic, anonymized, or linked via external sources in each subproject's respective `README.md` to comply with privacy standards and repository size limits.

---

```console
┌──(test㉿afuckingco)-[~/projects/portfolio-showcase]
└─$ tree -L 2 -I 'venv|__pycache__|.ipynb_checkpoints|data'
```

## 📂 Project Structure

```text
portfolio-showcase/
├── fraud-detection/          # XGBoost + Streamlit pipeline
├── bali-tourism-mlops/       # LSTM forecasting & MLOps scripts
├── kopikita/                 # Prophet forecasting & RFM analysis
├── air-quality-gru-reset/    # GRU time-series research
├── sentiment-streaming/      # Redis-based NLP stream simulation
├── dvwa-portfolio/           # Security research documentation
├── signbridge-ai/            # BISINDO CV sign-language translation
├── itb-stkom-research/       # Academic data-science research
├── inji-cho/                 # Leaflet GIS web app
├── 2TUFF.wav/                # PSP homebrew WAV player (C)
├── restaurant/               # Static site — Warung Rasa Nusantara
├── coffee-shop/              # Static site — Kopi Senja
├── minimarket/               # Static site — Toko Kita
├── apotek/                   # Static site — Apotek Sehat Farma
├── perusahaan/               # Static site — PT. Cipta Solusi Nusantara
├── kecap-manalagi-dewata/    # Next.js e-commerce
├── small-business.html       # Navigation hub for static sites
├── LICENSE                   # MIT License
└── README.md                 # Master documentation (this file)
```

---

```console
┌──(test㉿afuckingco)-[~/projects/portfolio-showcase]
└─$ cat KNOWN_LIMITATIONS.md
```

## ⚠️ Known Limitations & Trade-offs

- **Monorepo Overhead**: While consolidated for organizational clarity, installing all dependencies globally may cause version conflicts. *Mitigation*: Always use isolated virtual environments per subproject.
- **Compute Requirements**: Deep learning modules (LSTM/GRU) require significant RAM/GPU resources for training. Inference scripts are optimized for CPU, but training should be done on accelerated hardware.
- **Data Drift**: Models trained on historical or synthetic data may experience performance degradation in live, production environments without continuous monitoring and retraining (MLOps).

---

## 📦 Releases

| Version | Date | Highlights |
|---------|------|------------|
| **[v1.0.0](https://github.com/afuckingco/portfolio-showcase/releases/tag/v1.0.0)** | 2026-07-16 | Initial consolidated release — 15 projects (ML, Security, Web, Embedded, GIS) merged into a single monorepo. |

> Releases track stable snapshots of the monorepo. Each subproject maintains its own changelog within its directory.

---

```console
┌──(test㉿afuckingco)-[~/projects/portfolio-showcase]
└─$ echo $ROADMAP
```

## 📈 Future Improvements

- [ ] **Unified MLOps Pipeline**: Implement MLflow or DVC across all subprojects for standardized experiment tracking and model versioning.
- [ ] **CI/CD Integration**: GitHub Actions workflows to automatically run unit tests and linting on PRs for each subdirectory.
- [ ] **Model Registry API**: A centralized FastAPI gateway to serve predictions from all deployed models in this showcase.
- [ ] **Enhanced Documentation**: Auto-generated API docs (Swagger/OpenAPI) for all deployable services.
- [ ] **GitHub Pages**: Deploy static business sites + inji-cho live via GitHub Pages.

---

```console
┌──(test㉿afuckingco)-[~/projects/portfolio-showcase]
└─$ connect --author
```

## 👤 Author

**afuckingco** — Security researcher, AI/ML engineer, and systems architect.

<div align="center">
  <a href="https://github.com/afuckingco" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" />
  </a>
  <a href="https://www.linkedin.com/in/afiq-andico" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
  </a>
  <a href="mailto:anotherwaltzcompany@gmail.com" target="_blank">
    <img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" />
  </a>
</div>

---

> *Data without context is noise. Models without deployment are just math. This is the bridge between the two.*

```console
┌──(test㉿afuckingco)-[~/projects/portfolio-showcase]
└─$ exit
```
> *Connection closed. Build something useful.*
```
