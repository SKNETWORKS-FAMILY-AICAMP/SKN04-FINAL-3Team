from utiles.nodes import *
from utiles.GraphState import GraphState

from dotenv import load_dotenv
load_dotenv()

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
import json
<<<<<<< HEAD:web/langraph/langgraph_chatbot_model.py
import pickle
import faiss
import numpy as np
from typing import List

from langchain.schema import Document, BaseRetriever
from konlpy.tag import Okt
from rank_bm25 import BM25Okapi
import jpype

from pydantic import PrivateAttr




def run_model(question, chat_history=None):

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

    # from konlpy.jvm import init_jvm
    # try:
    #     jvmpath = r"C:\Program Files\Java\jdk-17\bin\server\jvm.dll"

    #     if not jpype.isJVMStarted():
    #         init_jvm(jvmpath)

    #     okt = Okt()
    #     print("Okt instance created successfully!")
    # except Exception as e:
    #     print(f"Error: {e}")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

    # BASE_DIR은 현재 파일이 위치한 디렉토리를 기준으로 설정
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

    # GraphState 상태 정의
    class GraphState(TypedDict):
        question: Annotated[List[str], add_messages]  # 질문(누적되는 list)
        context_naver_gangnam: Annotated[List, "context_naver_gangnam"]  # 문서의 검색 결과
        context_naver_jongro: Annotated[List, "context_naver_jongro"]  # 문서의 검색 결과
        context_naver_Junggu: Annotated[List, "context_naver_Junggu"]  # 문서의 검색 결과
        context_naver_yongsan: Annotated[List, "context_naver_yongsan"]  # 문서의 검색 결과
        context_opendata_gangnam: Annotated[List, "context_opendata_gangnam"]  # 문서의 검색 결과
        context_opendata_jongro: Annotated[List, "context_opendata_jongro"]  # 문서의 검색 결과
        context_opendata_Junggu: Annotated[List, "context_opendata_Junggu"]  # 문서의 검색 결과
        context_opendata_yongsan: Annotated[List, "context_opendata_yongsan"]  # 문서의 검색 결과
        answer: Annotated[str, "Answer"]  # 답변
        messages: Annotated[list, add_messages]  # 메시지(누적되는 list)
        webOrRetriever: Annotated[str, "webOrRetriever"]  # 웹 or 리트리버 검색
        ScheduleOrplace: Annotated[str, "ScheduleOrplace"]  # 일정 or 장소
        location: Annotated[str, "location"]  # 지역 리스트
        dayCheck: Annotated[str, "dayCheck"]  # 몇일 여행?
        languageCheck: Annotated[str, "languageCheck"]  # 언어판별
        translated_question: Annotated[str, "translated_question"]  # 번역된 질문
        location_error: Annotated[int, "location_error"]  # 장소 에러
        day_error: Annotated[int, "day_error"]  # 여행 일 수 에러
        language_error: Annotated[int, "language_error"]  # 언어 에러
        error_or_normal: Annotated[str, "error_or_normal"]  # 스케줄 에러
        pre_chat: Annotated[str, "pre_chat"]  # chat_history
=======

def run_model(question, chat_history=None):

>>>>>>> langraph:langgraph/langgraph_chatbot_model.py
        
    chat_history_json = chat_history
    ####-----노드 함수--------#####

    def json_to_string(state):
        try:
            # 입력이 None인 경우 빈 문자열 반환
            if chat_history_json is None:
                return { "pre_chat" : "" }
            # 이미 문자열인 경우 그대로 반환
            if isinstance(chat_history_json, str):
                return {"pre_chat" : chat_history_json}
            # JSON 데이터를 문자열로 변환
            return {"pre_chat" : json.dumps(chat_history_json, ensure_ascii=False, indent=4)}
        except:
            return {"pre_chat" : "이전 대화 내용을 불러오는데 실패했습니다."}


    # 그래프 생성
    workflow = StateGraph(GraphState)

    # 노드 정의
    workflow.add_node("location_check", location_check)
    workflow.add_node("location_check_schdule_change", location_check)
    workflow.add_node("Schedule_day_check", Schedule_day_check)
    workflow.add_node("retrieve_document_naver", retrieve_document_naver)
    workflow.add_node("retrieve_opendata", retrieve_document_opendata)
    workflow.add_node("llm_Schedule_answer", llm_Schedule_answer)
    workflow.add_node("Schedule_or_place_check", Schedule_or_place_check)
    workflow.add_node("llm_place_answer", llm_place_answer)
    workflow.add_node("language_check", language_check)
    workflow.add_node("translate_question", translate_question)
    workflow.add_node("error_handling", error_handling)
    workflow.add_node("language_check_is_normal", language_check_is_normal)
    workflow.add_node("day_locatoin_check", day_locatoin_check)
    workflow.add_node("error_check", error_check)
    workflow.add_node("error_check_schdule_change", error_check)
    workflow.add_node("initialize_error_status", initialize_error_status)
    workflow.add_node("language_error_node", language_error_node)
    workflow.add_node("llm_Schedule_change_answer", llm_Schedule_change_answer)
    workflow.add_node("json_to_string", json_to_string)
    workflow.add_node("retrieve_document_naver_search", retrieve_document_naver_search)



    workflow.set_entry_point("initialize_error_status")
    workflow.set_entry_point("json_to_string")
    workflow.add_edge("initialize_error_status", "translate_question") 

    workflow.add_edge("translate_question", "language_check") 

    workflow.add_conditional_edges(
        "language_check",  
        is_language_error,
        {
            "정상": "language_check_is_normal",  #일정
            "에러": "language_error_node",  # 장소검색
        },
    )
    workflow.add_edge("language_error_node", "error_handling") 


    workflow.add_edge("language_check_is_normal", "retrieve_document_naver") 
    workflow.add_edge("language_check_is_normal", "retrieve_opendata") 
    workflow.add_edge("retrieve_document_naver", "Schedule_or_place_check") 
    workflow.add_edge("retrieve_opendata", "Schedule_or_place_check") 

    workflow.add_conditional_edges(
        "Schedule_or_place_check",  
        is_place,
        {
            "일정": "day_locatoin_check",  #일정
            "장소검색": "retrieve_document_naver_search", # 장소검색
            "일정변경" : "location_check_schdule_change" 
        },
    )
    
    workflow.add_edge("location_check_schdule_change", "error_check_schdule_change")

    workflow.add_conditional_edges(
        "error_check_schdule_change",  
        is_error,
        {
            "에러": "error_handling",  #일정
            "정상": "llm_Schedule_change_answer",  
        },
    )
    
    workflow.add_edge("day_locatoin_check", "location_check") 
    workflow.add_edge("day_locatoin_check", "Schedule_day_check") 

    workflow.add_edge("location_check", "error_check") 
    workflow.add_edge("Schedule_day_check", "error_check") 

    workflow.add_edge("retrieve_document_naver_search", "llm_place_answer") 

    workflow.add_conditional_edges(
        "error_check",  
        is_error,
        {
            "에러": "error_handling",  #일정
            "정상": "llm_Schedule_answer",  
        },
    )

    workflow.add_edge("llm_Schedule_answer", END)  # 답변 -> 종료
    workflow.add_edge("llm_place_answer", END)  # 답변 -> 종료
    workflow.add_edge("error_handling", END)  # 답변 -> 종료
    workflow.add_edge("llm_Schedule_change_answer", END)  # 답변 -> 종료

    # 체크포인터 설정
    memory = MemorySaver()

    # 컴파일
    app = workflow.compile(checkpointer=memory)


    # config 설정(재귀 최대 횟수, thread_id)
    config = RunnableConfig(recursion_limit=20, configurable={"thread_id": 3})

    # 질문 입력
    inputs = GraphState(question=question)

    ans=app.stream(input=inputs, config=config, stream_mode='messages')


    return ans
