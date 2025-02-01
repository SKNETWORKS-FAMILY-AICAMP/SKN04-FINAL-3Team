from langraph.prompts.prompt_location import prompt_location

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter


def location_chain():

    model_location = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_location = (
        {
            "question": itemgetter("question"),
        }
        | prompt_location
        | model_location
        | StrOutputParser()
    )

    return chain_location