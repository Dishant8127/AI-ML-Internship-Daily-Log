import time
import faiss
import numpy as np
import pandas as pd


TOP_K = 5

EMBEDDINGS_PATH = "data/embeddings.npy"

FLAT_INDEX_PATH = "indexes/flat.index"
IVF_INDEX_PATH = "indexes/ivf.index"
HNSW_INDEX_PATH = "indexes/hnsw.index"
PQ_INDEX_PATH = "indexes/pq.index"


embeddings = np.load(EMBEDDINGS_PATH)

query_vectors = embeddings[:100]


indexes = {
    "Flat": faiss.read_index(FLAT_INDEX_PATH),
    "IVF": faiss.read_index(IVF_INDEX_PATH),
    "HNSW": faiss.read_index(HNSW_INDEX_PATH),
    "PQ": faiss.read_index(PQ_INDEX_PATH),
}

indexes["IVF"].nprobe = 10

baseline_index = indexes["Flat"]

baseline_results = []

for q in query_vectors:
    D, I = baseline_index.search(np.expand_dims(q, axis=0),TOP_K)

    baseline_results.append(I[0])


results = []

for name, index in indexes.items():

    start = time.time()

    all_results = []

    for q in query_vectors:
        D, I = index.search(np.expand_dims(q, axis=0),TOP_K)

        all_results.append(I[0])

    end = time.time()

    avg_time_ms = ((end - start) / len(query_vectors)) * 1000

    overlaps = []

    for base, current in zip(baseline_results, all_results):

        overlap = len(set(base).intersection(set(current))) / TOP_K

        overlaps.append(overlap)

    accuracy = np.mean(overlaps) * 100


    memory_mb = faiss.serialize_index(index).nbytes / (1024 * 1024)

    results.append({
        "Index": name,
        "Search Time (ms)": round(avg_time_ms, 4),
        "Memory Usage (MB)": round(memory_mb, 2),
        "Accuracy (%)": round(accuracy, 2)
    })


df = pd.DataFrame(results)

df.to_csv("results/benchmark_results.csv", index=False)



with open("results/report.txt", "w") as f:

    f.write("FAISS INDEX COMPARISON REPORT\n\n")

    for _, row in df.iterrows():

        f.write(f"""
Index Type: {row['Index']}
Search Time: {row['Search Time (ms)']} ms
Memory Usage: {row['Memory Usage (MB)']} MB
Accuracy: {row['Accuracy (%)']} %

""")
