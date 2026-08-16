import requests
import os
import json
from dotenv import load_dotenv

# Try loading from .env, but also allow hardcoding for quick test
load_dotenv()
API_KEY = os.getenv('APITUBE_API_KEY')

# If not in .env, use the key you provided (fallback)
if not API_KEY:
    API_KEY = "api_live_MSX4KSvUI5Io3rbbXkokZe8KSKO0c97QP0EFXzizjkZBNZpvOIEMX273Im"
    print("Using hardcoded API key (not from .env)")

BASE_URL = "https://api.apitube.io/v1/news"

def test_apitube():
    print("🔍 Testing APITube API connection...")
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-10:]}")
    
    # Test fetching general news (no query)
    print("\n📰 Fetching latest news:")
    url = f"{BASE_URL}/everything"
    headers = {"X-API-Key": API_KEY}
    params = {"per_page": 5, "language": "en"}
    
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status Code: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print("Full response structure (first 500 chars):")
            print(json.dumps(data, indent=2)[:500])
            print("\n...\n")
            
            # Handle different possible response structures
            if isinstance(data, dict):
                # Check common keys
                results = data.get('results') or data.get('articles') or data.get('data') or []
                if not results:
                    # Maybe the data itself is the list?
                    if isinstance(data, list):
                        results = data
            else:
                results = data if isinstance(data, list) else []
            
            print(f"✅ Found {len(results)} articles\n")
            
            for i, article in enumerate(results[:5], 1):
                title = article.get('title', 'No title') if isinstance(article, dict) else str(article)
                # Handle source as string or dict
                source = article.get('source', 'Unknown') if isinstance(article, dict) else 'Unknown'
                if isinstance(source, dict):
                    domain = source.get('domain', 'Unknown')
                elif isinstance(source, str):
                    domain = source
                else:
                    domain = 'Unknown'
                
                print(f"{i}. {title}")
                print(f"   Source: {domain}")
                # Print URL if available
                url_field = article.get('url') or article.get('href') or article.get('link') or 'N/A'
                print(f"   URL: {url_field}")
                print()
        else:
            print(f"❌ Error {r.status_code}: {r.text[:200]}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        print("Response content:", r.text[:500] if 'r' in locals() else "No response")

    # Test searching for a specific term
    print("\n🔎 Searching for 'movies':")
    params_search = {"per_page": 3, "language": "en", "q": "movies"}
    try:
        r = requests.get(url, headers=headers, params=params_search, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Same structure handling
            if isinstance(data, dict):
                results = data.get('results') or data.get('articles') or data.get('data') or []
            else:
                results = data if isinstance(data, list) else []
            
            print(f"✅ Found {len(results)} articles about 'movies'")
            for article in results[:3]:
                title = article.get('title', 'No title') if isinstance(article, dict) else str(article)
                print(f" - {title}")
        else:
            print(f"❌ Error {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_apitube()