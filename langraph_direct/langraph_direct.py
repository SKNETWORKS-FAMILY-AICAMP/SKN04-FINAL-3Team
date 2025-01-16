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

import random

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# Step 1: FAISS 인덱스 파일 로드
faiss_index_path = "Faiss/naver_map_gangnam_faiss_"  # 저장된 Faiss 파일 경로
embeddings = OpenAIEmbeddings()  # 임베딩 객체 초기화

# 저장된 FAISS 인덱스를 불러와서 Retriever 생성
retriever_naver_gangnam = FAISS.load_local(faiss_index_path, embeddings,allow_dangerous_deserialization=True).as_retriever()

# 검색 매개변수 설정 (예: 검색 결과 상위 10개 반환)
retriever_naver_gangnam.search_kwargs = {"k": 50}

# Step 1: FAISS 인덱스 파일 로드
faiss_index_path = "Faiss/naver_map_jongro_faiss_"  # 저장된 Faiss 파일 경로
embeddings = OpenAIEmbeddings()  # 임베딩 객체 초기화

# 저장된 FAISS 인덱스를 불러와서 Retriever 생성
retriever_naver_jongro = FAISS.load_local(faiss_index_path, embeddings,allow_dangerous_deserialization=True).as_retriever()

# 검색 매개변수 설정 (예: 검색 결과 상위 10개 반환)
retriever_naver_jongro.search_kwargs = {"k": 50}

# Step 1: FAISS 인덱스 파일 로드
faiss_index_path = "Faiss/naver_map_Junggu_faiss_"  # 저장된 Faiss 파일 경로
embeddings = OpenAIEmbeddings()  # 임베딩 객체 초기화

# 저장된 FAISS 인덱스를 불러와서 Retriever 생성
retriever_naver_Junggu = FAISS.load_local(faiss_index_path, embeddings,allow_dangerous_deserialization=True).as_retriever()

# 검색 매개변수 설정 (예: 검색 결과 상위 10개 반환)
retriever_naver_Junggu.search_kwargs = {"k": 50}

# Step 1: FAISS 인덱스 파일 로드
faiss_index_path = "Faiss/naver_map_yongsan_faiss_"  # 저장된 Faiss 파일 경로
embeddings = OpenAIEmbeddings()  # 임베딩 객체 초기화

# 저장된 FAISS 인덱스를 불러와서 Retriever 생성
retriever_naver_yongsan = FAISS.load_local(faiss_index_path, embeddings,allow_dangerous_deserialization=True).as_retriever()

# 검색 매개변수 설정 (예: 검색 결과 상위 10개 반환)
retriever_naver_yongsan.search_kwargs = {"k": 50}

# Step 1: FAISS 인덱스 파일 로드
faiss_index_path = "Faiss/opendata_gangnam_all"  # 저장된 Faiss 파일 경로
embeddings = OpenAIEmbeddings()  # 임베딩 객체 초기화

# 저장된 FAISS 인덱스를 불러와서 Retriever 생성
retriever_opendata_gangnam = FAISS.load_local(faiss_index_path, embeddings,allow_dangerous_deserialization=True).as_retriever()

# 검색 매개변수 설정 (예: 검색 결과 상위 10개 반환)
retriever_opendata_gangnam.search_kwargs = {"k": 50}

# Step 1: FAISS 인덱스 파일 로드
faiss_index_path = "Faiss/opendata_jongro_all"  # 저장된 Faiss 파일 경로
embeddings = OpenAIEmbeddings()  # 임베딩 객체 초기화

# 저장된 FAISS 인덱스를 불러와서 Retriever 생성
retriever_opendata_jongro = FAISS.load_local(faiss_index_path, embeddings,allow_dangerous_deserialization=True).as_retriever()

# 검색 매개변수 설정 (예: 검색 결과 상위 10개 반환)
retriever_opendata_jongro.search_kwargs = {"k": 50}

# Step 1: FAISS 인덱스 파일 로드
faiss_index_path = "Faiss/opendata_junggu_all"  # 저장된 Faiss 파일 경로
embeddings = OpenAIEmbeddings()  # 임베딩 객체 초기화

# 저장된 FAISS 인덱스를 불러와서 Retriever 생성
retriever_opendata_junggu = FAISS.load_local(faiss_index_path, embeddings,allow_dangerous_deserialization=True).as_retriever()

# 검색 매개변수 설정 (예: 검색 결과 상위 10개 반환)
retriever_opendata_junggu.search_kwargs = {"k": 50}

# Step 1: FAISS 인덱스 파일 로드
faiss_index_path = "Faiss/opendata_yongsan_all"  # 저장된 Faiss 파일 경로
embeddings = OpenAIEmbeddings()  # 임베딩 객체 초기화

# 저장된 FAISS 인덱스를 불러와서 Retriever 생성
retriever_opendata_yongsan = FAISS.load_local(faiss_index_path, embeddings,allow_dangerous_deserialization=True).as_retriever()

# 검색 매개변수 설정 (예: 검색 결과 상위 10개 반환)
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
    너는 여러 장소들의 정보를 받게될거야.
    여러 장소들의 구분은 <content> </content> 태그로 구분 되어 있어
    이 장소들을 바탕으로 일정을 만들어줘.
    Create a travel itinerary bot that generates schedules based on user questions. The schedule should be divided into morning, lunch, and evening plans for each travel day, and for each time of day, recommend a restaurant and tourist attractions or streets.

Extract key details from the user's questions to create a travel itinerary. Identify dates, times, and activities, then structure a plan with specific restaurant and sightseeing recommendations for morning, lunch, and evening.

#유의사항

- 일차가 1 일차면 아침일정을 추천하지마. 일차가 1 이 아니면 아침 일정을 만들어줘.
- 추천했던 장소를 한번더 추천하지마.
- 아침, 점심, 저녁 이동 경로가 가까워야돼
- {day}일차의 하루의 일정만 생성해줘.
- 질문에 여러일차를 추천해 달라고 해도 '일차' 에있는 하루의 일정만 생성해
- 일정을 만들고 마무리 멘트는 넣지마.

# Steps

1. **Request Analysis**: Carefully analyze the user's input to understand the itinerary requirements, including any specified food or sightseeing preferences.
2. **Confirm Details**: Verify dates, times, locations, activity preferences, and any specific requests for restaurants or attractions.
3. **Create Itinerary**: Using confirmed details, write a structured schedule detailing morning, lunch, and evening sections for each day, recommending one restaurant and tourist attraction or street for each time slot.

# Output Format

- Provide a detailed itinerary in a bullet-point list or table format, itemizing each day's morning, lunch, and evening plans.

# Examples

**Input**: "용산구에 1박2일 방문 할 예정이야. 일정을 생성 해줄 수 있어?"

**Schedule**:
- {day}일차

  - 점심: 점심 식사 장소: [점심 식사 장소] [음식점 주소] [영업 시간] [음식점 특징] [기타 정보] ,
         명소: [관광할 명소 또는 거리] [영업 시간] [명소 특징] [명소 위치] [기타 정보]
         카페 : [카페 주소] [영업 시간] [카페 정보] [카페 특징] 
  - 저녁: 저녁 식사 장소: [저녁 식사 장소] [음식점 주소] [음식점 특징] [기타 정보], 명소: [관광할 명소 또는 거리] [명소 특징] [명소 위치] [기타 정보]
        쇼핑몰 : [쇼핑몰 주소] [쇼핑몰 특징]
        숙소 : [숙소 위치] [숙소 정보] [숙소 특징] *숙소 정보 없으면 출력 하지 않기


# Notes

- Ensure that all parts of the itinerary are complete and relevant to the user's request.
- Attempt to clarify any ambiguous details related to time, location, or activity preferences.
- Include clear recommendations for restaurants and tourist attractions for each part of the day.
- 이전에 추천했던 장소는 넣지 말아줘
#답변언어 : 한국어

    # 장소 정보 : {context}

    # 사용자의 질문 : {question}
    
    # 이전 대화 내용 : {chat_history} 

    # 일차 : {day}
    """,
        input_variables=["context", "question","chat_history","day"],
    )

# LLM

# callback_manager = CallbackManager([NaturalTextStreamCallbackHandler()])

chat = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0,
    streaming=True,
    # callback_manager=callback_manager
)

model = ChatOpenAI(model_name="gpt-4o",
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
model_place_search = ChatOpenAI(model_name="gpt-4o",
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
    template="""너는 질문에 대해서 list를 반환해야돼.
    list에 들어갈 수 있는 str은 '용산구', '강남구', '중구', '종로구' 네가지가 있어.
    사용자가 질문을 하면 문장을 잘 보고 문장속의 지역을 추출해서 리스트에 넣어줘.
    만약 사용자의 질문에 '서울'을 방문 한다고 하면 리스트에 '용산구', '강남구', '중구', '종로구' 를 모두 넣어줘.
    사용자의 질문에 서울시가 아닌 다른지역을 물어보거나, 서울시에서도 '용산구', '강남구', '중구', '종로구'가 아닌 다른 지역을 물어보면 빈 리스트를 반환해.


    #입력 예시 : 1. 나는 서울시의 용산구를 방문 할거야 여행 계획을 세워 줄수 있어?, 
               2. 나는 종로구와 중구 일대를 방문하고 싶어 을지로는 꼭 가보고 싶은데 을지로 계획을 포함해서 여행 일정을 만들어 줄 수 있어?

    #대답 형식 예시 : ['종로구','강남구']


    #####
    입력 예시 1 : 나는 전라남도 여행을 계획중이야. 일정을 만들어 줄 수 있어?  
    답변 예시 1 : []

    #####

    #####
    입력 예시 2 : 나는 용산구와 종로구, 중구 일대를 관광하고 싶어 좋은 카페를 알고 싶은데 알려줄 수 있어?  
    답변 예시 2 : ['용산구','중구','종로구']

    #####

    #####
    입력 예시 3: 나는 서울시를 관광하고 싶어 1박2일 정도 방문하려고 하는데 일정을 만들어 줄 수 있어?
    답변 예시 3: ['용산구','중구','종로구','강남구']
    
    #####

    #####
    입력 예시 4 : 종로구에서 맛있는 고기집을 찾고 있어. 찾아줘
    답변 예시 4: ['종로구']

    #####


    #사용자의 질문: {question}

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
                    temperature=0, streaming=False)

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

            place_list.extend(random.sample(place_yongsan, 5))

        if jongro in location:
            place_jongro = state["context_naver_jongro"]
            place_list.extend(random.sample(place_jongro, 5))

        if gangman in location:
            place_gangman = state["context_naver_gangnam"]
            place_list.extend(random.sample(place_gangman, 5))

        if junggu in location:
            place_junggu = state["context_naver_Junggu"]

            place_list.extend(random.sample(place_junggu, 5))

    
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
    print(state["messages"])
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


##########----------#############



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
inputs = GraphState(question="중구에서 3박4일 일정 만들어줘")

ans=app.stream(input=inputs, config=config, stream_mode='messages')