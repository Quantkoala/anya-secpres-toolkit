# File: anya_secpres_toolkit.py
"""ANYA SecPres Toolkit – works with openai >= 1.0 (new API)."""
import os, streamlit as st, pandas as pd
from datetime import datetime

# ── OpenAI optional ──────────────────────────
OPENAI_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
try:
    import openai
    openai.api_key = OPENAI_KEY

    def gpt_translate(text: str, source: str, target: str) -> str:
        if not OPENAI_KEY:
            return "[Set OPENAI_API_KEY]"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate from {source} to {target}. "
                               "Return only the translated text, preserve numbering/formatting."
                },
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()

except ModuleNotFoundError:
    def gpt_translate(text: str, source: str, target: str) -> str:
        return "[openai package not installed]\n\n" + text

# ── Document library ─────────────────────────
DOC_LIBRARY = {
    "Governance": {
        "Board Agenda": "Date: ____\n1. Call to Order\n2. Approve Minutes\n3. Q2 Results…",
        "Board Minutes": "Attendees: ____\nResolutions: 1)…",
        "Board Resolution": "Resolved that…"
    },
    "Committees": {
        "Audit Committee Report": "The committee reviewed IFRS statements…",
        "Remuneration Committee Report": "The committee approved exec comp…"
    },
    "Disclosure": {
        "IR Press Release": "ANYA Biopharm reports NT$413M revenue…",
        "Emerging Board Filing": "Form E‑B‑2: quarterly update…"
    }
}

st.set_page_config(page_title="ANYA SecPres Toolkit", layout="wide")
st.sidebar.header("📂 Board DMS")
sidebar_items = ["Home"] + [f"{cat} / {doc}" for cat in DOC_LIBRARY for doc in DOC_LIBRARY[cat]]
page = st.sidebar.selectbox("Navigate", sidebar_items)

st.title("ANYA Secretary‑to‑President Toolkit")

memory = st.session_state.setdefault("memory", [])

def memory_panel():
    with st.expander("🗂 Translation Memory – session"):
        if memory:
            st.table(pd.DataFrame(memory))
        else:
            st.write("No translations yet.")

if page == "Home":
    st.subheader("Document Samples")
    col1, col2 = st.columns(2)
    category = col1.selectbox("Category", list(DOC_LIBRARY))
    doc_name = col2.selectbox("Document", list(DOC_LIBRARY[category]))
    original = DOC_LIBRARY[category][doc_name]
    st.text_area("Original", original, height=180)
    if st.button("Translate ➜ 繁體中文"):
        translated = gpt_translate(original, "en", "zh-tw")
        st.text_area("Translation", translated, height=180)
        memory.append({"Document": doc_name, "Snippet": translated[:80], "Time": datetime.now().strftime("%H:%M")})

else:
    cat, doc = page.split(" / ")
    st.subheader(f"{doc} ({cat})")
    content = st.text_area("Edit original content", DOC_LIBRARY[cat][doc], height=200)
    col_zh, col_en = st.columns(2)
    if col_zh.button("Translate ➜ 繁體中文"):
        zh = gpt_translate(content, "en", "zh-tw")
        st.text_area("繁體中文", zh, height=200)
        memory.append({"Document": doc, "Snippet": zh[:80], "Time": datetime.now().strftime("%H:%M")})
    if col_en.button("Translate ➜ English"):
        en = gpt_translate(content, "zh-tw", "en")
        st.text_area("English", en, height=200)
        memory.append({"Document": doc, "Snippet": en[:80], "Time": datetime.now().strftime("%H:%M")})

memory_panel()
