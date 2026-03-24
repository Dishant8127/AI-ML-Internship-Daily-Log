import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="QA Chat", layout="wide")

# -------------------------
# State
# -------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "history" not in st.session_state:
    st.session_state.history = []

st.sidebar.header("🧠 Session Manager")

try:
    res = requests.get(f"{BASE_URL}/get_sessions")
    session_list = res.json().get("sessions", [])
except:
    st.sidebar.error("Backend not running")
    session_list = []

selected_session = st.sidebar.selectbox(
    "Select Session",
    [""] + session_list
)

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("📂 Load"):
        if selected_session:
            st.session_state.session_id = selected_session

            res = requests.post(
                f"{BASE_URL}/get_history",
                json={"session_id": selected_session}
            )

            if res.status_code == 200:
                st.session_state.history = res.json().get("history", [])
                st.success("Session loaded")
            else:
                st.error("Failed to load session")

with col2:
    if st.button("❌ Delete"):
        if selected_session:
            res = requests.post(
                f"{BASE_URL}/delete_session",
                json={"session_id": selected_session}
            )

            if res.status_code == 200:
                st.success("Session deleted")

                if st.session_state.session_id == selected_session:
                    st.session_state.session_id = None
                    st.session_state.history = []

                st.rerun()
            else:
                st.error("Failed to delete")

if st.sidebar.button("➕ New Session"):
    res = requests.get(f"{BASE_URL}/start_session")
    if res.status_code == 200:
        st.session_state.session_id = res.json()["session_id"]
        st.session_state.history = []
        st.sidebar.success("New session created")
    else:
        st.sidebar.error("Failed to create session")

st.sidebar.write("Current Session:")
st.sidebar.code(st.session_state.session_id)

if st.sidebar.button("🗑 Clear Chat"):
    if st.session_state.session_id:
        requests.post(
            f"{BASE_URL}/clear_session",
            json={"session_id": st.session_state.session_id}
        )
        st.session_state.history = []
        st.sidebar.success("Chat cleared")

uploaded_files = st.sidebar.file_uploader(
    "📂 Upload Documents (.txt / .pdf)",
    accept_multiple_files=True
)

if uploaded_files:
    files = [("files", (file.name, file, file.type)) for file in uploaded_files]
    res = requests.post(f"{BASE_URL}/upload_docs", files=files)

    if res.status_code == 200:
        st.sidebar.success("Files uploaded")
    else:
        st.sidebar.error("Upload failed")

st.title("💬 Document Q&A Chat")

if not st.session_state.session_id:
    st.warning("⚠️ Please create or load a session")
    st.stop()

for chat in st.session_state.history:
    with st.chat_message("user"):
        st.write(chat["q"])

    with st.chat_message("assistant"):
        st.write(chat["a"])
        
question = st.chat_input("Ask your question...")

if question:
    with st.chat_message("user"):
        st.write(question)

    res = requests.post(
        f"{BASE_URL}/ask_session",
        json={
            "session_id": st.session_state.session_id,
            "question": question
        }
    )

    if res.status_code != 200:
        st.error(res.json())
    else:
        data = res.json()

        answer = data.get("answer", "No answer")
        source = data.get("source", "")
        confidence = data.get("confidence", 0)

        with st.chat_message("assistant"):
            st.write(answer)

            if source:
                st.caption(f"📄 Source: {source}")

            st.caption(f"🔢 Confidence: {confidence:.2f}")

        st.session_state.history = data.get("history", [])