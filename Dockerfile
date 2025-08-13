FROM python:3.11-slim

# 시스템 기본 패키지
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 소스 복사
COPY app /app/app
# 데이터 저장 디렉토리(볼륨으로도 사용 가능)
RUN mkdir -p /app/data
VOLUME ["/app/data"]

EXPOSE 8501
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

