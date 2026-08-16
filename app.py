from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import data
import secrets
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file (for local development)
load_dotenv()

app = Flask(__name__)

# ---------- APP CONFIG ----------
# Use environment variable for secret key, fallback to random for local
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# ---------- TMDB CONFIG ----------
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
TMDB_BASE = 'https://api.themoviedb.org/3'

# ---------- NEWSAPI CONFIG ----------
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')
NEWSAPI_BASE = 'https://newsapi.org/v2'

# ---------- ADMIN CREDENTIALS (can be overridden by env vars) ----------
ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'password123')


# ---------- TMDB HELPERS ----------
def search_tmdb_movie(query):
    if not TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/search/movie"
    params = {'api_key': TMDB_API_KEY, 'query': query, 'language': 'en-US'}
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json().get('results', []) if r.status_code == 200 else []
    except:
        return []

def search_tmdb_tv(query):
    if not TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/search/tv"
    params = {'api_key': TMDB_API_KEY, 'query': query, 'language': 'en-US'}
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json().get('results', []) if r.status_code == 200 else []
    except:
        return []

def search_tmdb_person(query):
    if not TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/search/person"
    params = {'api_key': TMDB_API_KEY, 'query': query, 'language': 'en-US'}
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json().get('results', []) if r.status_code == 200 else []
    except:
        return []

def discover_movies(genre_id=None, sort_by='popularity.desc'):
    if not TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/discover/movie"
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US', 'sort_by': sort_by}
    if genre_id:
        params['with_genres'] = genre_id
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json().get('results', []) if r.status_code == 200 else []
    except:
        return []

def get_genre_list():
    if not TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/genre/movie/list"
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
    try:
        r = requests.get(url, params=params, timeout=5)
        return r.json().get('genres', []) if r.status_code == 200 else []
    except:
        return []

def get_now_playing_movies(region='US', page=1):
    if not TMDB_API_KEY:
        return []
    url = f"{TMDB_BASE}/movie/now_playing"
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'region': region,
        'page': page
    }
    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            data = r.json()
            results = data.get('results', [])
            for movie in results:
                movie['image_url'] = f"https://image.tmdb.org/t/p/w185{movie['poster_path']}" if movie.get('poster_path') else None
            return results
        else:
            return []
    except:
        return []


# ---------- NEWSAPI HELPER ----------
def fetch_news(query=None, per_page=12):
    if not NEWSAPI_KEY:
        return []
    url = f"{NEWSAPI_BASE}/everything"
    params = {
        'apiKey': NEWSAPI_KEY,
        'language': 'en',
        'pageSize': per_page,
        'sortBy': 'publishedAt'
    }
    if query:
        params['q'] = query
    else:
        params['q'] = 'movie OR film OR cinema OR "TV show" OR "television series" OR Netflix OR "streaming series" OR "movie review"'
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    params['from'] = week_ago
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            normalized = []
            for a in articles:
                normalized.append({
                    'title': a.get('title', ''),
                    'description': a.get('description', ''),
                    'url': a.get('url', '#'),
                    'image': a.get('urlToImage'),
                    'source': a.get('source', {}).get('name', 'Unknown'),
                    'published_at': a.get('publishedAt', '')
                })
            return normalized
        else:
            return []
    except:
        return []


# ---------- LOGIN / LOGOUT ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))


# ---------- DECORATOR ----------
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------- PAGE ROUTES ----------
@app.route('/')
def home():
    news_articles = fetch_news(per_page=4)
    return render_template('home.html',
        news_articles=news_articles,
        reviews=data.get_reviews()[:4]
    )

@app.route('/news')
def news_page():
    local_news = data.get_news()
    query = request.args.get('q', '').strip()
    external_news = fetch_news(query=query if query else None, per_page=20)
    return render_template('list.html',
        items=local_news,
        title="All News",
        type="news",
        external_news=external_news,
        external_query=query,
        has_api_key=bool(NEWSAPI_KEY)
    )

@app.route('/reviews')
def reviews_page():
    return render_template('list.html', items=data.get_reviews(), title="All Reviews", type="reviews")

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

@app.route('/features')
def features():
    return render_template('page.html', title="Features", desc="Long-form breakdowns, think-pieces, and deep dives into the stories, characters, and franchises we can't stop talking about.")

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

@app.route('/shows')
def shows():
    return render_template('page.html', title="Our Shows", desc="From flagship reviews to series coverage, box office news, and franchise deep-dives — here's everything we produce.")

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

@app.route('/awards')
def awards():
    return render_template('page.html', title="Awards", desc="Coverage, predictions, and reactions from the biggest nights in film and television.")

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

@app.route('/events')
def events():
    return render_template('page.html', title="Events", desc="Premieres, festivals, and industry events — where African Frame shows up.")

@app.route('/videos')
def videos():
    return render_template('page.html', title="Videos", desc="All our video content in one place — reviews, breakdowns, and reactions.")

@app.route('/podcast')
def podcast():
    return render_template('page.html', title="Podcast", desc="The African Frame Podcast — long-form conversation on the films and shows that matter.")

@app.route('/community')
def community():
    return render_template('page.html', title="Community", desc="Join the conversation. Share your takes, debate your rankings, and connect with other film and series fans.")

@app.route('/shop')
def shop():
    return render_template('page.html', title="Shop", desc="Merchandise is on its way. Stay tuned for exclusive African Frame gear.", coming_soon=True)

@app.route('/origins')
def origins():
    return render_template('page.html', title="Origins", desc="From one man dissecting trailers alone, to a full slate of shows across four YouTube channels — this is how African Frame came together, frame by frame.", is_origins=True)


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
        suggestions.append({
            'label': m['title'],
            'year': m.get('release_date', '').split('-')[0] if m.get('release_date') else '',
            'type': 'movie',
            'id': m['id']
        })
    for t in tv_results[:5]:
        suggestions.append({
            'label': t['name'],
            'year': t.get('first_air_date', '').split('-')[0] if t.get('first_air_date') else '',
            'type': 'tv',
            'id': t['id']
        })
    for p in people_results[:5]:
        suggestions.append({
            'label': p['name'],
            'year': '',
            'type': 'person',
            'id': p['id']
        })
    return jsonify(suggestions[:12])


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
    except:
        pass
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
    except:
        pass
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
    except:
        pass
    return "TV show not found", 404


# ---------- ADMIN ----------
@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')


# ---------- API ROUTES ----------
@app.route('/api/data', methods=['GET'])
@login_required
def api_get_data():
    return jsonify(data.get_all())

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


# ---------- RUN ----------
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)