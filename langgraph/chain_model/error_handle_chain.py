from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate



def error_handle_chain():
    prompt_error_handle = PromptTemplate(
        template="""

        너는 에러를 판별해서 사용자에게 무슨 에러가 났는지 설명하는 봇이야.
        에러 상태가 1 이면 에러인 상태야.
        각 에러 별로 출력 해야 하는 문구는 다음과 같아
        출력은 {language}로 해줘.

        **지역 에러**

        - 질문에서 지역을 추출하지 못했습니다. 이 상황이 반복된다면, 질문에 '용산구, '중구', '종로구' , '강남구' 를 넣어서 구체적으로 질문 해보세요!

        **일자 에러**

        - 질문에서 여행 기간를 추출하지 못했습니다. 이 상황이 반복된다면, 질문에 '종로구에 3일동안 여행 할거야' 같이 여행 기간을 넣어서 구체적으로 질문 해보세요!

        **언어 판별 에러**

        - 죄송합니다. 입력하신 언어는 지원하지 않은 언어 입니다. 언어는 '한국어', '영어', '일본어', '중국어' 가 지원 됩니다.
          만약 지원 되는 언어를 사용해도 이 문제가 반복된다면, 저희에게 연락 바랍니다. ggoonngg1122345@gmail.com


        **주의 사항**

        - 언어 판별에러가 발생하면, {language} 가 아닌 사용자 질문에서 사용된 언어로 번역해서 출력해.
        - 여러 에러가 발생하면, 발생된 에러의 문구를 잘 다듬어서 합쳐서 출력해줘.

        # 지역 에러 상태: {state_location}

        # 언어 판별 에러 상태: {state_language}

        # 일자 에러 상태: {state_day}

        # 사용자 질문 : {question}

        """,
            input_variables=["state_location","state_day","state_language","language","question"]
        )

    model_error_handle = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_error_handle = (
        prompt_error_handle
        | model_error_handle
        | StrOutputParser()
    )

    return chain_error_handle