import streamlit as st
import requests

from PIL import Image



API_URL = "http://127.0.0.1:5000/search"


st.set_page_config(
    page_title="Visual Similarity Search",
    layout="wide"
)


st.title("🔍 Visual Similarity Search")


uploaded_file = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png"]
)


if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        width=300
    )

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

    if response.status_code == 200:

        results = response.json()

        st.subheader(
            "Top Similar Results"
        )

        cols = st.columns(5)

        for idx, result in enumerate(results):

            with cols[idx]:

                image_path = (
                    f"images/{result['filename']}"
                )

                st.image(
                    image_path,
                    use_container_width=True
                )

                st.write(
                    f"Similarity: "
                    f"{result['similarity']:.4f}"
                )

                metadata = result["metadata"]

                st.write(
                    metadata.get(
                        "articleType"
                    )
                )

                st.write(
                    metadata.get(
                        "baseColour"
                    )
                )

    else:

        st.error("API Error")