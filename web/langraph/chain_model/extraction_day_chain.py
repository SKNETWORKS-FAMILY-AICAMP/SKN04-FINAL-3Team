from langraph.prompts.prompt_day import prompt_day

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter


def day_chain():

    model_day = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_day = (
        {
            "question": itemgetter("question"),
        }
        | prompt_day
        | model_day
        | StrOutputParser()
    )

    return chain_day