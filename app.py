import streamlit as st
from agent import ask_agent

st.title("🚗 AI Car Assistant")
st.write("Ask me about car problems, or calculate fuel cost, loan payments, and ownership costs.")

if 'messages'not in st.session_state:
    st.session_state.messages=[]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


query = st.chat_input("Ask about cars...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = ask_agent(query)
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})