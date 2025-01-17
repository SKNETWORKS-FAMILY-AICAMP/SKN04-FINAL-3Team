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



# GPT API 호출을 처리하는 함수
def run_gpt_api(question):
    # OpenAI 임베딩 객체 초기화
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
    retriever_naver_gangnam.search_kwargs = {"k": 8}
    retriever_naver_jongro.search_kwargs = {"k": 8}
    retriever_naver_Junggu.search_kwargs = {"k": 8}
    retriever_naver_yongsan.search_kwargs = {"k": 8}
    retriever_opendata_gangnam.search_kwargs = {"k": 10}
    retriever_opendata_jongro.search_kwargs = {"k": 10}
    retriever_opendata_junggu.search_kwargs = {"k": 10}
    retriever_opendata_yongsan.search_kwargs = {"k": 10}

    # GraphState 클래스 정의 (데이터 상태 저장)
    class GraphState(TypedDict):
        question: Annotated[List[str], add_messages]  # 사용자의 질문
        context_naver_gangnam: Annotated[str, "context_naver_gangnam"]  # 강남구 관련 문서 검색 결과
        context_naver_jongro: Annotated[str, "context_naver_jongro"]  # 종로구 관련 문서 검색 결과
        context_naver_Junggu: Annotated[str, "context_naver_Junggu"]  # 중구 관련 문서 검색 결과
        context_naver_yongsan: Annotated[str, "context_naver_yongsan"]  # 용산구 관련 문서 검색 결과
        context_opendata: Annotated[str, "context_opendata"]  # 공공 데이터 검색 결과
        context_web: Annotated[str, "context_web"]  # 웹 검색 결과
        answer_llm_Summary_gangnam: Annotated[str, "answer_llm_Summary_gangnam"]  # 요약된 강남구 문서
        answer_llm_Summary_junggu: Annotated[str, "answer_llm_Summary_junggu"]  # 요약된 중구 문서
        answer_llm_Summary_jongro: Annotated[str, "answer_llm_Summary_jongro"]  # 요약된 종로구 문서
        answer_llm_Summary_yongsan: Annotated[str, "answer_llm_Summary_yongsan"]  # 요약된 용산구 문서
        answer_llm_Summary_opendata: Annotated[str, "answer_llm_Summary_opendata"]  # 요약된 공공 데이터
        answer: Annotated[str, "Answer"]  # 최종 답변
        messages: Annotated[list, add_messages]  # 대화 메시지 기록
        webOrRetriever: Annotated[str, "webOrRetriever"]  # 웹 또는 리트리버 선택
        ScheduleOrplace: Annotated[str, "ScheduleOrplace"]  # 일정 또는 장소 선택
        location: Annotated[str, "location"]  # 사용자 질문에 포함된 지역 정보

    #프롬포트
    ##########################################################################################################
    # Query Rewrite 프롬프트 정의
    prompt = PromptTemplate(
        template="""
        당신은 사용자의 질문을 바탕으로 여행 일정을 생성하는 봇입니다. 
        너는 여러 장소들의 정보를 받게될거야.
        여러 장소들의 구분은 <content> <content> 태그로 구분되어있어.
        
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

        **출력 형식**:
        답변은 명확하고 구조적인 형식으로 작성하세요. 각 시간대에 대해 장소 이름, 주소, 운영 시간, 특징 등을 포함해야 합니다.

        **예시 출력**:

        ### 1일차

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

        ### 2일차

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
            - **쇼핑몰 특징**: [쇼핑몰 특징]    
            

        # 장소 정보: {context}

        # 사용자의 질문: {question}
        
        # 이전 대화 내용 {chat_history} 
        """,
            input_variables=["context", "question", "chat_history"],
        )

    # LLM
    model = ChatOpenAI(model_name="gpt-4o",
                        temperature=0, streaming=True)

    chain = (
        {
            "question": itemgetter("question"),
            # "context_web": itemgetter("context_web"),
            "context": itemgetter("context"),
            "chat_history": itemgetter("chat_history"),
        }
        | prompt
        | model
        | StrOutputParser()
    )

    prompt_place_search = PromptTemplate(
        template="""
        너는 여러 장소들의 정보를 받게될거야.
        여러 장소들의 구분은 <content> <content> 태그로 구분되어있어.
        너는 입력받은 장소 정보를 정리하여 사용자의 질문에 맞는 정보를 출력해 주는 봇이야.
        장소의 정보를 잘 요약해서 출력해줘.
        장소를 출력할때 각 장소의 어떤 점이 좋은지도 간단하게 요약해서 알려줘.




        # 장소 정보: {context}

        #사용자의 질문: {question}
        
        #이전 대화 내용 {chat_history} 
        """,
            input_variables=["context", "question"],
        )

    # LLM
    model_place_search = ChatOpenAI(model_name="gpt-4o",
                        temperature=0, streaming=True)

    chain_place_search = (
        {
            "question": itemgetter("question"),
            # "context_web": itemgetter("context_web"),
            "context": itemgetter("context"),
            "chat_history": itemgetter("chat_history"),
        }
        | prompt_place_search
        | model_place_search
        | StrOutputParser()
    )

    prompt_opendata_Summary = PromptTemplate(
        template="""
        너는 입력받은 내용을 요약해주는 봇이야.
        입력 받는 내용은 특정 장소의 특징을 알려주는 내용이야.
        너는 여러 장소들의 정보를 받게될거야.
        여러 장소들의 구분은 <content> <content> 태그로 구분되어있어.

        요약은 다음과 같이 해줬으면 좋겠어.

        아래 항목에서 없는 데이터는 빼도 돼.

        - 장소 이름:
        - 위치 :
        - 전화번호 :
        - 웹사이트 URL :
        - 운영 날짜 및 시간:
        - 교통정보
        - 기타 편의 여부 :
        - 지원언어 :

        # 요약 해야할 내용: {answer_llm_Summary}


        """,
            input_variables=["answer_llm_Summary"],
        )


    # LLM
    model_summary = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=True)

    chain_Summary_opendata = (
        # {
        #     "answer_llm_Summary": itemgetter("answer_llm_Summary_opendata")
        # }
        prompt_opendata_Summary
        | model_summary
        | StrOutputParser()
    )


    prompt_naver_Summary = PromptTemplate(
        template="""
        너는 입력받은 내용을 요약해주는 봇이야.
        입력 받는 내용은 특정 장소의 특징을 알려주는 내용이야.
        너는 여러 장소들의 정보를 받게될거야.
        여러 장소들의 구분은 <content> <content> 태그로 구분되어있어.

        요약은 다음과 같이 해줬으면 좋겠어

        - "store_name": 
        - "category":  
        - "rating":  
        - "directions_text": 
        - "store_id": 
        - "address": 
        - "phone_num": 
        - "business_hours": 
        - "info": 
        - "convenience_facilities_and_services": 
        - "Parking": 
        - "sns": 
        - "store의 좋은점": 
        - "menu": 



        # 요약 해야할 내용: {answer_llm_Summary}


        """,
            input_variables=["answer_llm_Summary"],
        )


    # LLM
    model_summary = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=True)

    chain_Summary_gangnam = (
        # {
        #     "answer_llm_Summary": itemgetter("answer_llm_Summary_gangnam")
        # }
        prompt_naver_Summary
        | model_summary
        | StrOutputParser()
    )
    chain_Summary_Junggu = (
        # {
        #     "answer_llm_Summary": itemgetter("answer_llm_Summary_junggu")
        # }
        prompt_naver_Summary
        | model_summary
        | StrOutputParser()
    )
    chain_Summary_jongro = (
        # {
        #     "answer_llm_Summary": itemgetter("answer_llm_Summary_jongro")
        # }
        prompt_naver_Summary
        | model_summary
        | StrOutputParser()
    )
    chain_Summary_yongsan = (
        # {
        #     "answer_llm_Summary": itemgetter("answer_llm_Summary_yongsan")
        # }
        prompt_naver_Summary
        | model_summary
        | StrOutputParser()
    )


    prompt_location = PromptTemplate(
        template="""
        너는 질문에 대해서 **Python의 list**를 반환해야 돼.
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
                        temperature=0, streaming=True)

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
                        temperature=0, streaming=True)

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
                        temperature=0, streaming=True)

    chain_Web_or_retriever = (
        {
            "question": itemgetter("question"),
        }
        | prompt_Web_or_retriever
        | model_web_check
        | StrOutputParser()
    )

    prompt_web = PromptTemplate(
        template="""너는 웹 검색을 통한 {context_web}의 내용를 종합해서 서울시의 중구,종로구,용산구,강남구 관광 일정을 추천해주는 봇이야.
        사용자의 질문에 따라서 여러가지 서울의 관광지, 식당, 숙소, 쇼핑몰 등을 추천해야해.
        처음에 사용자가 서울에 며칠동안 머무르는지 물어보고, 그에 따라서 관광 일정을 추천해주면 돼.
        그 다음 사용자가 서울에 오는 이유에 대해 파악하고 그에 맞는 여행 일정을 추천해주면 돼.
        대화하다가 추천한 여행 일정이 사용자의 마음에 들지 않아서 변경해달라고 하면 마음에 들지 않은 부분을
        캐치하고 그 부분들만 수정해서 다시 추천해주면 돼.
        일정 중간 중간 숙소나 식당, 쇼핑몰 등을 추천해주면 돼.

        어떤 장소가 궁금해서 물어본다면 특정 장소의 정보들을 정확하게 알려줘.
        (예:가게 정보, 메뉴, 별점, 위치, 연락처, 운영 시간, 리뷰 등)
        여행 일정에 대한 동선이 짧도록 추천해줘.
        언어는 사용자가 입력한 언어를 기준으로 알려줘. 
        화폐 기준도 사용자가 입력한 언어를 사용하는 국가의 화폐를 기준으로 적용해줘.

        *유의사항
        - 너 마음대로 식당을 만들지 말고 반드시 존재하는 식당을 추천해야 해


        - 너가 제공한 내용의 출처를 링크로 남겨줘

        # 웹 검색 정보 : {context_web}

        #사용자의 질문: {question}
        
        #이전 대화 내용 {chat_history} 
        """,
            input_variables=["context_web", "question"],
        )
    #input_variables=["context_web","context_opendata","context_naver", "question"],
    # LLM
    model_web = ChatOpenAI(model_name="gpt-4o",
                        temperature=0, streaming=True)

    chain_web = (
        {
            "question": itemgetter("question"),
            "context_web": itemgetter("context_web"),
            # "context_opendata": itemgetter("context_opendata"),
            # "context_naver": itemgetter("context_naver"),
            "chat_history": itemgetter("chat_history"),
        }
        | prompt_web
        | model_web
        | StrOutputParser()
    )

    # 웹 검색 or 리트리버 검색
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

        if yongsan in location:
            retrieved_docs_yongsan = retriever_naver_yongsan.invoke(latest_question)
            retrieved_docs_yongsan = "\n".join(
            [
                f"<document><content>{doc.page_content}</content>"
                for doc in retrieved_docs_yongsan
            ]
            )

        if jonglo in location:
            retrieved_docs_jongro = retriever_naver_jongro.invoke(latest_question)
            retrieved_docs_jongro = "\n".join(
            [
                f"<document><content>{doc.page_content}</content>"
                for doc in retrieved_docs_jongro
            ]
            )

        if gangman in location:
            retrieved_docs_gangman = retriever_naver_gangnam.invoke(latest_question)
            retrieved_docs_gangman = "\n".join(
            [
                f"<document><content>{doc.page_content}</content>"
                for doc in retrieved_docs_gangman
            ]
            )

        if junggu in location:
            retrieved_docs_junggu = retriever_naver_Junggu.invoke(latest_question)
            retrieved_docs_junggu = "\n".join(
            [
                f"<document><content>{doc.page_content}</content>"
                for doc in retrieved_docs_junggu
            ]
            )

        # 검색된 문서를 형식화합니다.(프롬프트 입력으로 넣어주기 위함)

            # 검색된 문서를 context 키에 저장합니다.
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

        # 검색된 문서를 형식화합니다.(프롬프트 입력으로 넣어주기 위함)
        retrieved_docs = "\n".join(
            [
                f"<document><content>{doc.page_content}</content>"
                for doc in doc_list
            ]
    )

        # 검색된 문서를 context 키에 저장합니다.
        return {"context_opendata": retrieved_docs}

    # 요약 생성 노드----------------------------------------------------------------------------
    def llm_Summary_naver(state: GraphState) -> GraphState:
        location_str = state['location']

        location = ast.literal_eval(location_str)

        yongsan = '용산구'
        jonglo = '종로구'
        gangman = '강남구'
        junggu = '중구'
        response_yongsan ='none'
        response_jongro ='none'
        response_junggu ='none'
        response_gangnam ='none'

        if yongsan in location:
            context_naver_yongsan = state["context_naver_yongsan"]

            # 체인을 호출하여 답변을 생성합니다.
            response_yongsan = chain_Summary_yongsan.invoke(
                {
                    "answer_llm_Summary": context_naver_yongsan,
                }
            )
        # 생
        if jonglo in location:
            context_naver_jongro = state["context_naver_jongro"]

            # 체인을 호출하여 답변을 생성합니다.
            response_jongro = chain_Summary_jongro.invoke(
                {
                    "answer_llm_Summary": context_naver_jongro,
                }
            )
        if gangman in location:
            context_naver_gangnam = state["context_naver_gangnam"]

            # 체인을 호출하여 답변을 생성합니다.
            response_gangnam = chain_Summary_gangnam.invoke(
                {
                    "answer_llm_Summary": context_naver_gangnam,
                }
            )
        if junggu in location:
            context_naver_Junggu = state["context_naver_Junggu"]

            # 체인을 호출하여 답변을 생성합니다.
            response_junggu = chain_Summary_Junggu.invoke(
                {
                    "answer_llm_Summary": context_naver_Junggu,
                }
            )
        
        # 생성된 답변, (유저의 질문, 답변) 메시지를 상태에 저장합니다.
        return {
            "answer_llm_Summary_gangnam": response_gangnam,
            "answer_llm_Summary_jongro": response_jongro,
            "answer_llm_Summary_junggu": response_junggu,
            "answer_llm_Summary_yongsan": response_yongsan
        } 


    def llm_Summary_opendata(state: GraphState) -> GraphState:

        # 검색된 문서를 상태에서 가져옵니다.
        context_opendata = state["context_opendata"]

        # 체인을 호출하여 답변을 생성합니다.
        response = chain_Summary_opendata.invoke(
            {
                "answer_llm_Summary": context_opendata,
            }
        )
        # 생성된 답변, (유저의 질문, 답변) 메시지를 상태에 저장합니다.
        return {
            "answer_llm_Summary_opendata": response
        } 


    # 요약 생성 노드 끝----------------------------------------------------------------------------



    # 일정 생성 노드----------------------------------------------------------------------------

    def llm_Schedule_answer(state: GraphState) -> GraphState:
        # 질문을 상태에서 가져옵니다.
        latest_question = state["question"][-1].content
        location_str = state['location']

        location = ast.literal_eval(location_str)

        Summary_list = []
        Summary_yongsan =[]
        Summary_jongro =[]
        Summary_gangman =[]
        Summary_junggu =[]
        # 문서에서 검색하여 관련성 있는 문서를 찾습니다.
        yongsan = '용산구'
        jonglo = '종로구'
        gangman = '강남구'
        junggu = '중구'

        if yongsan in location:
            Summary_yongsan = state["answer_llm_Summary_yongsan"]

        if jonglo in location:
            Summary_jongro = state["answer_llm_Summary_jongro"]

        if gangman in location:
            Summary_gangman = state["answer_llm_Summary_gangnam"]

        if junggu in location:
            Summary_junggu = state["answer_llm_Summary_junggu"]

    
        Summary_opendata = state["answer_llm_Summary_opendata"]

    
        Summary_list.extend(Summary_yongsan)
        Summary_list.extend(Summary_jongro)
        Summary_list.extend(Summary_gangman)
        Summary_list.extend(Summary_junggu)
        Summary_list.extend(Summary_opendata)

        # 검색된 문서를 형식화합니다.(프롬프트 입력으로 넣어주기 위함)
        retrieved_docs = "\n".join(
            [
                f"{doc}"
                for doc in Summary_list
            ]
        )

        # 체인을 호출하여 답변을 생성합니다.
        response = chain.invoke(
            {
                "question": latest_question,
                "context": retrieved_docs,
                "chat_history": messages_to_history(state["messages"]),
            }
        )
        # 생성된 답변, (유저의 질문, 답변) 메시지를 상태에 저장합니다.
        # print(state["messages"])
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

        Summary_list = []
        Summary_yongsan =[]
        Summary_jongro =[]
        Summary_gangman =[]
        Summary_junggu =[]
        # 문서에서 검색하여 관련성 있는 문서를 찾습니다.
        yongsan = '용산구'
        jonglo = '종로구'
        gangman = '강남구'
        junggu = '중구'

        if yongsan in location:
            Summary_yongsan = state["answer_llm_Summary_yongsan"]

        if jonglo in location:
            Summary_jongro = state["answer_llm_Summary_jongro"]

        if gangman in location:
            Summary_gangman = state["answer_llm_Summary_gangnam"]

        if junggu in location:
            Summary_junggu = state["answer_llm_Summary_junggu"]

    
        Summary_opendata = state["answer_llm_Summary_opendata"]

    
        Summary_list.extend(Summary_yongsan)
        Summary_list.extend(Summary_jongro)
        Summary_list.extend(Summary_gangman)
        Summary_list.extend(Summary_junggu)
        Summary_list.extend(Summary_opendata)

        # 검색된 문서를 형식화합니다.(프롬프트 입력으로 넣어주기 위함)
        retrieved_docs = "\n".join(
            [
                f"{doc}"
                for doc in Summary_list
            ]
        )

        # 체인을 호출하여 답변을 생성합니다.
        response = chain_place_search.invoke(
            {
                "question": latest_question,
                "context": retrieved_docs,
                "chat_history": messages_to_history(state["messages"]),
            }
        )
        # 생성된 답변, (유저의 질문, 답변) 메시지를 상태에 저장합니다.
        # print(state["messages"])
        return {
            "answer": response,
            "messages": [("user", latest_question), ("assistant", response)],
        }

    # 장소 검색 노드  끝----------------------------------------------------------------------------


    # 웹 검색 답변 생성 노드
    def llm_answer_web(state: GraphState) -> GraphState:
        # 질문을 상태에서 가져옵니다.
        latest_question = state["question"][-1].content
        # 검색된 문서를 상태에서 가져옵니다.
        # context_naver = state["context_naver"]
        # context_opendata = state["context_opendata"]
        context_web = state["context_web"]

        # 체인을 호출하여 답변을 생성합니다.
        response = chain_web.invoke(
            {
                "question": latest_question,
                "context_web": context_web,
                # "context_naver": context_naver,
                # "context_opendata": context_opendata,
                "chat_history": messages_to_history(state["messages"]),
            }
        )
        # 생성된 답변, (유저의 질문, 답변) 메시지를 상태에 저장합니다.
        # print(state["messages"])
        return {
            "answer": response,
            "messages": [("user", latest_question), ("assistant", response)],
        }

    # Web Search 노드
    def web_search(state: GraphState) -> GraphState:
        # 검색 도구 생성
        tavily_tool = TavilySearch()

        search_query = state["question"][-1].content

        # 다양한 파라미터를 사용한 검색 예제
        search_result = tavily_tool.search(
            query=search_query,  # 검색 쿼리
            topic="general",  # 일반 주제
            max_results=2,  # 최대 검색 결과
            format_output=True,  # 결과 포맷팅
        )

        return {"context_web": search_result}

    # 그래프 생성
    workflow = StateGraph(GraphState)

    # 노드 정의
    workflow.add_node("location_check", location_check)
    workflow.add_node("retrieve_document_naver", retrieve_document_naver)
    workflow.add_node("retrieve_opendata", retrieve_document_opendata)
    workflow.add_node("llm_Summary_opendata", llm_Summary_opendata)
    workflow.add_node("llm_Summary_naver", llm_Summary_naver)
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
            "일정": "llm_Schedule_answer",  #일정
            "장소검색": "llm_place_answer",  # 장소검색
        },
    )

    workflow.add_edge("location_check", "retrieve_document_naver")  # 검색 -> 답변
    workflow.add_edge("location_check", "retrieve_opendata")  # 검색 -> 답변
    workflow.add_edge("retrieve_document_naver", "llm_Summary_naver")  # 질문 -> 검색
    workflow.add_edge("retrieve_opendata", "llm_Summary_opendata")  # 질문 -> 검색
    workflow.add_edge("llm_Summary_naver", "Schedule_or_place_check") 
    workflow.add_edge("llm_Summary_opendata", "Schedule_or_place_check") 

    workflow.add_edge("llm_Schedule_answer", END)  # 답변 -> 종료
    workflow.add_edge("llm_place_answer", END)  # 답변 -> 종료

    # 그래프 진입점 설정
    workflow.set_entry_point("location_check")

    # 체크포인터 설정
    memory = MemorySaver()

    # 컴파일
    app = workflow.compile(checkpointer=memory)

    def typewriter_effect(text, delay=0.05):
        """
        텍스트를 한 글자씩 출력하는 효과를 주는 함수.
        :param text: 출력할 문자열
        :param delay: 글자 출력 간의 딜레이 (초 단위)
        """
        for char in text:
            sys.stdout.write(char)  # 글자를 출력
            sys.stdout.flush()  # 출력 버퍼를 비워 즉시 표시
            time.sleep(delay)  # 딜레이 추가
        print()  # 줄 바꿈

    # config 설정(재귀 최대 횟수, thread_id)
    config = RunnableConfig(recursion_limit=20, configurable={"thread_id": random_uuid()})


    def run_gpt(question = question):
        user_input = question
        if question == "": 
            user_input = input('일정이나 장소를 물어 보세요 : ')

        # 질문 입력
        inputs = GraphState(question=user_input)

        res = app.invoke(input=inputs, config=config)

        # typewriter_effect(res.get('answer'), delay=0.01)

        return res.get('answer')

    return run_gpt()

if __name__ == "__main__":
    # run_gpt_api 호출 및 결과 출력
    result = run_gpt_api("안녕 내가 다리를 다쳐서 병원을 가야되는데 용산에 병원 하나 알려줘")
    print("Result:", result)