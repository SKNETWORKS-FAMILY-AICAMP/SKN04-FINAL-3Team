from prompts.schedule_prompt import schedule_prompt
from models.openai_models import get_chat_openai
from langchain_core.output_parsers import StrOutputParser


def schedule_chain():
    model = get_chat_openai(model_name="gpt-4o-mini", temperature=0, streaming=True)
    
    chain = (
        schedule_prompt
        | model
        | StrOutputParser()
    )
    return chain