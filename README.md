# SKN04-FINAL-3Team

# 🤗 팀명 : SeouLogue
 
### 🤭 팀원

<p align="center">
  <table>
	<tr>
	  <td align="center">
		<img src="readme_img/IMG_0853.JPG" width="160" height="160"/><br>박병헌 [팀장]
	  </td>
	  <td align="center">
		<img src="readme_img/60a24a4a2a4b1ac9.png" width="160" height="160"/><br>이지수
	  </td>
	  <td align="center">
		<img src="readme_img/13FCBA48-E24F-495C-B418-042286F31758_1_201_a.jpg" width="160" height="160"/><br>이진섭
	  </td>
	  <td align="center">
		<img src="readme_img/ae88b44779e026ae.jpg" width="160" height="160"/><br>오종수
	  </td>
	</tr>
  </table>
</p>

### 💼 역할 분담

### 👨‍💻 박병헌
- **모델**
- **Retriever 구축**
- **README 작성** 
### 👨‍💻 이지수
- **Front-end** 
- **Back-end(DB)**
- **AWS 배포**


### 👩‍💻 이진섭
- **Back-end**
- **모델 평가** 
- **README 작성** 

### 👨‍💻 오종수
- **Front-end**

---

## 프로젝트 개요
코로나 이후 국내 관광 산업은 외국인 관광객의 급격한 증가와 함께 다시금 활기를 띠고 있습니다. 2023년 방한 외래객 수는 약 1,103만 명에 이르며, 이들의 총지출액은 약 11조 원으로 추정됩니다. 이는 국내 대표 IT 기업인 네이버의 2023년 매출액(약 9조 원)보다도 많은 규모로, 외국인 관광객이 한국 경제에 미치는 영향이 상당함을 보여줍니다. 국적별 비중을 살펴보면 일본, 중국, 미국 순으로 가장 많은 관광객이 방문하고 있으며, 향후 이러한 추세는 더욱 가속화될 것으로 전망됩니다.

그러나 외국인 관광객들은 국내 한국어 중심의 앱 환경으로 인해 여러 불편을 겪고 있습니다. 예를 들어, 구글 맵은 한국 지도 데이터를 해외로 반출할 수 없다는 안보 관련 규제로 인해 길찾기 기능이 제대로 작동하지 않고, 네이버 지도는 다국어 지원 범위가 제한적이며 번역의 완성도가 낮아 활용도가 떨어진다는 지적이 있습니다. 카카오 맵 역시 영어 주소 인식에 어려움이 있어, 외국인이 단일 한국 토종 앱만으로 원활하게 정보를 얻기에는 한계가 있습니다. 이로 인해 많은 관광객들은 방한 전후로 여러 글로벌 앱과 국내 앱을 병행해 사용하고 있어 서비스 이용이 복잡해지는 문제가 발생합니다.

본 프로젝트는 이러한 문제점을 해결하고, 방한 외국인 관광객들이 국내에서 편리하고 만족스러운 여행 경험을 할 수 있도록 통합 정보 제공 및 다국어 지원 플랫폼을 구축하는 것을 목표로 합니다. 이를 통해 국내 관광 산업의 성장에 발맞춰, 더욱더 많은 외국인 관광객들이 한국을 쉽고 즐겁게 여행할 수 있도록 돕고자 합니다.

## Data

naver 지도 크롤링 <br>
지역: 용산구, 강남구, 종로구, 중구 <br>
키워드: 음식점, 카페, 술집
<br>
<br>
opendata<br>
지역: 용산구, 강남구, 종로구, 중구 <br>
한국보건산업진흥원_외국인환자 유치기관 현황: https://www.data.go.kr/data/3050000/fileData.do<br>
서울시 의료관광허가 의료기관 정보: https://data.seoul.go.kr/dataList/OA-12973/S/1/datasetView.do <br>
서울시 관광 음식: https://data.seoul.go.kr/dataList/OA-21054/S/1/datasetView.do<br>
서울시 관광 명소: https://data.seoul.go.kr/dataList/OA-21050/S/1/datasetView.do<br>
서울특별시_관광 쇼핑: https://data.seoul.go.kr/dataList/OA-21053/S/1/datasetView.do<br>
서울특별시_관광 문화: https://data.seoul.go.kr/dataList/OA-21052/S/1/datasetView.do<br>
서울특별시_ 관광 자연: https://data.seoul.go.kr/dataList/OA-21051/S/1/datasetView.do<br>
서울특별시_관광거리 정보: https://data.seoul.go.kr/dataList/OA-12929/S/1/datasetView.do<br>
서울특별시_ 관광안내소: https://data.seoul.go.kr/dataList/OA-20350/S/1/datasetView.do<br>
관광숙박업: https://www.localdata.go.kr/data/dataView.do



## Preprocess

1.	지역별 데이터 분할<br>
	•	수집된 데이터를 서울의 행정구(區) 단위로 분할하여 관리함으로써, 지역별 검색 및 분석의 효율성을 높였습니다.
2.	다국어 주소 컬럼 추가<br>
•	방문객 국적에 따라 주소 정보를 효과적으로 제공하기 위해, 각 주소를 여러 나라의 언어로 번역하여 추가 컬럼을 생성했습니다.
3.	데이터 임베딩 및 저장<br>
•	정제된 데이터를 기반으로 text-embedding-3-small 모델을 사용하여 임베딩을 수행한 뒤, Faiss 데이터베이스에 저장하여 고속 벡터 검색이 가능하도록 구성했습니다.<br>
•	BM25 알고리즘도 함께 사용하여 텍스트 기반 검색에서의 검색 정확도를 높였습니다.
---



## 기술 스택

| **Category**           | **Tools**                                                                                                                                                                                                                                                                                                                                |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Data Modeling**      | ![BeautifulSoup](https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) <img src="https://img.shields.io/badge/langchain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white"> <img src="https://img.shields.io/badge/openai-412991?style=for-the-badge&logo=openai&logoColor=white"> |
| **SCM**                | <img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white"/>                                                                                                                                                                                                                                           |
| **Front-End / Back-End** | <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white">                                                                                                                                                                                                                                                                       |
| **Deploy**             | <img src="https://img.shields.io/badge/Amazon_AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white">                                                                                                                                                                                                                                                                 |

## Prerequisites



### Conda 환경 생성 및 활성화 ## 
```
conda create -n myenv python=3.11
conda activate myenv
pip install -r requirements.txt
```
---

### .env 환경변수 파일 필요 

<p>

```
OPENAI_API_KEY=***********
NCP_CLIENT_ID=***********
NCP_CLIENT_SECRET=***********
faiss_path=./data/db
DB_NAME=postgres
DB_USER=seoulogue
DB_PASSWORD=***********
DB_HOST='***********'
DB_PORT=****
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com/"
LANGCHAIN_API_KEY="***********"
LANGCHAIN_PROJECT="practice"
TAVILY_API_KEY=***********
DJANGO_SECRET_KEY="***********"
```
### 네이버 API 발급 과정 

네이버 클라이언트 아이디와 시크릿을 발급받아서 .env에 설정
네이버 지도 API를 보여줄 사이트의 URL 및 도메인을 WEB 서비스 URL에 등록

<img src="/Users/jururu/Desktop/AI/SKN04-FINAL-3Team-1/readme_img/image.png" width="300" height="250">

## 서비스 페이지 로컬 실행 시

### settings DATABASES 다음과 같이 변경

<p>

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',  # 데이터베이스 이름
        'USER': 'postgres',       # PostgreSQL 사용자 이름
        'PASSWORD': '****',   # PostgreSQL 사용자 비밀번호
        'HOST': '127.0.0.1',           # 또는 DB 서버 IP
        'PORT': '5432',                # 기본값
    }
}
```

### django 실행 명령어
```
cd web
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser # 본인 계정 생성
python manage.py collectstatic
yes
python manage.py runserver
```

## System Architecture

### 프로그램의 전체적인 구성 도표 삽입 및 설명

<p>
  <img src="/Users/jururu/Desktop/AI/SKN04-FINAL-3Team-1/readme_img/Architecture.png" width="500" height="250">
</p>

## 서비스 설명
<img src="/Users/jururu/Desktop/AI/SKN04-FINAL-3Team-1/readme_img/service_page.png" width="500" height="300">

서비스 페이지 화면<br>

챗봇에게 일정 생성이나 장소 추천 등을 요청하면, 답변받은 정보를 바탕으로 지도 화면 하단에 장소 요약 목록을 확인할 수 있습니다. <br>

또한 일정에 포함된 장소들은 지도 위에 마커로 표시되며, 방문 순서에 따라 번호가 매겨집니다. 생성한 일정 자체를 즐겨찾기에 등록할 수 있고, 일정에 포함된 각 장소들도 장소 즐겨찾기로 추가 가능합니다.<br>

챗봇과의 대화 내용은 채팅 목록으로 저장할 수 있어, 나중에 다시 확인하거나 이어서 작업하기 편리합니다. 다만 로그인하지 않은 상태에서는 기본적인 챗봇 기능만 사용 가능하며, 즐겨찾기나 채팅 목록 저장 같은 개인화 기능은 사용할 수 없습니다.




## 소감


### 👨‍💻 박병헌: 
생각보다 어려운 과정이였고, 모델의 디테일한 부분을 잡아가는 것이 힘들었다. 그러나 함께 하는 프로젝트로 힘을 낼 수 있었고 프로젝트를 무사히 마칠 수 있었다. 프로젝트를 진행하면서 langgraph, git, langchain, 배포 과정을 온몸으로 느낄 수 있었다. 


### 👨‍💻 이지수:

이번 프로젝트에서 django로 백엔드를 개발하고 웹 페이지의 전반적인 작동을 할 수 있도록 기능을 구현했습니다.
프로젝트를 진행하면서 웹 페이지가 어떻게 동작하는지 익히고 django의 구성 및 각 파일들의 역할에 대해서 많이 배웠습니다.처음에는 Database 테이블을 어떻게 구축해야할 지 막막했는데 필요한 데이터가 어떤 것들이 있는 지 그리고 어떤 구조로 만들어야 DB를 효율적으로 구축할 수 있을지 고민을 스스로 많이 할 수 있어 좋은 기회가 되었다고 생각합니다. 마지막으로 프로젝트의 진행 상황을 쉽게 알 수 있도록 jira와 confluence를 통해 문서를 관리하고 일정을 조율하는 것이 굉장히 의미가 있었다고 생각합니다.

### 👩‍💻 이진섭: 
다른 팀원들과 함께 이렇게 오랜 기간 프로젝트를 진행한 것은 처음이었고, 때로는 의견 차이와 코딩의 어려움도 있었지만, 결국 무사히 완성하게 되어 정말 기쁘고 행복합니다.

### 👨‍💻 오종수:
초기 기획과 목표 설정이 부족했던 점이 프로젝트 전반에 예상치 못한 어려움을 초래한 것이 아쉬웠습니다.
