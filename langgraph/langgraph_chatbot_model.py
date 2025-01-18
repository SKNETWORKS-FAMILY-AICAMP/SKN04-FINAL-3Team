# from chain_model.extraction_day_chain import day_chain
# from chain_model.extraction_loacation_chain import location_chain
# from chain_model.extraction_schedule_or_place_chain import sch_or_place_chain
# from chain_model.place_search_chain import place_search_chain
# from chain_model.schedule_chain import schedule_chain

import os
import random
import re
import ast
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv
# from operator import itemgetter
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnableConfig
# from langchain_core.output_parsers import StrOutputParser
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import OpenAIEmbeddings
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from langchain_teddynote.messages import invoke_graph, stream_graph
from langchain_teddynote.messages import messages_to_history, random_uuid
from langchain_teddynote.tools.tavily import TavilySearch

# chains 불러오기
from chains.core_chains import day_chain, location_chain, schedule_or_place_chain, place_search_chain, schedule_chain

# Load environment variables
load_dotenv()

# Constants
## BASE_DIR은 현재 파일이 위치한 디렉토리를 기준으로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
## FAISS 인덱스 파일 경로를 리스트에 추가
FAISS_INDEX_PATHS = [
    os.path.join(BASE_DIR, "Faiss", path) for path in [
        "naver_map_gangnam_faiss", "naver_map_jongro_faiss",
        "naver_map_Junggu_faiss", "naver_map_yongsan_faiss",
        "opendata_gangnam_all", "opendata_jongro_all",
        "opendata_junggu_all", "opendata_yongsan_all"
    ]
]
SEARCH_K = 50
# REGIONS = ['용산구', '종로구', '강남구', '중구']
REGIONS = ['yongsan', 'jongro', 'gangnam', 'junggu']

# GraphState 정의
class GraphState(TypedDict):
    question: Annotated[List[str], add_messages]  # 질문(누적되는 list)
    context_naver_gangnam: Annotated[List, "context_naver_gangnam"]  # 문서의 검색 결과
    context_naver_jongro: Annotated[List, "context_naver_jongro"]  # 문서의 검색 결과
    context_naver_Junggu: Annotated[List, "context_naver_junggu"]  # 문서의 검색 결과
    context_naver_yongsan: Annotated[List, "context_naver_yongsan"]  # 문서의 검색 결과
    context_opendata: Annotated[List, "context_opendata"]  # 문서의 검색 결과
    answer: Annotated[str, "Answer"]  # 답변
    messages: Annotated[list, add_messages]  # 메시지(누적되는 list)
    webOrRetriever: Annotated[str, "webOrRetriever"]  # 웹 or 리트리버 검색
    ScheduleOrplace: Annotated[str, "ScheduleOrplace"]  # 일정 or 장소
    location: Annotated[str, "location"]  # 지역 리스트
    dayCheck: Annotated[str, "dayCheck"]  # 몇일 여행?

# Utility function for FAISS retriever loading
def load_faiss_retrievers() -> List[FAISS]:
    embeddings = OpenAIEmbeddings()
    return [
        FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True).as_retriever()
        for path in FAISS_INDEX_PATHS
    ]

# FAISS 인덱스를 로드하고 리트리버를 생성
retrievers = load_faiss_retrievers()
# 리트리버의 검색 매개변수를 설정 (검색 결과의 개수)
for retriever in retrievers:
    retriever.search_kwargs = {"k": SEARCH_K}
    
# Utility function for region-based retrieval
def retrieve_documents(retrievers, latest_question, locations, prefix="naver"):
    result = {f"context_{prefix}_{region}": [] for region in REGIONS}

    for region, retriever in zip(REGIONS, retrievers):
        if region in locations:
            result[f"context_{prefix}_{region}"] = retriever.invoke(latest_question)
    return result

# retrieve document naver/opendata
def retrieve_naver_documents(state: GraphState) -> GraphState:
    latest_question = state["question"][-1].content
    locations = ast.literal_eval(state["location"])
    return retrieve_documents(retrievers[:4], latest_question, locations, prefix="naver")

def retrieve_opendata_documents(state: GraphState) -> GraphState:
    latest_question = state["question"][-1].content
    locations = ast.literal_eval(state["location"])
    return retrieve_documents(retrievers[4:], latest_question, locations, prefix="opendata")

# Graph Node Functions
## 지역 판별
def extract_location(state: GraphState) -> GraphState:
    response = location_chain().invoke({"question": state["question"][-1].content})
    return {"location": response}

## 웹 검색 or 리트리버 검색
def extract_trip_days(state: GraphState) -> GraphState:
    response = day_chain().invoke({"question": state["question"][-1].content})
    return {"dayCheck": response}

## 장소검색 or 일정 검색
def is_schedule_or_place_search(state: GraphState) -> GraphState:
    response = schedule_or_place_chain().invoke({"question": state["question"][-1].content})
    return {"ScheduleOrplace": response}

def clean_tags(text: str, tag: str = "content") -> str:
    """Remove specified tags from the text."""
    import re
    pattern = rf"<\/?{tag}>"
    return re.sub(pattern, "", text).strip()

def generate_schedule(state: GraphState) -> GraphState:
    latest_question = state["question"][-1].content
    locations = ast.literal_eval(state["location"])
    day_count = int(state["dayCheck"])

    place_list = []
    for day in range(1, day_count + 1):
        for region in REGIONS:
            context_key = f"context_naver_{region}"
            if region in locations:
                place_list.extend(state[context_key][:4])

        place_list_text = "\n".join(f"<content>{doc.page_content}</content>" for doc in place_list)
        # print("Messages:", state["messages"])
        response = schedule_chain().invoke({
            "question": latest_question,
            "context": place_list_text,
            "chat_history": messages_to_history(state["messages"]),
            "day": day
        })
        response = clean_tags(response, "content")
        return {"answer": response, "messages": [("user", latest_question), ("assistant", response)]}

def generate_place_recs(state: GraphState) -> GraphState:
    latest_question = state["question"][-1].content
    locations = ast.literal_eval(state["location"])
    place_list = []

    # 지역 기반 문서 검색 결과 가져오기
    for region in REGIONS:
        context_key = f"context_naver_{region}"
        if region in locations:
            place_list.extend(state[context_key][:5])

    # llm 입력 데이터 생성
    place_list_text = "\n".join(f"<content>{doc.page_content}</content>" for doc in place_list)
    
    # llm 호출
    response = place_search_chain().invoke({
        "question": latest_question,
        "context": place_list_text,
        "chat_history": messages_to_history(state["messages"]),
    })
    
    # 태그 제거 및 최종 결과 반환
    response = clean_tags(response, "content")
    # print(response)
    return {"answer": response, "messages": [("user", latest_question), ("assistant", response)]}

# def clean_output(output: str) -> str:
#     """Remove <content> tags from the output."""
#     return re.sub(r"<\/?content>", "", output)

# Build Workflow
workflow = StateGraph(GraphState)
workflow.add_node("extract_location", extract_location)
workflow.add_node("extract_trip_days", extract_trip_days)
workflow.add_node("retrieve_naver_documents", retrieve_naver_documents)
workflow.add_node("retrieve_opendata_documents", retrieve_opendata_documents)
# workflow.add_node("llm_Summary_opendata", llm_Summary_opendata)
# workflow.add_node("llm_Summary_naver", llm_Summary_naver)
workflow.add_node("generate_schedule", generate_schedule)
workflow.add_node("is_schedule_or_place_search", is_schedule_or_place_search)
workflow.add_node("generate_place_recs", generate_place_recs)

workflow.add_conditional_edges(
    "is_schedule_or_place_search", lambda state: state["ScheduleOrplace"],
    {"일정": "extract_trip_days", "장소검색": "generate_place_recs"}
)
workflow.add_edge("extract_location", "retrieve_naver_documents")      # 검색 -> 답변
workflow.add_edge("extract_location", "retrieve_opendata_documents")   # 검색 -> 답변
workflow.add_edge("retrieve_naver_documents", "is_schedule_or_place_search")      # 검색 -> 답변
workflow.add_edge("retrieve_opendata_documents", "is_schedule_or_place_search")   # 검색 -> 답변
workflow.add_edge("extract_trip_days", "generate_schedule")
workflow.add_edge("generate_schedule", END)  # 답변 -> 종료
workflow.add_edge("generate_place_recs", END)  # 답변 -> 종료

# 그래프 진입점 설정
workflow.set_entry_point("extract_location")

# 체크포인터 설정
memory = MemorySaver()

# 컴파일
app = workflow.compile(checkpointer=memory)

# Main Execution Function
def run_model(question: str):
    # 입력 데이터를 메시지 형식으로 변환
    # inputs = GraphState(
    #     question=[{"role": "user", "content": question}],
    #     messages=[]
    # )

    # config 설정(재귀 최대 횟수, thread_id)
    config = RunnableConfig(recursion_limit=20, configurable={"thread_id": random_uuid()})
    
    # 질문 입력
    # inputs = GraphState(question=[{"content": question}])
    inputs = GraphState(question=question)
    result = app.stream(input=inputs, config=config, stream_mode="messages")
    
    return result
