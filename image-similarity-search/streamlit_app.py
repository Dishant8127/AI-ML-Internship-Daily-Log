import streamlit as st
import requests

from PIL import Image

# Flask API URL
API_URL = "http://127.0.0.1:5000/search"

# Page Config
st.set_page_config(
    page_title="Image Similarity Search",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>

.main {
    padding-top: 20px;
}

.block-container {
    padding-top: 2rem;
}

.match-card {
    background-color: #111827;
    padding: 10px;
    border-radius: 15px;
    border: 1px solid #374151;
    text-align: center;
}

.small-text {
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# Title
st.title("🔍 Image Similarity Search")

st.write(
    "Upload an image and find visually similar images using OpenCLIP embeddings."
)

# Upload image
uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:

    # Open uploaded image
    image = Image.open(uploaded_file)

    # Center uploaded image
    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:

        st.image(
            image,
            caption="Uploaded Image",
            width=250
        )

    st.divider()

    # Search button
    if st.button("🔍 Find Similar Images"):

        with st.spinner("Searching for similar images..."):

            try:

                # Send image to Flask API
                response = requests.post(
                    API_URL,
                    files={
                        "image": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    }
                )

                # Success
                if response.status_code == 200:

                    results = response.json()

                    matches = results.get("matches", [])

                    st.success("Search Completed!")

                    if len(matches) == 0:

                        st.warning("No similar images found.")

                    else:

                        st.subheader("🎯 Top Matches")

                        # Create 3 columns
                        cols = st.columns(3)

                        for index, match in enumerate(matches[:3]):

                            with cols[index]:

                                # Open matched image
                                matched_image = Image.open(
                                    match['image_path']
                                )

                                # Show smaller image
                                st.image(
                                    matched_image,
                                    caption=f"Match #{index + 1}",
                                    width=220
                                )

                                # Similarity %
                                similarity_percent = round(
                                    match['similarity'] * 100,
                                    2
                                )

                                # Info
                                st.markdown(
                                    f"""
                                    <div class="match-card">

                                    📂 <b>{match['category']}</b><br><br>

                                    📊 <b>{similarity_percent}% Similar</b>

                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                                # Progress bar
                                st.progress(match['similarity'])

                else:
                    st.error(f"API Error: {response.text}")

            except Exception as e:
                st.error(f"Error: {e}")