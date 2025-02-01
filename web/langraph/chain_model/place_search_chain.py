from langraph.prompts.prompt_place_search_chi import prompt_place_search_chi
from langraph.prompts.prompt_place_search_ja import prompt_place_search_ja
from langraph.prompts.prompt_place_search_kr import prompt_place_search_kr
from langraph.prompts.prompt_place_search_eng import prompt_place_search_eng

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


def place_search_chain(language):
    if language == '한국어':
      prompt_place_search = prompt_place_search_kr
    elif language == '영어':
      prompt_place_search = prompt_place_search_eng
    elif language == '중국어':
      prompt_place_search = prompt_place_search_chi
    elif language == '일본어':
      prompt_place_search = prompt_place_search_ja

    # LLM
    model_place_search = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=True)

    chain_place_search = (
        prompt_place_search
        | model_place_search
        | StrOutputParser()
    )

    return chain_place_search