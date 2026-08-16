import json
import os

DATA_FILE = "data.json"

DEFAULT_DATA = {
    "news": [
        {"id": "n1", "tag": "Industry", "title": "Local Studio Announces Slate Of Five New Features", "meta": "2 hrs ago · 4 min read"},
        {"id": "n2", "tag": "Casting", "title": "Lead Role Recast Weeks Before Production Start", "meta": "5 hrs ago · 3 min read"},
        {"id": "n3", "tag": "Festival", "title": "Official Selection List Released For This Year's Festival", "meta": "Yesterday · 6 min read"},
        {"id": "n4", "tag": "Streaming", "title": "Platform Confirms Local Original Renewed For Season Two", "meta": "Yesterday · 3 min read"},
    ],
    "reviews": [
        {"id": "r1", "tag": "Drama", "title": "A Quiet Return", "blurb": "A patient, aching family drama that trusts its silences.", "score": "9.1"},
        {"id": "r2", "tag": "Action", "title": "Last Line Of Defence", "blurb": "Big set pieces, thin plotting — style carries it most of the way.", "score": "7.3"},
        {"id": "r3", "tag": "Comedy", "title": "Wedding Season", "blurb": "Sharp, warm, and unafraid to let a joke breathe.", "score": "8.6"},
        {"id": "r4", "tag": "Horror", "title": "The Nightwatch", "blurb": "A strong first act that the back half can't sustain.", "score": "6.2"},
    ],
    "architecture": [
        {"id": "a1", "tag": "Design", "title": "Set Design That Tells the Story", "meta": "3 days ago · 5 min read"},
        {"id": "a2", "tag": "Technical", "title": "How Camera Movement Shapes Emotion", "meta": "1 week ago · 7 min read"},
        {"id": "a3", "tag": "Perspective", "title": "The Architecture of Suspense in Horror", "meta": "2 weeks ago · 6 min read"},
    ]
}

def _load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return DEFAULT_DATA.copy()
    return DEFAULT_DATA.copy()

def _save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_news():
    return _load().get("news", [])

def get_reviews():
    return _load().get("reviews", [])

def get_architecture():
    return _load().get("architecture", [])

def get_all():
    return _load()

def update_news(news_list):
    data = _load()
    data["news"] = news_list
    _save(data)

def update_reviews(reviews_list):
    data = _load()
    data["reviews"] = reviews_list
    _save(data)

def update_architecture(arch_list):
    data = _load()
    data["architecture"] = arch_list
    _save(data)

def reset_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    _save(DEFAULT_DATA.copy())