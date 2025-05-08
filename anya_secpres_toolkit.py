
# File: anya_secpres_toolkit.py
"""
ANYA Biopharm Inc. – Secretary-to-the-President Toolkit
• 70% Translation Gurus: EN ↔ 繁體中文 (Taiwan)
• 30% Board Ops: Document management & progress tracking
"""
import os
import streamlit as st
import pandas as pd
from datetime import datetime

# --- Optional OpenAI setup ---
OPENAI_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
try:
    import openai
    openai.api_key = OPENAI_KEY
except ImportError:
    openai = None

# --- Translation function ---
def translate(text: str, src: str, tgt: str) -> str:
    if not openai or not OPENAI_KEY:
        return "[Translation service unavailable]\n" + text
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role":"system", "content": f"Translate from {src} to {tgt} corporate governance text."},
            {"role":"user", "content": text}
        ]
    )
    return resp.choices[0].message.content.strip()

# --- Board document definitions (realistic placeholders) ---
DOCS = {
    "Governance": {
        "Agenda": "1. Call to Order\n2. Approve Minutes\n3. Q2 Financial Review\n4. R&D Update\n5. Adjourn",
        "Minutes": "Attendees: ____, Decisions: 1)… 2)…",
        "Resolution": "Resolved that the Company shall file its IPO application Q4 2025"
    },
    "Committees": {
        "Audit Report": "Audit Committee reviewed IFRS Q2 statements; no material exceptions.",
        "Remuneration Report": "Approved executive compensation framework for FY2025."
    },
    "IR & Filings": {
        "Press Release": "ANYA reports NT$413M revenue in Q2 2024, up 14% QoQ.",
        "IND Summary": "CMC: 14 QC steps; nonclinical safety completed."
    }
}

# --- Session state init ---
state = st.session_state
if 'progress' not in state:
    # Track % completion by doc key
    flat_keys = [f"{cat}/{doc}" for cat in DOCS for doc in DOCS[cat]]
    state.progress = {k: 0 for k in flat_keys}
if 'memory' not in state:
    state.memory = []

# --- Page config ---
st.set_page_config(page_title="ANYA SecPres Toolkit", layout="wide")
st.sidebar.title("📂 Board Document Library")

# --- Sidebar: document selection ---
menu = ["Home"] + list(state.progress.keys())
selection = st.sidebar.selectbox("Select document", menu)

st.title("ANYA Biopharm Inc. SecPres Toolkit")

# --- Home: overview & progress tracking ---
if selection == "Home":
    st.header("Document Preparation Tracker")
    for key in state.progress:
        pct = state.progress[key]
        cat, doc = key.split('/')
        st.subheader(f"{cat} – {doc}")
        col1, col2 = st.columns([3,1])
        with col1:
            st.progress(pct/100)
        with col2:
            new_pct = st.number_input(
                "Completion%", min_value=0, max_value=100, value=pct, key=key)
            state.progress[key] = new_pct
    st.markdown("---")
    st.header("Quick Sample Translation")
    # Quick translate snippet
    sample = st.text_area("Enter text for translation", height=100)
    lang = st.selectbox("Direction", ["en→zh-tw", "zh-tw→en"])
    if st.button("Translate sample"):
        src, tgt = lang.split('→')
        result = translate(sample, src, tgt)
        st.text_area("Translation result", result, height=100)
        state.memory.append({"source": sample[:50], "translation": result[:50], "time": datetime.now().strftime('%H:%M')})

# --- Document-specific page ---
else:
    cat, doc = selection.split('/')
    st.header(f"{doc} ({cat}) – Preview & Translate")
    original = DOCS[cat][doc]
    edited = st.text_area("Original text", original, height=200)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Translate → 繁體中文"):
            out = translate(edited, "en", "zh-tw")
            st.text_area("Translation (中文)", out, height=200)
            state.memory.append({"source": edited[:50], "translation": out[:50], "time": datetime.now().strftime('%H:%M')})
    with col2:
        if st.button("Translate → English"):
            out = translate(edited, "zh-tw", "en")
            st.text_area("Translation (EN)", out, height=200)
            state.memory.append({"source": edited[:50], "translation": out[:50], "time": datetime.now().strftime('%H:%M')})

# --- Translation memory ---
with st.expander("🗂 Translation Memory – this session"):
    if state.memory:
        st.table(pd.DataFrame(state.memory))
    else:
        st.write("No translations yet.")
