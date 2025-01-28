# SKN04-FINAL-3Team

# 🤗 팀명 : 
 
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
- **모델**: pass
- **Retriever 구축**: pass
- **README 작성** 
### 👨‍💻 이지수
- **Front-end** : pass
- **Back-end**: pass
- **AWS 배포**: Django로 제작된 페이지를 AWS환경에서 배포


### 👩‍💻 이진섭
- **테스트 및 산출물 관리** : pass


### 👨‍💻 오종수
- **조장**
: pass
---

## 프로젝트 개요
~~- **상세 페이지 설계서 작성**~~
~~- **요구사항 정의서 작성**~~
~~- **streamlit으로 구현된 페이지를 django로 이식** ~~
~~- **AWS 배포**~~
pass~~

~~이 프로젝트는 다나와 사이트에서 노트북 제품 정보를 **크롤링**하여, 사용자가 입력하는 질문에 대해 할루시네이션이 없는 답변을 제공하는 **대화형 챗봇**  streamlit 페이지를 django로 이식하여 배포까지 진행하는 프로젝트입니다.~~

## Data

~~다나와 사이트(https://prod.danawa.com/list/?cate=112758)에서 셀레니움을 통해~~ ~~크롤링하여 노트북 데이터를 수집 하였습니다. ~~
<br>
~~수집한 데이터 : 노트북 모델명, 상세 스펙, 가격~~


## Preprocess

~~csv 파일로 저장된 데이터를 document에 저장하여 metadata를 추가하고 contents에 불필요한 문자를 제거하여 정제했습니다.~~
<br>
~~정제된 데이터를 'text-embedding-3-small'모델을 사용하여 Faiss DB에 임베딩하여 저장했습니다.~~

---



## 기술 스텍

| Data Modeling | SCM | Front-End / Back-End | Deploy |
|-----------------|--------|---------------------|------------------|
| ![BeautifulSoup](https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) <img src="https://img.shields.io/badge/langchain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white"><img src="https://img.shields.io/badge/openai-412991?style=for-the-badge&logo=openai&logoColor=white">|<img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white"/>| <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white"> | <img src="https://img.shields.io/badge/Amazon_AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white">

## Prerequisites



### Conda 환경 생성 및 활성화
```
conda env create -f environment.yml
conda activate best_laptop_env
```
---

### .env 환경변수 파일 필요 

<p>

```
OPENAI_API_KEY ="sk-*******************************************************************"
faiss_path ="./data/db"
```

### .env.prod 파일 필요
```
DEBUG=0
SECRET_KEY=****************************************
DJANGO_ALLOWED_HOSTS=localhost ******************* [::1]
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=postgres
SQL_USER=postgres
SQL_PASSWORD=****
SQL_HOST=best-laptop.c****************************
SQL_PORT=5432
```
### .env.prod.db 파일 필요
```
POSTGRES_USER=************************
POSTGRES_PASSWORD=***************************************
POSTGRES_DB=**************************
```


## Usage

AWS 에서 EC2 인스턴스을 만들어 다음 명령어를 입력
```cmd
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo docker-compose up -d --build
sudo docker-compose exec web python manage.py collectstatic
```
```cmd
본인이 설정한 EC2 환경의 Ip주소로 접속
```

## System Architecture

### 프로그램의 전체적인 구성 도표 삽입 및 설명

<p>
  <img src="readmeImage/Architecture.png" alt="이미지 설명" width="500" height="350">
</p>

저희 시스템은 Selenium을 통해 크롤링한 데이터를 FAISS(Vector DB)에 임베딩하여 벡터 기반 검색을 수행합니다.   
사용자가 입력한 질문은 retriever와 체인 모델을 거쳐, 저희가 개발한 모델로 응답이 생성됩니다.   
최종 결과는 배포된 웹 페이지를 통해 사용자에게 직관적으로 제공됩니다.  
 
---
## Test Case

### 잘못된 질문 예시 케이스
<img src="readmeImage\test1.png" alt="이미지 설명" width="" height="500">
<img src="readmeImage\test2.png" alt="이미지 설명" width="" height="500">

### 올바른 질문 예시 케이스
<img src="readmeImage\test3.png" alt="이미지 설명" width="" height="500">


## 수행 결과

**요구사항 정의서**
<p>
  <img src="readmeImage\SRS.png" alt="이미지 설명" width="" height="200">
</p>

**상세 페이지 설계서**
<p>
  <img src="readmeImage\detailpagestructre.png" alt="이미지 설명" width="500" height="350">
</p>


<br>
**Django로 구현하여 배포한 페이지**
<p>
  <img src="readmeImage\page.png" alt="이미지 설명" width="500" height="350">
</p>

위의 요구사항 정의서와 상세 페이지 설계서를 반영하여 Django를 통해 Front-end와 Back-end를 구축하고 AWS를 통해 배포 하였습니다.

## 한 줄 소감


### 👨‍💻 박병헌

### 👨‍💻 이지수

### 👩‍💻 이진섭


### 👨‍💻 오종수
