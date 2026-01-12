from __future__ import annotations
import psycopg
from psycopg.rows import dict_row
from app.config import settings

def conn():
    return psycopg.connect(
        host=settings.PG_HOST,
        port=settings.PG_PORT,
        dbname=settings.PG_DB,
        user=settings.PG_USER,
        password=settings.PG_PASSWORD,
        row_factory=dict_row,
    )

def run_sql_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(sql)
        c.commit()
