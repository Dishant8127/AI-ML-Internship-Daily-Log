import os
import json
import pandas as pd

from tqdm import tqdm

from model import generate_embedding


IMAGE_FOLDER = "images"

EMBEDDING_FOLDER = "embeddings"

OUTPUT_JSON = os.path.join(
    EMBEDDING_FOLDER,
    "embeddings.json"
)



df = pd.read_csv(
    "styles.csv",
    on_bad_lines='skip'
)

metadata_dict = {}

for _, row in df.iterrows():

    filename = f"{row['id']}.jpg"

    metadata_dict[filename] = {

        "gender": str(row.get("gender")),

        "masterCategory": str(
            row.get("masterCategory")
        ),

        "subCategory": str(
            row.get("subCategory")
        ),

        "articleType": str(
            row.get("articleType")
        ),

        "baseColour": str(
            row.get("baseColour")
        ),

        "season": str(
            row.get("season")
        ),

        "usage": str(
            row.get("usage")
        ),

        "productDisplayName": str(
            row.get("productDisplayName")
        )
    }


if os.path.exists(OUTPUT_JSON):

    try:

        with open(OUTPUT_JSON, "r") as f:

            database = json.load(f)

    except:

        database = []

else:

    database = []


done_files = {
    item["filename"]
    for item in database
}


image_files = os.listdir(
    IMAGE_FOLDER
)

for filename in tqdm(image_files):

    if filename in done_files:

        continue

    path = os.path.join(
        IMAGE_FOLDER,
        filename
    )

    try:

        embedding = generate_embedding(path).tolist()

        item = {

            "filename": filename,

            "embedding": embedding,

            "metadata": metadata_dict.get(
                filename,
                {}
            )
        }

        database.append(item)

        with open(OUTPUT_JSON, "w") as f:

            json.dump(
                database,
                f,
                indent=4
            )

    except Exception as e:

        print(f"Error: {filename}")
        print(e)

print("Embedding Complete.")