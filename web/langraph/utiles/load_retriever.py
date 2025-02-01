from langraph.utiles.load_data import load_bm25, load_faiss_index, load_faiss_metadata, load_documents
from langraph.utiles.BM25_retriever import HybridBM25FaissRetriever
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

documents_gangnam = load_documents(os.path.join(BASE_DIR, "faiss_bm25", "gangnam", "documents_gangnam.json"))
documents_jongro = load_documents(os.path.join(BASE_DIR, "faiss_bm25", "jongro", "documents_jongro.json"))
documents_yongsan = load_documents(os.path.join(BASE_DIR, "faiss_bm25", "yongsan", "documents_yongsan.json"))
documents_junggu = load_documents(os.path.join(BASE_DIR, "faiss_bm25", "junggu", "documents_Junggu.json"))

bm25_gangnam = load_bm25(os.path.join(BASE_DIR, "faiss_bm25", "gangnam", "bm25_gangnam.pkl"))
bm25_jongro = load_bm25(os.path.join(BASE_DIR, "faiss_bm25", "jongro", "bm25_jongro.pkl"))
bm25_yongsan = load_bm25(os.path.join(BASE_DIR, "faiss_bm25", "yongsan", "bm25_yongsan.pkl"))
bm25_junggu = load_bm25(os.path.join(BASE_DIR, "faiss_bm25", "junggu", "bm25_Junggu.pkl"))

faiss_index_gangnam = load_faiss_index(os.path.join(BASE_DIR, "faiss_bm25", "gangnam", "faiss_gangnam.index"))
faiss_index_jongro = load_faiss_index(os.path.join(BASE_DIR, "faiss_bm25", "jongro", "faiss_jongro.index"))
faiss_index_yongsan = load_faiss_index(os.path.join(BASE_DIR, "faiss_bm25", "yongsan", "faiss_yongsan.index"))
faiss_index_junggu = load_faiss_index(os.path.join(BASE_DIR, "faiss_bm25", "junggu", "faiss_Junggu.index"))

metadata_list_gangnam = load_faiss_metadata(os.path.join(BASE_DIR, "faiss_bm25", "gangnam", "faiss_metadata_gangnam.pkl"))
metadata_list_jongro = load_faiss_metadata(os.path.join(BASE_DIR, "faiss_bm25", "jongro", "faiss_metadata_jongro.pkl"))
metadata_list_yongsan = load_faiss_metadata(os.path.join(BASE_DIR, "faiss_bm25", "yongsan", "faiss_metadata_yongsan.pkl"))
metadata_list_junggu = load_faiss_metadata(os.path.join(BASE_DIR, "faiss_bm25", "junggu", "faiss_metadata_Junggu.pkl"))

retriever_naver_gangnam = HybridBM25FaissRetriever(
    bm25=bm25_gangnam,
    faiss_index=faiss_index_gangnam,
    documents=documents_gangnam,
    metadata_list=metadata_list_gangnam,
    top_k=25
)

retriever_naver_jongro = HybridBM25FaissRetriever(
    bm25=bm25_jongro,
    faiss_index=faiss_index_jongro,
    documents=documents_jongro,
    metadata_list=metadata_list_jongro,
    top_k=25
)

retriever_naver_yongsan = HybridBM25FaissRetriever(
    bm25=bm25_yongsan,
    faiss_index=faiss_index_yongsan,
    documents=documents_yongsan,
    metadata_list=metadata_list_yongsan,
    top_k=25
)

retriever_naver_Junggu = HybridBM25FaissRetriever(
    bm25=bm25_junggu,
    faiss_index=faiss_index_junggu,
    documents=documents_junggu,
    metadata_list=metadata_list_junggu,
    top_k=25
)

retriever_naver_gangnam_search = HybridBM25FaissRetriever(
    bm25=bm25_gangnam,
    faiss_index=faiss_index_gangnam,
    documents=documents_gangnam,
    metadata_list=metadata_list_gangnam,
    top_k=3
)

retriever_naver_jongro_search = HybridBM25FaissRetriever(
    bm25=bm25_jongro,
    faiss_index=faiss_index_jongro,
    documents=documents_jongro,
    metadata_list=metadata_list_jongro,
    top_k=3
)

retriever_naver_yongsan_search = HybridBM25FaissRetriever(
    bm25=bm25_yongsan,
    faiss_index=faiss_index_yongsan,
    documents=documents_yongsan,
    metadata_list=metadata_list_yongsan,
    top_k=3
)

retriever_naver_Junggu_search = HybridBM25FaissRetriever(
    bm25=bm25_junggu,
    faiss_index=faiss_index_junggu,
    documents=documents_junggu,
    metadata_list=metadata_list_junggu,
    top_k=3
)

embeddings = OpenAIEmbeddings()

# FAISS 인덱스 파일 경로를 리스트에 추가
faiss_index_paths = []

faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "opendata_gangnam_all"))
faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "opendata_jongro_all"))
faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "opendata_junggu_all"))
faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "opendata_yongsan_all"))

# FAISS 인덱스를 로드하고 리트리버를 생성
retrieves = []
for path in faiss_index_paths:
    retrieves.append(FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True).as_retriever())

# 각 리트리버를 변수에 할당
retriever_opendata_gangnam = retrieves[0]
retriever_opendata_jongro = retrieves[1]
retriever_opendata_junggu = retrieves[2]
retriever_opendata_yongsan = retrieves[3]

retriever_opendata_gangnam.search_kwargs = {"k": 50}
retriever_opendata_jongro.search_kwargs = {"k": 50}
retriever_opendata_junggu.search_kwargs = {"k": 50}
retriever_opendata_yongsan.search_kwargs = {"k": 50}