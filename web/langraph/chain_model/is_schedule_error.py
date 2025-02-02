from langraph.prompts.prompt_schedule_error import prompt_schedule_error

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


def schedule_error_chain():

    model_schedule_error = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_schedule_error = (

        prompt_schedule_error
        | model_schedule_error
        | StrOutputParser()
    )

    return chain_schedule_error
