<div align="center">

# ✨ TikTok Creator Intelligence

**Turning comment noise into content clarity — one insight at a time.**

![Status](https://img.shields.io/badge/status-in%20development-f9a8d4?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-c084fc?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/streamlit-app-fb7185?style=for-the-badge&logo=streamlit&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-university%20project-a78bfa?style=for-the-badge)
![Last Updated](https://img.shields.io/badge/last%20updated-April%202026-f0abfc?style=for-the-badge)

</div>

---

## 💡 The Problem

> *Small TikTok creators struggle to extract meaningful insights from user comments because the feedback is unstructured, scattered, and difficult to analyze manually.*

Comments are gold — but only if you can read them at scale. A creator posting three times a week can receive hundreds of comments per video: some love it, some have questions, some have complaints. Reading every single one and spotting patterns? Nearly impossible manually.

This project builds a tool that does exactly that.

---

## 👤 Who Is This For?

A **small TikTok creator** (1k–10k followers) who:
- Posts content regularly and wants to grow
- Currently guesses what resonates based on likes and gut feeling
- Has **no time** to manually read and categorize hundreds of comments
- Wants **real, data-backed feedback** from their audience

---

## 🗺️ How It Works

```
📥 INPUT                    🧠 NLP PIPELINE               📊 OUTPUT
─────────────────────────   ──────────────────────────    ─────────────────────────────
CSV file with TikTok     →  1. Text Preprocessing      →  Sentiment distribution
comments + video metrics    2. Sentiment Analysis           (e.g. 70% positive)
(likes, views)              3. Keyword Extraction       →  Top topics from comments
                                                        →  Audience insights
                                                        →  Content recommendations
```

---

## 🎯 Goals

### Main Goal
By **July 2026**, deliver a working web-based NLP prototype that:
- Accepts a CSV file of TikTok comments
- Returns sentiment summaries, keyword insights & content recommendations
- Processes up to **300 comments** in a matter of seconds

### Sub-Goals
- [ ] Build a **text preprocessing pipeline** (cleaning, normalization, tokenization)
- [ ] Implement **sentiment classification** — positive, negative, neutral
- [ ] Develop a clean **Streamlit interface** for file upload and insight display
- [ ] Generate simple, actionable **content recommendations** from patterns

### Out of Scope
- ❌ No TikTok API integration — data is CSV-based
- ❌ No custom deep learning model training
- ❌ No mobile app

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3.10+ |
| Web Interface | Streamlit |
| NLP | spaCy, NLTK |
| Data Processing | pandas, scikit-learn |
| Visualization | matplotlib / plotly |

---

## 🗓️ Project Log

> *Updated every time a task is completed — follow the journey.*

| Date | Task | Status |
|------|------|--------|
| April 10, 2026 | 📌 Project scoping — defined problem statement, user profile, SMART goals, NLP pipeline sketch, and non-goals | ✅ Done |

---

## 🚀 Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the Streamlit app
streamlit run app/main.py
```

---

## 📁 Project Structure

```
tiktok-creator-intelligence/
├── app/                  # Streamlit app (coming soon)
├── data/                 # Sample CSV data (coming soon)
├── notebooks/            # Exploration & development notebooks
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 📄 Documentation

Full project documentation (PDF) will be added upon completion of the course.

---

<div align="center">

Made with 💜 by **Chinelo Lydia Nweke**  
NLP Course Project · Spring 2026

</div>
