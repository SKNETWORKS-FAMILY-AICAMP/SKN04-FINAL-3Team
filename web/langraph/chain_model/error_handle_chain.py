from langraph.prompts.prompt_error_handle import prompt_error_handle

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


def error_handle_chain():

    model_error_handle = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_error_handle = (
        prompt_error_handle
        | model_error_handle
        | StrOutputParser()
    )

    return chain_error_handle