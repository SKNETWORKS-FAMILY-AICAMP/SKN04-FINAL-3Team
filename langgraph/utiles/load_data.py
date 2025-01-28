import json
import faiss
import pickle
from typing import List
from rank_bm25 import BM25Okapi


def load_documents(filepath: str) -> List[dict]:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

def load_bm25(filepath: str) -> BM25Okapi:
    with open(filepath, "rb") as f:
        bm25 = pickle.load(f)
    return bm25

def load_faiss_index(filepath: str) -> faiss.Index:
    faiss_index = faiss.read_index(filepath)
    return faiss_index

def load_faiss_metadata(filepath: str) -> List[dict]:
    with open(filepath, "rb") as f:
        metadata_list = pickle.load(f)
    return metadata_list