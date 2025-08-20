import os
import datetime as dt
import pandas as pd
import sqlite3
from pathlib import Path
import random
from sqlalchemy import create_engine, text

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_FILE = DATA_DIR / f"orders_{dt.date.today().strftime('%Y%m%d')}.csv"
DB_FILE = DATA_DIR / "warehouse.db"

PRODUCTS = ["키보드", "마우스", "모니터", "노트북 스탠드", "USB 허브"]
REGIONS = ["서울", "부산", "대구", "광주", "대전", "인천"]
SEED = 42
random.seed(SEED)

def pg_url():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "appuser")
    pw   = os.getenv("POSTGRES_PASSWORD", "apppw")
    db   = os.getenv("POSTGRES_DB", "warehouse")
    return f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}"

def generate_raw_orders(n: int = 300):
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

def transform(df: pd.DataFrame):
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["revenue"] = df["unit_price"] * df["quantity"]
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["day"] = df["order_date"].dt.day

    dim_date = df[["order_date", "year", "month", "day"]].drop_duplicates().copy()
    dim_date["date_key"] = dim_date["order_date"].dt.strftime("%Y%m%d").astype(int)

    fact_orders = df.copy()
    fact_orders["date_key"] = fact_orders["order_date"].dt.strftime("%Y%m%d").astype(int)
    fact_orders = fact_orders[[
        "order_id", "date_key", "product", "region", "unit_price", "quantity", "revenue"
    ]]
    return dim_date, fact_orders

def load_sqlite(dim_date, fact_orders, db_path=DB_FILE):
    with sqlite3.connect(db_path) as conn:
        dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)
        fact_orders.to_sql("fact_orders", conn, if_exists="replace", index=False)

def load_postgres(dim_date, fact_orders):
    engine = create_engine(pg_url(), pool_pre_ping=True)
    with engine.begin() as conn:
        # 스키마 테이블 생성 (간단 DDL)
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
              date_key INT REFERENCES dim_date(date_key),
              product TEXT,
              region TEXT,
              unit_price INT,
              quantity INT,
              revenue BIGINT
            );
        """))
        # 덮어쓰기 대신 간단히 truncate 후 insert
        conn.execute(text("TRUNCATE TABLE fact_orders, dim_date;"))
        dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
        fact_orders.to_sql("fact_orders", conn, if_exists="append", index=False)

def transform_and_load(csv_path=RAW_FILE, use_postgres=True):
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    df = pd.read_csv(csv_path)
    dim_date, fact_orders = transform(df)
    if use_postgres:
        load_postgres(dim_date, fact_orders)
    else:
        load_sqlite(dim_date, fact_orders)
    return "postgres" if use_postgres else "sqlite"

def run_etl(rows: int = 300, use_postgres: bool = True):
    csv_path = generate_raw_orders(rows)
    target = transform_and_load(csv_path, use_postgres=use_postgres)
    return csv_path, target

if __name__ == "__main__":
    rows = int(os.getenv("ETL_ROWS", "300"))
    csv, target = run_etl(rows, use_postgres=True)
    print(f"CSV 생성: {csv}")
    print(f"적재 대상: {target}")

