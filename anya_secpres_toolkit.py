# anya_secpres_toolkit.py – rate‑limit safe and syntax‑clean
import os, time, streamlit as st, pandas as pd
from datetime import datetime

# --- OpenAI optional ------------------------------------------------------
OPENAI_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
try:
    import openai
    from openai import RateLimitError
    openai.api_key = OPENAI_KEY
except ModuleNotFoundError:
    openai, RateLimitError = None, Exception

def translate(text: str, src: str, tgt: str) -> str:
    """Translate with exponential back‑off to handle rate limits."""
    if not openai or not OPENAI_KEY:
        return "[OPENAI not configured]"
    sys_msg = (f"You are a professional translator. Translate from {src} to {tgt}. "
               "Return only translated text; keep formatting.")
    msgs = [{"role": "system", "content": sys_msg}, {"role": "user", "content": text}]

    delay = 2
    for attempt in range(4):
        try:
            resp = openai.chat.completions.create(model="gpt-3.5-turbo", temperature=0.2, messages=msgs)
            return resp.choices[0].message.content.strip()
        except RateLimitError:
            if attempt == 3:
                return "[Rate‑limit reached — try later]"
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            return f"[Translation error: {e}]"

# --- Sample board docs ----------------------------------------------------
DOCS = {
    "Governance": {
        "Board Agenda": "Date: ____\n1. Call to Order\n2. Approve Minutes\n3. Q2 Results…",
        "Board Minutes": "Attendees: ____\nResolutions: 1)…"
    },
    "Disclosure": {
        "IR Press Release": "ANYA Biopharm reports NT$413M revenue…"
    }
}

# --- Streamlit layout -----------------------------------------------------
st.set_page_config(page_title="ANYA SecPres Toolkit", layout="wide")

st.sidebar.header("📂 Board DMS")
options = ["Home"] + [f"{cat} / {doc}" for cat in DOCS for doc in DOCS[cat]]
page = st.sidebar.selectbox("Navigate", options)

st.title("ANYA Secretary‑to‑President Toolkit")

memory = st.session_state.setdefault("memory", [])

# --- Home page ------------------------------------------------------------
if page == "Home":
    cat = st.selectbox("Category", list(DOCS))
    doc = st.selectbox("Document", list(DOCS[cat]))
    src_text = DOCS[cat][doc]
    st.text_area("Original", src_text, height=160)
    if st.button("Translate ➜ 繁體中文"):
        trg_text = translate(src_text, "en", "zh-tw")
        st.text_area("Translation", trg_text, height=160)
        memory.append({"doc": doc, "snippet": trg_text[:60], "time": datetime.now().strftime('%H:%M')})

# --- Specific document page ----------------------------------------------
else:
    cat, doc = page.split(" / ")
    content = st.text_area("Original", DOCS[cat][doc], height=160)
    col_zh, col_en = st.columns(2)
    if col_zh.button("Translate ➜ 繁體中文"):
        zh = translate(content, "en", "zh-tw")
        st.text_area("ZH", zh, height=160)
        memory.append({"doc": doc, "snippet": zh[:60], "time": datetime.now().strftime('%H:%M')})
    if col_en.button("Translate ➜ English"):
        en = translate(content, "zh-tw", "en")
        st.text_area("EN", en, height=160)
        memory.append({"doc": doc, "snippet": en[:60], "time": datetime.now().strftime('%H:%M')})

# --- Translation memory ---------------------------------------------------
with st.expander("🗂 Translation Memory – session"):
    if memory:
        st.table(pd.DataFrame(memory))
    else:
        st.write("No translations yet.")
