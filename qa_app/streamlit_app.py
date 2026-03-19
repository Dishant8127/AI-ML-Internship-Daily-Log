import streamlit as st
import requests

st.title(" Q&A from Documents")

uploaded_file = st.file_uploader("Upload File", type=["txt", "pdf"])
question = st.text_input("Ask a question")

if st.button("Get Answer"):
    if uploaded_file and question:
        files = {"file": uploaded_file}
        data = {"question": question}

        response = requests.post(
            "http://127.0.0.1:5000/ask_file",
            files=files,
            data=data
        )

        result = response.json()

        st.success(f"Answer: {result['answer']}")
        st.write(f"Confidence: {result['confidence']}")
        st.write(f"Start: {result['start']} | End: {result['end']}")