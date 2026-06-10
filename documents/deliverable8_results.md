======================================================================
DELIVERABLE 8 - EVALUATION & QUALITY REPORT
TikTok Creator Intelligence | real @ichbinnelo dataset
======================================================================

----------------------------------------------------------------------
SECTION 1: PERFORMANCE METRICS  +  SECTION 2: BENCHMARK COMPARISON
----------------------------------------------------------------------

Held-out test set: 37 real comments from @ichbinnelo, manually labelled.
Class distribution: negative=2, neutral=15, positive=20

| System | Accuracy | Macro F1 |
|---|---|---|
| Baseline A: majority class (always 'positive') | 54.1% | 23.4% |
| Baseline B (ablation): VADER on cleaned text, emojis stripped | 86.5% | 84.3% |
| Full system: VADER on original text (emojis kept) | **91.9%** | **94.1%** |

Gain over naive baseline : +37.8 pts accuracy, +70.7 pts Macro F1
Gain from keeping emojis : +5.4 pts accuracy, +9.8 pts Macro F1

Why these metrics?
- Accuracy: overall correctness; the test set roughly mirrors the real
  class balance, so accuracy is directly interpretable.
- Macro F1: averages F1 over all three classes equally, so the rare
  negative class (high-value to detect for creators) counts as much
  as the dominant positive class.

Classification report (full system vs manual labels):
```
              precision    recall  f1-score   support

    negative       1.00      1.00      1.00         2
     neutral       0.93      0.87      0.90        15
    positive       0.90      0.95      0.93        20

    accuracy                           0.92        37
   macro avg       0.94      0.94      0.94        37
weighted avg       0.92      0.92      0.92        37

```

----------------------------------------------------------------------
SECTION 3: PIPELINE EFFICIENCY TEST
----------------------------------------------------------------------

Measured on the real dataset (1211 comments + 161 videos), 10 full runs, current pipeline (merge, preprocess,
sentiment, keywords, niche analysis, request extraction).

| Scale | Avg Latency | Worst Case | Cost/Query | Est. Monthly Cost |
|---|---|---|---|---|
| 100 queries/mo | 0.28 s | 0.34 s | EUR 0.00 | EUR 0.00 |
| 1,000 queries/mo | 0.28 s | 0.34 s | EUR 0.00 | EUR 0.00 |
| 10,000 queries/mo | 0.28 s | 0.34 s | EUR 0.00 | EUR 0.00 |

Cost is EUR 0.00 at every scale: the pipeline is fully local (lexicon + statistics), no API calls, no GPU.

Per-stage breakdown (mean):

| Stage | Mean time | Share of total |
|---|---|---|
| sentiment | 109 ms | 39% |
| requests | 62 ms | 22% |
| niche | 42 ms | 15% |
| preprocess | 24 ms | 9% |
| keywords | 23 ms | 8% |
| merge | 18 ms | 7% |

Bottleneck: **sentiment** (39% of total latency). Throughput: ~4,346 comments/second end-to-end.


----------------------------------------------------------------------
SECTION 4: ERROR ANALYSIS (current system)
----------------------------------------------------------------------

| Error Category | Count | Root Cause | Fix Priority |
|---|---|---|---|
| Non-English comments excluded | 267/1211 | only German was translated at scrape time; rest is dropped | HIGH |
| ...of which likely langdetect false positives | 142/267 | 1-2 word comments ('wow') misdetected as other languages | HIGH |
| Hype slang scored negative | 1/3 slang comments | VADER lexicon predates Gen-Z usage of hard/crazy/sick as praise | MEDIUM |
| Test-set misclassifications | 3/37 | mostly neutral/positive boundary (see below) | MEDIUM |
| Potential sarcasm scored positive | 5/1211 | lexicon scoring cannot read tone | LOW |

Concrete misclassified examples (full system vs manual label):

- "uhh can u like my video now" — labelled neutral, predicted positive
- "Teamwork 🎀 followed right away 💝🥰🫶🏽" — labelled positive, predicted neutral
- "boosting! ☘️" — labelled neutral, predicted positive

Boundary pattern: 2 neutral comments predicted positive, 1 positive predicted neutral — the +/-0.05 compound threshold is the sensitive part.

Already fixed during development (worth presenting):
- Emoji-only comments were DROPPED in an early version (clean_text
  stripped them to empty). Fixed: VADER now scores the ORIGINAL
  text, and emoji-only comments are kept. The ablation result in
  Section 2 quantifies exactly how much this fix is worth.
- Generic keyword garbage ('content' recommended as a topic) was
  fixed with a platform-word filter and token-level cluster seeds.

Top fixes, prioritized:
1. [HIGH] Trust short comments as English when ASCII-only instead of
   dropping them on langdetect's guess - recovers most of the
   excluded comments at zero risk.
2. [MEDIUM] Add custom VADER lexicon entries for TikTok hype slang
   (hard, crazy, sick, dead => positive in this domain).
3. [LOW] Flag sarcasm-marker comments for manual review instead of
   trusting the positive score.

======================================================================
Section 5 (user evaluation) is collected separately via the tester
questionnaire - see documents/user_testing_questionnaire.md.
======================================================================