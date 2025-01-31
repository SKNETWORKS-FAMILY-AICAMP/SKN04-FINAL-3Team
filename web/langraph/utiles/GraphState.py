from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages


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