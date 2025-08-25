# 📊 Mini Data Pipeline Project
가짜 주문 데이터 → ETL → PostgreSQL 적재 → API → 대시보드 시각화
**Docker Compose + GitHub Actions + Docker Hub 자동 배포 파이프라인**

---

## 🚀 프로젝트 개요
데이터 엔지니어링 기본기를 빠르게 체험할 수 있는 **학습형 미니 파이프라인**을 구축했습니다.
로컬 실행부터 Docker 컨테이너화, CI/CD를 통한 배포까지 전 과정을 담았습니다.

---

## 📌 핵심 기능
- **ETL 파이프라인**: 주문 데이터 생성 → 변환 → PostgreSQL 적재
- **데이터베이스**: PostgreSQL 16 (초기 버전은 SQLite)
- **API 서버**: FastAPI (ETL 트리거 & 데이터 조회)
- **대시보드**: Streamlit (API 호출 기반 KPI/차트)
- **스케줄러**: APScheduler (매일 09:00 자동 ETL 실행)
- **CI/CD**: GitHub Actions → Docker Hub 자동 빌드/푸시
- **컨테이너 오케스트레이션**: docker-compose로 전체 실행

---

## 🛠 기술 스택
| 영역             | 기술 |
|------------------|------|
| 언어             | Python 3.11 |
| 데이터 처리      | pandas |
| 대시보드         | Streamlit |
| API 서버         | FastAPI, Uvicorn |
| 데이터베이스     | PostgreSQL, SQLite(초기) |
| 배포/환경        | Docker, docker-compose |
| 스케줄링         | APScheduler |
| CI/CD            | GitHub Actions, Docker Hub |

---

## 📂 프로젝트 구조
```
mini-pipeline/
├─ app/
│  ├─ pipeline.py        # ETL 파이프라인
│  ├─ api.py             # FastAPI 서버
│  ├─ streamlit_app.py   # Streamlit 대시보드
│  ├─ scheduler.py       # ETL 스케줄러
│  └─ requirements.txt   # 의존성 목록
├─ data/                 # CSV/DB 저장 (볼륨 마운트)
├─ .env                  # 환경변수 설정
├─ Dockerfile            # 베이스 이미지
├─ docker-compose.yml    # 서비스 오케스트레이션
├─ .github/workflows/    # GitHub Actions
│  └─ docker-image.yml
└─ README.md
```

---

## ⚙️ 실행 방법

### 1️⃣ 로컬 실행
```bash
python3 -m pip install -r app/requirements.txt
python3 app/pipeline.py
streamlit run app/streamlit_app.py
```
- 접속: http://localhost:8501

---

### 2️⃣ Docker 단일 실행
```bash
docker build -t mini-pipeline:local .
docker run --rm -p 8501:8501 -v $(pwd)/data:/app/data mini-pipeline:local
```

---

### 3️⃣ docker-compose (전체 실행)
```bash
docker compose build
docker compose up -d
```
- 대시보드: http://localhost:8501
- API: http://localhost:8000/health

---

## 🔄 GitHub Actions → Docker Hub 자동 배포
1. Docker Hub 리포지토리 생성: `username/mini-pipeline`
2. GitHub Secrets 추가:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`
3. main 브랜치 push 시 자동 빌드 & 푸시
4. 서버에서 실행:
```bash
docker compose pull
docker compose up -d
```

---

## 📈 대시보드 미리보기
![dashboard preview](images/dashboard-preview.jpg)

- 일자별 매출 추이
- 지역별/제품별 매출 분석
- 총 매출, 주문 수, 평균 주문 금액 KPI

---

## 📅 개발 진행 플랜
| Day | 작업 내용 |
|-----|-----------|
| 1일차 | CSV 생성 + SQLite 적재 |
| 2일차 | Streamlit 대시보드 |
| 3일차 | Dockerfile 작성 |
| 4일차 | GitHub 연동 |
| 5일차 | Docker Hub 설정 |
| 6일차 | GitHub Actions CI/CD |
| 7일 ~ 10일 | PostgreSQL + FastAPI + Scheduler + Compose 확장 |

---

## 🛡️ 주요 이슈 해결
- FK로 인한 TRUNCATE 오류 → `TRUNCATE fact_orders, dim_date;` 동시 실행
- ModuleNotFoundError → `from app.pipeline import ...` + `app/__init__.py`
- TabError → 스페이스 4칸 들여쓰기 통일
- UndefinedTable → API startup에서 스키마 보장, 빈값은 0/[] 반환
- sqlite_master 오류 → `to_sql(..., conn, ...)` 사용 (`conn.connection` 금지)

---

## 💡 확장 아이디어
- Airflow/Dagster로 워크플로우 관리
- Great Expectations로 데이터 품질 검증
- 클라우드 DB(RDS, Cloud SQL) 연동
- 대시보드에 필터/권한/캐시 기능 추가

---

## 👤 Author
- GitHub: [KSH](https://github.com/SH-coder-user/mini-pipeline)
- Docker Hub: [dockerhub-KSH](https://hub.docker.com/repository/docker/skadlf915/mini-pipeline/general)

---
