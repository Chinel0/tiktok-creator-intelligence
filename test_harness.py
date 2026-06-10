"""
test_harness.py
Local verification harness: runs the SAME pipeline the app runs on every
dataset and prints exactly what each tester would see on the
Recommendations page.

Run before every push:
    python test_harness.py            # all datasets
    python test_harness.py WUDH       # one dataset (name match)

Nothing in here is deployed - it is a development tool only.
"""

import sys
from pathlib import Path

import pandas as pd

# Windows consoles default to cp1252 and crash on emojis - print them
# as replacement chars instead of dying.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from nlp.preprocessor import preprocess
from nlp.sentiment import analyze_sentiment
from nlp.keywords import extract_keywords
# Import the real app functions so the harness tests what the app actually does
from app.components.recommendations import _generate_recommendations
from app.components.upload import normalize_comment_columns, merge_video_metadata
from nlp.niche_analyzer import analyze_niches
from nlp.request_extractor import extract_requests


# Each entry: name -> (comments_csv, videos_csv or None, expect_niche_signal)
# expect_niche_signal=True only for generated data where we control the signal;
# real accounts may genuinely have flat engagement - that is a fact, not a bug.
DATASETS = {
    'CHINELO (real)': ('comments_20260526_233400.csv', 'videos_merged.csv', False),
    'TERA (real)':    ('tera_comments.csv', 'tera_videos.csv', False),
    'TERA (tester files)': ('TERA_synthetic_data.csv', 'TERA_synthetic_videos.csv', False),
    'YETUNDE (synthetic)': ('YETUNDE_synthetic_data.csv', 'YETUNDE_synthetic_videos.csv', True),
    'DENZEL (synthetic)':  ('DENZEL_synthetic_data.csv', 'DENZEL_synthetic_videos.csv', True),
    'WUDH (synthetic)':    ('WUDH_synthetic_data.csv', 'WUDH_synthetic_videos.csv', True),
    'ESTHER (synthetic)':  ('ESTHER_synthetic_data.csv', 'ESTHER_synthetic_videos.csv', True),
    'BASTI (synthetic)':   ('BASTI_synthetic_data.csv', 'BASTI_synthetic_videos.csv', True),
    'JUDITH (synthetic)':  ('JUDITH_synthetic_data.csv', 'JUDITH_synthetic_videos.csv', True),
    'PAUL (synthetic)':    ('PAUL_synthetic_data.csv', 'PAUL_synthetic_videos.csv', True),
}

# Words that should never appear as the "topic" of a recommendation.
# If one shows up, the recommendation is generic garbage - flag it.
GENERIC_TOPICS = {'content', 'video', 'videos', 'more', 'want', 'make', 'thing', 'stuff'}


def run_dataset(name: str, comments_file: str, videos_file: str | None,
                expect_signal: bool = False) -> list[str]:
    """Run the full pipeline on one dataset. Returns list of red flags found."""
    flags = []
    print()
    print('=' * 70)
    print(f'  {name}')
    print('=' * 70)

    comments_path = ROOT / 'data' / comments_file
    if not comments_path.exists():
        print(f'  SKIPPED - file not found: {comments_file}')
        return [f'{name}: comments file missing']

    df = pd.read_csv(comments_path, encoding='utf-8-sig')
    df = normalize_comment_columns(df)
    if df is None:
        print('  FAILED - columns match neither accepted format')
        return [f'{name}: column normalization failed']
    print(f'  Comments: {len(df)} rows from {comments_file}')

    # ---- video metadata (uses the app's real merge function) ----
    videos = None
    if videos_file:
        videos_path = ROOT / 'data' / videos_file
        if videos_path.exists():
            videos = pd.read_csv(videos_path, encoding='utf-8-sig')
            df, matched = merge_video_metadata(df, videos)
            print(f'  Videos:   {len(videos)} rows from {videos_file} '
                  f'(merged: {matched} comments matched)')
            if matched == 0:
                flags.append(f'{name}: video merge matched 0 comments')
            if 'video_type' in df.columns and df['video_type'].isna().all():
                flags.append(f'{name}: video_type empty after merge')
        else:
            print(f'  Videos:   MISSING file {videos_file}')
            flags.append(f'{name}: videos file missing')

    # ---- pipeline (exactly what the app runs) ----
    df_clean = preprocess(df)
    df_analyzed, summary = analyze_sentiment(df_clean)
    keywords, clusters = extract_keywords(df_analyzed)
    analysis = analyze_niches(df_analyzed, videos)
    requests = extract_requests(df_analyzed)
    keep, improve, ideas = _generate_recommendations(
        summary, keywords, clusters, analysis, requests)

    print(f'\n  Sentiment: {summary["positive"]}% pos / '
          f'{summary["neutral"]}% neu / {summary["negative"]}% neg '
          f'({summary["total"]} analyzed)')

    print(f'  Top keywords: {", ".join(w for w, _ in keywords[:8])}')

    print('\n  Clusters:')
    for cname, words in clusters.items():
        if words:
            print(f'    {cname}: {words[:6]}')
        for w in words:
            if all(tok in GENERIC_TOPICS for tok in w.split()):
                flags.append(f'{name}: generic keyword "{w}" survived into cluster {cname}')

    # ---- niche engagement signal (needs video metadata or video_type) ----
    _print_niche_signal(analysis, name, flags, expect_signal)

    # ---- audience requests ----
    print(f'\n  Audience requests ({len(requests)} found):')
    for r in requests[:6]:
        print(f'    {r["count"]:>3}x  "{r["request"][:60]}"  [{r["top_video_type"]}]')
    if not requests:
        print('    (no repeated requests - real accounts may genuinely have none)')
    if expect_signal and len(requests) < 3:
        flags.append(f'{name}: expected >=3 repeated requests in generated data, '
                     f'got {len(requests)}')

    # ---- the recommendations a tester would actually read ----
    print('\n  --- RECOMMENDATIONS PAGE OUTPUT ---')
    for section, recs in [('POST MORE', keep), ('IMPROVE', improve)]:
        for r in recs:
            print(f'  [{section}] {r["title"]}')
            print(f'       Why: {r["reason"]}')
            _flag_if_generic(name, r['title'] + ' ' + r['reason'], flags)
    for idea in ideas:
        print(f'  [IDEA-{idea["confidence"]}] {idea["title"]} - {idea["description"]}')
        _flag_if_generic(name, idea['title'], flags)

    return flags


def _print_niche_signal(analysis, name: str, flags: list,
                        expect_signal: bool = False):
    """Print the niche analyzer output and verify signal exists."""
    if analysis is None:
        print('\n  Niche analysis: NONE (no video_type available)')
        flags.append(f'{name}: no niche data at all')
        return

    src = 'video metadata' if analysis['has_video_metadata'] else 'comments only'
    print(f'\n  Niche analysis (from {src}):')
    header = (f'    {"niche":24} {"videos":>6} {"com/vid":>8} {"avg_views":>10} '
              f'{"disc/1k":>8} {"pos%":>6} {"passion%":>9}')
    print(header)
    for t in analysis['ranked']:
        m = analysis['niches'][t]
        views = m['avg_views'] if m['avg_views'] is not None else '-'
        disc = m['discussion_per_1k'] if m['discussion_per_1k'] is not None else '-'
        print(f'    {t:24} {m["videos"]:>6} {m["comments_per_video"]:>8} '
              f'{str(views):>10} {str(disc):>8} {m["positive_pct"]:>6} {m["passion_pct"]:>9}')

    print(f'    -> best: {analysis["best"]} | weakest: {analysis["weakest"]} | '
          f'engagement ratio: {analysis["engagement_ratio"]}x | '
          f'views ratio: {analysis["views_ratio"]}x | most loved: {analysis["most_loved"]}')

    # For generated data we require a real winner niche (>= 2x the weakest)
    if expect_signal:
        ratio = analysis['engagement_ratio']
        if not analysis['best'] or ratio is None or ratio < 2:
            flags.append(f'{name}: weak niche signal (engagement ratio {ratio}x < 2x)')


def _flag_if_generic(name: str, text: str, flags: list):
    """Flag recommendations whose topic slot is a bare generic word."""
    lowered = text.lower()
    for word in GENERIC_TOPICS:
        if f'"{word}"' in lowered:
            flags.append(f'{name}: generic topic "{word}" in: {text[:70]}')


def main():
    only = sys.argv[1].upper() if len(sys.argv) > 1 else None
    all_flags = []
    ran = 0

    for name, (comments_file, videos_file, expect_signal) in DATASETS.items():
        if only and only not in name.upper():
            continue
        all_flags.extend(run_dataset(name, comments_file, videos_file, expect_signal))
        ran += 1

    print()
    print('=' * 70)
    print(f'  SUMMARY: {ran} datasets run, {len(all_flags)} red flags')
    print('=' * 70)
    for f in all_flags:
        print(f'  FLAG: {f}')
    if not all_flags:
        print('  All clear.')

    # Non-zero exit if flags found, so this can gate a push
    sys.exit(1 if all_flags else 0)


if __name__ == '__main__':
    main()
