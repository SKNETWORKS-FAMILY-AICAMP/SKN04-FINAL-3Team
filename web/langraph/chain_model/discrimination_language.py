from langraph.prompts.prompt_discrimination_language import prompt_discrimination_language

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter


def discrimination_language():

    model_discrimination_language = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_discrimination_language = (
        {
            "question": itemgetter("question"),
        }
        | prompt_discrimination_language
        | model_discrimination_language
        | StrOutputParser()
    )

    return chain_discrimination_language
