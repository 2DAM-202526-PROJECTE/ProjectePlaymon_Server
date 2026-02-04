import os
from psycopg_pool import ConnectionPool

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Falta DATABASE_URL")

# Serverless-friendly: no obrir 5 connexions de cop
pool = ConnectionPool(conninfo=DATABASE_URL, min_size=0, max_size=1, open=False)

def fetch_all(query: str, params=None):
    params = params or ()
    if pool.closed:
        pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

def fetch_one(query: str, params=None):
    params = params or ()
    if pool.closed:
        pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()
