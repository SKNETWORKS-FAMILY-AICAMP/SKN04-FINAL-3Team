from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate 
from operator import itemgetter


def location_chain():
    prompt_location = PromptTemplate(
        template="""너는 질문에 대해서 **Python의 list**를 반환해야 돼.
        list에 들어갈 수 있는 str은 ['용산구', '강남구', '중구', '종로구'] 네 가지 중 일부야.

        아래 **지역 판별 규칙**에 따라, 사용자의 질문에서 해당 지역을 **최대한** 찾아서 list에 넣어줘.
        만약 '서울'에 해당하는 표현(예: 'Seoul', 'ソウル', '首尔', '首爾')이 있으면, ['용산구','강남구','중구','종로구'] 전부 넣어줘.

        - **용산구**:
        - 한국어: "용산구"
        - 영어: "Yongsan", "Yongsan-gu"
        - 일본어: "龍山", "ヨンサン"
        - 중국어: "龙山", 등

        - **강남구**:
        - 한국어: "강남구"
        - 영어: "Gangnam", "Gangnam-gu"
        - 일본어: "カンナム"
        - 중국어: "江南", 등

        - **중구**:
        - 한국어: "중구"
        - 영어: "Junggu", "Jung-gu"
        - 일본어: "チュング"
        - 중국어: "中区", 등

        - **종로구**:
        - 한국어: "종로구"
        - 영어: "Jongno", "Jong-ro"
        - 일본어: "ジョンノ"
        - 중국어: "鐘路区", 등

        - **서울**:
        - 한국어: "서울"
        - 영어: "Seoul"
        - 일본어: "ソウル"
        - 중국어: "首尔", "首爾"
        => '서울' 관련 표현이면 list에 ['용산구','강남구','중구','종로구'] 전부 넣기

        위 규칙에 없는 지역(예: 부산, 전라남도, Myeongdong 등)은 무시하고 list에 넣지 말아줘.
        만약 전혀 일치하는 구나 "서울"이 없다면 빈 list를 반환해.

        출력 예시:
        - "I want to go to Yongsan" → ["용산구"]
        - "ソウル特別市を旅行したい" → ["용산구","강남구","중구","종로구"]
        - "I want to visit Gangnam and Myeongdong" → ["강남구"]  # (명동은 중구이지만, 직접 '중구'나 'Myeong-dong' 매핑을 안 넣었다면 생략)

        주의: 최종 출력은 **파이썬 리스트** 형태로, 따옴표(쿼트)와 쉼표(콤마)를 정확히 써서 예) ["용산구","종로구"] 처럼 출력해.

        #사용자의 질문:{question}
        """,
            input_variables=["question"],
        )

    model_location = ChatOpenAI(model_name="gpt-4o-mini",
                        temperature=0, streaming=False)

    chain_location = (
        {
            "question": itemgetter("question"),
        }
        | prompt_location
        | model_location
        | StrOutputParser()
    )

    return chain_location