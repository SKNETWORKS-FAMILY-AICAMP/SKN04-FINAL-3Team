from langraph.chain_model.extraction_day_chain import day_chain
from langraph.chain_model.extraction_loacation_chain import location_chain
from langraph.chain_model.extraction_schedule_or_place_chain import sch_or_place_chain
from langraph.chain_model.place_search_chain import place_search_chain
from langraph.chain_model.schedule_chain import schedule_chain
from langraph.chain_model.discrimination_language import discrimination_language
from langraph.chain_model.translation_question import translation_question
from langraph.chain_model.error_handle_chain import error_handle_chain
from langraph.chain_model.is_schedule_error import schedule_error_chain
from langraph.chain_model.schedule_change_chain import schedule_change_chain
from langraph.chain_model.over_ten_day_chain import over_ten_day_chain
from langraph.utiles.load_retriever import retriever_naver_yongsan, retriever_naver_jongro, retriever_naver_gangnam, retriever_naver_Junggu
from langraph.utiles.load_retriever import retriever_naver_yongsan_search, retriever_naver_jongro_search, retriever_naver_gangnam_search, retriever_naver_Junggu_search
from langraph.utiles.load_retriever import retriever_opendata_yongsan, retriever_opendata_jongro, retriever_opendata_gangnam, retriever_opendata_junggu
from langraph.utiles.GraphState import GraphState


import ast
import random


def initialize_error_status(state):
    return{
            "language_error": 0,
            "location_error": 0,
            "day_error": 0,
                }

def language_check_is_normal(state):
    pass

def day_locatoin_check(state):

    pass

def translate_question(state: GraphState) -> GraphState:
    chain_translation_question = translation_question()
    response = chain_translation_question.invoke(
        {
            "question": state["question"][-1].content
        }
    )

    return {"translated_question": response}

def language_check(state: GraphState) -> GraphState:
    chain_discrimination_language = discrimination_language()
    response = chain_discrimination_language.invoke(
        {"question": state["question"][-1].content}
    )

    return {"languageCheck": response}

def Schedule_day_check(state: GraphState) -> GraphState:
    chain_day = day_chain()
    response = chain_day.invoke(
        {"question": state["question"][-1].content}
    )

    try :
        ast.literal_eval(response)
    except :
        return {"day_error" : 1}

    return {"dayCheck": response}

# 장소검색 or 일정 검색
def Schedule_or_place_check(state: GraphState) -> GraphState:
    # 관련성 체크를 실행("yes" or "no")
    chain_sch_or_placeSearch = sch_or_place_chain()
    response = chain_sch_or_placeSearch.invoke(
        {"question": state["question"][-1].content}
    )

    return {"ScheduleOrplace": response}


# 일정 장소검색 리트리버 분기 체크하는 함수(router)
def is_place(state: GraphState) -> GraphState:
    if state["ScheduleOrplace"] == "일정":
        return "일정"
    elif state["ScheduleOrplace"] == "일정변경":
        return "일정변경"
    else:
        return "장소검색"
    

def error_check(state: GraphState) -> GraphState:
    
    error_or_normal_chain = schedule_error_chain()
    response = error_or_normal_chain.invoke(
        {
            "state_location": state["location_error"],
            "state_day": state["day_error"]
        }
    )

    return {"error_or_normal": response}


#  분기 체크하는 함수(router)
def is_error(state: GraphState) -> GraphState:
    if state["error_or_normal"] == "에러":
        return "에러"
    else:
        return "정상"
    
def is_language_error(state: GraphState) -> GraphState:
    if state["languageCheck"] == "언어정보없음":
        return "에러"
    else:
        return "정상"

def language_error_node(state):
    return{"language_error": 1}

# 지역 판별
def location_check(state: GraphState) -> GraphState:

    chain_location = location_chain()

    response = chain_location.invoke(
        {"question": state["question"][-1].content}
    )
    try :
        location_list = ast.literal_eval(response)
    except :
        return {"location_error" : 1}
    
    if len(location_list) == 0:
        return {"location_error" : 1}
    
    return {"location": response}

def error_handling(state: GraphState) -> GraphState:
    state_location = state["location_error"]
    state_day = state["day_error"]
    state_language = state["language_error"]
    language = state['languageCheck']
    latest_question = state["question"][-1].content


    error_handler_chain = error_handle_chain()
    response = error_handler_chain.invoke(
        {
            "state_location": state_location,
            "state_day": state_day,
            "state_language": state_language,
            "language" : language,
            "question" : latest_question

        }
    )

    return {"translated_question": response}

    
# 문서 검색 노드--------------------------------------------------------------------------------------------------------------------------
def retrieve_document_naver(state: GraphState) -> GraphState:
    # 질문을 상태에서 가져옵니다.
    latest_question = state["translated_question"]
    
    retrieved_docs_yongsan = []
    retrieved_docs_jongro = []
    retrieved_docs_gangman = []
    retrieved_docs_junggu = []

    retrieved_docs_yongsan = retriever_naver_yongsan.invoke(latest_question)
    retrieved_docs_jongro = retriever_naver_jongro.invoke(latest_question)
    retrieved_docs_gangman = retriever_naver_gangnam.invoke(latest_question)
    retrieved_docs_junggu = retriever_naver_Junggu.invoke(latest_question)

    return {"context_naver_gangnam": retrieved_docs_gangman,
            "context_naver_jongro": retrieved_docs_jongro,
            "context_naver_Junggu": retrieved_docs_junggu,
            "context_naver_yongsan": retrieved_docs_yongsan}


def retrieve_document_naver_search(state: GraphState) -> GraphState:
    # 질문을 상태에서 가져옵니다.
    latest_question = state["translated_question"]
    
    retrieved_docs_yongsan = []
    retrieved_docs_jongro = []
    retrieved_docs_gangman = []
    retrieved_docs_junggu = []

    retrieved_docs_yongsan = retriever_naver_yongsan_search.invoke(latest_question)
    retrieved_docs_jongro = retriever_naver_jongro_search.invoke(latest_question)
    retrieved_docs_gangman = retriever_naver_gangnam_search.invoke(latest_question)
    retrieved_docs_junggu = retriever_naver_Junggu_search.invoke(latest_question)

    return {"context_naver_gangnam": retrieved_docs_gangman,
            "context_naver_jongro": retrieved_docs_jongro,
            "context_naver_Junggu": retrieved_docs_junggu,
            "context_naver_yongsan": retrieved_docs_yongsan}

#------------------------------------------------------------------------------------------------------------------------------------------------


def retrieve_document_opendata(state: GraphState) -> GraphState:
    # 질문을 상태에서 가져옵니다.
    latest_question = state["translated_question"]

    retrieved_docs_yongsan = []
    retrieved_docs_jongro = []
    retrieved_docs_gangman = []
    retrieved_docs_junggu = []

    retrieved_docs_yongsan = retriever_opendata_yongsan.invoke(latest_question)
    retrieved_docs_jongro = retriever_opendata_jongro.invoke(latest_question)
    retrieved_docs_gangman = retriever_opendata_gangnam.invoke(latest_question)
    retrieved_docs_junggu = retriever_opendata_junggu.invoke(latest_question)

    return {
        "context_opendata_gangnam": retrieved_docs_gangman,
        "context_opendata_jongro": retrieved_docs_jongro,
        "context_opendata_Junggu": retrieved_docs_junggu,
        "context_opendata_yongsan": retrieved_docs_yongsan,
            }




# 일정 생성 노드----------------------------------------------------------------------------

def llm_Schedule_answer(state: GraphState) -> GraphState:
    # 질문을 상태에서 가져옵니다.
    latest_question = state["question"][-1].content
    location_str = state['location']
    day_str = state['dayCheck']
    language = state['languageCheck']

    location = ast.literal_eval(location_str)

    if len(location) == 1:
        num_retriever_search = 10
    elif len(location) == 2:
        num_retriever_search = 7
    elif len(location) == 3:
        num_retriever_search = 5
    elif len(location) == 4:
        num_retriever_search = 4

    if len(location) == 1:
        num_retriever_search_opendata = 5
    elif len(location) == 2:
        num_retriever_search_opendata = 4
    elif len(location) == 3:
        num_retriever_search_opendata = 3
    elif len(location) == 4:
        num_retriever_search_opendata = 2
    
    try : day = ast.literal_eval(day_str)
    except : return {'day_error' : 1}

    if language == '언어정보없음':
        return {'language_error' :1}
    
    response_list = []
    place_list = []
    place_yongsan =[]
    place_jongro =[]
    place_gangman =[]
    place_junggu =[]
    additional_list=[]
    # 문서에서 검색하여 관련성 있는 문서를 찾습니다.
    yongsan = '용산구'
    jongro = '종로구'
    gangman = '강남구'
    junggu = '중구'

    chain = schedule_chain(language)
    place_yongsan = state["context_naver_yongsan"]
    place_jongro = state["context_naver_jongro"]
    place_gangman = state["context_naver_gangnam"]
    place_junggu = state["context_naver_Junggu"]
    place_opendata_yongsan = state["context_opendata_yongsan"]
    place_opendata_jongro = state["context_opendata_jongro"]
    place_opendata_gangnam = state["context_opendata_gangnam"]
    place_opendata_junggu = state["context_opendata_Junggu"]

    if int(day_str) < 11 :

        for i in range(1, day+1):
            if yongsan in location:      
                if len(place_yongsan) < num_retriever_search:
                    break
                selected = random.sample(place_yongsan, num_retriever_search)

                for item in selected:
                    place_yongsan.remove(item)

                if language == '영어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in selected]) 
                elif language == '한국어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in selected]) 
                elif language == '일본어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 일본어이름 : ' + i.metadata.get('store_name_japanese') + ', 일본어주소 : ' + i.metadata.get('address_japanese') for i in selected]) 
                elif language == '중국어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 중국어이름 : ' + i.metadata.get('store_name_chinese') + ', 중국어주소 : ' + i.metadata.get('address_chinese') for i in selected]) 
                place_list.extend(selected)

                selected_opened = random.sample(place_opendata_yongsan, num_retriever_search_opendata)
                for item in selected_opened:
                    place_opendata_yongsan.remove(item)
                place_list.extend(selected_opened)

            if jongro in location:
                if len(place_jongro) < num_retriever_search:
                    print("남은 요소가 부족합니다.")
                    break
                selected = random.sample(place_jongro, num_retriever_search)

                for item in selected:
                    place_jongro.remove(item)
                if language == '영어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in selected]) 
                elif language == '한국어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in selected]) 
                elif language == '일본어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 일본어이름 : ' + i.metadata.get('store_name_japanese') + ', 일본어주소 : ' + i.metadata.get('address_japanese') for i in selected]) 
                elif language == '중국어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 중국어이름 : ' + i.metadata.get('store_name_chinese') + ', 중국어주소 : ' + i.metadata.get('address_chinese') for i in selected]) 
                place_list.extend(selected)
                selected_opened = random.sample(place_opendata_jongro, num_retriever_search_opendata)
                for item in selected_opened:
                    place_opendata_jongro.remove(item)
                place_list.extend(selected_opened)

            if gangman in location:
                if len(place_gangman) < num_retriever_search:
                    print("남은 요소가 부족합니다.")
                    break
                selected = random.sample(place_gangman, num_retriever_search)

                for item in selected:
                    place_gangman.remove(item)         
                if language == '영어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in selected]) 
                elif language == '한국어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in selected]) 
                elif language == '일본어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 일본어이름 : ' + i.metadata.get('store_name_japanese') + ', 일본어주소 : ' + i.metadata.get('address_japanese') for i in selected]) 
                elif language == '중국어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 중국어이름 : ' + i.metadata.get('store_name_chinese') + ', 중국어주소 : ' + i.metadata.get('address_chinese') for i in selected]) 
                place_list.extend(selected)
                selected_opened = random.sample(place_opendata_gangnam, num_retriever_search_opendata)
                for item in selected_opened:
                    place_opendata_gangnam.remove(item)
                place_list.extend(selected_opened)

            if junggu in location:
                if len(place_junggu) < num_retriever_search:
                    print("남은 요소가 부족합니다.")
                    break
                selected = random.sample(place_junggu, num_retriever_search)

                for item in selected:
                    place_junggu.remove(item)   
                if language == '영어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in selected]) 
                elif language == '한국어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in selected]) 
                elif language == '일본어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 일본어이름 : ' + i.metadata.get('store_name_japanese') + ', 일본어주소 : ' + i.metadata.get('address_japanese') for i in selected]) 
                elif language == '중국어':
                    additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 좌표 : ' + i.metadata.get('coordinates') + ', 중국어이름 : ' + i.metadata.get('store_name_chinese') + ', 중국어주소 : ' + i.metadata.get('address_chinese') for i in selected]) 
                place_list.extend(selected)
                selected_opened = random.sample(place_opendata_junggu, num_retriever_search_opendata)
                for item in selected_opened:
                    place_opendata_junggu.remove(item)
                place_list.extend(selected_opened)

            #검색된 문서를 형식화합니다.(프롬프트 입력으로 넣어주기 위함)
            place_list_text = "\n".join(
            [
                f"<content>{doc.page_content}</content>"
                for doc in place_list
            ]
            )

            additional_text = "\n".join(
            [
                f"<additional>{doc}</additional>"
                for doc in additional_list
            ]
            )

            # 체인을 호출하여 답변을 생성합니다.
            response = chain.invoke(
                {
                    "question": latest_question,
                    "context": place_list_text,
                    "chat_history": state["pre_chat"],
                    "day" : i,
                    "language" : language,
                    "additional" : additional_text
                }
            )
            place_list.clear()
            response_list.append(response)
            print('\n')
    else:
        chain = over_ten_day_chain()
        response = chain.invoke(
            {
                "language" : language,
            }
        )

    response_list_text = "\n".join(
    [
        f"{doc}"
        for doc in response_list
    ]
    )
    # 생성된 답변, (유저의 질문, 답변) 메시지를 상태에 저장합니다.
    return {
        "answer": response,
        "messages": [("user", latest_question), ("assistant", response_list_text)],
    }
# 일정 생성 노드 끝----------------------------------------------------------------------------

# 일정 변경 노드-------------------------------------------------------------------------------

def llm_Schedule_change_answer(state: GraphState) -> GraphState:
    # 질문을 상태에서 가져옵니다.
    latest_question = state["question"][-1].content
    location_str = state['location']
    language = state['languageCheck']

    location = ast.literal_eval(location_str)

    if len(location) == 1:
        num_retriever_search = 8
    elif len(location) == 2:
        num_retriever_search = 7
    elif len(location) == 3:
        num_retriever_search = 5
    elif len(location) == 4:
        num_retriever_search = 4

    if language == '언어정보없음':
        return {'language_error' :1}

    place_list = []
    place_yongsan =[]
    place_jongro =[]
    place_gangman =[]
    place_junggu =[]
    # 문서에서 검색하여 관련성 있는 문서를 찾습니다.
    yongsan = '용산구'
    jongro = '종로구'
    gangman = '강남구'
    junggu = '중구'


    if yongsan in location:
        place_yongsan = state["context_naver_yongsan"]

        place_list.extend(place_yongsan[:num_retriever_search])
        place_list.extend(state["context_opendata_yongsan"][:num_retriever_search])

    if jongro in location:
        place_jongro = state["context_naver_jongro"]

        place_list.extend(place_jongro[:num_retriever_search])
        place_list.extend(state["context_opendata_jongro"][:num_retriever_search])

    if gangman in location:
        place_gangman = state["context_naver_gangnam"]
        place_list.extend(place_gangman[:num_retriever_search])
        place_list.extend(state["context_opendata_gangnam"][:num_retriever_search])


    if junggu in location:
        place_junggu = state["context_naver_Junggu"]

        place_list.extend(place_junggu[:num_retriever_search])
        place_list.extend(state["context_opendata_Junggu"][:num_retriever_search])


    #검색된 문서를 형식화합니다.(프롬프트 입력으로 넣어주기 위함)
    place_list_text = "\n".join(
    [
        f"<content>{doc.page_content}</content>"
        for doc in place_list
    ]
    )

    change_chain = schedule_change_chain()
    # 체인을 호출하여 답변을 생성합니다.
    response = change_chain.invoke(
        {
            "question": latest_question,
            "context": place_list_text,
            "chat_history": state["pre_chat"],
            "language" : language
        }
    )


    # 생성된 답변, (유저의 질문, 답변) 메시지를 상태에 저장합니다.
    return {
        "answer": response,
        "messages": [("user", latest_question), ("assistant", response)],
    }

# 장소 검색 노드 ----------------------------------------------------------------------------

def llm_place_answer(state: GraphState) -> GraphState:
    # 질문을 상태에서 가져옵니다.
    latest_question = state["question"][-1].content

    language = state['languageCheck']

    place_list = []
    place_yongsan =[]
    place_jongro =[]
    place_gangman =[]
    place_junggu =[]
    additional_list=[]


    place_yongsan = state["context_naver_yongsan"]
    place_list.extend(place_yongsan)
    if language == '영어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in place_yongsan]) 
    elif language == '한국어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in place_yongsan]) 
    elif language == '일본어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 일본어이름 : ' + i.metadata.get('store_name_japanese') + ', 일본어주소 : ' + i.metadata.get('address_japanese') for i in place_yongsan]) 
    elif language == '중국어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 중국어이름 : ' + i.metadata.get('store_name_chinese') + ', 중국어주소 : ' + i.metadata.get('address_chinese') for i in place_yongsan]) 

    place_jongro = state["context_naver_jongro"]
    place_list.extend(place_jongro)
    if language == '영어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in place_jongro]) 
    elif language == '한국어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in place_jongro]) 
    elif language == '일본어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 일본어이름 : ' + i.metadata.get('store_name_japanese') + ', 일본어주소 : ' + i.metadata.get('address_japanese') for i in place_jongro]) 
    elif language == '중국어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 중국어이름 : ' + i.metadata.get('store_name_chinese') + ', 중국어주소 : ' + i.metadata.get('address_chinese') for i in place_jongro]) 

    place_gangman = state["context_naver_gangnam"]
    place_list.extend(place_gangman)
    if language == '영어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in place_gangman]) 
    elif language == '한국어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in place_gangman]) 
    elif language == '일본어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 일본어이름 : ' + i.metadata.get('store_name_japanese') + ', 일본어주소 : ' + i.metadata.get('address_japanese') for i in place_gangman]) 
    elif language == '중국어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 중국어이름 : ' + i.metadata.get('store_name_chinese') + ', 중국어주소 : ' + i.metadata.get('address_chinese') for i in place_gangman]) 

    place_junggu = state["context_naver_Junggu"]
    place_list.extend(place_junggu)
    if language == '영어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in place_junggu]) 
    elif language == '한국어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 영문이름 : ' + i.metadata.get('store_name_english') + ', 영문주소 : ' + i.metadata.get('address_english') for i in place_junggu]) 
    elif language == '일본어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 일본어이름 : ' + i.metadata.get('store_name_japanese') + ', 일본어주소 : ' + i.metadata.get('address_japanese') for i in place_junggu]) 
    elif language == '중국어':
        additional_list.extend(['장소이름 : ' + i.metadata.get('store_name') + ', 중국어이름 : ' + i.metadata.get('store_name_chinese') + ', 중국어주소 : ' + i.metadata.get('address_chinese') for i in place_junggu]) 

    place_opendata_junggu = state["context_opendata_yongsan"]
    place_opendata_junggu = place_opendata_junggu[:3]
    place_list.extend(place_opendata_junggu)

    place_junggu = state["context_opendata_jongro"]
    place_opendata_junggu = place_opendata_junggu[:3]
    place_list.extend(place_opendata_junggu)

    place_opendata_junggu = state["context_opendata_gangnam"]
    place_opendata_junggu = place_opendata_junggu[:3]
    place_list.extend(place_opendata_junggu)

    place_opendata_junggu = state["context_naver_Junggu"]
    place_opendata_junggu = place_opendata_junggu[:3]
    place_list.extend(place_opendata_junggu)

    place_list_text = "\n".join(
    [
        f"<content>{doc.page_content}</content>"
        for doc in place_list
    ]
    )
    
    additional_text = "\n".join(
    [
        f"<additional>{doc}</additional>"
        for doc in additional_list
    ]
    )

    # 체인을 호출하여 답변을 생성합니다.
    chain_place_search = place_search_chain(language)

    response = chain_place_search.invoke(
        {
            "question": latest_question,
            "context": place_list_text,
            "chat_history": state['pre_chat'],
            "language" : language,
            "additional" : additional_text
        }
    )

    # 생성된 답변, (유저의 질문, 답변) 메시지를 상태에 저장합니다.
    return {
        "answer": response,
        "messages": [("user", latest_question), ("assistant", response)],
    }
