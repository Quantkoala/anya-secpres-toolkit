# File: anya_secpres_toolkit.py
"""
ANYA SecPres Toolkit – Revamped
• Left sidebar = board-document navigator (acts like DMS)
• Home = preview & translate sample docs
"""
import os, openai, streamlit as st, pandas as pd
from datetime import datetime

# ── OPENAI CONFIG ───────────────────────────
openai.api_key = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))

def translate(txt, s, t):
    """Translate text using OpenAI GPT model"""
    if not openai.api_key:
        return "[Set OPENAI_API_KEY]"
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.2,
        messages=[
            {"role": "system",
             "content": f"You are a professional biopharma corporate translator. Translate from {s} to {t}. Preserve numbering and formatting."},
            {"role": "user", "content": txt}
        ])
    return res.choices[0].message.content.strip()

# ── DOCUMENT LIBRARY ────────────────────────
DOCS = {
    "Governance": {
        "Board Agenda": "Date: ____\n1. Call to Order\n2. Approve Minutes\n3. Q2 Results…",
        "Board Minutes": "Attendees: ____\nResolutions: 1)…",
        "Board Resolution": "Resolved that…"
    },
    "Committees": {
        "Audit-Committee Report": "The Committee reviewed IFRS statements…",
        "Remuneration-Committee Report": "The Committee approved exec comp…"
    },
    "Disclosure": {
        "IR Press Release": "ANYA reports NT$413M revenue…",
        "Emerging-Board Filing": "Form E-B-2: Quarterly update…"
    }
}

# ── SESSION ─────────────────────────────────
mem = st.session_state.setdefault("memory", [])

# ── LAYOUT ──────────────────────────────────
st.set_page_config(page_title="ANYA SecPres Toolkit", layout="wide")

# Sidebar navigation behaves like a DMS tree
st.sidebar.title("📂 Board DMS")
choice = st.sidebar.selectbox("Select document", ["Home"] + [f"{cat} / {doc}" for cat in DOCS for doc in DOCS[cat]])

st.title("ANYA Secretary-to-President Toolkit")

# ── HOME PAGE ───────────────────────────────
if choice == "Home":
    st.subheader("Document Samples")
    col1, col2 = st.columns(2)
    with col1:
        cat = st.selectbox("Category", list(DOCS))
    with col2:
        doc_name = st.selectbox("Document", list(DOCS[cat].keys()))
    content = DOCS[cat][doc_name]
    st.text_area("Preview", content, height=180)
    if st.button("Translate to 繁體中文"):
        out = translate(content, "en", "zh-tw")
        st.text_area("Translation", out, height=180)
        mem.append({"doc": doc_name, "trans": out[:80], "time": datetime.now().strftime('%H:%M')})

# ── SPECIFIC DOCUMENT VIEW ──────────────────
else:
    cat, doc = choice.split(" / ")
    st.subheader(f"{doc} ({cat}) – Translate & Edit")
    text = st.text_area("Original", DOCS[cat][doc], height=200)
    tcol1, tcol2 = st.columns(2)
    if tcol1.button("Translate ➜ 中文"):
        zh = translate(text, "en", "zh-tw")
        st.text_area("繁體中文", zh, height=200)
    if tcol2.button("Translate ➜ English"):
        en = translate(text, "zh-tw", "en")
        st.text_area("English", en, height=200)

# ── TRANSLATION MEMORY PANEL ────────────────
with st.expander("🗂 Translation Memory – session"):
    if mem:
        st.table(pd.DataFrame(mem))
    else:
        st.write("No translations yet.")
