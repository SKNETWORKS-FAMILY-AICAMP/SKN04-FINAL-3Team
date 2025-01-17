# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
# API 키 정보 로드
load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from operator import itemgetter
from langchain_core.runnables import RunnableConfig
from langchain_teddynote.messages import invoke_graph, stream_graph, random_uuid
from langchain_teddynote.messages import messages_to_history
from langchain_teddynote.tools.tavily import TavilySearch
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
import time
import sys
import ast
import os
import random



def run_gpt_api(question):

    embeddings = OpenAIEmbeddings()

    # BASE_DIR은 현재 파일이 위치한 디렉토리를 기준으로 설정
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # FAISS 인덱스 파일 경로를 리스트에 추가
    faiss_index_paths = []
    faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "naver_map_gangnam_faiss"))
    faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "naver_map_jongro_faiss"))
    faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "naver_map_Junggu_faiss"))
    faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "naver_map_yongsan_faiss"))
    faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "opendata_gangnam_all"))
    faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "opendata_jongro_all"))
    faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "opendata_junggu_all"))
    faiss_index_paths.append(os.path.join(BASE_DIR, "Faiss", "opendata_yongsan_all"))

    # FAISS 인덱스를 로드하고 리트리버를 생성
    retrieves = []
    for path in faiss_index_paths:
        retrieves.append(FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True).as_retriever())

    # 각 리트리버를 변수에 할당
    retriever_naver_gangnam = retrieves[0]
    retriever_naver_jongro = retrieves[1]
    retriever_naver_Junggu = retrieves[2]
    retriever_naver_yongsan = retrieves[3]
    retriever_opendata_gangnam = retrieves[4]
    retriever_opendata_jongro = retrieves[5]
    retriever_opendata_junggu = retrieves[6]
    retriever_opendata_yongsan = retrieves[7]

    # 리트리버의 검색 매개변수를 설정 (검색 결과의 개수)
    retriever_naver_gangnam.search_kwargs = {"k": 50}
    retriever_naver_jongro.search_kwargs = {"k": 50}
    retriever_naver_Junggu.search_kwargs = {"k": 50}
    retriever_naver_yongsan.search_kwargs = {"k": 50}
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
        context_opendata: Annotated[List, "context_opendata"]  # 문서의 검색 결과
        answer: Annotated[str, "Answer"]  # 답변
        messages: Annotated[list, add_messages]  # 메시지(누적되는 list)
        webOrRetriever: Annotated[str, "webOrRetriever"]  # 웹 or 리트리버 검색
        ScheduleOrplace: Annotated[str, "ScheduleOrplace"]  # 일정 or 장소
        location: Annotated[str, "location"]  # 지역 리스트
        dayCheck: Annotated[str, "dayCheck"]  # 몇일 여행?

    ####-----프롬포트----------#####
    ##############################
    prompt = PromptTemplate(
        template="""
        당신은 사용자의 질문을 바탕으로 여행 일정을 생성하는 봇입니다. 
        너는 여러 장소들의 정보를 받게될거야.
        여러 장소들의 구분은 <content> </content> 태그로 구분되어있어.
        
        You are a multilingual assistant. 
        사용자가 {question}에서 사용한 언어와 같은 언어로 답변해줘

        -만약 사용자가 사용한 언어가 한국어라면 한국어로 답변 
        -만약 사용자가 사용한 언어가 영어라면 영어로 답변
        -만약 사용자가 사용한 언어가 일본어라면 일본어로 답변
        -만약 사용자가 사용한 언어가 중국어라면 중국어로 답변
        
        생성된 일정은 아침, 점심, 저녁으로 나누어 구성하며, 각 시간대에 **실제로 존재하는** 식당, 관광 명소, 거리 등을 추천해야 합니다.

        ### 장소 이름 표기 규칙
        - **장소 이름**: 반드시 "한국어 이름"을 먼저 쓰고, 괄호 안에 "사용자의 질문에서 사용한 언어 장소 이름"을 적어주세요.
        - 예시 (사용자의 질문에서 사용한 언어 → 한국어):
            - 영어 → 경복궁 (Gyeongbokgung Palace)
            - 일본어 → 경복궁 (景福宮)
            - 중국어 간체 → 경복궁 (景福宫)
            - 중국어 번체 → 경복궁 (景福宮)

        ### 주소 표기 규칙
        - **주소**: 주소 역시 같은 방식으로  "한국어 주소"(사용자의 질문에서 사용한 언어 주소)로 작성해 주세요.
        - 예시:
            - 영어 → 서울특별시 종로구 사직로 161 (161 Sajik-ro, Jongno-gu, Seoul) 
            - 일본어 → 서울특별시 종로구 사직로 161 (ソウル特別市 鍾路区 社稷路 161)
            - 중국어 간체 → 서울특별시 종로구 사직로 161 (首尔特别市 钟路区 社稷路 161)
            - 중국어 번체 → 서울특별시 종로구 사직로 161 (首爾特別市 鐘路區 社稷路 161)

        - 전체 문장 및 설명은 "사용자의 질문에서 사용한 언어"로 작성하되, 장소 이름 및 주소만 위 규칙을 지키세요.

    
        ### 여행 일정 생성 가이드라인

        1. **정확한 데이터 기반 추천**:
        - 제공된 데이터 또는 신뢰할 수 있는 출처(예: 공공 데이터, 지도 서비스)를 바탕으로 실제 존재하는 장소만 추천하세요.
        - 추천된 장소는 이름, 주소, 운영 시간, 특징 등 주요 정보를 반드시 포함해야 합니다.

        2. **반복 추천 방지**:
        - 각 일자에 추천된 장소는 다른 일자에 다시 추천하지 마.
        - 이미 방문한 장소를 제외하고, 새로운 장소를 추천해야 해.

        4. **핵심 정보 추출**:
        - 사용자의 질문에서 다음 정보를 추출하세요:
        - 여행 날짜 및 시간
        - 방문하고 싶은 지역
        - 요청한 활동(예: 관광, 식사, 쇼핑 등)

        5. **이동 동선 최소화**:
        - 일정에서의 경로는 효율적이어야 합니다.
        - 추천된 장소들이 서로 가까운 곳에 위치하도록 구성하세요.

        6. **사용자 맞춤 일정 생성**:
        - 사용자 요청에 따라 여행 일정을 맞춤화하세요. 예를 들어, 음식 취향이나 특정 활동 요청을 반영하세요.
        - 사용자가 특정 지역(예: 서울)을 언급하면, 강남구, 종로구, 용산구, 중구 등의 인기 있는 지역을 기준으로 일정을 생성하세요.

        7. **추천 장소 검증**:
        - 추천된 장소가 실제로 존재하는지 데이터로 검증하세요.
        - 운영 정보나 주소 등이 없는 장소는 제외하세요.

        ### 출력 형식
        답변은 명확하고 구조적인 형식으로 작성하세요. 각 시간대에 대해 장소 이름, 주소, 운영 시간, 특징 등을 포함해야 합니다.

        **예시 출력**:

        - **{day}일차**:

        - **아침**
          - **아침 식사 장소**: [음식점 이름]
            - **주소**: [음식점 주소]
            - **영업 시간**: [영업 시간]
            - **음식점 특징**: [음식점 특징]
            - **기타 정보**: [기타 정보]
          - **명소**: [명소 이름]
            - **명소 특징**: [명소 특징]
            - **명소 위치**: [명소 위치]
            - **영업 시간**: [영업 시간]
            - **기타 정보**: [기타 정보]

        - **점심**
          - **점심 식사 장소**: [음식점 이름]
            - **주소**: [음식점 주소]
            - **영업 시간**: [영업 시간]
            - **음식점 특징**: [음식점 특징]
            - **기타 정보**: [기타 정보]
          - **명소**: [명소 이름]
            - **명소 특징**: [명소 특징]
            - **명소 위치**: [명소 위치]
            - **영업 시간**: [영업 시간]
            - **기타 정보**: [기타 정보]
          - **카페**: [카페 이름]
            - **카페 주소**: [카페 주소]
            - **영업 시간**: [영업 시간]
            - **카페 정보**: [카페 정보]  
            - **카페 특징**: [카페 특징]  

        - **저녁**
          - **저녁 식사 장소**: [음식점 이름]
            - **주소**: [음식점 주소]
            - **영업 시간**: [영업 시간]
            - **음식점 특징**: [음식점 특징]
            - **기타 정보**: [기타 정보]
          - **명소**: [명소 이름]
            - **명소 특징**: [명소 특징]
            - **명소 위치**: [명소 위치]
            - **영업 시간**: [영업 시간]
            - **기타 정보**: [기타 정보] 
          - **숙소**: [숙소 이름]
            - **숙소 특징**: [숙소 특징]
            - **숙소 위치**: [숙소 위치]
            - **숙소 정보**: [숙소 정보] *숙소 정보 없으면 출력 하지 않기   
          - **쇼핑몰**: [쇼핑몰 이름]
            - **쇼핑몰 주소**: [쇼핑몰 주소]
            - **쇼핑몰 정보**: [쇼핑몰 정보]    

        ### 주의사항
        - 추천된 장소는 반드시 실제로 존재해야 합니다.
        - 비현실적이거나 가상의 장소는 추천하지 마세요.
        - 답변은 사용자가 쉽게 이해할 수 있도록 간결하게 작성하세요.
        - 장소의 신뢰성을 확인하기 위해 데이터 검증을 수행하세요.
        - 일차가 1 일차면 아침일정을 추천하지마. 일차가 1 이 아니면 아침 일정을 만들어줘.
        - {day}일차의 하루의 일정만 생성해줘.
        - 질문에 여러일차를 추천해 달라고 해도 '일차' 에있는 하루의 일정만 생성해
        - 일정을 만들고 마무리 멘트는 넣지마.
        - 추천했던 장소를 한번더 추천하지마.


        # 장소 정보: {context}

        # 사용자의 질문: {question}
        
        # 이전 대화 내용 {chat_history} 

        # 일차 : {day}
        """,
            input_variables=["context", "question","chat_history","day"],
        )

    # LLM

    # callback_manager = CallbackManager([NaturalTextStreamCallbackHandler()])

    model = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, 
                        streaming=True,
                        # callback_manager=callback_manager,
                        )

    chain = (

        prompt
        | model
        | StrOutputParser()
    )


    prompt_place_search = PromptTemplate(
        template="""
        너는 여러 장소들의 정보를 받게될거야.
        여러 장소들의 구분은 <content> </content> 태그로 구분 되어 있어.
        너는 입력받은 장소 정보를 정리하여 사용자의 질문에 맞는 정보를 출력해 주는 봇이야.
        장소의 정보를 잘 요약해서 출력해줘.
        장소를 출력할때 각 장소의 어떤 점이 좋은지도 간단하게 요약해서 알려줘.

    

        # 장소 정보: {context}

        #사용자의 질문: {question}
        
        #이전 대화 내용 {chat_history} 
        """,
            input_variables=["context", "question","chat_history"],
        )

    # LLM
    model_place_search = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=True)

    chain_place_search = (
        # {
        #     "question": itemgetter("question"),
        #     # "context_web": itemgetter("context_web"),
        #     "context": itemgetter("context"),
        #     "chat_history": itemgetter("chat_history"),
        # }
        prompt_place_search
        | model_place_search
        | StrOutputParser()
    )

    prompt_day = PromptTemplate(
        template="""

        너는 사용자의 질문을 보고 의도를 파악해서 사용자가 몇일의 여행을 가는지 알아내야돼.
        몇일을 가는지 알게되면 그 결과를 숫자로 반환해.
        

        # Examples 1

        **Input**: "용산구에 1박2일 방문 할 예정이야. 일정을 생성 해줄 수 있어?"

        **answer**: 2


        # Examples 2

        **Input**: "서울시에 5박6일 방문 할 예정이야. 일정을 생성 해줄 수 있어?"

        **answer**: 6


        # Examples 3

        **Input**: "종로구에 여행을 가려고해 9일동안 머물건데 일정을 만들어줘"

        **answer**: 9
        


        #사용자의 질문: {question}

        """,
            input_variables=["question"],
        )

    model_day = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_day = (
        {
            "question": itemgetter("question"),
        }
        | prompt_day
        | model_day
        | StrOutputParser()
    )


    prompt_keyword = PromptTemplate(
        template="""
            사용자의 질문에서 중요 키워드를 추출하는 작업을 수행하세요.

            # Steps

            1. **질문 분석**: 사용자가 입력한 질문을 주의 깊게 읽고 분석합니다.
            2. **중요 키워드 식별**: 질문의 핵심 내용을 파악하고, 문장에서 중요한 의미를 지닌 단어, 구문, 또는 개념을 식별합니다.
            3. **키워드 추출**: 식별한 중요한 요소들을 키워드로 추출합니다.

            # Output Format

            - 추출된 중요 키워드를 콤마(,)로 구분한 리스트로 제공합니다.

            # Examples

            **Input**: "자동차 산업의 현재 트렌드와 미래 전망은 무엇인가요?"

            **Keywords**: "자동차 산업, 현재 트렌드, 미래 전망"

            **Input**: "Python을 사용한 머신러닝 알고리즘 구현 방법은?"

            #사용자의 질문 : {question}
        """,
            input_variables=["question"],
        )

    model_keyword = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_keyword = (
        {
            "question": itemgetter("question"),
        }
        | prompt_keyword
        | model_keyword
        | StrOutputParser()
    )

    prompt_location = PromptTemplate(
        template="""너는 질문에 대해서 **Python의 list**를 반환해야 돼.
        list에 들어갈 수 있는 str은 ['용산구', '강남구', '중구', '종로구'] 네 가지 중 일부야.

        아래 **지역 판별 규칙**에 따라, 사용자의 질문에서 해당 지역을 **최대한** 찾아서 list에 넣어줘.
        만약 '서울'에 해당하는 표현(예: 'Seoul', 'ソウル', '首尔', '首爾')이 있으면, ['용산구','강남구','중구','종로구'] 전부 넣어줘.

        - **용산구**:
        - 한국어: "용산구"
        - 영어: "Yongsan", "Yongsan-gu"
        - 일본어: "龍山", "ヨンサン"
        - 중국어: "龙山", 등

        - **강남구**:
        - 한국어: "강남구"
        - 영어: "Gangnam", "Gangnam-gu"
        - 일본어: "カンナム"
        - 중국어: "江南", 등

        - **중구**:
        - 한국어: "중구"
        - 영어: "Junggu", "Jung-gu"
        - 일본어: "チュング"
        - 중국어: "中区", 등

        - **종로구**:
        - 한국어: "종로구"
        - 영어: "Jongno", "Jong-ro"
        - 일본어: "ジョンノ"
        - 중국어: "鐘路区", 등

        - **서울**:
        - 한국어: "서울"
        - 영어: "Seoul"
        - 일본어: "ソウル"
        - 중국어: "首尔", "首爾"
        => '서울' 관련 표현이면 list에 ['용산구','강남구','중구','종로구'] 전부 넣기

        위 규칙에 없는 지역(예: 부산, 전라남도, Myeongdong 등)은 무시하고 list에 넣지 말아줘.
        만약 전혀 일치하는 구나 "서울"이 없다면 빈 list를 반환해.

        출력 예시:
        - "I want to go to Yongsan" → ["용산구"]
        - "ソウル特別市を旅行したい" → ["용산구","강남구","중구","종로구"]
        - "I want to visit Gangnam and Myeongdong" → ["강남구"]  # (명동은 중구이지만, 직접 '중구'나 'Myeong-dong' 매핑을 안 넣었다면 생략)

        주의: 최종 출력은 **파이썬 리스트** 형태로, 따옴표(쿼트)와 쉼표(콤마)를 정확히 써서 예) ["용산구","종로구"] 처럼 출력해.

        #사용자의 질문:{question}
        """,
            input_variables=["question"],
        )

    model_location = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_location = (
        {
            "question": itemgetter("question"),
        }
        | prompt_location
        | model_location
        | StrOutputParser()
    )


    prompt_sch_or_placeSearch = PromptTemplate(
        template="""너는 질문에 대해서 두가지의 옵션으로 대답하는 봇이야.
        너의 대답은 '일정', '장소검색' 두가지로만 대답할 수 있어.
        사용자가 질문을 하면 문맥을 잘 살펴서 사용자가 여행일정을 만들어 달라고 하면 '일정' 이라고 대답해야돼.
        그렇지 않으면 '장소검색' 를 출력해줘.

        #'일정' 출력 예시 : 1. 나는 서울시의 용산구를 방문 할거야 여행 계획을 세워 줄수 있어?, 2. 나는 종로구와 중구 일대를 방문하고 싶어 을지로는 꼭 가보고 싶은데 을지로 계획을 포함해서 여행 일정을 만들어 줄 수 있어?

        #대답 형식 : '일정' or '장소검색'

        #사용자의 질문: {question}
        

        """,
            input_variables=["question"],
        )

    model_sch_or_placeSearch = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_sch_or_placeSearch = (
        {
            "question": itemgetter("question"),
        }
        | prompt_sch_or_placeSearch
        | model_sch_or_placeSearch
        | StrOutputParser()
    )



    prompt_Web_or_retriever = PromptTemplate(
        template=""" 너는 사용자의 질문에 대해서 두가지의 옵션으로 대답하는 봇이야.
        너의 대답은 'web', 'retriever' 두가지로만 대답할 수 있어.
        사용자가 질문을 하면 문맥을 잘 살펴서 웹에서 정보를 검색하기를 원하면 'web' 이라고 대답해야돼.
        그렇지 않으면 'retriever' 를 출력해줘. 

        #대답 형식 : 'web' or 'retriever'

        #사용자의 질문: {question}
        

        """,
            input_variables=["question"],
        )
    model_web_check = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_Web_or_retriever = (
        {
            "question": itemgetter("question"),
        }
        | prompt_Web_or_retriever
        | model_web_check
        | StrOutputParser()
    )

    ####-----프롬포트 끝----------#####
    ##############################


    ####-----노드 함수--------#####
    ##############################



    # from rag.utils import format_docs
    # 웹 검색 or 리트리버 검색
    def Schedule_day_check(state: GraphState) -> GraphState:
        
        response = chain_day.invoke(
            {"question": state["question"][-1].content}
        )

        return {"dayCheck": response}

    def web_or_retriever_check(state: GraphState) -> GraphState:
        
        response = chain_Web_or_retriever.invoke(
            {"question": state["question"][-1].content}
        )

        return {"webOrRetriever": response}

    # 웹 리트리버 분기 체크하는 함수(router)
    def is_web(state: GraphState) -> GraphState:
        if state["webOrRetriever"] == "web":
            return "web"
        else:
            return "retriever"

    # 장소검색 or 일정 검색
    def Schedule_or_place_check(state: GraphState) -> GraphState:
        # 관련성 체크를 실행("yes" or "no")
        response = chain_sch_or_placeSearch.invoke(
            {"question": state["question"][-1].content}
        )

        return {"ScheduleOrplace": response}


    # 일정 장소검색 리트리버 분기 체크하는 함수(router)
    def is_place(state: GraphState) -> GraphState:
        if state["ScheduleOrplace"] == "일정":
            return "일정"
        else:
            return "장소검색"
        
    # 지역 판별
    def location_check(state: GraphState) -> GraphState:
        # 관련성 체크를 실행("yes" or "no")
        response = chain_location.invoke(
            {"question": state["question"][-1].content}
        )

        return {"location": response}

        
    # 문서 검색 노드--------------------------------------------------------------------------------------------------------------------------
    def retrieve_document_naver(state: GraphState) -> GraphState:
        # 질문을 상태에서 가져옵니다.
        latest_question = state["question"][-1].content
        location_str = state['location']

        location = ast.literal_eval(location_str)

        # 문서에서 검색하여 관련성 있는 문서를 찾습니다.
        yongsan = '용산구'
        jonglo = '종로구'
        gangman = '강남구'
        junggu = '중구'
        retrieved_docs_yongsan = []
        retrieved_docs_jongro = []
        retrieved_docs_gangman = []
        retrieved_docs_junggu = []

        # if yongsan in location:
        #     retrieved_docs_yongsan = retriever_naver_yongsan.invoke(latest_question)
        #     retrieved_docs_yongsan = "\n".join(
        #     [
        #         f"<content>{doc.page_content}</content>"
        #         for doc in retrieved_docs_yongsan
        #     ]
        #     )

        # if jonglo in location:
        #     retrieved_docs_jongro = retriever_naver_jongro.invoke(latest_question)
        #     retrieved_docs_jongro = "\n".join(
        #     [
        #         f"<content>{doc.page_content}</content>"
        #         for doc in retrieved_docs_jongro
        #     ]
        #     )

        # if gangman in location:
        #     retrieved_docs_gangman = retriever_naver_gangnam.invoke(latest_question)
        #     retrieved_docs_gangman = "\n".join(
        #     [
        #         f"<content>{doc.page_content}</content>"
        #         for doc in retrieved_docs_gangman
        #     ]
        #     )

        # if junggu in location:
        #     retrieved_docs_junggu = retriever_naver_Junggu.invoke(latest_question)
        #     retrieved_docs_junggu = "\n".join(
        #     [
        #         f"<content>{doc.page_content}</content>"
        #         for doc in retrieved_docs_junggu
        #     ]
        #     )
        if yongsan in location:
            retrieved_docs_yongsan = retriever_naver_yongsan.invoke(latest_question)


        if jonglo in location:
            retrieved_docs_jongro = retriever_naver_jongro.invoke(latest_question)


        if gangman in location:
            retrieved_docs_gangman = retriever_naver_gangnam.invoke(latest_question)


        if junggu in location:
            retrieved_docs_junggu = retriever_naver_Junggu.invoke(latest_question)


        # 검색된 문서를 형식화합니다.(프롬프트 입력으로 넣어주기 위함)

            # 검색된 문서를 context 키에 저장합니다.
        # return {"context_naver_gangnam": retrieved_docs_gangman,
        #         "context_naver_jongro": retrieved_docs_jongro,
        #         "context_naver_Junggu": retrieved_docs_junggu,
        #         "context_naver_yongsan": retrieved_docs_yongsan}
        return {"context_naver_gangnam": retrieved_docs_gangman,
                "context_naver_jongro": retrieved_docs_jongro,
                "context_naver_Junggu": retrieved_docs_junggu,
                "context_naver_yongsan": retrieved_docs_yongsan}

    #------------------------------------------------------------------------------------------------------------------------------------------------


    def retrieve_document_opendata(state: GraphState) -> GraphState:
        # 질문을 상태에서 가져옵니다.
        latest_question = state["question"][-1].content
        location_str = state['location']

        location = ast.literal_eval(location_str)

        doc_list = []
        # 문서에서 검색하여 관련성 있는 문서를 찾습니다.
        yongsan = '용산구'
        jonglo = '종로구'
        gangman = '강남구'
        junggu = '중구'
        retrieved_docs_yongsan = []
        retrieved_docs_jongro = []
        retrieved_docs_gangman = []
        retrieved_docs_junggu = []

        if yongsan in location:
            retrieved_docs_yongsan = retriever_opendata_yongsan.invoke(latest_question)

        if jonglo in location:
            retrieved_docs_jongro = retriever_opendata_jongro.invoke(latest_question)

        if gangman in location:
            retrieved_docs_gangman = retriever_opendata_gangnam.invoke(latest_question)

        if junggu in location:
            retrieved_docs_junggu = retriever_opendata_junggu.invoke(latest_question)

    
        doc_list.extend(retrieved_docs_yongsan)
        doc_list.extend(retrieved_docs_jongro)
        doc_list.extend(retrieved_docs_gangman)
        doc_list.extend(retrieved_docs_junggu)

    #     # 검색된 문서를 형식화합니다.(프롬프트 입력으로 넣어주기 위함)
    #     retrieved_docs = "\n".join(
    #         [
    #             f"<document><content>{doc.page_content}</content>"
    #             for doc in doc_list
    #         ]
    # )

    #     # 검색된 문서를 context 키에 저장합니다.
    #     return {"context_opendata": retrieved_docs}
        # 검색된 문서를 context 키에 저장합니다.
        return {"context_opendata": doc_list}




    # 일정 생성 노드----------------------------------------------------------------------------

    def llm_Schedule_answer(state: GraphState) -> GraphState:
        # 질문을 상태에서 가져옵니다.
        latest_question = state["question"][-1].content
        location_str = state['location']
        day_str = state['dayCheck']

        location = ast.literal_eval(location_str)
        day = ast.literal_eval(day_str)

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

        for i in range(1, day+1):
            if yongsan in location:
                place_yongsan = state["context_naver_yongsan"]

                place_list.extend(random.sample(place_yongsan, 4))

            if jongro in location:
                place_jongro = state["context_naver_jongro"]
                place_list.extend(random.sample(place_jongro, 4))

            if gangman in location:
                place_gangman = state["context_naver_gangnam"]
                place_list.extend(random.sample(place_gangman, 4))

            if junggu in location:
                place_junggu = state["context_naver_Junggu"]

                place_list.extend(random.sample(place_junggu, 4))

        
            place_opendata = state["context_opendata"]
            
            place_list.extend(random.sample(place_opendata, 5))

            #검색된 문서를 형식화합니다.(프롬프트 입력으로 넣어주기 위함)
            place_list_text = "\n".join(
            [
                f"<content>{doc.page_content}</content>"
                for doc in place_list
            ]
            )

            # 체인을 호출하여 답변을 생성합니다.
            response = chain.invoke(
                {
                    "question": latest_question,
                    "context": place_list_text,
                    "chat_history": messages_to_history(state["messages"]),
                    "day" : i
                }
            )
            place_list.clear()
            print('\n')

        # 생성된 답변, (유저의 질문, 답변) 메시지를 상태에 저장합니다.
        print(state["messages"])
        return {
            "answer": response,
            "messages": [("user", latest_question), ("assistant", response)],
        }
    # 일정 생성 노드 끝----------------------------------------------------------------------------

    # 장소 검색 노드 ----------------------------------------------------------------------------

    def llm_place_answer(state: GraphState) -> GraphState:
        # 질문을 상태에서 가져옵니다.
        latest_question = state["question"][-1].content
        location_str = state['location']

        location = ast.literal_eval(location_str)

        place_list = []
        place_yongsan =[]
        place_jongro =[]
        place_gangman =[]
        place_junggu =[]
        # 문서에서 검색하여 관련성 있는 문서를 찾습니다.
        yongsan = '용산구'
        jonglo = '종로구'
        gangman = '강남구'
        junggu = '중구'

        if yongsan in location:
            place_yongsan = state["context_naver_yongsan"]
            place_yongsan = place_yongsan[:5]
            place_list.extend(place_yongsan)

        if jonglo in location:
            place_jongro = state["context_naver_jongro"]
            place_jongro = place_jongro[:5]
            place_list.extend(place_jongro)

        if gangman in location:
            place_gangman = state["context_naver_gangnam"]
            place_gangman = place_gangman[:5]
            place_list.extend(place_gangman)

        if junggu in location:
            place_junggu = state["context_naver_Junggu"]
            place_junggu = place_junggu[:5]
            place_list.extend(place_junggu)

    
        place_opendata = state["context_opendata"]
        place_opendata = place_opendata[:7]

        place_list.extend(place_opendata)

        place_list_text = "\n".join(
        [
            f"<content>{doc.page_content}</content>"
            for doc in place_list
        ]
        )

        # 체인을 호출하여 답변을 생성합니다.
        response = chain_place_search.invoke(
            {
                "question": latest_question,
                "context": place_list_text,
                "chat_history": messages_to_history(state["messages"]),
            }
        )
        # 생성된 답변, (유저의 질문, 답변) 메시지를 상태에 저장합니다.
        print(state["messages"])
        return {
            "answer": response,
            "messages": [("user", latest_question), ("assistant", response)],
        }

    # 장소 검색 노드  끝----------------------------------------------------------------------------



    # 그래프 생성
    workflow = StateGraph(GraphState)

    # 노드 정의
    workflow.add_node("location_check", location_check)
    workflow.add_node("Schedule_day_check", Schedule_day_check)
    workflow.add_node("retrieve_document_naver", retrieve_document_naver)
    workflow.add_node("retrieve_opendata", retrieve_document_opendata)
    # workflow.add_node("llm_Summary_opendata", llm_Summary_opendata)
    # workflow.add_node("llm_Summary_naver", llm_Summary_naver)
    workflow.add_node("llm_Schedule_answer", llm_Schedule_answer)
    workflow.add_node("Schedule_or_place_check", Schedule_or_place_check)
    workflow.add_node("llm_place_answer", llm_place_answer)


    # 엣지 정의
    # workflow.add_conditional_edges(
    #     "web_Or_Retriever",  # 관련성 체크 노드에서 나온 결과를 is_relevant 함수에 전달합니다.
    #     is_web,
    #     {
    #         "web": "web_search",  # 웹 검색을 요청하면 웹검색을 합니다
    #         "retriever": "query_rewrite",  # 아니면 리트리버
    #     },
    # )
    # 엣지 정의
    workflow.add_conditional_edges(
        "Schedule_or_place_check",  
        is_place,
        {
            "일정": "Schedule_day_check",  #일정
            "장소검색": "llm_place_answer",  # 장소검색
        },
    )

    workflow.add_edge("location_check", "retrieve_document_naver")  # 검색 -> 답변
    workflow.add_edge("location_check", "retrieve_opendata")  # 검색 -> 답변
    # workflow.add_edge("retrieve_document_naver", "llm_Summary_naver")  # 질문 -> 검색
    # workflow.add_edge("retrieve_opendata", "llm_Summary_opendata")  # 질문 -> 검색
    workflow.add_edge("retrieve_document_naver", "Schedule_or_place_check") 
    workflow.add_edge("retrieve_opendata", "Schedule_or_place_check") 
    workflow.add_edge("Schedule_day_check", "llm_Schedule_answer") 

    workflow.add_edge("llm_Schedule_answer", END)  # 답변 -> 종료
    workflow.add_edge("llm_place_answer", END)  # 답변 -> 종료

    # 그래프 진입점 설정
    workflow.set_entry_point("location_check")
    # workflow.set_entry_point("Schedule_or_place_check")

    # 체크포인터 설정
    memory = MemorySaver()

    # 컴파일
    app = workflow.compile(checkpointer=memory)


    # config 설정(재귀 최대 횟수, thread_id)
    config = RunnableConfig(recursion_limit=20, configurable={"thread_id": random_uuid()})

    # 질문 입력
    inputs = GraphState(question=question)

    ans=app.stream(input=inputs, config=config, stream_mode='messages')


    return ans


if __name__ == "__main__":
    # run_gpt_api 호출 및 결과 출력
    result = run_gpt_api("중구의 숭례도담도담이라는 음식점의 정보를 알려줘")

    for chunk, meta in result:

        if meta.get('langgraph_node') == 'llm_Schedule_answer':

            print(chunk.content, end='')


    # for chunk, meta in result:

    #     if meta.get('langgraph_node') == 'llm_place_answer':

    #         print(chunk.content, end='')
    
    # print("Result:", result)

