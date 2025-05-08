
"""ANYA SecPres Toolkit
A minimal Streamlit board‑document manager + EN↔繁體中文 translator.
Works even if OPENAI_API_KEY is missing (falls back to dummy translation).
"""
import os, streamlit as st, pandas as pd
from datetime import datetime

# -------- OpenAI optional --------
OPENAI_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
try:
    import openai
    openai.api_key = OPENAI_KEY
    def gpt_translate(text: str, source: str, target: str) -> str:
        if not OPENAI_KEY:
            return "[Set OPENAI_API_KEY in Settings → Secrets]\n\n" + text
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            messages=[
                {"role": "system",
                 "content": f"You are a professional translator. Translate from {source} to {target}. "
                            f"Return only translated text; keep formatting/numbering."},
                {"role": "user", "content": text}
            ]
        )
        return resp.choices[0].message.content.strip()
except ModuleNotFoundError:
    def gpt_translate(text: str, source: str, target: str) -> str:
        return "[OpenAI package not installed]\n\n" + text

# -------- Sample board documents --------
DOC_LIBRARY = {
    "Governance": {
        "Board Agenda": "Date: ____\n1. Call to order\n2. Approve minutes\n3. Q2 results\n4. R&D update\n5. Other business",
        "Board Minutes": "Attendees: ____\nResolutions: 1) Approved Q2 results 2) Approved R&D budget",
        "Board Resolution": "Resolved that the Company shall file IPO application in Q4 2025."
    },
    "Committees": {
        "Audit Committee Report": "The committee reviewed the IFRS Q2 statements and found no material misstatements.",
        "Remuneration Committee Report": "The committee approved executive compensation for FY 2025."
    },
    "Disclosure": {
        "IR Press Release": "ANYA Biopharm reports NT$413 million revenue for Q2 2024, up 14 % QoQ.",
        "Emerging Board Filing": "Form E‑B‑2: quarterly operating update submitted on ____."
    }
}

# -------- Streamlit layout --------
st.set_page_config(page_title="ANYA SecPres Toolkit", layout="wide")

st.sidebar.header("📂 Board DMS")
sidebar_items = ["Home"] + [f"{cat} / {doc}" for cat in DOC_LIBRARY for doc in DOC_LIBRARY[cat]]
page = st.sidebar.selectbox("Navigate", sidebar_items)

st.title("ANYA Secretary‑to‑President Toolkit")

# Session state for translation memory
memory = st.session_state.setdefault("memory", [])

def translation_memory_panel():
    with st.expander("🗂 Translation Memory (this session)"):
        if memory:
            st.table(pd.DataFrame(memory))
        else:
            st.write("No translations yet.")

# ---------- Home page ---------
if page == "Home":
    st.subheader("👉 Select a sample document to preview & translate")
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", list(DOC_LIBRARY))
    with col2:
        doc_name = st.selectbox("Document", list(DOC_LIBRARY[category]))
    original = DOC_LIBRARY[category][doc_name]
    st.text_area("Original document", original, height=180)
    if st.button("Translate to 繁體中文"):
        translated = gpt_translate(original, "en", "zh-tw")
        st.text_area("Translation", translated, height=180)
        memory.append({"Document": doc_name, "Snippet": translated[:80], "Time": datetime.now().strftime("%H:%M")})

# ---------- Specific doc page ---------
else:
    cat, doc = page.split(" / ")
    st.subheader(f"{doc} ({cat})")
    content = st.text_area("Edit original content", DOC_LIBRARY[cat][doc], height=200)
    col_en, col_zh = st.columns(2)
    if col_zh.button("Translate ➜ 繁體中文"):
        zh = gpt_translate(content, "en", "zh-tw")
        st.text_area("繁體中文", zh, height=200)
        memory.append({"Document": doc, "Snippet": zh[:80], "Time": datetime.now().strftime("%H:%M")})
    if col_en.button("Translate ➜ English"):
        en = gpt_translate(content, "zh-tw", "en")
        st.text_area("English", en, height=200)
        memory.append({"Document": doc, "Snippet": en[:80], "Time": datetime.now().strftime("%H:%M")})

translation_memory_panel()
