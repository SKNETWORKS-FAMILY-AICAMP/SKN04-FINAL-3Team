from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate 


def schedule_error_chain():
    prompt_schedule_error = PromptTemplate(
        template="""
        너는 에러를 판별하는 봇이야.
        아래의 두가지 상태중에서 하나라도 1 이면 '에러' 라고 출력해.
        모두 0 이면 '정상' 이라고 출력해.

        **상태**
        - 지역 상태 : {state_location}
        - 여행 기간 상태 : {state_day}
        

        """,
            input_variables=["state_location","state_day"]
        )

    model_schedule_error = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_schedule_error = (

        prompt_schedule_error
        | model_schedule_error
        | StrOutputParser()
    )

    return chain_schedule_error
