import streamlit as st
from agent import advisor_agent

st.set_page_config(
    page_title="Student Learning Advisor",
    layout="wide"
)

st.title("Agentic RAG Learning Advisor")

question = st.text_area("Ask your question")

if st.button("Generate Plan"):

    if question.strip():

        with st.spinner("Thinking..."):

            result = advisor_agent(question)

        st.markdown(result)

    else:
        st.warning("Enter a question.")