from utiles.nodes import *
from utiles.GraphState import GraphState

from dotenv import load_dotenv
load_dotenv()

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
import json


def run_model(question, chat_history=None):
        
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
