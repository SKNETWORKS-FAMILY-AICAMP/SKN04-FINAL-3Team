from langchain.prompts import PromptTemplate


prompt_day = PromptTemplate(
        template="""

        너는 사용자의 질문을 보고 의도를 파악해서 사용자가 몇일의 여행을 가는지 알아내야돼.
        몇일을 가는지 알게되면 그 결과를 숫자로 반환해.
        

        # Examples 1

        **Input**: 
        
        -"용산구에 1박2일 방문 할 예정이야. 일정을 생성 해줄 수 있어?"

        **answer**: 
        
        2


        # Examples 2

        **Input**: 
        
        - "서울시에 5박6일 방문 할 예정이야. 일정을 생성 해줄 수 있어?"

        **answer**: 
        
        6

        # Examples 3

        **Input**: 
        
        - "종로구에 여행을 가려고해 9일동안 머물건데 일정을 만들어줘"

        **answer**: 
        
        9
        

        # 몇일 여행을 가는지 알 수 없는 경우 '정보없음' 을 출력해.


        #사용자의 질문: {question}

        """,
            input_variables=["question"],
        )