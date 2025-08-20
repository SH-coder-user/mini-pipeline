import os
import requests
import streamlit as st
import pandas as pd

API_URL = os.getenv("API_URL", "http://api:8000")

st.set_page_config(page_title="미니 데이터 파이프라인", page_icon="📊", layout="wide")
st.title("📊 미니 데이터 파이프라인 대시보드")
st.caption("가짜 주문 데이터 → ETL → Postgres → FastAPI → Streamlit")

with st.sidebar:
    st.header("⚙️ 작업")
    rows = st.slider("생성할 주문 수", min_value=100, max_value=1000, value=300, step=50)
    if st.button("1) 샘플 데이터 생성 & ETL 실행"):
        r = requests.post(f"{API_URL}/run-etl", params={"rows": rows}, timeout=60)
        if r.ok:
            st.success(f"ETL 실행 완료 (rows={rows})")
        else:
            st.error(f"실패: {r.status_code}")
    st.caption(f"API: {API_URL}")

def fetch_json(path: str):
    r = requests.get(f"{API_URL}{path}", timeout=30)
    r.raise_for_status()
    return r.json()

try:
    k = fetch_json("/orders/kpis")
    c1, c2, c3 = st.columns(3)
    c1.metric("총 매출", f"{int(k['total_revenue']):,} 원")
    c2.metric("총 주문 수", f"{int(k['orders']):,} 건")
    c3.metric("평균 주문 금액", f"{int(k['avg_revenue']):,} 원")

    st.divider()
    st.subheader("📈 일자별 매출 추이")
    daily = pd.DataFrame(fetch_json("/orders/daily"))
    if not daily.empty:
        daily["order_date"] = pd.to_datetime(daily["order_date"])
        st.line_chart(daily.set_index("order_date"))
    else:
        st.info("데이터가 없습니다. 좌측에서 ETL을 먼저 실행하세요.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📍 지역별 매출")
        by_region = pd.DataFrame(fetch_json("/orders/by_region"))
        if not by_region.empty:
            st.bar_chart(by_region.set_index("region"))

    with col2:
        st.subheader("📦 제품별 매출")
        by_product = pd.DataFrame(fetch_json("/orders/by_product"))
        if not by_product.empty:
            st.bar_chart(by_product.set_index("product"))

except Exception as e:
    st.error(f"API 호출 실패: {e}")
    st.info("컨테이너가 모두 올라왔는지 확인하세요.")

