import os
from psycopg_pool import ConnectionPool

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Falta DATABASE_URL (posa'l a .env)")

pool = ConnectionPool(conninfo=DATABASE_URL, min_size=1, max_size=5)

def fetch_all(query: str, params=None):
    params = params or ()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

def fetch_one(query: str, params=None):
    params = params or ()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()
