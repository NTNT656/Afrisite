from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import data
import secrets
import requests
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import secure_filename
from supabase_client import supabase

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# ---------- UPLOAD CONFIG (only for validation) ----------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- TMDB CONFIG ----------
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
TMDB_BASE = 'https://api.themoviedb.org/3'

# ---------- ADMIN CREDENTIALS ----------
ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'password123')

# ---------- FIELD DEFINITIONS ----------
COLLECTION_FIELDS = {
    'news': [
        {'name': 'title', 'label': 'Title', 'type': 'text'},
        {'name': 'category', 'label': 'Category', 'type': 'text'},
        {'name': 'body', 'label': 'Body', 'type': 'textarea'},
        {'name': 'image_url', 'label': 'Image URL', 'type': 'text'},
        {'name': 'people_tags', 'label': 'People Tags (comma-separated IDs)', 'type': 'text'}
    ],
    'reviews': [
        {'name': 'title', 'label': 'Title', 'type': 'text'},
        {'name': 'genre', 'label': 'Genre', 'type': 'text'},
        {'name': 'score', 'label': 'Score (0-10)', 'type': 'text'},
        {'name': 'author', 'label': 'Author', 'type': 'text'},
        {'name': 'body', 'label': 'Review Body', 'type': 'textarea'},
        {'name': 'people_tags', 'label': 'People Tags (comma-separated IDs)', 'type': 'text'}
    ],
    'features': [
        {'name': 'title', 'label': 'Title', 'type': 'text'},
        {'name': 'category', 'label': 'Category', 'type': 'text'},
        {'name': 'body', 'label': 'Body', 'type': 'textarea'},
        {'name': 'image_url', 'label': 'Image URL', 'type': 'text'},
        {'name': 'people_tags', 'label': 'People Tags (comma-separated IDs)', 'type': 'text'}
    ],
    'shows': [
        {'name': 'name', 'label': 'Show Name', 'type': 'text'},
        {'name': 'description', 'label': 'Description', 'type': 'textarea'},
        {'name': 'category', 'label': 'Category', 'type': 'text'},
        {'name': 'youtube_url', 'label': 'YouTube URL', 'type': 'text'}
    ],
    'events': [
        {'name': 'title', 'label': 'Title', 'type': 'text'},
        {'name': 'description', 'label': 'Description', 'type': 'textarea'},
        {'name': 'date', 'label': 'Date', 'type': 'text'},
        {'name': 'location', 'label': 'Location', 'type': 'text'}
    ],
    'videos': [
        {'name': 'title', 'label': 'Title', 'type': 'text'},
        {'name': 'description', 'label': 'Description', 'type': 'textarea'},
        {'name': 'embed_url', 'label': 'Embed URL', 'type': 'text'},
        {'name': 'show', 'label': 'Show', 'type': 'text'}
    ],
    'podcast_episodes': [
        {'name': 'title', 'label': 'Title', 'type': 'text'},
        {'name': 'description', 'label': 'Description', 'type': 'textarea'},
        {'name': 'embed_url', 'label': 'Embed URL', 'type': 'text'},
        {'name': 'episode_number', 'label': 'Episode Number', 'type': 'text'}
    ],
    'community_posts': [
        {'name': 'title', 'label': 'Title', 'type': 'text'},
        {'name': 'body', 'label': 'Body', 'type': 'textarea'},
        {'name': 'author', 'label': 'Author', 'type': 'text'}
    ],
    'awards': [
        {'name': 'title', 'label': 'Title', 'type': 'text'},
        {'name': 'category', 'label': 'Category', 'type': 'text'},
        {'name': 'year', 'label': 'Year', 'type': 'text'},
        {'name': 'description', 'label': 'Description', 'type': 'textarea'}
    ],
    'people': [
        {'name': 'name', 'label': 'Name', 'type': 'text'},
        {'name': 'role', 'label': 'Role', 'type': 'text'},
        {'name': 'bio', 'label': 'Bio', 'type': 'textarea'},
        {'name': 'image_url', 'label': 'Image URL', 'type': 'text'}
    ]
}

# ---------- DECORATORS ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- TMDB HELPERS ----------
def search_tmdb_movie(query):
    if not TMDB_API_KEY: return []
    url = f"{TMDB_BASE}/search/movie"
    params = {'api_key': TMDB_API_KEY, 'query': query, 'language': 'en-US'}
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json().get('results', []) if r.status_code == 200 else []
    except: return []

def search_tmdb_tv(query):
    if not TMDB_API_KEY: return []
    url = f"{TMDB_BASE}/search/tv"
    params = {'api_key': TMDB_API_KEY, 'query': query, 'language': 'en-US'}
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json().get('results', []) if r.status_code == 200 else []
    except: return []

def search_tmdb_person(query):
    if not TMDB_API_KEY: return []
    url = f"{TMDB_BASE}/search/person"
    params = {'api_key': TMDB_API_KEY, 'query': query, 'language': 'en-US'}
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json().get('results', []) if r.status_code == 200 else []
    except: return []

def discover_movies(genre_id=None, sort_by='popularity.desc'):
    if not TMDB_API_KEY: return []
    url = f"{TMDB_BASE}/discover/movie"
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US', 'sort_by': sort_by}
    if genre_id: params['with_genres'] = genre_id
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json().get('results', []) if r.status_code == 200 else []
    except: return []

def get_genre_list():
    if not TMDB_API_KEY: return []
    url = f"{TMDB_BASE}/genre/movie/list"
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json().get('genres', []) if r.status_code == 200 else []
    except: return []

def get_now_playing_movies(region='US', page=1):
    if not TMDB_API_KEY: return []
    url = f"{TMDB_BASE}/movie/now_playing"
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US', 'region': region, 'page': page}
    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            results = r.json().get('results', [])
            for movie in results:
                movie['image_url'] = f"https://image.tmdb.org/t/p/w185{movie['poster_path']}" if movie.get('poster_path') else None
            return results
        return []
    except: return []

# ---------- LOGIN / LOGOUT ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

# ---------- ADMIN DASHBOARD ----------
@app.route('/admin')
@login_required
def admin_dashboard():
    stats = {
        'news': len(data.get_news()),
        'reviews': len(data.get_reviews()),
        'features': len(data.get_features()),
        'shows': len(data.get_shows()),
        'events': len(data.get_events()),
        'videos': len(data.get_videos()),
        'podcast_episodes': len(data.get_podcast_episodes()),
        'community_posts': len(data.get_community_posts()),
        'awards': len(data.get_awards()),
        'people': len(data.get_people())
    }
    return render_template('admin_dashboard.html', stats=stats)

# ---------- GENERIC ADMIN CRUD ROUTES ----------
def admin_list(collection, title):
    items = data.get_all_items(collection)
    return render_template('admin_list.html',
                           collection=collection,
                           items=items,
                           title=title)

def admin_edit(collection, item_id=None):
    item = data.get_item(collection, item_id) if item_id else {}
    fields = COLLECTION_FIELDS.get(collection, [])

    if request.method == 'POST':
        form_data = {}
        for field in fields:
            val = request.form.get(field['name'], '').strip()
            if field['name'] == 'people_tags' and val:
                val = [tag.strip() for tag in val.split(',') if tag.strip()]
            form_data[field['name']] = val

        # Handle image removal
        if 'remove_image' in request.form:
            form_data['image_url'] = None

        # Handle image upload to Supabase Storage
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                base, ext = os.path.splitext(filename)
                unique_name = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
                file_content = file.read()
                try:
                    # Upload to bucket 'review-images'
                    supabase.storage.from_('review-images').upload(
                        unique_name,
                        file_content,
                        file_options={"content-type": file.content_type}
                    )
                    # Get public URL
                    image_url = supabase.storage.from_('review-images').get_public_url(unique_name)
                    form_data['image_url'] = image_url
                except Exception as e:
                    print(f"Upload error: {e}")
                    if item.get('image_url'):
                        form_data['image_url'] = item['image_url']
                    else:
                        form_data['image_url'] = None
            elif file.filename == '' and 'image_url' not in form_data and item.get('image_url'):
                form_data['image_url'] = item.get('image_url')

        if 'image_url' not in form_data:
            form_data['image_url'] = item.get('image_url') if item_id else None

        if item_id:
            data.update_item(collection, item_id, form_data)
        else:
            data.add_item(collection, form_data)
        return redirect(url_for(f'admin_{collection}'))

    return render_template('admin_edit.html',
                           collection=collection,
                           item=item,
                           fields=fields,
                           is_new=item_id is None)

def admin_delete(collection, item_id):
    if data.delete_item(collection, item_id):
        return redirect(url_for(f'admin_{collection}'))
    return "Error deleting", 400

# ---- Register routes for each collection ----
collections = [
    ('news', 'News'),
    ('reviews', 'Reviews'),
    ('features', 'Features'),
    ('shows', 'Shows'),
    ('events', 'Events'),
    ('videos', 'Videos'),
    ('podcast_episodes', 'Podcast Episodes'),
    ('community_posts', 'Community Posts'),
    ('awards', 'Awards'),
    ('people', 'People')
]

for col, label in collections:
    app.add_url_rule(f'/admin/{col}',
                     endpoint=f'admin_{col}',
                     view_func=lambda c=col, l=label: admin_list(c, l),
                     methods=['GET'])
    app.add_url_rule(f'/admin/{col}/new',
                     endpoint=f'admin_{col}_new',
                     view_func=lambda c=col: admin_edit(c),
                     methods=['GET', 'POST'])
    app.add_url_rule(f'/admin/{col}/<item_id>',
                     endpoint=f'admin_{col}_edit',
                     view_func=lambda c=col, item_id=None: admin_edit(c, item_id),
                     methods=['GET', 'POST'])
    app.add_url_rule(f'/admin/{col}/delete/<item_id>',
                     endpoint=f'admin_{col}_delete',
                     view_func=lambda c=col, item_id=None: admin_delete(c, item_id),
                     methods=['POST'])

# Special case for Origins
@app.route('/admin/origins', methods=['GET', 'POST'])
@login_required
def admin_origins():
    origins = data.get_origins()
    if request.method == 'POST':
        new_content = request.form.get('content', '')
        data.update_origins({'title': origins.get('title', 'Origins'), 'content': new_content})
        return redirect(url_for('admin_origins'))
    return render_template('admin_origins.html', origins=origins)

# ---------- PUBLIC PAGES ----------
@app.route('/')
def home():
    news = data.get_news()[:4]
    reviews = data.get_reviews()[:4]
    shows = data.get_shows()
    return render_template('home.html',
                           news_articles=news,
                           reviews=reviews,
                           shows=shows)

@app.route('/news')
def news_page():
    items = data.get_news()
    return render_template('list.html', items=items, title="All News", type="news")

@app.route('/reviews')
def reviews_page():
    items = data.get_reviews()
    genre_filter = request.args.get('genre')
    if genre_filter:
        items = [r for r in items if r.get('genre', '').lower() == genre_filter.lower()]
    return render_template('list.html', items=items, title="All Reviews", type="reviews")

@app.route('/features')
def features_page():
    items = data.get_features()
    return render_template('list.html', items=items, title="Features", type="features")

@app.route('/shows')
def shows_page():
    items = data.get_shows()
    return render_template('list.html', items=items, title="Our Shows", type="shows")

@app.route('/streaming')
def streaming():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        movies = search_tmdb_movie(query)
        tvshows = search_tmdb_tv(query)
        combined = movies + tvshows
        for m in combined:
            m['image_url'] = f"https://image.tmdb.org/t/p/w185{m['poster_path']}" if m.get('poster_path') else None
            m['media_type'] = 'movie' if 'title' in m else 'tv'
            m['display_title'] = m.get('title') or m.get('name')
            m['date'] = m.get('release_date') or m.get('first_air_date') or 'N/A'
        results = combined
    return render_template('page.html', title="What To Stream", desc="Search for movies or TV shows to watch.",
                           query=query, results=results, search_type='movie_tv', show_search=True, is_streaming_search=True)

@app.route('/boxoffice')
def boxoffice():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        raw = search_tmdb_movie(query)
        for r in raw:
            r['image_url'] = f"https://image.tmdb.org/t/p/w185{r['poster_path']}" if r.get('poster_path') else None
        results = raw
    else:
        results = get_now_playing_movies(region='US', page=1)
    return render_template('page.html',
        title="Box Office",
        desc="Currently showing in theaters — updated daily.",
        query=query,
        results=results,
        is_boxoffice=True,
        search_type='movie',
        show_search=True
    )

@app.route('/genre')
def genre():
    genres = get_genre_list()
    genre_id = request.args.get('genre', '').strip()
    results = []
    if genre_id:
        raw = discover_movies(genre_id=genre_id)
        for r in raw:
            r['image_url'] = f"https://image.tmdb.org/t/p/w185{r['poster_path']}" if r.get('poster_path') else None
        results = raw
    return render_template('page.html', title="Browse By Genre", desc="Click a genre to discover movies.",
                           genres=genres, selected_genre=genre_id, results=results)

@app.route('/people')
def people():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        people = search_tmdb_person(query)
        for p in people[:20]:
            known_for = ', '.join([k.get('title') or k.get('name') or '' for k in p.get('known_for', [])[:3]]) if p.get('known_for') else ''
            results.append({
                'id': p.get('id'),
                'name': p.get('name'),
                'profile_path': p.get('profile_path'),
                'known_for_department': p.get('known_for_department', 'Actor'),
                'known_for': known_for,
                'popularity': p.get('popularity', 0),
                'image_url': f"https://image.tmdb.org/t/p/w185{p.get('profile_path')}" if p.get('profile_path') else None
            })
    return render_template('page.html', title="People", desc="Search for actors, directors, and other film industry professionals.",
                           query=query, results=results, is_people_search=True, show_search=True)

# Static pages
@app.route('/awards')
def awards():
    items = data.get_awards()
    return render_template('page.html', title="Awards", desc="Coverage, predictions, and reactions from the biggest nights in film and television.", items=items)

@app.route('/events')
def events():
    items = data.get_events()
    return render_template('page.html', title="Events", desc="Premieres, festivals, and industry events — where African Frame shows up.", items=items)

@app.route('/videos')
def videos():
    items = data.get_videos()
    return render_template('page.html', title="Videos", desc="All our video content in one place — reviews, breakdowns, and reactions.", items=items)

@app.route('/podcast')
def podcast():
    items = data.get_podcast_episodes()
    return render_template('page.html', title="Podcast", desc="The African Frame Podcast — long-form conversation on the films and shows that matter.", items=items)

@app.route('/community')
def community():
    items = data.get_community_posts()
    return render_template('page.html', title="Community", desc="Join the conversation. Share your takes, debate your rankings, and connect with other film and series fans.", items=items)

@app.route('/shop')
def shop():
    return render_template('page.html', title="Shop", desc="Merchandise is on its way. Stay tuned for exclusive African Frame gear.", coming_soon=True)

@app.route('/origins')
def origins():
    origins_data = data.get_origins()
    return render_template('page.html', title="Origins", desc=origins_data.get('content', ''), is_origins=True)

# ---------- COOKIE & PRIVACY POLICIES ----------
@app.route('/cookie-policy')
def cookie_policy():
    return render_template('cookie_policy.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

# ---------- TMDB DETAIL ROUTES ----------
@app.route('/tmdb/person/<int:person_id>')
def tmdb_person_detail(person_id):
    url = f"{TMDB_BASE}/person/{person_id}"
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US', 'append_to_response': 'combined_credits'}
    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            person = r.json()
            return render_template('tmdb_detail.html', person=person, type='person')
    except: pass
    return "Person not found", 404

@app.route('/tmdb/movie/<int:movie_id>')
def tmdb_movie_detail(movie_id):
    url = f"{TMDB_BASE}/movie/{movie_id}"
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            movie = r.json()
            return render_template('tmdb_detail.html', movie=movie, type='movie')
    except: pass
    return "Movie not found", 404

@app.route('/tmdb/tv/<int:tv_id>')
def tmdb_tv_detail(tv_id):
    url = f"{TMDB_BASE}/tv/{tv_id}"
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            tv = r.json()
            return render_template('tmdb_detail.html', tv=tv, type='tv')
    except: pass
    return "TV show not found", 404

# ---------- API ROUTES ----------
@app.route('/api/data', methods=['GET'])
@login_required
def api_get_data():
    return jsonify(data._load())

@app.route('/api/news', methods=['POST'])
@login_required
def api_update_news():
    new_news = request.json
    if isinstance(new_news, list):
        data.update_news(new_news)
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'invalid data'}), 400

@app.route('/api/reviews', methods=['POST'])
@login_required
def api_update_reviews():
    new_reviews = request.json
    if isinstance(new_reviews, list):
        data.update_reviews(new_reviews)
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'invalid data'}), 400

@app.route('/api/reset', methods=['POST'])
@login_required
def api_reset():
    data.reset_data()
    return jsonify({'status': 'ok'})

# ---------- AUTOCOMPLETE ----------
@app.route('/api/autocomplete')
def autocomplete():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    movie_results = search_tmdb_movie(query)
    tv_results = search_tmdb_tv(query)
    people_results = search_tmdb_person(query)
    suggestions = []
    for m in movie_results[:5]:
        suggestions.append({'label': m['title'], 'year': m.get('release_date', '').split('-')[0] if m.get('release_date') else '', 'type': 'movie', 'id': m['id']})
    for t in tv_results[:5]:
        suggestions.append({'label': t['name'], 'year': t.get('first_air_date', '').split('-')[0] if t.get('first_air_date') else '', 'type': 'tv', 'id': t['id']})
    for p in people_results[:5]:
        suggestions.append({'label': p['name'], 'year': '', 'type': 'person', 'id': p['id']})
    return jsonify(suggestions[:12])

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)