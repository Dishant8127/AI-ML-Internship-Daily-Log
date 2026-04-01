import streamlit as st
import requests

st.title("Article / Blog Generator")

topic = st.text_input("Enter a topic:")

if st.button("Generate"):
    if not topic.strip():
        st.error("Please enter a topic.")
    else:
        with st.spinner("Generating..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/generate_article",
                    json={"topic": topic}
                )
                if response.status_code == 200:
                    article = response.json().get("article", "")
                    st.subheader("Generated Article / Blog")
                    st.write(article)
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")