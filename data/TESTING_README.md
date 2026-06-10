# Test Datasets for TikTok Creator Intelligence

## Overview

Each beta tester gets **two files**: a comments CSV and a videos CSV.
Upload both for the full analysis — the videos file is what unlocks
niche-level insights (which of your content types performs best).

---

## Dataset Files

| Creator  | Followers | Comments | Niches | Files |
|----------|-----------|----------|--------|-------|
| **Tera** | 1,315 | 627 | Lifestyle, gifts, God's love, lip sync | `TERA_synthetic_data.csv` + `TERA_synthetic_videos.csv` |
| **Yetunde** | 108 | 300 | Makeup, dancing, lifestyle | `YETUNDE_synthetic_data.csv` + `YETUNDE_synthetic_videos.csv` |
| **Denzel** | 5,000 | 1,311 | Music, school, gaming | `DENZEL_synthetic_data.csv` + `DENZEL_synthetic_videos.csv` |
| **Wudh** | 7,000 | 1,067 | Germany, travel, Asian culture | `WUDH_synthetic_data.csv` + `WUDH_synthetic_videos.csv` |
| **Esther** | 4,000 | 1,299 | Dancing, football, Kenya | `ESTHER_synthetic_data.csv` + `ESTHER_synthetic_videos.csv` |
| **Basti** | 8,000 | 1,333 | African food, Berlin, travel | `BASTI_synthetic_data.csv` + `BASTI_synthetic_videos.csv` |
| **Judith** | 9,000 | 1,118 | Motivation, dancing, choir, Lagos life | `JUDITH_synthetic_data.csv` + `JUDITH_synthetic_videos.csv` |
| **Paul** | 10,000 | 1,013 | Cooking, nature, biking, fitness | `PAUL_synthetic_data.csv` + `PAUL_synthetic_videos.csv` |

Note: Tera's files are her **real scraped data** (not synthetic).

---

## How to Use

1. **Download** both of your creator's files (comments + videos)
2. **Go to the app** (link your creator provides)
3. **Sign up** with any username and password
4. **Upload your data**
   - Step 1: upload your **comments CSV**
   - Step 2: upload your **videos CSV** (optional but strongly recommended)
   - Step 3: click **Run Analysis**
5. **Explore the results**
   - **Dashboard**: overall sentiment, top keywords, summary stats
   - **Insights**: detailed findings, keyword clusters, example comments
   - **Recommendations**: which niche to lean on and why, what your audience asks for
6. **Give feedback** (see questions below)

---

## File Structure

**Comments CSV:**
```
Comment Text          — the actual comment
Comment Language      — language code (en = English)
Comment Like Count    — likes on this comment
Author Nickname       — commenter's handle
video_type            — content category
comment_date          — when posted
video_id              — which video it belongs to
```

**Videos CSV** (same schema as the real scraper output):
```
video_id, description, view_count, like_count, comment_count,
share_count, upload_date, hashtags, url, scraped_at, video_type
```

---

## What Makes This Data Realistic

- **Niche-specific comments** — makeup comments on makeup videos, travel comments on travel videos
- **Real engagement differences** — each creator has content types that genuinely outperform others, like real accounts do
- **Explicit audience requests** — comments like "teach me german", "recipe please", "tutorial for this choreo" at realistic rates
- **Mild critiques** — a small share of comments mention fixable issues (audio, captions, length)
- **Realistic like counts** — most comments get 0 likes, a few get many

---

## Feedback Questions

After testing, please answer:

1. **Sentiment**: did the positive/negative/neutral percentages seem right?
2. **Keywords**: were the top keywords actually relevant to the content?
3. **Recommendations**: were they specific and actionable — could a real creator change their content plan based on them?
4. **Niche insights**: did the app correctly identify which content type performs best?
5. **UI/UX**: was the app easy to use?
6. **Bugs**: did anything crash or break?

---

**Generated:** June 2026
**For:** TikTok Creator Intelligence Beta Testing
