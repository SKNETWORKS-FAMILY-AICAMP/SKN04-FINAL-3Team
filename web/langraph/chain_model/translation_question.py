from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from operator import itemgetter


def translation_question():
    prompt_translation_question = PromptTemplate(
        template="""

        너는 사용자의 질문을 번역하는 봇이야.

        사용자의 질문을 한국어로 번역해.
        
        #사용자의 질문: {question}

        """,
            input_variables=["question", "language"],
        )

    model_translation_question = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_translation_question = (
        {
            "question": itemgetter("question"),
        }
        | prompt_translation_question
        | model_translation_question
        | StrOutputParser()
    )

    return chain_translation_question