from langgraph_chatbot_model import run_model


if __name__ == "__main__":
    # run_gpt_api 호출 및 결과 출력
    user_input = input('중구, 용산구, 종로구, 강남구 일정을 물어보세요 : ')
    result = run_model(user_input)

    for chunk, meta in result:

        if meta.get('langgraph_node') == 'llm_Schedule_answer':

            print(chunk.content, end='')


        if meta.get('langgraph_node') == 'llm_place_answer':

            print(chunk.content, end='')

        if meta.get('langgraph_node') == 'error_handling':

            print(chunk.content, end='')
    