from transformers import pipeline
from sentence_transformers import SentenceTransformer

qa_pipeline = pipeline(
    "question-answering",
    model="deepset/deberta-v3-large-squad2"
)

embedding_model = SentenceTransformer("all-mpnet-base-v2")
