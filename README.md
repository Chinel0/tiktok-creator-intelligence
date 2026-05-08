<div align="center">

# TikTok Creator Intelligence

**Turning comment noise into content clarity — one insight at a time.**

![Status](https://img.shields.io/badge/status-in%20development-f9a8d4?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-c084fc?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/streamlit-app-fb7185?style=for-the-badge&logo=streamlit&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-university%20project-a78bfa?style=for-the-badge)
![Last Updated](https://img.shields.io/badge/last%20updated-April%202026-f0abfc?style=for-the-badge)

</div>

---

## The Problem

> *Small TikTok creators struggle to extract meaningful insights from user comments because the feedback is unstructured, scattered, and difficult to analyze manually.*

Comments are gold — but only if you can read them at scale. A creator posting three times a week can receive hundreds of comments per video: some love it, some have questions, some have complaints. Reading every single one and spotting patterns? Nearly impossible manually.

This project builds a tool that does exactly that.

---

## Who Is This For?

A **small TikTok creator** (1k–10k followers) who:
- Posts content regularly and wants to grow
- Currently guesses what resonates based on likes and gut feeling
- Has **no time** to manually read and categorize hundreds of comments
- Wants **real, data-backed feedback** from their audience

---

## How It Works

```
INPUT                     NLP PIPELINE                  OUTPUT
─────────────────────────   ──────────────────────────    ─────────────────────────────
CSV file with TikTok     →  1. Text Preprocessing      →  Sentiment distribution
comments + video metrics    2. Sentiment Analysis           (e.g. 70% positive)
(likes, views)              3. Keyword Extraction       →  Top topics from comments
                                                        →  Audience insights
                                                        →  Content recommendations
```

---

## Goals

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
- No TikTok API integration — data is CSV-based
- No custom deep learning model training
- No mobile app

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3.10+ |
| Web Interface | Streamlit |
| NLP | spaCy, NLTK |
| Data Processing | pandas, scikit-learn |
| Visualization | matplotlib / plotly |

---

## State of the Art (S3 — Related Work)

### 1) Existing products / prototypes

1. **Hootsuite Insights**
   - Social media monitoring and sentiment analysis.
   - Tracks audience reactions and trends across channels.
   - Strong for brand-level listening and reporting workflows.
2. **Brandwatch**
   - AI-based sentiment and trend analysis.
   - Large-scale social media analytics with enterprise dashboards.
   - Supports deep segmentation and long-horizon brand monitoring.
3. **MonkeyLearn**
   - Sentiment analysis and keyword extraction.
   - General-purpose NLP workflow for business text analytics.
   - Useful as a flexible baseline for text classification pipelines.

### 2) Limitations of existing solutions

- Designed primarily for large companies, not small creators.
- Expensive and not easily accessible for early-stage creator budgets.
- Not tailored to TikTok-specific content and creator workflows.
- Strong on visualization, weaker on direct actionable guidance.
- Do not consistently connect comments to concrete content strategy decisions.

### 3) Reverse engineering (common tech stack)

**Methods used**
- Sentiment analysis (text classification: positive, negative, neutral).
- Keyword extraction (TF-IDF, frequency-based methods).
- Topic clustering and trend tracking over time windows.

**Models / tools**
- BERT-family models for contextual text understanding.
- spaCy and scikit-learn for preprocessing, vectorization, and baseline modeling.
- Rule-based normalization and lightweight statistical features for fast iteration.

**Interface patterns**
- Web dashboards for upload, filtering, and visualization.
- Time-series panels for trend movement and topic shifts.
- Export and reporting views for decision support.

### 4) Parts I can reuse

- Text preprocessing pipeline (cleaning and normalization).
- Sentiment classification methods.
- Keyword extraction techniques.
- Basic dashboard structure for displaying results.

### 5) My contribution (delta)

- Focus on small TikTok creators (1k-10k followers).
- Simple and accessible system using CSV input.
- Links comments to individual video performance.
- Generates actionable insights, not just data.
- Helps creators decide what content and niche to focus on.

---

## UX Design (S4)

The UX is designed as a simple flow from upload to action, so creators can move from raw comments to clear content decisions quickly.

### Screen 1 — Dashboard Overview 
After processing, the dashboard gives a high-level summary of sentiment and key performance signals.

![Dashboard Screen Screen](https://github.com/user-attachments/assets/e8a4d398-fd4e-4fae-ba78-4236effe5e8f)

### Screen 2 —  Upload File
The user starts by uploading a CSV with TikTok comments and metrics. The main goal is a fast, low-friction entry point.

![Upload File](https://github.com/user-attachments/assets/8f1e916d-2c28-4755-923e-65283cb3b2cd)

### Screen 3 — Insight Details
This screen highlights top keywords, themes, and deeper audience feedback patterns.

![Insight Screen](https://github.com/user-attachments/assets/5d26322e-a3fc-4b03-a97c-029cea1d3c83)

### Screen 4 — Recommendation
On this screen you see a recommendation of what you can do right.
<img src="https://github.com/user-attachments/assets/4bf9de88-239f-4655-a683-a4e7884c2aaf" alt="Recommendations view showing next-post ideas based on analysis">

### Clear User Flow
1. Upload TikTok comment CSV  
2. Run preprocessing and sentiment analysis  
3. Review dashboard summary  
4. Explore detailed keyword/theme insights  
5. Act on recommendations for next content

At the last step, users see a recommendations view that converts the analysis into next-post ideas.

![User Flow Diagram](https://github.com/user-attachments/assets/e48451b0-6098-4fed-a84c-566fb8462953)

Read more about the UX design in [`documents/ux design.md`](documents/ux%20design.md).

---

## Project Log

> *Updated every time a task is completed — follow the journey.*

| # | Milestone | Due Date | Project Deliverable | Status |
|---|-----------|----------|---------------------|--------|
| S1 | Introduction & NLP Landscape | March 27, 2026 | Introduced project idea; mapped TikTok creator pain point to the NLP problem space | Done |
| S2 | Problem Definition & Relevance | April 10, 2026 | Defined problem statement, user profile (1k-10k followers), SMART goals, NLP pipeline sketch, and non-goals | Done |
| S3 | State of the Art (SOTA) | April 17, 2026 | Scouted comparable sentiment/NLP products, documented limitations, reverse-engineered common stack, defined project delta | Done |
| S4 | UX Design | April 24, 2026 | Design Streamlit UI wireframes: file upload flow, sentiment dashboard, keyword view, recommendations panel | Done |
| S5 | Agile Workflow Planning | May 8, 2026 | Define sprints, user stories, and acceptance criteria for each pipeline component | Upcoming |
| S6 | Data Strategy | May 15, 2026 | Source / generate sample TikTok comment CSVs; define preprocessing schema and data quality rules | Upcoming |
| S7 | NLP Modeling (Isolated) | May 22, 2026 | Implement and evaluate sentiment classifier + keyword extractor as standalone modules | Upcoming |
| S8 | End-2-End System Architecture | June 5, 2026 | Connect preprocessing -> NLP -> Streamlit dashboard into a working end-to-end prototype | Upcoming |
| S9 | Evaluation & Quality | June 12, 2026 | Evaluate model accuracy, measure latency on 300-comment CSV, document quality metrics | Upcoming |
| S10 | Optimizing your System | June 19, 2026 | Profile bottlenecks, tune model/pipeline for speed and accuracy improvements | Upcoming |
| S11 | Reflection & Storytelling | June 26, 2026 | Write project reflection; prepare narrative on learnings, trade-offs, and next steps | Upcoming |
| S12 | Final Presentation | July 3, 2026 | Deliver live demo and final presentation of the complete TikTok Creator Intelligence prototype | Upcoming |

---

## Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the Streamlit app
streamlit run app/main.py
```

---

## Project Structure

```
tiktok-creator-intelligence/
├── app/                  # Streamlit app (coming soon)
├── data/                 # Sample CSV data (coming soon)
├── notebooks/            # Exploration & development notebooks
├── requirements.txt      # Python dependencies
└── README.md
```

---

## Documentation

Full project documentation (PDF) will be added upon completion of the course.

---

<div align="center">

Made by **Chinelo Lydia Nweke**  
NLP Course Project · Spring 2026

</div>
