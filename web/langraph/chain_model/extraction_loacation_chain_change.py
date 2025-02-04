from langraph.prompts.prompt_location_change import prompt_location_change

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter


def location_chain_change():

    model_location = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_location = (
        {
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history"),
        }
        | prompt_location_change
        | model_location
        | StrOutputParser()
    )

    return chain_location