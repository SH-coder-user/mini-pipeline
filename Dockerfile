FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential tzdata \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
COPY .env /app/.env

# 시간대
ENV TZ=Asia/Seoul

# 기본은 아무 것도 실행하지 않음(서비스별로 커맨드 지정)
CMD ["python", "-c", "print('base image ready')"]

