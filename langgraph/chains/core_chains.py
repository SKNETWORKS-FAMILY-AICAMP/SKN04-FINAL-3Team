from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

# prompts 불러오기
from prompts.day_prompt import day_prompt
from prompts.location_prompt import location_prompt
from prompts.schedule_or_place_prompt import schedule_or_place_prompt
from prompts.place_search_prompt import place_search_prompt
from prompts.schedule_prompt import schedule_prompt

# 여행 일수 추출 체인
def day_chain():
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, streaming=False)
    chain = (
        {"question": itemgetter("question")}
        | day_prompt
        | model
        | StrOutputParser()
    )
    return chain

# 여행 지역 추출 체인
def location_chain():
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, streaming=False)
    chain = (
        {"question": itemgetter("question")}
        | location_prompt
        | model
        | StrOutputParser()
    )
    return chain

# 일정 또는 장소 검색 판단 체인
def schedule_or_place_chain():
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, streaming=False)
    chain = (
        {"question": itemgetter("question")}
        | schedule_or_place_prompt
        | model
        | StrOutputParser()
    )
    return chain

# 장소 검색 체인
def place_search_chain():
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, streaming=True)
    chain = (
        # {"context": itemgetter("context"), "question": itemgetter("question"), "chat_history": itemgetter("chat_history")}
        # | 
        place_search_prompt
        | model
        | StrOutputParser()
    )
    return chain

# 여행 일정 생성 체인
def schedule_chain():
    model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, streaming=True)
    chain = (
        # {"context": itemgetter("context"), "question": itemgetter("question"), "chat_history": itemgetter("chat_history"), "day": itemgetter("day")}
        # | 
        schedule_prompt
        | model
        | StrOutputParser()
    )
    return chain
