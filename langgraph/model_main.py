from langgraph_chatbot_model import run_model
import sys

if __name__ == "__main__":
    # run_gpt_api 호출 및 결과 출력
    try:
        user_input = input('중구, 용산구, 종로구, 강남구 일정을 물어보세요 : ')
        user_input = user_input.encode('utf-8', 'ignore').decode('utf-8')
    except UnicodeDecodeError as e:
        print("UnicodeDecodeError occured:", e)
        
    result = run_model(user_input)

    for chunk, meta in result:

        if meta.get('langgraph_node') == 'generate_schedule':
            print(chunk.content, end='')
            pass


        if meta.get('langgraph_node') == 'generate_place_recs':
            print(chunk.content, end='')
            pass
    