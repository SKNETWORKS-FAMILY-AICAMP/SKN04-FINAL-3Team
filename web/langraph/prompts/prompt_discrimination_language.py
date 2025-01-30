from langchain.prompts import PromptTemplate 


prompt_discrimination_language = PromptTemplate(
        template="""
        너는 사용자의 질문에서 언어를 판별하는 봇이야.
        입력되는 사용자의 질문이 어떤 언어인지 대답해줘.
        너가 구분 해야할 언어는 '한국어', '영어', '일본어', '중국어' 야.
        답변도 '한국어', '영어', '일본어', '중국어' 안에서 답해줘.

        4가지 언어중에서 선택 할 수 없다면. '언어정보없음' 출력해줘


        #사용자의 질문: {question}

        
        

        """,
            input_variables=["question"],
        )