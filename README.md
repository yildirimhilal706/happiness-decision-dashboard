# 🌍 Happiness Decision Dashboard

> **Where should you live?** An interactive decision-support dashboard built on the World Happiness Report (2015-2024). Pick your own priorities — see the world re-rank itself through your lens.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://happiness-decision-dashboard.streamlit.app/)

🔗 **Live demo:** [happiness-decision-dashboard.streamlit.app](https://happiness-decision-dashboard.streamlit.app/)

---

## ✨ Features

- 🎯 **Custom weighted scoring** — Adjust 6 KPIs with interactive sliders to reflect your priorities
- 👤 **Preset profiles** — Student, Retiree, Family, Entrepreneur, Balanced templates
- 🗺️ **Interactive world map** — Re-colors based on your custom KDS score
- 📊 **Side-by-side comparison** — Your ranking vs the official WHR ranking
- 🇹🇷 **Turkey deep dive** — Local context spotlight for Turkish readers
- 🏆 **Top 10 with real flags** — Powered by flagcdn.com
- 🔬 **K-means clustering** — Discover country groups via PCA + radar charts *(coming soon)*
- 🤖 **AI commentary** — Claude-generated insights on your custom ranking *(coming soon)*

---

## 🎯 The Problem

Traditional happiness rankings assume everyone weighs life factors the same way. But a 22-year-old student, a 65-year-old retiree, and a 35-year-old entrepreneur have wildly different priorities — yet they all see the same generic top-10 list.

This dashboard challenges that assumption.

## 🛠️ Tech Stack

- **Frontend:** Streamlit + Plotly + custom CSS
- **Data:** pandas, scikit-learn
- **Clustering:** K-means + PCA (from scikit-learn)
- **AI:** Anthropic Claude API *(in progress)*
- **Deploy:** Streamlit Cloud

## 📊 Methodology

1. **Normalization** — All 6 KPIs are min-max scaled to [0, 1]. Corruption is inverted (lower = better).
2. **Weighted scoring** — User-defined weights are applied: `KDS_score = Σ(weight_i × normalized_metric_i) × 10`
3. **Profile templates** — Pre-built weight configurations represent different life stages
4. **Clustering** — K-means (k=4) on 10-year average country profiles
5. **PCA projection** — 6D → 2D for visualization (75.2% variance retained)

## 🚀 Quick Start

```bash
git clone https://github.com/yildirimhilal706/happiness-decision-dashboard.git
cd happiness-decision-dashboard
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate    # macOS / Linux
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## 📁 Project Structure
## 📂 Data Source

- **Dataset:** [World Happiness 2015-2024 (Kaggle)](https://www.kaggle.com/datasets/hilalyldrm/happiness-decision)
- **Original report:** [worldhappiness.report](https://worldhappiness.report/)
- **License:** Educational and research use

## 📝 Articles

- 📖 [Medium (English) — *coming soon*]()
- 📖 [Medium (Türkçe) — *coming soon*]()

## 👥 Contributors

- **[@yildirimhilal706](https://github.com/yildirimhilal706)** — Lead developer, dashboard & deployment
- Co-developed with a Management Information Systems graduate

## 📜 License

MIT — see [LICENSE](LICENSE)

---

<p align="center">
  Built with curiosity, deployed with Streamlit, designed in earth tones.
</p>
