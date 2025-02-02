from prompts.prompt_schedule_change import prompt_schedule_change
from prompts.prompt_schedule_change_chi import prompt_schedule_change_chi
from prompts.prompt_schedule_change_eng import prompt_schedule_change_eng
from prompts.prompt_schedule_change_ja import prompt_schedule_change_ja

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


def schedule_change_chain(language):  
    if language == '한국어':
      change_prompt = prompt_schedule_change
    elif language == '영어':
      change_prompt = prompt_schedule_change_eng
    elif language == '중국어':
      change_prompt = prompt_schedule_change_chi
    elif language == '일본어':
      change_prompt = prompt_schedule_change_ja
    # LLM
    change_model = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, 
                        streaming=True,
                        # callback_manager=callback_manager,
                        )

    change_chain = (
        change_prompt
        | change_model
        | StrOutputParser()
    )

    return change_chain