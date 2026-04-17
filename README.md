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

## 🔎 State of the Art (S3 — Related Work)

### 1) Similar products/prototypes (examples)

1. **Brandwatch Consumer Intelligence** — social listening and sentiment analytics across major social platforms.
2. **Sprout Social (Listening)** — sentiment/topic tracking and engagement analytics for social media teams.
3. **Hugging Face demo ecosystem** (e.g., sentiment + topic extraction Spaces) — open prototypes for text classification and keyword discovery.

### 2) Why these do not fully fit this use case

- **Cost and access**: enterprise tools are expensive for small creators.
- **Workflow mismatch**: many tools are built for brands/agencies, not quick creator-level CSV analysis.
- **Limited transparency/customization**: hosted products often hide pipeline details and are harder to adapt for course-specific experimentation.
- **Prototype gaps**: demo apps are useful references but often not end-to-end creator dashboards.

### 3) Reverse engineering: common stack used by others

- **LLMs / Transformer classifiers** for sentiment and zero-shot labeling.
- **Embedding models** (e.g., Sentence-Transformers/BERT variants) for semantic similarity and topic grouping.
- **RAG + Vector DBs** (e.g., Chroma/Pinecone/FAISS) in newer assistants to ground responses in retrieved comments/knowledge.
- **Dashboard layer** (often Streamlit/React) for upload, filtering, and insight visualization.

### 4) Reusable parts for this project

- Reuse open-source sentiment/topic models as baselines.
- Reuse embedding-based clustering/keyword patterns for grouping creator feedback.
- Reuse dashboard interaction patterns from existing social listening demos.

### 5) Our delta / contribution

- **Creator-first scope**: optimized for small TikTok creators (not enterprise marketing teams).
- **Fast CSV-to-insight loop**: upload comments and get sentiment + keywords + actionable content recommendations quickly.
- **Practical lightweight stack**: maintainable, transparent pipeline suitable for course delivery and future extension.

---

## 🗓️ Project Log

> *Updated every time a task is completed — follow the journey.*

| # | Milestone | Due Date | Project Deliverable | Status |
|---|-----------|----------|---------------------|--------|
| S1 | Introduction & NLP Landscape | March 27, 2026 | 📖 Introduced project idea; mapped TikTok creator pain point to the NLP problem space | ✅ Done |
| S2 | Problem Definition & Relevance | April 10, 2026 | 📌 Defined problem statement, user profile (1k–10k followers), SMART goals, NLP pipeline sketch, and non-goals | ✅ Done |
| S3 | State of the Art (SOTA) | April 17, 2026 | 🔎 Scouted comparable sentiment/NLP products, documented limitations, reverse-engineered common stack, defined project delta | ✅ Done |
| S4 | UX Design | April 24, 2026 | 🎨 Design Streamlit UI wireframes: file upload flow, sentiment dashboard, keyword view, recommendations panel | ⏳ Upcoming |
| S5 | Agile Workflow Planning | May 8, 2026 | 🗂️ Define sprints, user stories, and acceptance criteria for each pipeline component | ⏳ Upcoming |
| S6 | Data Strategy | May 15, 2026 | 📊 Source / generate sample TikTok comment CSVs; define preprocessing schema and data quality rules | ⏳ Upcoming |
| S7 | NLP Modeling (Isolated) | May 22, 2026 | 🧠 Implement and evaluate sentiment classifier + keyword extractor as standalone modules | ⏳ Upcoming |
| S8 | End-2-End System Architecture | June 5, 2026 | 🏗️ Connect preprocessing → NLP → Streamlit dashboard into a working end-to-end prototype | ⏳ Upcoming |
| S9 | Evaluation & Quality | June 12, 2026 | 🧪 Evaluate model accuracy, measure latency on 300-comment CSV, document quality metrics | ⏳ Upcoming |
| S10 | Optimizing your System | June 19, 2026 | ⚡ Profile bottlenecks, tune model/pipeline for speed and accuracy improvements | ⏳ Upcoming |
| S11 | Reflection & Storytelling | June 26, 2026 | 📝 Write project reflection; prepare narrative on learnings, trade-offs, and next steps | ⏳ Upcoming |
| S12 | Final Presentation | July 3, 2026 | 🎤 Deliver live demo and final presentation of the complete TikTok Creator Intelligence prototype | ⏳ Upcoming |

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
