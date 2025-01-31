from prompts.prompt_sch_or_place_search import prompt_sch_or_place_search

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter


def sch_or_place_chain():

    model_sch_or_placeSearch = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_sch_or_placeSearch = (
        {
            "question": itemgetter("question"),
        }
        | prompt_sch_or_place_search
        | model_sch_or_placeSearch
        | StrOutputParser()
    )

    return chain_sch_or_placeSearch
