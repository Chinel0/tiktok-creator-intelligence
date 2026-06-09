import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

creators = {
    'YETUNDE': {
        'followers': 108,
        'videos': 22,
        'comments': ["love the vibe", "teach me", "so cute", "omg yes", "obsessed",
                    "goals", "that fit tho", "boots boots", "yes queen", "iconic",
                    "serving looks", "the makeup", "your energy", "so pretty"],
        'niches': {
            'lifestyle': {'count': 8, 'type': 'Lifestyle & Vlog'},
            'dancing': {'count': 8, 'type': 'Engagement / Growth'},
            'makeup': {'count': 6, 'type': 'Hair & Beauty'}
        }
    },

    'DENZEL': {
        'followers': 5000,
        'videos': 80,
        'comments': ["fire track", "go crazy", "bars", "that beat", "hard",
                    "spit that", "remix this", "next level", "mad talent",
                    "keep it up", "drop more", "this one different", "sick"],
        'niches': {
            'music': {'count': 40, 'type': 'Engagement / Growth'},
            'school': {'count': 25, 'type': 'Student Life'},
            'gaming': {'count': 15, 'type': 'Lifestyle & Vlog'}
        }
    },

    'WUDH': {
        'followers': 7000,
        'videos': 65,
        'comments': ["so relatable", "love this content", "teach me german",
                    "where is this", "want to visit", "so cool", "your journey",
                    "same energy", "love the vibe", "this made my day"],
        'niches': {
            'asian': {'count': 25, 'type': 'Lifestyle & Vlog'},
            'germany': {'count': 20, 'type': 'Travel & Places'},
            'travel': {'count': 20, 'type': 'Travel & Places'}
        }
    },

    'ESTHER': {
        'followers': 4000,
        'videos': 90,
        'comments': ["this is so good", "love the energy", "teach me this dance",
                    "your talent", "yes queen", "east african pride",
                    "so talented", "amazing moves", "the rhythm"],
        'niches': {
            'dancing': {'count': 45, 'type': 'Engagement / Growth'},
            'football': {'count': 25, 'type': 'Lifestyle & Vlog'},
            'community': {'count': 20, 'type': 'Lifestyle & Vlog'}
        }
    },

    'BASTI': {
        'followers': 8000,
        'videos': 110,
        'comments': ["berlin looks amazing", "love your travels", "that food looks good",
                    "so aesthetic", "travel goals", "the vibe", "teach me cooking",
                    "where is this", "want to go", "beautiful content"],
        'niches': {
            'berlin': {'count': 35, 'type': 'Travel & Places'},
            'travel': {'count': 40, 'type': 'Travel & Places'},
            'food': {'count': 25, 'type': 'Food & Cooking'},
            'culture': {'count': 10, 'type': 'Lifestyle & Vlog'}
        }
    },

    'JUDITH': {
        'followers': 9000,
        'videos': 90,
        'comments': ["so relatable", "nigerian girls stay strong", "lmaoooo",
                    "the choir part", "real talk", "love this energy",
                    "your voice tho", "facts", "insecurity is real",
                    "stay safe queen", "love your honesty", "goals"],
        'niches': {
            'lifestyle': {'count': 35, 'type': 'Lifestyle & Vlog'},
            'choir': {'count': 20, 'type': 'Lifestyle & Vlog'},
            'dancing': {'count': 20, 'type': 'Engagement / Growth'},
            'insecurity': {'count': 15, 'type': 'Motivation'}
        }
    },

    'PAUL': {
        'followers': 10000,
        'videos': 80,
        'comments': ["that view tho", "so beautiful", "want to visit",
                    "nice trail", "how did you get there", "tutorial please",
                    "your fitness", "that workout", "swimming looks fun",
                    "cooking skills", "that looks delicious", "nature lover"],
        'niches': {
            'nature': {'count': 30, 'type': 'Travel & Places'},
            'biking': {'count': 25, 'type': 'Lifestyle & Vlog'},
            'fitness': {'count': 15, 'type': 'Lifestyle & Vlog'},
            'cooking': {'count': 10, 'type': 'Food & Cooking'}
        }
    }
}

base_id = 7700000000000000000
short_comments = ['yes', 'wow', 'omg', 'lol', 'same', 'love', 'fire', 'goals']

for creator_name, config in creators.items():
    print(f"Generating {creator_name}...")

    all_comments = []
    video_idx = 0
    base_video_id = base_id + len(creator_name) * 100
    current_date = datetime(2025, 10, 1)

    for niche_name, niche_info in config['niches'].items():
        video_count = niche_info['count']
        video_type = niche_info['type']

        for i in range(video_count):
            video_id = str(base_video_id + video_idx)
            comment_count = random.randint(8, 20)

            for j in range(comment_count):
                if random.random() < 0.35:
                    comment_text = random.choice(short_comments)
                else:
                    comment_text = random.choice(config['comments'])

                like_rand = random.random()
                if like_rand < 0.60:
                    like_count = 0
                elif like_rand < 0.85:
                    like_count = random.randint(1, 3)
                elif like_rand < 0.95:
                    like_count = random.randint(4, 10)
                else:
                    like_count = random.randint(11, 30)

                comment_date = (current_date + timedelta(days=video_idx*2, hours=random.randint(0, 48))).isoformat() + '+00:00'

                all_comments.append({
                    'Comment Text': comment_text,
                    'Comment Language': 'en',
                    'Comment Like Count': like_count,
                    'Author Nickname': f'user_{random.randint(1000, 9999)}',
                    'video_type': video_type,
                    'comment_date': comment_date,
                    'video_id': video_id,
                })

            video_idx += 1

    df = pd.DataFrame(all_comments)
    df.to_csv(f'data/{creator_name}_synthetic_data.csv', index=False, encoding='utf-8-sig')

    print(f"  {creator_name}: {len(df)} comments")
    print(f"    Zero likes: {(df['Comment Like Count'] == 0).sum()}, Positive: {(df['Comment Like Count'] > 0).sum()}")

print("\n" + "="*60)
print("ALL 7 DATASETS GENERATED!")
print("="*60)
