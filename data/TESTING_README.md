# Synthetic Test Datasets for TikTok Creator Intelligence

## Overview

8 personalized synthetic datasets, one for each beta tester. Each CSV contains realistic TikTok comments from a creator in their niche.

**Total:** 8,266 comments across 8 creators

---

## Dataset Files

| Creator  | Followers | Comments | Niches | File |
|----------|-----------|----------|--------|------|
| **Tera** | 1,315 | 627 | Lifestyle, gifts, God's love, lip sync | `TERA_synthetic_data.csv` |
| **Yetunde** | 108 | 309 | Lifestyle, dancing, makeup | `YETUNDE_synthetic_data.csv` |
| **Denzel** | 5,000 | 1,145 | Music, school, gaming | `DENZEL_synthetic_data.csv` |
| **Wudh** | 7,000 | 895 | Asian culture, Germany, travel | `WUDH_synthetic_data.csv` |
| **Esther** | 4,000 | 1,285 | Dancing, football, Kenya | `ESTHER_synthetic_data.csv` |
| **Basti** | 8,000 | 1,574 | Berlin, travel, African food | `BASTI_synthetic_data.csv` |
| **Judith** | 9,000 | 1,268 | Nigeria life, choir, insecurity | `JUDITH_synthetic_data.csv` |
| **Paul** | 10,000 | 1,163 | Nature, biking, cooking | `PAUL_synthetic_data.csv` |

---

## How to Use

### For Each Tester

1. **Download** your creator's CSV file
   - Example: if you're testing with Tera's data, download `TERA_synthetic_data.csv`

2. **Go to the app** 
   - Click the link your creator provides (deployed Streamlit app)

3. **Sign up** 
   - Create an account with any username and password

4. **Upload your data**
   - Click "Upload Data" tab
   - Click "Upload CSV" subtab
   - Select your creator's CSV file
   - Click "Run Analysis"

5. **Explore the results**
   - **Dashboard**: Overall sentiment, top keywords, summary stats
   - **Insights**: Detailed findings, keyword clusters, example comments
   - **Recommendations**: Content ideas based on audience feedback
   - **User Profile**: Your account and analysis history

6. **Give feedback**
   - Is the sentiment analysis accurate?
   - Are the keywords actually relevant to the content?
   - Do the recommendations make sense?
   - What's missing or broken?

---

## Data Structure

Each CSV has these columns:

```
Comment Text          — The actual comment
Comment Language      — Language code (en = English)
Comment Like Count    — How many people liked this comment
Author Nickname       — Commenter's TikTok handle
video_type           — Content category (Lifestyle, Music, etc.)
comment_date         — When the comment was posted
video_id             — Which video it's attached to
```

**Example rows:**
```
"love your vibe"     | en | 1 | user_5432 | Lifestyle & Vlog | 2025-10-02T... | 760000...
"fire track"         | en | 0 | user_1829 | Engagement...     | 2025-10-03T... | 760000...
"same"               | en | 2 | user_7654 | Student Life      | 2025-10-04T... | 760000...
```

---

## Realistic Features

✅ **Emoji-heavy** — Real TikTok comments are short and emoji-loaded  
✅ **Diverse** — Mix of short words, questions, long comments  
✅ **Low engagement** — Most comments get 0 likes (realistic for follower size)  
✅ **Themed content** — Comments match each creator's actual niches  
✅ **Volume** — Enough comments to show real patterns (300-1500 per creator)  

---

## Why Synthetic Data?

- ✅ No privacy concerns (not real user data)
- ✅ Reproducible testing (consistent results)
- ✅ Personalized (each tester's content niche)
- ✅ Fast feedback loop (test before deployment)
- ✅ Realistic patterns (based on actual TikTok data)

---

## Feedback Questions

After testing, please answer:

1. **Sentiment**: Did the positive/negative/neutral percentages seem right?
2. **Keywords**: Were the top keywords actually relevant to your content?
3. **Recommendations**: Did the content ideas make sense?
4. **UI/UX**: Was the app easy to use?
5. **Bugs**: Did anything crash or break?
6. **Overall**: Would this help you understand your audience better?

---

## Notes for Creators

- These are **simulated comments**, not your real audience
- The NLP analysis is the real part (VADER sentiment + TF-IDF keywords)
- For actual scraping, you'll either:
  - Use the CSV upload flow (no browser automation)
  - Or use the local scraper scripts (for your own account)
- The app currently does **not** deploy the live TikTok scraper (that requires TikTok API access)

---

**Generated:** June 2026  
**For:** TikTok Creator Intelligence Beta Testing  
**Status:** Ready to use with Streamlit Cloud deployment
