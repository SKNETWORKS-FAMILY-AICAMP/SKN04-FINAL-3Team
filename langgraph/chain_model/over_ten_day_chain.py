from prompts.prompt_over_ten_day import prompt_over_ten_day


from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


def over_ten_day_chain():  

    # LLM
    model = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, 
                        streaming=True,
                        # callback_manager=callback_manager,
                        )

    chain = (
        prompt_over_ten_day
        | model
        | StrOutputParser()
    )

    return chain