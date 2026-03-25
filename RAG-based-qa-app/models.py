from transformers import pipeline
from sentence_transformers import SentenceTransformer

qa_pipeline = pipeline(
    "question-answering",
    model="deepset/deberta-v3-base-squad2",
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
