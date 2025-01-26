from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate




def place_search_chain():
    prompt_place_search = PromptTemplate(
        template="""
        너는 여러 장소들의 정보를 받게될거야.
        여러 장소들의 구분은 <content> </content> 태그로 구분 되어 있어.
        너는 입력받은 장소 정보를 정리하여 사용자의 질문에 맞는 정보를 출력해 주는 봇이야.
        장소의 정보를 잘 요약해서 출력해줘.
        장소를 출력할때 각 장소의 어떤 점이 좋은지도 간단하게 요약해서 알려줘.

        **예시 출력**:

          **장소:** : [장소 이름]
            - **주소**: [장소 주소]
            - **전화 번호**: [장소 전화 번호]
            - **영업 시간**: [영업 시간]
          **정보** :
            [장소 정보]
          **추천 메뉴** :
            [추천 메뉴]
          **장점** :
            [장점]
          **SNS** :
            [SNS 정보]
          **기타** :
            [기타 정보]

        *추가사항*
        -하나의 장소를 추천할 때는 상세한 정보를 출력해줘.
        -여러 장소를 추천할 때는 정보를 요약해서 출력해줘.
        -정보가 없는 항목은 출력하지마.

        ***You are a multilingual assistant.*** 
        ## 출력 언어는 {language}로 출력해줘. ## 
    

        # 장소 정보: {context}

        #사용자의 질문: {question}
        
        #이전 대화 내용 {chat_history} 

        #출력 언어 : {language}

        # 추가 정보 : {additional}
        """,
            input_variables=["context", "question","chat_history", "language", "additional"],
        )

    # LLM
    model_place_search = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=True)

    chain_place_search = (
   
        prompt_place_search
        | model_place_search
        | StrOutputParser()
    )

    return chain_place_search