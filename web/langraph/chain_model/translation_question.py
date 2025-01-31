from prompts.prompt_translation_question import prompt_translation_question

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter


def translation_question():

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