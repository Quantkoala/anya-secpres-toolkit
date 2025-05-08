# anya_secpres_toolkit.py  – handles OpenAI rate limits gracefully
import os, time, streamlit as st, pandas as pd
from datetime import datetime
from typing import Callable

# Optional OpenAI
OPENAI_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
try:
    import openai
    from openai import RateLimitError
    openai.api_key = OPENAI_KEY
except ModuleNotFoundError:
    openai, RateLimitError = None, Exception

# ---- robust translator --------------------------------------------------
def _call_chat(messages):
    return openai.chat.completions.create(model="gpt-3.5-turbo", temperature=0.2, messages=messages)

def translate(text: str, src: str, tgt: str) -> str:
    """Translate with retry (exponential back‑off)."""
    if not openai or not OPENAI_KEY:
        return "[Missing OPENAI_API_KEY or openai package]\n\n" + text
    sys_msg = (f"You are a professional translator. Translate from {src} to {tgt}. "
               "Return only translated text, preserve numbering/formatting.")
    messages = [{"role":"system","content":sys_msg}, {"role":"user","content":text}]
    delay = 2
    for attempt in range(4):     # up to 4 tries: 2s,4s,8s,16s
        try:
            resp = _call_chat(messages)
            return resp.choices[0].message.content.strip()
        except RateLimitError:
            if attempt == 3:
                return "[Rate‑limit reached, please try again later]"
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            return f"[Translation error: {e}]"

# ---- Sample board docs ---------------------------------------------------
DOCS = {
    "Governance": {"Board Agenda": "Date: ____\n1. Call to order\n2. Approve minutes"},
    "Disclosure": {"IR Press Release": "ANYA reports NT$413M revenue…"}
}

st.set_page_config(page_title="ANYA SecPres Toolkit", layout="wide")
page = st.sidebar.selectbox("Navigate", ["Home"] + [f"{c} / {d}" for c in DOCS for d in DOCS[c]])

memory = st.session_state.setdefault("memory", [])

if page == "Home":
    cat = st.selectbox("Category", list(DOCS))
    doc = st.selectbox("Document", list(DOCS[cat]))
    txt = DOCS[cat][doc]
    st.text_area("Original", txt, height=160)
    if st.button("Translate ➜ 繁體中文"):
        out = translate(txt, "en", "zh-tw")
        st.text_area("Translation", out, height=160)
        memory.append({"doc": doc, "snippet": out[:60], "time": datetime.now().strftime('%H:%M')})
else:
    c, d = page.split(" / ")
    txt = st.text_area("Original", DOCS[c][d], height=160)
    if st.button("Translate ➜ 繁體中文"):
        out = translate(txt, "en", "zh-tw")
        st.text_area("ZH", out, height=160)
    if st.button("Translate ➜ English"):
        out = translate(txt, "zh-tw", "en")
        st.text_area("EN", out, height=160)

with st.expander("Memory"):
    if memory: st.table(pd.DataFrame(memory)) else: st.write("No translations yet.")
