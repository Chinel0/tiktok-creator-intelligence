"""
generate_synthetic_data.py
Generates paired synthetic datasets for beta testers:
    data/{NAME}_synthetic_data.csv    - comments (app's required format)
    data/{NAME}_synthetic_videos.csv  - video metadata (real scraper schema)

Design goals (so the analysis has something true to find):
  1. Each creator has a HOT niche that genuinely outperforms (2.5-4x more
     comments per video, higher views) and a weak niche.
  2. Comments are niche-specific (makeup comments on makeup videos).
  3. ~17% of comments are explicit requests ("teach me german", "recipe
     please") so the request extractor has real signal.
  4. ~5% mild critiques so the "What to Improve" section has material.
  5. comment_count in the videos file equals the generated comment rows.

TERA is excluded: her files are real scraped data (tera_comments.csv /
tera_videos.csv); this script just copies her videos file to the
consistent _synthetic_videos.csv name.

Run:  python generate_synthetic_data.py
"""

import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

DATA = Path(__file__).parent / 'data'

SHORT_REACTIONS = ['yes', 'wow', 'omg', 'lol', 'same', 'love', 'fire', 'goals',
                   'so cool', 'obsessed', 'no way', 'this made my day',
                   '🔥🔥🔥', '😍😍', '❤️❤️❤️', '😭❤️', '👏👏', '💯', '🤩✨']

# Appended to ~35% of text comments - real TikTok comments are emoji-heavy
EMOJIS = ['🔥', '😍', '❤️', '✨', '😭', '👏', '🙌', '💯', '😂', '🤩']

CRITIQUES = ['the audio is a bit low on this one', 'video is too short make it longer',
             'the captions are hard to read', 'camera is shaky here',
             'the music is louder than your voice']

CREATORS = {
    'YETUNDE': {
        'followers': 108, 'handle': 'yetunde',
        'niches': [
            dict(niche='makeup', type='Hair & Beauty', videos=6,
                 cpv=(18, 28), views=(300, 900),
                 tags='#makeup #grwm #softglam #fyp',
                 descs=['grwm soft glam look', 'everyday makeup routine', 'trying the new palette'],
                 talk=['the makeup is perfect', 'your skin is glowing', 'this look is everything',
                       'the blend on the eyes wow', 'face card never declines', 'the lashes tho',
                       'you look stunning', 'best glam on my fyp', 'the highlight is unreal'],
                 asks=['makeup tutorial please', 'what products do you use',
                       'how do you do your eyeliner', 'teach me this look',
                       'whats the lipstick shade']),
            dict(niche='dancing', type='Engagement / Growth', videos=8,
                 cpv=(10, 16), views=(150, 400),
                 tags='#dance #trend #fyp',
                 descs=['new dance trend', 'dancing in my room', 'this trend was hard'],
                 talk=['the moves tho', 'so smooth', 'you ate this', 'clean footwork',
                       'serving energy', 'you understood the assignment'],
                 asks=['teach me this dance', 'what song is this', 'do the new trend next']),
            dict(niche='lifestyle', type='Lifestyle & Vlog', videos=8,
                 cpv=(4, 9), views=(80, 250),
                 tags='#dayinmylife #vlog #fyp',
                 descs=['day in my life', 'come with me to class', 'little life update'],
                 talk=['love the vibe', 'so cute', 'your energy is everything', 'cozy vibes'],
                 asks=['vlog more please', 'where is your top from']),
        ],
    },

    'DENZEL': {
        'followers': 5000, 'handle': 'denzel',
        'niches': [
            dict(niche='music', type='Engagement / Growth', videos=40,
                 cpv=(18, 30), views=(3000, 12000),
                 tags='#music #rap #newartist #fyp',
                 descs=['new track snippet', 'freestyle friday', 'studio session clip'],
                 talk=['fire track', 'this beat is hard', 'bars', 'flow is crazy',
                       'this one different', 'mad talent', 'put this on spotify now',
                       'chorus stuck in my head', 'underrated fr'],
                 asks=['drop the full track', 'when is the album coming',
                       'do a remix with afrobeats', 'spit more bars like this',
                       'put this on streaming please']),
            dict(niche='school', type='Student Life', videos=25,
                 cpv=(8, 14), views=(1000, 4000),
                 tags='#studentlife #uni #fyp',
                 descs=['uni day in my life', 'exam season is here', 'campus moments'],
                 talk=['so relatable', 'uni is exactly like this', 'the struggle is real',
                       'me during finals fr'],
                 asks=['make a video about exam tips', 'how do you balance school and music',
                       'study routine please']),
            dict(niche='gaming', type='Lifestyle & Vlog', videos=15,
                 cpv=(4, 8), views=(500, 1500),
                 tags='#gaming #fyp',
                 descs=['late night gaming', 'this game is wild', 'ranked grind'],
                 talk=['that play was clean', 'rip lol', 'so funny'],
                 asks=['what game is this', 'stream when', 'play with viewers next time']),
        ],
    },

    'WUDH': {
        'followers': 7000, 'handle': 'wudh',
        'niches': [
            dict(niche='germany', type='Travel & Places', videos=22,
                 cpv=(16, 28), views=(4000, 15000),
                 tags='#germany #berlin #expat #fyp',
                 descs=['living in germany as a foreigner', 'berlin street tour',
                        'german culture shock moments', 'exploring berlin neighbourhoods'],
                 talk=['berlin looks amazing', 'germany is on my bucket list',
                       'the architecture wow', 'your journey is inspiring',
                       'culture shocks are so real', 'this city is beautiful',
                       'i felt this as an immigrant too'],
                 asks=['teach me german', 'how did you move to germany',
                       'make a video about german food', 'where is this in berlin',
                       'visa tips please', 'how expensive is berlin']),
            dict(niche='travel', type='Travel & Places', videos=18,
                 cpv=(16, 28), views=(4000, 15000),
                 tags='#travel #europe #wanderlust #fyp',
                 descs=['weekend trip vlog', 'cheapest way to travel europe', 'hidden gems trip'],
                 talk=['want to visit so bad', 'adding this to my list',
                       'the views are unreal', 'travel goals fr', 'this place is a dream'],
                 asks=['where is this', 'travel vlog please', 'how much did the trip cost',
                       'make a packing tips video']),
            dict(niche='asian', type='Lifestyle & Vlog', videos=25,
                 cpv=(5, 10), views=(800, 2500),
                 tags='#asian #relatable #fyp',
                 descs=['asian household things', 'growing up asian', 'my daily life abroad'],
                 talk=['so relatable', 'asian parents are the same everywhere lol',
                       'this is too accurate', 'same energy', 'love the vibe'],
                 asks=['make more food videos', 'cook with your mom next time']),
        ],
    },

    'ESTHER': {
        'followers': 4000, 'handle': 'esther',
        'niches': [
            dict(niche='dancing', type='Engagement / Growth', videos=45,
                 cpv=(15, 26), views=(2000, 9000),
                 tags='#dance #kenya #afrobeats #fyp',
                 descs=['afrobeats choreo', 'dance challenge accepted', 'new moves loading'],
                 talk=['east african pride', 'the rhythm is unreal', 'so talented',
                       'amazing moves', 'you ate this', 'energy is unmatched',
                       'kenya to the world'],
                 asks=['teach me this dance', 'tutorial for this choreo please',
                       'what song is this', 'do a slow breakdown of the steps']),
            dict(niche='football', type='Lifestyle & Vlog', videos=25,
                 cpv=(7, 12), views=(800, 3000),
                 tags='#football #skills #fyp',
                 descs=['football skills session', 'matchday vibes', 'training clips'],
                 talk=['your skills tho', 'baller fr', 'that touch was clean'],
                 asks=['which team do you support', 'more football content',
                       'do a crossbar challenge']),
            dict(niche='community', type='Lifestyle & Vlog', videos=20,
                 cpv=(4, 8), views=(500, 1500),
                 tags='#kenya #community #fyp',
                 descs=['home is home', 'community day', 'life lately'],
                 talk=['love this energy', 'beautiful people', 'this is wholesome'],
                 asks=['show more of kenya', 'vlog the next event please']),
        ],
    },

    'BASTI': {
        'followers': 8000, 'handle': 'basti',
        'niches': [
            dict(niche='food', type='Food & Cooking', videos=25,
                 cpv=(18, 30), views=(5000, 18000),
                 tags='#food #africanfood #berlinfood #fyp',
                 descs=['trying african food in berlin', 'cooking jollof tonight',
                        'street food hunt', 'rating berlin restaurants'],
                 talk=['the food looks amazing', 'im hungry now thanks', 'that looks delicious',
                       'jollof supremacy', 'chef vibes', 'my mouth is watering',
                       'this is making me homesick'],
                 asks=['recipe please', 'teach me cooking this', 'what restaurant is this',
                       'make a video about african restaurants in berlin',
                       'cook egusi next please']),
            dict(niche='travel', type='Travel & Places', videos=50,
                 cpv=(10, 18), views=(2000, 8000),
                 tags='#berlin #travel #germany #fyp',
                 descs=['berlin hidden spots', 'weekend city trip', 'exploring germany'],
                 talk=['berlin looks amazing', 'so aesthetic', 'travel goals',
                       'the vibe of this city', 'beautiful shots', 'want to go so bad'],
                 asks=['where is this', 'make a video about hidden spots in berlin',
                       'best area to stay in berlin', 'do a berlin food tour']),
            dict(niche='culture', type='Lifestyle & Vlog', videos=10,
                 cpv=(4, 8), views=(800, 2000),
                 tags='#culture #life #fyp',
                 descs=['thoughts on living abroad', 'culture talk', 'life update'],
                 talk=['love your honesty', 'deep one this', 'so true'],
                 asks=['talk about this more', 'part two please']),
        ],
    },

    'JUDITH': {
        'followers': 9000, 'handle': 'judith',
        'niches': [
            dict(niche='insecurity', type='Motivation', videos=15,
                 cpv=(20, 35), views=(4000, 15000),
                 tags='#motivation #selflove #fyp',
                 descs=['lets talk about insecurity', 'you are enough', 'real talk tonight'],
                 talk=['this made me cry', 'needed to hear this today', 'real talk',
                       'insecurity is real', 'thank you for saying this', 'felt every word',
                       'you have no idea how timely this is', 'love your honesty'],
                 asks=['talk about confidence next', 'make a video about dealing with body shaming',
                       'how do you stay positive', 'do one about comparison please']),
            dict(niche='dancing', type='Engagement / Growth', videos=20,
                 cpv=(10, 16), views=(1500, 5000),
                 tags='#dance #naija #fyp',
                 descs=['naija dance vibes', 'dance break', 'trend check'],
                 talk=['the energy tho', 'you ate this', 'naija to the world', 'so smooth'],
                 asks=['teach me this dance', 'what song is this']),
            dict(niche='choir', type='Lifestyle & Vlog', videos=20,
                 cpv=(5, 10), views=(800, 2500),
                 tags='#choir #worship #fyp',
                 descs=['choir rehearsal moments', 'sunday service clips', 'voice practice'],
                 talk=['your voice tho', 'the harmony is heavenly', 'this blessed me',
                       'the choir part wow'],
                 asks=['sing the full song please', 'do a vocal cover next']),
            dict(niche='lifestyle', type='Lifestyle & Vlog', videos=35,
                 cpv=(5, 10), views=(800, 2500),
                 tags='#nigeria #lagoslife #fyp',
                 descs=['lagos life diaries', 'day in my life', 'nigeria things'],
                 talk=['so relatable', 'nigerian girls stay strong', 'lmaoooo', 'facts',
                       'this is too real'],
                 asks=['vlog a market day', 'show us your hair routine']),
        ],
    },

    'PAUL': {
        'followers': 10000, 'handle': 'paul',
        'niches': [
            dict(niche='cooking', type='Food & Cooking', videos=10,
                 cpv=(20, 32), views=(6000, 20000),
                 tags='#cooking #homechef #fyp',
                 descs=['cooking dinner from scratch', 'campfire cooking', 'meal prep sunday'],
                 talk=['that looks delicious', 'cooking skills on point', 'chef paul',
                       'my stomach is growling', 'the sizzle sound wow'],
                 asks=['recipe please', 'tutorial for this dish', 'what seasoning did you use',
                       'make a one pot meal video']),
            dict(niche='nature', type='Travel & Places', videos=30,
                 cpv=(12, 20), views=(3000, 10000),
                 tags='#nature #hiking #outdoors #fyp',
                 descs=['sunrise hike', 'forest trail therapy', 'lake day'],
                 talk=['that view tho', 'so beautiful', 'nature is healing', 'so peaceful',
                       'want to visit', 'nature lover forever', 'this is therapy'],
                 asks=['where is this trail', 'how did you get there', 'drone shots please',
                       'make a camping gear video']),
            dict(niche='biking', type='Lifestyle & Vlog', videos=25,
                 cpv=(5, 9), views=(1000, 3000),
                 tags='#cycling #bikelife #fyp',
                 descs=['morning ride', 'new route today', 'bike maintenance day'],
                 talk=['nice trail', 'ride safe man', 'the speed tho'],
                 asks=['what bike do you ride', 'route details please']),
            dict(niche='fitness', type='Lifestyle & Vlog', videos=15,
                 cpv=(5, 9), views=(1000, 3000),
                 tags='#fitness #workout #fyp',
                 descs=['full body workout', 'swim session', 'gym progress'],
                 talk=['your fitness is goals', 'that workout looks brutal', 'swimming looks fun'],
                 asks=['workout routine please', 'how many days a week do you train']),
        ],
    },
}


def comment_like_count() -> int:
    r = random.random()
    if r < 0.60:
        return 0
    if r < 0.85:
        return random.randint(1, 3)
    if r < 0.95:
        return random.randint(4, 10)
    return random.randint(11, 30)


def pick_comment(niche: dict) -> str:
    r = random.random()
    if r < 0.28:
        text = random.choice(SHORT_REACTIONS)
    elif r < 0.45:                    # 17% explicit requests
        text = random.choice(niche['asks'])
    elif r < 0.50:                    # 5% mild critiques
        text = random.choice(CRITIQUES)
    else:
        text = random.choice(niche['talk'])

    # ~35% of text comments get emojis appended, like real TikTok comments.
    # VADER reads emojis for sentiment, so this exercises that path too.
    if text and not any(e in text for e in EMOJIS) and random.random() < 0.35:
        text += ' ' + ''.join(random.choices(EMOJIS, k=random.randint(1, 2)))
    return text


def generate_creator(name: str, cfg: dict, base_video_id: int) -> tuple:
    comment_rows, video_rows = [], []
    video_idx = 0
    upload_date = datetime(2025, 8, 1)

    for niche in cfg['niches']:
        for _ in range(niche['videos']):
            video_id = str(base_video_id + video_idx)
            upload_date += timedelta(days=random.randint(2, 4))

            n_comments = random.randint(*niche['cpv'])
            for _ in range(n_comments):
                cdate = upload_date + timedelta(hours=random.randint(1, 96))
                comment_rows.append({
                    'Comment Text': pick_comment(niche),
                    'Comment Language': 'en',
                    'Comment Like Count': comment_like_count(),
                    'Author Nickname': f'user_{random.randint(1000, 9999)}',
                    'video_type': niche['type'],
                    'comment_date': cdate.isoformat() + '+00:00',
                    'video_id': video_id,
                })

            views = random.randint(*niche['views'])
            likes = int(views * random.uniform(0.06, 0.14))
            video_rows.append({
                'video_id': video_id,
                'description': f"{random.choice(niche['descs'])} {niche['tags']}",
                'view_count': views,
                'like_count': likes,
                'comment_count': n_comments,
                'share_count': int(likes * random.uniform(0.05, 0.20)),
                'upload_date': upload_date.strftime('%Y-%m-%d'),
                'hashtags': niche['tags'],
                'url': f"https://www.tiktok.com/@{cfg['handle']}/video/{video_id}",
                'scraped_at': '2026-06-10T12:00:00',
                'video_type': niche['type'],
            })
            video_idx += 1

    return pd.DataFrame(comment_rows), pd.DataFrame(video_rows)


def main():
    print(f"{'creator':10} {'comments':>9} {'videos':>7}   comments/video by type")
    print('-' * 78)

    for i, (name, cfg) in enumerate(CREATORS.items()):
        base_id = 7700000000000000000 + i * 1_000_000
        comments, videos = generate_creator(name, cfg, base_id)

        comments.to_csv(DATA / f'{name}_synthetic_data.csv', index=False, encoding='utf-8-sig')
        videos.to_csv(DATA / f'{name}_synthetic_videos.csv', index=False, encoding='utf-8-sig')

        per_type = videos.groupby('video_type')['comment_count'].mean().round(1)
        signal = ' | '.join(f'{t}: {v}' for t, v in per_type.sort_values(ascending=False).items())
        print(f'{name:10} {len(comments):>9} {len(videos):>7}   {signal}')

    # TERA: real data - just provide her videos file under the consistent name
    src, dst = DATA / 'tera_videos.csv', DATA / 'TERA_synthetic_videos.csv'
    shutil.copy(src, dst)
    print(f"{'TERA':10} {'(real)':>9} {'copied':>7}   tera_videos.csv -> TERA_synthetic_videos.csv")

    print('\nDone. Each tester now has a comments file + a videos file.')


if __name__ == '__main__':
    main()
