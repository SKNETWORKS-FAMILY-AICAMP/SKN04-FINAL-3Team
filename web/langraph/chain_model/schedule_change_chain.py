from langraph.prompts.prompt_schedule_change import prompt_schedule_change

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


def schedule_change_chain():  
    change_prompt = prompt_schedule_change

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