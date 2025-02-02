
from langchain.prompts import PromptTemplate

prompt_over_ten_day = PromptTemplate(
        template="""
        
        '11일 이상의 여행 일정 생성은 지원하지 않습니다. 10일 이하로 다시 시도해주세요.' 라는 내용을 출력해.

        # 출력 언어 : {language}

        """,
            input_variables=["language"]
        )