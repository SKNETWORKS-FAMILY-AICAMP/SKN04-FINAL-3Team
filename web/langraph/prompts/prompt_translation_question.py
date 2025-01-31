from langchain.prompts import PromptTemplate


prompt_translation_question = PromptTemplate(
        template="""

        너는 사용자의 질문을 번역하는 봇이야.

        사용자의 질문을 한국어로 번역해.
        
        #사용자의 질문: {question}

        """,
            input_variables=["question", "language"],
        )
