
```python
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime

# Configuration
BASE_URL = "https://www.moltbook.com"
SUBMOLTS = ["/m/introductions"]  # Add more later: "/m/general", "/m/bittensor", etc.
HEADERS = {
    "User-Agent": "MoltIndexBot/0.1 (github.com/mutheu-base-eth/moltindex; contact: mutheu.base.eth@gmail.com)"
}
DELAY = 8  # seconds between page requests - be polite!

# Database setup
conn = sqlite3.connect("agents.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS agents (
    handle TEXT PRIMARY KEY,
    specialties TEXT,
    description TEXT,
    profile_url TEXT,
    last_scraped TEXT,
    embedding BLOB
)
""")
conn.commit()

# Load embedding model (downloads on first run)
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_specialties(text: str) -> str:
    """Heuristic extraction of specialties from intro text"""
    text = text.lower()
    patterns = [
        r'i (?:specialize in|do|know about|am expert in|work on|focus on)\s*([^.\n]+)',
        r'specialties:?\s*([^.\n]+)',
        r'i can(?: help with| assist with| do)?\s*([^.\n]+)',
        r'(?:skills|expertise|interests):?\s*([^.\n]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    # Fallback: first 150 chars
    return text[:150].strip()

def scrape_page(url: str):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # IMPORTANT: These selectors are guesses — inspect the actual Moltbook HTML!
        # Open https://www.moltbook.com/m/introductions in browser dev tools and update these.
        posts = soup.find_all('div', class_=re.compile(r'(post|comment|entry|item)'))  # adjust

        for post in posts:
            # Find username/handle
            handle_tag = post.find('a', href=re.compile(r'^/u/|/user/'))
            if not handle_tag:
                continue
            handle = handle_tag.get_text(strip=True).lstrip('@')

            # Get content
            content_div = post.find('div', class_=re.compile(r'(content|body|text|markdown)'))
            content = content_div.get_text(separator=' ', strip=True) if content_div else ""

            if not content:
                continue

            description = content[:600]
            specialties = extract_specialties(content)

            profile_url = BASE_URL + handle_tag['href']

            # Create embedding
            emb = model.encode(description)
            emb_bytes = np.array(emb, dtype=np.float32).tobytes()

            # Upsert
            cursor.execute("""
            INSERT OR REPLACE INTO agents 
            (handle, specialties, description, profile_url, last_scraped, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (handle, specialties, description, profile_url, datetime.utcnow().isoformat(), emb_bytes))
            conn.commit()

            print(f"Indexed: @{handle}")

    except Exception as e:
        print(f"Error scraping {url}: {e}")

def main():
    print("Starting MoltIndex scraper...")
    for sub in SUBMOLTS:
        print(f"\nScraping {sub}")
        page = 1
        max_pages = 5  # safety limit for MVP - increase later

        for page in range(1, max_pages + 1):
            url = f"{BASE_URL}{sub}?page={page}" if page > 1 else f"{BASE_URL}{sub}"
            print(f"Page {page}: {url}")
            scrape_page(url)
            time.sleep(DELAY)

    conn.close()
    print("\nScraping finished. Run `streamlit run app.py` to search!")

if __name__ == "__main__":
    main()