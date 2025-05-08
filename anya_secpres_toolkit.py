# File: anya_secpres_toolkit.py
import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Anya SecPres Toolkit",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar Navigation ---
st.sidebar.title("Anya SecPres Toolkit")
page = st.sidebar.radio(
    "Menu", [
        "Home", "Translation Toolkit", "Batch Translation", "Translation Memory", "Meeting Management",
        "Compliance Checklist", "Document Repository", "Actual Financials", "Balance Sheet & Ratios",
        "Financial Modeling", "R&D Translation", "IR Presentation Demo", "Regulatory Filing Sample",
        "Board Ops Dashboard", "Glossary & Workflow", "Download CV"
    ]
)

# --- Styles & Branding ---
st.markdown("<style>\n.section-title { font-size:24px; font-weight:bold; margin-top:20px; color:#006699;}\n.kpi {background-color:#eef5f9; padding:12px; border-radius:10px;}\ntextarea {width:100%; height:160px;}\n</style>", unsafe_allow_html=True)

# Initialize translation memory
if 'trans_memory' not in st.session_state:
    st.session_state.trans_memory = []

# --- Home ---
if page == "Home":
    st.markdown('<div class="section-title">Welcome to the Anya SecPres Toolkit</div>', unsafe_allow_html=True)
    st.write("This specialized app demonstrates my capabilities as Secretary to the President at ANYA Biopharm Inc., focusing on 70% translation and 30% board operations management.")

# --- Translation Toolkit ---
elif page == "Translation Toolkit":
    st.markdown('<div class="section-title">Translation Toolkit</div>', unsafe_allow_html=True)
    st.write("Perform domain-specific Chinese↔English translation with glossary support and iterative refinement.")
    src = st.text_area("Enter text (ZH/EN)")
    if st.button("Draft Translate → EN"):
        out = src.replace("公司","The Company").replace("平台","platform") + " [MT]"
        st.write(out)
        st.session_state.trans_memory.append((src,out,datetime.now().strftime("%Y-%m-%d %H:%M")))
    term = st.text_input("Glossary lookup")
    glossary={"GMP":"Good Manufacturing Practice","MIRA":"Metal Ion & Reducing Agent","滲透劑":"permeation enhancer"}
    if term: st.write(f"**{term}**: {glossary.get(term,'N/A')}")
    refined = st.text_area("Refine translation")
    if st.button("Submit Final"): st.success("Submitted for review.")

# --- Batch Translation ---
elif page == "Batch Translation":
    st.markdown('<div class="section-title">Batch Translation</div>', unsafe_allow_html=True)
    files=st.file_uploader("Upload DOCX/CSV",accept_multiple_files=True,type=["docx","csv"])
    if files:
        res=[]
        for f in files:
            txt=f.read().decode('utf-8',errors='ignore')[:150]
            tr=txt.replace("公司","The Company")
            res.append({"file":f.name,"translation":tr})
            st.session_state.trans_memory.append((txt,tr,datetime.now().strftime("%Y-%m-%d %H:%M")))
        st.table(pd.DataFrame(res))

# --- Translation Memory ---
elif page == "Translation Memory":
    st.markdown('<div class="section-title">Translation Memory</div>', unsafe_allow_html=True)
    df=pd.DataFrame(st.session_state.trans_memory,columns=["Source","Translation","Time"])
    st.dataframe(df if not df.empty else "No entries.")

# --- Meeting Management ---
elif page == "Meeting Management":
    st.markdown('<div class="section-title">Meeting Manager</div>', unsafe_allow_html=True)
    date=st.date_input("Date")
    items=st.text_area("Agenda items (one per line)")
    if st.button("Generate"):
        st.write(f"**Agenda {date}:**")
        for i,it in enumerate(items.splitlines(),1): st.write(f"{i}. {it}")
        st.write("**Minutes Template**: Attendees, Decisions, Actions.")

# --- Compliance Checklist ---
elif page == "Compliance Checklist":
    st.markdown('<div class="section-title">Compliance</div>', unsafe_allow_html=True)
    for c in ["Quorum","Docs filed","Bylaws followed"]: st.checkbox(c)

# --- Document Repository ---
elif page == "Document Repository":
    st.markdown('<div class="section-title">Docs</div>', unsafe_allow_html=True)
    for d in ["Minutes.pdf","Resolutions.docx"]: st.write(d)

# --- Actual Financials ---
elif page == "Actual Financials":
    st.markdown('<div class="section-title">Income Statement</div>', unsafe_allow_html=True)
    df=pd.DataFrame({"Metric":["Rev","OpInc","NetInc"],"2023":[413,-43,-45]})
    st.table(df)

# --- Balance Sheet & Ratios ---
elif page == "Balance Sheet & Ratios":
    st.markdown('<div class="section-title">Balance & Ratios</div>', unsafe_allow_html=True)
    df2=pd.DataFrame({"M":["Assets","Liab","Equity"],"2023":[550,380,170]})
    st.table(df2)

# --- Financial Modeling ---
elif page == "Financial Modeling":
    st.markdown('<div class="section-title">Cash Runway</div>', unsafe_allow_html=True)
    cash=st.slider("Cash (M)",100,500,200)
    burn=st.number_input("Burn (M)",10,100,20)
    st.metric("Runway mo",f"{cash/burn:.1f}")

# --- R&D Translation ---
elif page == "R&D Translation":
    st.markdown('<div class="section-title">R&D Excerpt</div>', unsafe_allow_html=True)
    st.write("ZH: MIRA/JE...  EN: The platform integrates...")

# --- IR Presentation Demo ---
elif page == "IR Presentation Demo":
    st.markdown('<div class="section-title">IR Slide</div>', unsafe_allow_html=True)
    col1,col2=st.columns(2)
    col1.metric("Rev(2023)","413M")
    col2.metric("NetLoss","-45M")

# --- Regulatory Filing Sample ---
elif page == "Regulatory Filing Sample":
    st.markdown('<div class="section-title">TFDA CMC</div>', unsafe_allow_html=True)
    st.write("ZH: 製程...  EN: The process includes 14 QC steps.")

# --- Board Ops Dashboard ---
elif page == "Board Ops Dashboard":
    st.markdown('<div class="section-title">Board KPIs</div>', unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.metric("Meetings",4)
    b.metric("PrepHrs",6)
    c.metric("Compliant","100%")

# --- Glossary & Workflow ---
elif page == "Glossary & Workflow":
    st.markdown('<div class="section-title">Glossary</div>', unsafe_allow_html=True)
    for k,v in {"GMP":"GoodManufacture","IND":"InvestigationalDrug"}.items(): st.write(f"{k}: {v}")

# --- Download CV ---
elif page == "Download CV":
    st.markdown('<div class="section-title">Download</div>', unsafe_allow_html=True)
    with open("Capabilities_ANYA.docx","rb") as f: st.download_button("CV",f,file_name="SecPres_Capabilities.docx")
