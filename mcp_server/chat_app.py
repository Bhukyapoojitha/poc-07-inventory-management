import streamlit as st

from mcp_server.chat_interface import process_message

st.set_page_config(
    page_title="POC-07 MCP Chat",
    page_icon="📦"
)

st.title(" Inventory Management MCP Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input(
    "Ask an inventory question..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    result = process_message(
        prompt,
        session_id="streamlit-session"
    )

    answer = result.get(
        "output",
        "No response"
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.write(answer)