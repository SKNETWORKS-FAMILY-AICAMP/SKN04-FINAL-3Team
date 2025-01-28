from langchain.schema import Document, BaseRetriever
from konlpy.tag import Okt
from rank_bm25 import BM25Okapi
from pydantic import PrivateAttr
from langchain_openai import OpenAIEmbeddings
from typing import List
import faiss
import numpy as np


class HybridBM25FaissRetriever(BaseRetriever):
    # Pydantic이 인식하지 않는 속성은 PrivateAttr로 선언 (언더스코어 사용)
    _bm25: BM25Okapi = PrivateAttr()
    _faiss_index: faiss.Index = PrivateAttr()
    _documents: List[dict] = PrivateAttr()
    _metadata_list: List[dict] = PrivateAttr()
    _embeddings: OpenAIEmbeddings = PrivateAttr()
    _okt: Okt = PrivateAttr()

    # 초기화 메서드에서 PrivateAttr에 값 할당
    def __init__(
        self, 
        bm25: BM25Okapi, 
        faiss_index: faiss.Index, 
        documents: List[dict], 
        metadata_list: List[dict], 
        top_k: int = 5
    ):
        super().__init__()
        self._bm25 = bm25
        self._faiss_index = faiss_index
        self._documents = documents
        self._metadata_list = metadata_list
        self._top_k = top_k
        self._embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
        )
        self._okt = Okt()

    def get_openai_embedding(self, text: str) -> np.ndarray:
        """
        LangChain의 OpenAIEmbeddings를 사용하여 텍스트의 임베딩을 얻습니다.
        """
        vector = self._embeddings.embed_query(text)  # List[float]
        return np.array(vector, dtype=np.float32)

    def tokenize_korean(self, text: str) -> List[str]:
        """
        Okt를 사용하여 한국어 텍스트를 토큰화합니다.
        """
        return self._okt.morphs(text)

    def _bm25_search(self, query: str) -> List[int]:
        """
        BM25를 사용하여 상위 top_k 문서 인덱스를 반환합니다.
        """
        tokenized_query = self.tokenize_korean(query)
        scores = self._bm25.get_scores(tokenized_query)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        top_docs = [r[0] for r in ranked[:self._top_k]]
        return top_docs

    def _faiss_search(self, query_emb: np.ndarray) -> List[int]:
        """
        Faiss를 사용하여 상위 top_k 문서 인덱스를 반환합니다.
        """
        distances, indices = self._faiss_index.search(query_emb, self._top_k)
        return list(indices[0])

    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        BM25와 Faiss를 사용하여 관련 문서를 검색하고, LangChain의 Document 객체로 반환합니다.
        """
        # BM25 검색
        bm25_indices = self._bm25_search(query)

        # Faiss 검색
        query_emb = self.get_openai_embedding(query).reshape(1, -1)
        faiss_indices = self._faiss_search(query_emb)

        # 결과 통합 (합집합)
        combined_indices = list(set(bm25_indices + faiss_indices))

        # Document 객체 생성
        docs = []
        for idx in combined_indices:
            content = self._documents[idx]["page_content"]
            meta = self._documents[idx]["metadata"]
            doc = Document(page_content=content, metadata=meta)
            docs.append(doc)

        return docs

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """
        비동기 방식으로 관련 문서를 검색합니다.
        """
        return self.get_relevant_documents(query)