from prompts.prompt_schedule_kr import prompt_schedule_kr
from prompts.prompt_schedule_chi import prompt_schedule_chi
from prompts.prompt_schedule_eng import prompt_schedule_eng
from prompts.prompt_schedule_ja import prompt_schedule_ja

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


def schedule_chain(language):  
    if language == '한국어':
      prompt = prompt_schedule_kr
    elif language == '영어':
      prompt = prompt_schedule_eng
    elif language == '중국어':
      prompt = prompt_schedule_chi
    elif language == '일본어':
      prompt = prompt_schedule_ja

    # LLM
    model = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, 
                        streaming=True,
                        # callback_manager=callback_manager,
                        )

    chain = (
        prompt
        | model
        | StrOutputParser()
    )

    return chain