import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd
from pipeline import run_etl, DB_FILE

st.set_page_config(page_title="미니 데이터 파이프라인", page_icon="📊", layout="wide")
st.title("📊 미니 데이터 파이프라인 대시보드")
st.caption("가짜 주문 데이터 → ETL → SQLite → 시각화 (Streamlit)")

# 사이드바
with st.sidebar:
    st.header("⚙️ 작업")
    rows = st.slider("생성할 주문 수", min_value=100, max_value=1000, value=300, step=50)
    if st.button("1) 샘플 데이터 생성 & ETL 실행"):
        csv, db = run_etl(rows)
        st.success(f"CSV: {csv.name}, DB: {db.name}")
    st.divider()
    st.caption("DB 파일 경로")
    st.code(str(DB_FILE))

# 데이터 로드
def load_df():
    if not Path(DB_FILE).exists():
        st.warning("DB가 없습니다. 왼쪽에서 먼저 ETL을 실행해주세요!")
        return None, None
    conn = sqlite3.connect(DB_FILE)
    fact = pd.read_sql_query("SELECT * FROM fact_orders", conn)
    dim = pd.read_sql_query("SELECT * FROM dim_date", conn)
    conn.close()
    return fact, dim

fact, dim = load_df()
if fact is not None:
    # KPI
    total_rev = int(fact["revenue"].sum())
    total_ord = fact["order_id"].nunique()
    avg_basket = fact["revenue"].mean()

    c1, c2, c3 = st.columns(3)
    c1.metric("총 매출", f"{total_rev:,.0f} 원")
    c2.metric("총 주문 수", f"{total_ord:,} 건")
    c3.metric("평균 주문 금액", f"{avg_basket:,.0f} 원")

    st.divider()

    # 일자별 매출
    st.subheader("📈 일자별 매출 추이")
    df_daily = fact.copy()
    # 날짜 되살리기 (dim_date 조인 없이 간단히)
    df_daily["order_date"] = df_daily["date_key"].astype(str).apply(
        lambda x: pd.to_datetime(x, format="%Y%m%d")
    )
    daily = df_daily.groupby("order_date", as_index=False)["revenue"].sum()
    st.line_chart(daily.set_index("order_date"))

    # 지역/제품별 분석
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📍 지역별 매출")
        by_region = fact.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
        st.bar_chart(by_region.set_index("region"))

    with col2:
        st.subheader("📦 제품별 매출")
        by_product = fact.groupby("product", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
        st.bar_chart(by_product.set_index("product"))

    st.divider()
    st.subheader("원천 테이블 미리보기")
    st.dataframe(fact.head(30))

