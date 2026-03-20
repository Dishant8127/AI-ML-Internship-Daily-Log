import streamlit as st
import requests

# Flask API URL
BASE_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="RAG QA System", layout="wide")

st.title("📄 Document QA System (Mini RAG)")

# -------------------------
# Upload Section
# -------------------------
st.header("📤 Upload Documents")

uploaded_files = st.file_uploader(
    "Upload PDF or TXT files",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if st.button("Upload"):
    if uploaded_files:
        files = []

        for file in uploaded_files:
            files.append(("files", (file.name, file.getvalue())))

        response = requests.post(
            f"{BASE_URL}/upload_docs",
            files=files
        )

        if response.status_code == 200:
            st.success("Documents uploaded successfully ✅")
        else:
            st.error("Upload failed ❌")
    else:
        st.warning("Please upload at least one file")

# -------------------------
# Ask Question Section
# -------------------------
st.header("❓ Ask Question")

question = st.text_input("Enter your question")

if st.button("Get Answer"):
    if question:
        response = requests.post(
            f"{BASE_URL}/ask_docs",
            json={"question": question}
        )

        if response.status_code == 200:
            data = response.json()

            answers = data.get("answers", [])

            if answers:
                for i, ans in enumerate(answers):
                    st.subheader(f"Answer {i+1}")

                    st.write(f"**Answer:** {ans['answer']}")
                    st.write(f"**Confidence:** {ans['confidence']}")
                    st.write(f"**Source:** {ans['source_doc']}")

                    # Optional: status
                    if "status" in ans:
                        st.write(f"**Status:** {ans['status']}")

                    st.divider()
            else:
                st.warning(data.get("message", "No answer found"))
        else:
            st.error("Error fetching answer ❌")
    else:
        st.warning("Please enter a question")
