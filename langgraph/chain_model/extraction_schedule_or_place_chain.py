from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate 
from operator import itemgetter


def sch_or_place_chain():
    prompt_sch_or_placeSearch = PromptTemplate(
        template="""너는 질문에 대해서 세가지의 옵션으로 대답하는 봇이야.
        너의 대답은 '일정', '장소검색', '일정변경' 세가지로만 대답할 수 있어.
        사용자가 질문을 하면 문맥을 잘 살펴서 사용자가 여행일정을 만들어 달라고 하면 '일정' 이라고 대답해야돼.
        사용자가 일정(장소)을 변경 하고 싶다거나 일정(장소)을 바꾸고 싶다고 하면 '일정변경'을 이라고 대답해.
        위에 두 경우가 아니면 '장소검색' 를 출력해줘.

        **'일정' 출력 예시** : 
        1. 나는 서울시의 용산구를 방문 할거야 여행 계획을 세워 줄수 있어?, 
        2. 나는 종로구와 중구 일대를 방문하고 싶어 을지로는 꼭 가보고 싶은데 을지로 계획을 포함해서 여행 일정을 만들어 줄 수 있어?
        3. 나는 강남구에 3일간 머물거야.

        
        **대답 형식** : '일정' or '일정변경' or '장소검색'

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

    return chain_sch_or_placeSearch
