import streamlit as st
from agent import ask_agent

st.title("🚗 AI Car Assistant")
st.write("Ask me about car problems, or calculate fuel cost, loan payments, and ownership costs.")

query = st.text_input("Your question:")

if st.button('Ask'):
    if query:
        with st.spinner("Thinking..."):
            answer=ask_agent(query)
        st.write("### Answer:")
        st.write(answer)
