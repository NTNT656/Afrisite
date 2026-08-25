from supabase_client import supabase
import uuid
from datetime import datetime

# ---- Mapping of collection names to table names ----
TABLE_MAP = {
    'news': 'news',
    'reviews': 'reviews',
    'features': 'features',
    'shows': 'shows',
    'events': 'events',
    'videos': 'videos',
    'podcast_episodes': 'podcast_episodes',
    'community_posts': 'community_posts',
    'awards': 'awards',
    'people': 'people'
}

# ---- Generic helpers ----
def get_all_items(collection):
    table = TABLE_MAP.get(collection)
    if not table:
        return []
    try:
        response = supabase.table(table).select('*').order('created_at', desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching {collection}: {e}")
        return []

def add_item(collection, item):
    table = TABLE_MAP.get(collection)
    if not table:
        return None
    try:
        if 'id' not in item:
            item['id'] = str(uuid.uuid4())
        if 'created_at' not in item:
            item['created_at'] = datetime.now().isoformat()
        if 'people_tags' in item and isinstance(item['people_tags'], str):
            item['people_tags'] = [tag.strip() for tag in item['people_tags'].split(',') if tag.strip()]
        elif 'people_tags' not in item:
            item['people_tags'] = []
        response = supabase.table(table).insert(item).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding to {collection}: {e}")
        return None

def update_item(collection, item_id, updated):
    table = TABLE_MAP.get(collection)
    if not table:
        return False
    try:
        if 'people_tags' in updated and isinstance(updated['people_tags'], str):
            updated['people_tags'] = [tag.strip() for tag in updated['people_tags'].split(',') if tag.strip()]
        elif 'people_tags' not in updated:
            updated['people_tags'] = []
        response = supabase.table(table).update(updated).eq('id', item_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating {collection}: {e}")
        return False

def delete_item(collection, item_id):
    table = TABLE_MAP.get(collection)
    if not table:
        return False
    try:
        response = supabase.table(table).delete().eq('id', item_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error deleting from {collection}: {e}")
        return False

def get_item(collection, item_id):
    table = TABLE_MAP.get(collection)
    if not table:
        return None
    try:
        response = supabase.table(table).select('*').eq('id', item_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching item from {collection}: {e}")
        return None

# ---- Specific accessors ----
def get_news(): return get_all_items('news')
def get_reviews(): return get_all_items('reviews')
def get_features(): return get_all_items('features')
def get_shows(): return get_all_items('shows')
def get_events(): return get_all_items('events')
def get_videos(): return get_all_items('videos')
def get_podcast_episodes(): return get_all_items('podcast_episodes')
def get_community_posts(): return get_all_items('community_posts')
def get_awards(): return get_all_items('awards')
def get_people(): return get_all_items('people')

def get_origins():
    try:
        response = supabase.table('origins').select('*').limit(1).execute()
        if response.data:
            return response.data[0]
        return {'title': 'Origins', 'content': ''}
    except:
        return {'title': 'Origins', 'content': ''}

def update_origins(data_dict):
    try:
        existing = supabase.table('origins').select('id').limit(1).execute()
        if existing.data:
            supabase.table('origins').update(data_dict).eq('id', existing.data[0]['id']).execute()
        else:
            data_dict['id'] = str(uuid.uuid4())
            supabase.table('origins').insert(data_dict).execute()
        return True
    except Exception as e:
        print(f"Error updating origins: {e}")
        return False

# ---- Backwards compatibility ----
def update_news(news_list):
    supabase.table('news').delete().neq('id', '').execute()
    for item in news_list:
        if 'id' not in item:
            item['id'] = str(uuid.uuid4())
        if 'created_at' not in item:
            item['created_at'] = datetime.now().isoformat()
        supabase.table('news').insert(item).execute()

def update_reviews(reviews_list):
    supabase.table('reviews').delete().neq('id', '').execute()
    for item in reviews_list:
        if 'id' not in item:
            item['id'] = str(uuid.uuid4())
        if 'created_at' not in item:
            item['created_at'] = datetime.now().isoformat()
        supabase.table('reviews').insert(item).execute()

def reset_data():
    tables = ['news', 'reviews', 'features', 'shows', 'events', 'videos',
              'podcast_episodes', 'community_posts', 'awards', 'people']
    for table in tables:
        supabase.table(table).delete().neq('id', '').execute()
    supabase.table('origins').delete().neq('id', '').execute()
    supabase.table('origins').insert({
        'id': str(uuid.uuid4()),
        'title': 'Origins',
        'content': 'From one man dissecting trailers alone, to a full slate of shows...'
    }).execute()

def get_content_by_person(person_id):
    results = []
    for collection in ['news', 'reviews', 'features']:
        items = get_all_items(collection)
        for item in items:
            if person_id in item.get('people_tags', []):
                results.append({
                    'type': collection,
                    'title': item.get('title'),
                    'id': item.get('id'),
                    'date': item.get('created_at')
                })
    return sorted(results, key=lambda x: x.get('date', ''), reverse=True)