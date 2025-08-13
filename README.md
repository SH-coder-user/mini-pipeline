# 미니 데이터 파이프라인 (초보자용 7일 코스)

가짜 주문 데이터 → ETL → SQLite → Streamlit 대시보드.
Docker 이미지로 빌드하고 GitHub Actions로 Docker Hub에 자동 푸시합니다.

## 빠른 시작
```bash
python3 app/pipeline.py
streamlit run app/streamlit_app.py

