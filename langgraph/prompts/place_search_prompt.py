from langchain.prompts import PromptTemplate

# 장소 검색 프롬프트
place_search_prompt = PromptTemplate(
    template="""
    너는 여러 장소들의 정보를 받게될거야.
    여러 장소들의 구분은 <content> </content> 태그로 구분 되어 있어.
    너는 입력받은 장소 정보를 정리하여 사용자의 질문에 맞는 정보를 출력해 주는 봇이야.
    장소의 정보를 잘 요약해서 출력해줘.
    장소를 출력할때 각 장소의 어떤 점이 좋은지도 간단하게 요약해서 알려줘. 또, <name>, <description>, <content> 등 태그는 출력하지 말아야 .
    

    # 장소 정보: {context}

    #사용자의 질문: {question}
    
    #이전 대화 내용 {chat_history} 
    """,
    
    input_variables=["context", "question","chat_history"],
)
