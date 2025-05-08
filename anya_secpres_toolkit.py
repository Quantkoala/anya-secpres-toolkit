
# File: anya_secpres_toolkit.py
"""
ANYA Biopharm Inc. – Secretary‑to‑the‑President Toolkit (Public Corp Standard)
• 70% Translation: EN ↔ 繁體中文 (Taiwan)
• 30% Board Ops: Document Management & Progress Tracking
"""
import os
import time
import streamlit as st
import pandas as pd
from datetime import datetime

# --- OpenAI Configuration (Optional) ---
OPENAI_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
try:
    import openai
    from openai import RateLimitError
    openai.api_key = OPENAI_KEY
except ImportError:
    openai = None
    RateLimitError = Exception

@st.cache_data(show_spinner=False)
def translate(text: str, src: str, tgt: str) -> str:
    """API translation with retry/backoff."""
    if not openai or not OPENAI_KEY:
        return "[Translation service unavailable]\n" + text
    messages = [
        {"role": "system", "content": f"Translate from {src} to {tgt}. Preserve formatting."},
        {"role": "user", "content": text}
    ]
    delay = 1
    for attempt in range(4):
        try:
            resp = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.1,
                messages=messages
            )
            return resp.choices[0].message.content.strip()
        except RateLimitError:
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            return f"[Error: {e}]"
    return "[Rate limit exceeded]"

# --- Document Library (Standard Public Co Docs) ---
DOCS = {
    "Corporate Governance": {
        "Board Charter": {"en": "Board Charter content...", "zh": "董事會章程內容..."},
        "Audit Committee Charter": {"en": "Audit Charter...", "zh": "審計委員會章程..."},
        "Proxy Statement Excerpt": {"en": "Proxy Statement excerpt...", "zh": "委託書說明書摘錄..."}
    },
    "SEC Filings": {
        "Form 10-K Excerpt": {"en": "Form 10-K excerpt...", "zh": "10-K 摘錄..."},
        "Form 10-Q Excerpt": {"en": "Form 10-Q excerpt...", "zh": "10-Q 摘錄..."},
        "Form 8-K Press Release": {"en": "Form 8-K release...", "zh": "8-K 新聞稿..."}
    },
    "Investor Relations": {
        "Earnings Release Q2 2024": {"en": "Q2 2024 earnings...", "zh": "2024年第二季財報..."},
        "Investor Presentation": {"en": "Investor deck...", "zh": "投資者簡報..."}
    }
}

# --- Streamlit Setup ---
st.set_page_config(page_title="ANYA SecPres Toolkit", layout="wide")
st.sidebar.title("📂 Board Document Library")

# Initialize session state
if 'progress' not in st.session_state:
    keys = [f"{c}/{d}" for c in DOCS for d in DOCS[c]]
    st.session_state.progress = {k: 0 for k in keys}
if 'memory' not in st.session_state:
    st.session_state.memory = []
if 'glossary' not in st.session_state:
    st.session_state.glossary = {}

# Sidebar navigation
option = st.sidebar.selectbox(
    "Navigate", 
    ["Home"] + list(st.session_state.progress.keys()) + ["Upload & Translate", "Glossary", "Memory", "Dashboard"]
)

st.title("ANYA Biopharm Inc. SecPres Toolkit")

# --- Home: Progress Tracker & Quick Translate ---
if option == "Home":
    st.header("Document Progress Tracker")
    for key, val in st.session_state.progress.items():
        cat, doc = key.split("/")
        st.subheader(f"{cat} – {doc}")
        col1, col2 = st.columns([4,1])
        with col1:
            st.progress(val/100)
        with col2:
            new = st.number_input("%", 0, 100, val, key=key)
            st.session_state.progress[key] = new
    st.markdown("---")
    st.header("Quick Translation Sample")
    inp = st.text_area("Enter text", height=100)
    direction = st.radio("Direction", ["en→zh", "zh→en"])
    if st.button("Translate Sample"):
        src, tgt = direction.split("→")
        out = translate(inp, src, tgt)
        st.text_area("Translation", out, height=100)
        st.session_state.memory.append({"source": inp[:50], "translation": out[:50], "time": datetime.now().strftime('%H:%M')})

# --- Document Library ---
elif option in st.session_state.progress:
    cat, doc = option.split("/")
    st.header(f"{doc} ({cat})")
    pair = DOCS[cat][doc]
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("English")
        txt_en = st.text_area("", pair['en'], height=200)
    with col2:
        st.subheader("繁體中文")
        txt_zh = st.text_area("", pair['zh'], height=200)
    if st.button("Translate → 繁體中文"):
        res = translate(txt_en, "en", "zh")
        st.text_area("Translation", res, height=200)
        st.session_state.memory.append({"doc": doc, "translation": res[:50], "time": datetime.now().strftime('%H:%M')})
    if st.button("Translate → English"):
        res = translate(txt_zh, "zh", "en")
        st.text_area("Translation", res, height=200)
        st.session_state.memory.append({"doc": doc, "translation": res[:50], "time": datetime.now().strftime('%H:%M')})

# --- Upload & Translate ---
elif option == "Upload & Translate":
    st.header("Upload & Translate (.txt / .docx)")
    src = st.selectbox("Source", ["en", "zh"])
    tgt = "zh" if src == "en" else "en"
    uploaded = st.file_uploader("Upload file", type=["txt","docx"])
    if uploaded and st.button("Translate File"):
        if uploaded.type == "text/plain":
            content = uploaded.read().decode('utf-8')
        else:
            import docx
            docobj = docx.Document(uploaded)
            content = "\n".join(p.text for p in docobj.paragraphs)
        res = translate(content, src, tgt)
        st.text_area("Translation", res, height=300)
        st.session_state.memory.append({"doc": uploaded.name, "translation": res[:50], "time": datetime.now().strftime('%H:%M')})

# --- Glossary ---
elif option == "Glossary":
    st.header("Glossary Manager")
    term = st.text_input("Term")
    definition = st.text_area("Definition")
    if st.button("Save Term") and term:
        st.session_state.glossary[term] = definition
    st.table(pd.DataFrame(list(st.session_state.glossary.items()), columns=["Term","Definition"]))

# --- Memory ---
elif option == "Memory":
    st.header("Translation Memory")
    if st.session_state.memory:
        st.table(pd.DataFrame(st.session_state.memory))
    else:
        st.write("No translations yet.")

# --- Dashboard ---
elif option == "Dashboard":
    st.header("Board Ops Dashboard")
    c1,c2,c3 = st.columns(3)
    c1.metric("Meetings/Year", 4)
    c2.metric("Avg Prep Hours", 5)
    c3.metric("Compliance", "100%")
