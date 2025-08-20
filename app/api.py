import os
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
import pandas as pd
from app.pipeline import run_etl, pg_url

app = FastAPI(title="Mini Pipeline API")

# ✅ 전역 엔진 1회 생성(모든 곳에서 공용)
engine = create_engine(pg_url(), pool_pre_ping=True)

@app.on_event("startup")
def ensure_tables():
    # ✅ API 기동 시 스키마 보장(없으면 생성)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_date (
              order_date TIMESTAMP,
              year INT,
              month INT,
              day INT,
              date_key INT PRIMARY KEY
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fact_orders (
              order_id TEXT PRIMARY KEY,
              date_key INT REFERENCES dim_date(date_key) ON DELETE CASCADE,
              product TEXT,
              region TEXT,
              unit_price INT,
              quantity INT,
              revenue BIGINT
            );
        """))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run-etl")
def trigger_etl(rows: int = None):
    rows = rows or int(os.getenv("ETL_ROWS", "300"))
    run_etl(rows=rows, use_postgres=True)
    return {"ok": True, "rows": rows}

def query_df(sql: str):
    with engine.begin() as conn:
        return pd.read_sql(text(sql), conn)

@app.get("/orders/daily")
def orders_daily():
    sql = """
    SELECT d.order_date::date AS order_date, SUM(f.revenue) AS revenue
    FROM fact_orders f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY 1
    ORDER BY 1;
    """
    try:
        return query_df(sql).to_dict(orient="records")
    except ProgrammingError:
        return []  # 테이블 없으면 빈 배열

@app.get("/orders/by_region")
def orders_by_region():
    sql = """
    SELECT region, SUM(revenue) AS revenue
    FROM fact_orders
    GROUP BY 1
    ORDER BY 2 DESC;
    """
    try:
        return query_df(sql).to_dict(orient="records")
    except ProgrammingError:
        return []

@app.get("/orders/by_product")
def orders_by_product():
    sql = """
    SELECT product, SUM(revenue) AS revenue
    FROM fact_orders
    GROUP BY 1
    ORDER BY 2 DESC;
    """
    try:
        return query_df(sql).to_dict(orient="records")
    except ProgrammingError:
        return []

@app.get("/orders/kpis")
def kpis():
    # ✅ COALESCE로 NULL 방지
    sql = """
    SELECT COUNT(DISTINCT order_id) AS orders,
           COALESCE(SUM(revenue), 0) AS total_revenue,
           COALESCE(AVG(revenue), 0) AS avg_revenue
    FROM fact_orders;
    """
    try:
        df = query_df(sql)
        if df.empty:
            return {"orders": 0, "total_revenue": 0, "avg_revenue": 0}
        return df.to_dict(orient="records")[0]
    except ProgrammingError:
        return {"orders": 0, "total_revenue": 0, "avg_revenue": 0}

