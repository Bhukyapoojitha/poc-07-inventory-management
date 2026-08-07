import streamlit as st

from rag_chain import ask_question

st.set_page_config(
    page_title="POC-07 Inventory RAG",
    page_icon="📦"
)

st.title("POC-07 Inventory Assistant")

question = st.text_input(
    "Ask a question about inventory management"
)

if question:
    result = ask_question(question)
    st.write(result["answer"])