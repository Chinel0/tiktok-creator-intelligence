"""
evaluation.py — Deliverable 8: Evaluation & Quality
Runs sections 1-4 against the CURRENT pipeline and writes a slide-ready
report to documents/deliverable8_results.md.

Ground truth: data/test_set_labels.csv — 37 comments from the real
@ichbinnelo dataset, manually labelled positive/neutral/negative.
This is a held-out set: none of these labels were used to build or
tune any part of the pipeline (nothing in the pipeline is trained).

System framing for the benchmark:
  Baseline A (naive)    : majority-class predictor (always 'positive')
  Baseline B (ablation) : VADER on CLEANED text — emojis, caps and
                          punctuation stripped. This is the system
                          without its key design decision.
  Full system           : VADER on ORIGINAL text (what the app ships) —
                          emojis/caps/punctuation reach the analyser.

Run:  python evaluation.py
"""

import io
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score

# Force UTF-8 on Windows terminals (test set contains emojis)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from nlp.preprocessor import preprocess, clean_text
from nlp.sentiment import analyze_sentiment
from nlp.keywords import extract_keywords
from nlp.niche_analyzer import analyze_niches
from nlp.request_extractor import extract_requests
from app.components.upload import normalize_comment_columns, merge_video_metadata

DATA_FILE = ROOT / "data" / "comments_20260526_233400.csv"
VIDEO_FILE = ROOT / "data" / "videos_merged.csv"
TEST_FILE = ROOT / "data" / "test_set_labels.csv"
REPORT_FILE = ROOT / "documents" / "deliverable8_results.md"

SEP = "-" * 70
_report_lines: list = []


def out(line: str = ""):
    """Print to console AND collect for the markdown report."""
    print(line)
    _report_lines.append(line)


# ── shared VADER ──────────────────────────────────────────────────────────────

def _sia():
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    nltk.download("vader_lexicon", quiet=True)
    return SentimentIntensityAnalyzer()


def _classify(compound: float) -> str:
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"


# ── Sections 1 + 2: metrics and benchmark ─────────────────────────────────────

def run_metrics_and_benchmark():
    test = pd.read_csv(TEST_FILE, encoding="utf-8-sig")
    y_true = test["true_label"].str.strip().str.lower().tolist()
    labels = sorted(set(y_true))
    sia = _sia()

    majority = pd.Series(y_true).mode()[0]
    y_naive = [majority] * len(test)

    # Ablation: emoji/caps/punctuation stripped before VADER
    y_ablat = [
        _classify(sia.polarity_scores(clean_text(t))["compound"])
        if len(clean_text(t)) >= 3 else "neutral"
        for t in test["Comment Text"]
    ]

    # Full system: VADER on original text (exactly what sentiment.py does)
    y_full = [_classify(sia.polarity_scores(str(t))["compound"])
              for t in test["Comment Text"]]

    def scores(y_pred):
        acc = round(accuracy_score(y_true, y_pred) * 100, 1)
        f1 = round(f1_score(y_true, y_pred, average="macro",
                            zero_division=0, labels=labels) * 100, 1)
        return acc, f1

    acc_a, f1_a = scores(y_naive)
    acc_b, f1_b = scores(y_ablat)
    acc_f, f1_f = scores(y_full)

    out(SEP)
    out("SECTION 1: PERFORMANCE METRICS  +  SECTION 2: BENCHMARK COMPARISON")
    out(SEP)
    out()
    out(f"Held-out test set: {len(test)} real comments from @ichbinnelo, "
        f"manually labelled.")
    out(f"Class distribution: "
        + ", ".join(f"{c}={y_true.count(c)}" for c in labels))
    out()
    out("| System | Accuracy | Macro F1 |")
    out("|---|---|---|")
    out(f"| Baseline A: majority class (always '{majority}') | {acc_a}% | {f1_a}% |")
    out(f"| Baseline B (ablation): VADER on cleaned text, emojis stripped | {acc_b}% | {f1_b}% |")
    out(f"| Full system: VADER on original text (emojis kept) | **{acc_f}%** | **{f1_f}%** |")
    out()
    out(f"Gain over naive baseline : +{round(acc_f - acc_a, 1)} pts accuracy, "
        f"+{round(f1_f - f1_a, 1)} pts Macro F1")
    out(f"Gain from keeping emojis : +{round(acc_f - acc_b, 1)} pts accuracy, "
        f"+{round(f1_f - f1_b, 1)} pts Macro F1")
    out()
    out("Why these metrics?")
    out("- Accuracy: overall correctness; the test set roughly mirrors the real")
    out("  class balance, so accuracy is directly interpretable.")
    out("- Macro F1: averages F1 over all three classes equally, so the rare")
    out("  negative class (high-value to detect for creators) counts as much")
    out("  as the dominant positive class.")
    out()
    out("Classification report (full system vs manual labels):")
    out("```")
    out(classification_report(y_true, y_full, labels=labels, zero_division=0))
    out("```")

    # Return predictions for error analysis
    test = test.copy()
    test["pred_full"] = y_full
    test["pred_ablation"] = y_ablat
    return test


# ── Section 3: pipeline efficiency ────────────────────────────────────────────

def run_efficiency(n_runs: int = 10):
    out(SEP)
    out("SECTION 3: PIPELINE EFFICIENCY TEST")
    out(SEP)
    out()

    raw = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    raw = normalize_comment_columns(raw)
    videos = pd.read_csv(VIDEO_FILE, encoding="utf-8-sig")

    stage_totals = {"merge": [], "preprocess": [], "sentiment": [],
                    "keywords": [], "niche": [], "requests": []}
    totals = []

    for _ in range(n_runs):
        df = raw.copy()
        t0 = time.perf_counter()

        t = time.perf_counter()
        df, _ = merge_video_metadata(df, videos)
        stage_totals["merge"].append(time.perf_counter() - t)

        t = time.perf_counter()
        df_clean = preprocess(df)
        stage_totals["preprocess"].append(time.perf_counter() - t)

        t = time.perf_counter()
        df_analyzed, _ = analyze_sentiment(df_clean)
        stage_totals["sentiment"].append(time.perf_counter() - t)

        t = time.perf_counter()
        extract_keywords(df_analyzed, top_n=20)
        stage_totals["keywords"].append(time.perf_counter() - t)

        t = time.perf_counter()
        analyze_niches(df_analyzed, videos)
        stage_totals["niche"].append(time.perf_counter() - t)

        t = time.perf_counter()
        extract_requests(df_analyzed)
        stage_totals["requests"].append(time.perf_counter() - t)

        totals.append(time.perf_counter() - t0)

    mean_s = float(np.mean(totals))
    worst_s = float(np.max(totals))

    out(f"Measured on the real dataset ({len(raw)} comments + {len(videos)} "
        f"videos), {n_runs} full runs, current pipeline (merge, preprocess,")
    out("sentiment, keywords, niche analysis, request extraction).")
    out()
    out("| Scale | Avg Latency | Worst Case | Cost/Query | Est. Monthly Cost |")
    out("|---|---|---|---|---|")
    for label in ["100 queries/mo", "1,000 queries/mo", "10,000 queries/mo"]:
        out(f"| {label} | {mean_s:.2f} s | {worst_s:.2f} s | EUR 0.00 | EUR 0.00 |")
    out()
    out("Cost is EUR 0.00 at every scale: the pipeline is fully local "
        "(lexicon + statistics), no API calls, no GPU.")
    out()

    # Bottleneck breakdown
    out("Per-stage breakdown (mean):")
    out()
    out("| Stage | Mean time | Share of total |")
    out("|---|---|---|")
    for stage, vals in sorted(stage_totals.items(),
                              key=lambda kv: -np.mean(kv[1])):
        m = float(np.mean(vals))
        out(f"| {stage} | {m*1000:.0f} ms | {m/mean_s*100:.0f}% |")
    out()
    bottleneck = max(stage_totals, key=lambda k: np.mean(stage_totals[k]))
    share = np.mean(stage_totals[bottleneck]) / mean_s * 100
    out(f"Bottleneck: **{bottleneck}** ({share:.0f}% of total latency). "
        f"Throughput: ~{len(raw)/mean_s:,.0f} comments/second end-to-end.")
    out()


# ── Section 4: error analysis ─────────────────────────────────────────────────

def run_error_analysis(test: pd.DataFrame):
    out(SEP)
    out("SECTION 4: ERROR ANALYSIS (current system)")
    out(SEP)
    out()

    raw = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    raw = normalize_comment_columns(raw)
    sia = _sia()
    n_raw = len(raw)

    # 1. Non-English exclusion (incl. langdetect false positives)
    non_en = raw[raw["Comment Language"].str.lower() != "en"]
    short_non_en = non_en[non_en["Comment Text"].fillna("").str.split()
                          .str.len() <= 2]

    # 2. Hype slang scored negative on the real data
    slang = ["hard", "crazy", "sick", "insane", "dead", "killed", "brutal"]
    en = raw[raw["Comment Language"].str.lower() == "en"].copy()
    has_slang = en["Comment Text"].str.lower().str.contains(
        "|".join(rf"\b{s}\b" for s in slang), na=False)
    slang_rows = en[has_slang].copy()
    slang_neg = sum(
        1 for t in slang_rows["Comment Text"]
        if _classify(sia.polarity_scores(str(t))["compound"]) == "negative"
    )

    # 3. Misclassifications on the labelled test set
    wrong = test[test["true_label"].str.lower() != test["pred_full"]]
    neutral_as_pos = wrong[(wrong["true_label"].str.lower() == "neutral")
                           & (wrong["pred_full"] == "positive")]
    pos_as_neutral = wrong[(wrong["true_label"].str.lower() == "positive")
                           & (wrong["pred_full"] == "neutral")]

    # 4. Sarcasm risk (marker words + confident positive score)
    markers = ["lol", "haha", "sure", "obviously"]
    has_marker = en["Comment Text"].str.lower().str.contains(
        "|".join(markers), na=False)
    sarcasm_risk = sum(
        1 for t in en[has_marker]["Comment Text"]
        if sia.polarity_scores(str(t))["compound"] > 0.3
    )

    out("| Error Category | Count | Root Cause | Fix Priority |")
    out("|---|---|---|---|")
    out(f"| Non-English comments excluded | {len(non_en)}/{n_raw} | "
        f"only German was translated at scrape time; rest is dropped | HIGH |")
    out(f"| ...of which likely langdetect false positives | "
        f"{len(short_non_en)}/{len(non_en)} | 1-2 word comments ('wow') "
        f"misdetected as other languages | HIGH |")
    out(f"| Hype slang scored negative | {slang_neg}/{len(slang_rows)} "
        f"slang comments | VADER lexicon predates Gen-Z usage of "
        f"hard/crazy/sick as praise | MEDIUM |")
    out(f"| Test-set misclassifications | {len(wrong)}/{len(test)} | "
        f"mostly neutral/positive boundary (see below) | MEDIUM |")
    out(f"| Potential sarcasm scored positive | {sarcasm_risk}/{n_raw} | "
        f"lexicon scoring cannot read tone | LOW |")
    out()

    out("Concrete misclassified examples (full system vs manual label):")
    out()
    shown = 0
    for _, r in wrong.iterrows():
        if shown >= 3:
            break
        out(f'- "{str(r["Comment Text"])[:70]}" — labelled '
            f'{r["true_label"].lower()}, predicted {r["pred_full"]}')
        shown += 1
    if neutral_as_pos is not None:
        out()
        out(f"Boundary pattern: {len(neutral_as_pos)} neutral comments "
            f"predicted positive, {len(pos_as_neutral)} positive predicted "
            f"neutral — the +/-0.05 compound threshold is the sensitive part.")
    out()
    out("Already fixed during development (worth presenting):")
    out("- Emoji-only comments were DROPPED in an early version (clean_text")
    out("  stripped them to empty). Fixed: VADER now scores the ORIGINAL")
    out("  text, and emoji-only comments are kept. The ablation result in")
    out("  Section 2 quantifies exactly how much this fix is worth.")
    out("- Generic keyword garbage ('content' recommended as a topic) was")
    out("  fixed with a platform-word filter and token-level cluster seeds.")
    out()
    out("Top fixes, prioritized:")
    out("1. [HIGH] Trust short comments as English when ASCII-only instead of")
    out("   dropping them on langdetect's guess - recovers most of the")
    out("   excluded comments at zero risk.")
    out("2. [MEDIUM] Add custom VADER lexicon entries for TikTok hype slang")
    out("   (hard, crazy, sick, dead => positive in this domain).")
    out("3. [LOW] Flag sarcasm-marker comments for manual review instead of")
    out("   trusting the positive score.")
    out()


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    out("=" * 70)
    out("DELIVERABLE 8 - EVALUATION & QUALITY REPORT")
    out("TikTok Creator Intelligence | real @ichbinnelo dataset")
    out("=" * 70)
    out()

    test = run_metrics_and_benchmark()
    out()
    run_efficiency(n_runs=10)
    out()
    run_error_analysis(test)

    out("=" * 70)
    out("Section 5 (user evaluation) is collected separately via the tester")
    out("questionnaire - see documents/user_testing_questionnaire.md.")
    out("=" * 70)

    REPORT_FILE.write_text("\n".join(_report_lines), encoding="utf-8")
    print(f"\nSlide-ready report written to {REPORT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
