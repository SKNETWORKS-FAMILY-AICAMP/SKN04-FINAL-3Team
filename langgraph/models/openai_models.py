from langchain_openai import ChatOpenAI

def get_chat_openai(model_name="gpt-4o-mini", temperature=0, streaming=False):
    return ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        streaming=streaming,
    )
