import os
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Falta DATABASE_URL")

def _connect():
    # dict_row fa que fetchone/fetchall retorni dicts (més còmode pel JSON)
    return psycopg.connect(DATABASE_URL, connect_timeout=10, row_factory=dict_row)

def fetch_all(query: str, params=None):
    params = params or ()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

def fetch_one(query: str, params=None):
    params = params or ()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()

def execute_one(query: str, params=None):
    params = params or ()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()
