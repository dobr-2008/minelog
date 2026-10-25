from __future__ import annotations

import hashlib
import os 
import streamlit as st 
from dotenv import load_dotenv

from main import analyze_log , format_report
from ai_explainer import AiexplanationError, explain_with_local_ai

load_dotenv()

st.set_page_config(page_title="MineLog" , page_icon="🔎", layout="wide")

st.title("🔎MineLog")
st.caption("Minecraft crash and server log investigator")
st.write(
    "upload a minecraft log to find common failure patterns"
    "Ai explanations use the local model endpoint you configure"
)

with st.sidebar:
    st.header("Local Ai Settings")
    base_url = st.text_input(
        "LM studio base URL",
        
    )