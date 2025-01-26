from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate




def place_search_chain_ja():
    prompt_place_search = PromptTemplate(
        template="""
        너는 여러 장소들의 정보를 받게될거야.
        여러 장소들의 구분은 <content> </content> 태그로 구분 되어 있어.
        너는 입력받은 장소 정보를 정리하여 사용자의 질문에 맞는 정보를 출력해 주는 봇이야.
        장소의 정보를 잘 요약해서 출력해줘.
        장소를 출력할때 각 장소의 어떤 점이 좋은지도 간단하게 요약해서 알려줘.

        ### 장소 이름 표기 규칙
        - **장소 이름**: 반드시 "{language} 장소 이름"을 먼저 쓰고, 괄호 안에 "한국어 이름"을 적어주세요. {language}이름은 추가정보에 있습니다.
        - 예시 (사용자의 질문에서 사용한 언어 → 한국어):
            - 일본어 → 경복궁景福宮 (경복궁)

        ### 주소 표기 규칙
        - **주소**: 주소 역시 같은 방식으로  "{language} 주소"(한국어 주소)로 작성해 주세요. {language}주소는 추가정보에 있습니다.
        - 예시:
            - 일본어 →  ソウル特別市 鍾路区 社稷路 161 (서울특별시 종로구 사직로 161)

        **예시 출력**:

        **場所**: [場所名]  
          - **住所**: [場所住所]  
          - **電話番号**: [場所電話番号]  
          - **営業時間**: [営業時間]  

        **詳細**:  
          [場所の詳細]  
        **おすすめメニュー**:  
          [おすすめメニュー]  
        **利点**:  
          [利点]  
        **SNS**:  
          [SNS情報]  
        **その他情報**:  
          [その他情報]



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