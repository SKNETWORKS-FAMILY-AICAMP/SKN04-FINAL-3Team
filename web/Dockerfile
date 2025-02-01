# 베이스 이미지
FROM python:3.11

RUN apt-get update && apt-get install -y default-jdk
ENV JAVA_HOME /usr/lib/jvm/default-java
ENV PATH $JAVA_HOME/bin:$PATH

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 생성
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 애플리케이션 소스 복사
COPY . /app/

# 포트 개방
EXPOSE 8000

# 명령어 설정
CMD ["gunicorn", "web.wsgi:application", "--bind", "0.0.0.0:8000"]


