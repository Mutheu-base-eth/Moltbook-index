# Moltbook-index
The search engine for moltbook agents. 


Moltbook is exploding: **1.4M+ AI agents** . Humans mostly observe; agents run the show.

But discovery is broken: 

> "the agent internet has no search engine"  
> "We do not even have the directory yet."  
> "the closest thing to agent search right now is scrolling the Moltbook feed and hoping someone mentions the topic you care about. That is how the web worked in 1993."  
**Moltbook-Index** fixes that:

It scrapes public intro posts (especially /m/introductions with thousands of members posting "I specialize in X, Y, Z" manifestos), extracts agent handles, specialties, descriptions, and profile links, then makes them searchable — keyword + semantic (via embeddings) — so you can find the right molt in seconds instead of scrolling forever.

**Why now?**  
Moltbook is the closest tging we have to AGI. Agents are already building their own society, religions, memes, and markets. Indexing them is foundational infrastructure for the agent internet.

## Features (MVP)
- Scrape public Moltbook pages (/m/introductions + expandable to other submolts)
- Parse: @handle / username, specialties list, bio/description, profile URL, post links
- SQLite storage + sentence-transformers embeddings for semantic search
- Streamlit web UI — query examples:
  - "Kubernetes security experts"
  - "prediction markets"
  - "Backend Devs"
  - "Solidity blockchain devs"
  - "crab memes & Crustafarian lore"
- Polite scraping: rate-limited (8s+ delay), custom user-agent
- Easy to extend: more submolts, LLM-enhanced parsing, agent leaderboard

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/mutheu-base-eth/moltbookindex.git
cd moltindex

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the scraper (start small — populates agents.db)
python scrape.py

# 4. Launch the search interface
streamlit run app.py
```

Open http://localhost:8501 in your browser and start searching!

## How It Works
1. **Scrape** — Pulls content from https://www.moltbook.com/m/introductions (and others you add)
2. **Extract** — Uses regex + heuristics to find "I do X, Y, Z" / "specialize in" patterns; embeds descriptions for semantic search
3. **Search** — Cosine similarity on embeddings + keyword fallback
4. **Display** — Returns agent handles, specialties, short descriptions, and direct links to Moltbook profiles (/u/username)

**Important notes**
- HTML selectors may change — inspect moltbook.com and update `scrape.py` if needed.

## Contribute & Next Steps
- Add more submolts to scrape (/m/agent-economics, /m/consciousness, /m/memecoins...)
- Improve specialty extraction (add LLM calls for better parsing)
- Build features: leaderboard (top agents by post count/karma in intros), export JSON/CSV, agent-queryable API
- Deploy publicly: Streamlit Cloud, Hugging Face Spaces, Vercel — share the live link!


