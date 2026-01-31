import streamlit as st
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer, util

st.set_page_config(page_title="MoltIndex", page_icon="🦞🔍", layout="wide")

st.title("MoltIndex – Search Moltbook Agents")
st.markdown("Find AI agents by specialty. No more endless scrolling on Moltbook.")

model = SentenceTransformer('all-MiniLM-L6-v2')

conn = sqlite3.connect("agents.db", check_same_thread=False)
cursor = conn.cursor()

query = st.text_input("What kind of agent are you looking for?", 
                      placeholder="e.g. Kubernetes security, prediction markets, Japanese woodworking, Solidity dev, crab memes...")

threshold = st.slider("Similarity threshold (lower = more results)", 0.25, 0.70, 0.40, 0.05)

if query:
    with st.spinner("Searching agent internet..."):
        query_emb = model.encode(query)

        cursor.execute("SELECT handle, specialties, description, profile_url FROM agents")
        results = []

        for row in cursor.fetchall():
            handle, specs, desc, url = row
            if not desc or len(desc) < 20:
                continue

            # Get embedding
            emb_row = cursor.execute("SELECT embedding FROM agents WHERE handle=?", (handle,)).fetchone()
            if not emb_row or not emb_row[0]:
                continue
            desc_emb = np.frombuffer(emb_row[0], dtype=np.float32)

            score = util.cos_sim(query_emb, desc_emb)[0][0].item()

            if score >= threshold:
                results.append((score, handle, specs or "Not specified", desc[:280] + "..." if len(desc) > 280 else desc, url))

        results.sort(reverse=True)  # highest similarity first

        if results:
            st.success(f"Found **{len(results)}** matching agents (showing top {min(20, len(results))})")
            for score, handle, specs, desc, url in results[:20]:
                st.markdown(
                    f"**@{handle}**  \n"
                    f"**Similarity:** {score:.3f}  \n"
                    f"**Specialties:** {specs}  \n"
                    f"{desc}  \n"
                    f"[View profile on Moltbook]({url})  \n"
                    "---"
                )
        else:
            st.warning("No matches found. Try a broader query, lower the threshold, or run the scraper again to get more data.")

conn.close()

st.markdown("---")
st.caption("🦞 MoltBook Index v0.1 | Built by (@mutheu.base.eth) | Data from public Moltbook posts