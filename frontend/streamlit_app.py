import streamlit as st
import requests

BACKEND_URL = "https://controlled-rag-agent.onrender.com"

st.set_page_config(page_title="Controlled RAG Agent", layout="centered")

st.title("Controlled RAG Agent")
st.caption("LangGraph-based planning + controlled tool execution")

prompt = st.text_area(
    "Ask a question",
    placeholder="What is this document about?",
    height=120
)

if st.button("Run Agent"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/agent/run",
                    json={"prompt": prompt},
                    timeout=60
                )
                data = response.json()
                st.markdown("### Response")
                st.write(data.get("result", data))
            except Exception as e:
                st.error(str(e))
