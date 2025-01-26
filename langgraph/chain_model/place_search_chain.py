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

        ***You are a multilingual assistant.*** 
        ## 출력 언어는 {language}로 출력해줘. ## 

        ### 장소 이름 표기 규칙
        - **장소 이름**: 반드시 "한국어 이름"을 먼저 쓰고, 괄호 안에 "{language} 장소 이름"을 적어주세요. {language}이름은 추가정보에 있습니다.
        - 예시 (사용자의 질문에서 사용한 언어 → 한국어):
            - 영어 → 경복궁 (Gyeongbokgung Palace)
            - 일본어 → 경복궁 (景福宮)
            - 중국어 간체 → 경복궁 (景福宫)
            - 중국어 번체 → 경복궁 (景福宮)

        ### 주소 표기 규칙
        - **주소**: 주소 역시 같은 방식으로  "한국어 주소"({language} 주소)로 작성해 주세요. {language}주소는 추가정보에 있습니다.
        - 예시:
            - 영어 → 서울특별시 종로구 사직로 161 (161 Sajik-ro, Jongno-gu, Seoul) 
            - 일본어 → 서울특별시 종로구 사직로 161 (ソウル特別市 鍾路区 社稷路 161)
            - 중국어 간체 → 서울특별시 종로구 사직로 161 (首尔特别市 钟路区 社稷路 161)
            - 중국어 번체 → 서울특별시 종로구 사직로 161 (首爾特別市 鐘路區 社稷路 161)

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

        ***반드시 장소이름 표기 규칙을 지켜주세요.*** 
        ***반드시 주소 표기 규칙을 지켜주세요.***

        *추가사항*
        -하나의 장소를 추천할 때는 상세한 정보를 출력해줘.
        -여러 장소를 추천할 때는 정보를 요약해서 출력해줘.
        -정보가 없는 항목은 출력하지마.
        -'[' ']'는 출력하지마.

  
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