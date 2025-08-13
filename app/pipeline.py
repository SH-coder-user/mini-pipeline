import os
import datetime as dt
import pandas as pd
import sqlite3
from pathlib import Path
import random

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_FILE = DATA_DIR / f"orders_{dt.date.today().strftime('%Y%m%d')}.csv"
DB_FILE = DATA_DIR / "warehouse.db"

PRODUCTS = ["키보드", "마우스", "모니터", "노트북 스탠드", "USB 허브"]
REGIONS = ["서울", "부산", "대구", "광주", "대전", "인천"]
SEED = 42
random.seed(SEED)

def generate_raw_orders(n: int = 300):
    """가짜 주문 데이터 생성 → CSV 저장"""
    dates = pd.date_range(end=dt.date.today(), periods=30).to_pydatetime().tolist()
    rows = []
    for _ in range(n):
        d = random.choice(dates)
        product = random.choice(PRODUCTS)
        region = random.choice(REGIONS)
        price = random.randint(10000, 300000)
        qty = random.randint(1, 5)
        rows.append({
            "order_id": f"O{random.randint(100000,999999)}",
            "order_date": d.date().isoformat(),
            "product": product,
            "unit_price": price,
            "quantity": qty,
            "region": region,
        })
    df = pd.DataFrame(rows).drop_duplicates(subset=["order_id"])
    df.to_csv(RAW_FILE, index=False, encoding="utf-8")
    return RAW_FILE

def transform_and_load(csv_path=RAW_FILE, db_path=DB_FILE):
    """CSV → 변환(매출 등 계산) → SQLite 적재"""
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    # 기본 클린업
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["revenue"] = df["unit_price"] * df["quantity"]
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["day"] = df["order_date"].dt.day

    # 차원/사실 테이블 나누기 (아주 간단 버전)
    dim_date = df[["order_date", "year", "month", "day"]].drop_duplicates().copy()
    dim_date["date_key"] = dim_date["order_date"].dt.strftime("%Y%m%d").astype(int)

    fact_orders = df.copy()
    fact_orders["date_key"] = fact_orders["order_date"].dt.strftime("%Y%m%d").astype(int)
    fact_orders = fact_orders[[
        "order_id", "date_key", "product", "region", "unit_price", "quantity", "revenue"
    ]]

    with sqlite3.connect(db_path) as conn:
        dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)
        fact_orders.to_sql("fact_orders", conn, if_exists="replace", index=False)

    return db_path

def run_etl(rows=300):
    csv_path = generate_raw_orders(rows)
    db_path = transform_and_load(csv_path)
    return csv_path, db_path

if __name__ == "__main__":
    csv, db = run_etl()
    print(f"CSV 생성: {csv}")
    print(f"DB 적재: {db}")

