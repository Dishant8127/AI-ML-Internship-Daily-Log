import os
import faiss
import numpy as np


EMBEDDINGS_PATH = "data/embeddings.npy"

FLAT_INDEX_PATH = "indexes/flat.index"
IVF_INDEX_PATH = "indexes/ivf.index"
HNSW_INDEX_PATH = "indexes/hnsw.index"
PQ_INDEX_PATH = "indexes/pq.index"



embeddings = np.load(EMBEDDINGS_PATH)

dimension = embeddings.shape[1]


flat_index = faiss.IndexFlatL2(dimension)

flat_index.add(embeddings)

faiss.write_index(flat_index,FLAT_INDEX_PATH)


# IVF Index


nlist = 10

quantizer = faiss.IndexFlatL2(dimension)

ivf_index = faiss.IndexIVFFlat(quantizer,dimension,nlist,faiss.METRIC_L2)

ivf_index.train(embeddings)

ivf_index.add(embeddings)

faiss.write_index(ivf_index,IVF_INDEX_PATH)


# HNSW Index


hnsw_index = faiss.IndexHNSWFlat(dimension,32)

hnsw_index.add(embeddings)

faiss.write_index(hnsw_index, HNSW_INDEX_PATH)



#PQ Index


m = 8

nbits = 4

pq_index = faiss.IndexPQ(dimension,m,nbits)

pq_index.train(embeddings)

pq_index.add(embeddings)

faiss.write_index(pq_index,PQ_INDEX_PATH)

