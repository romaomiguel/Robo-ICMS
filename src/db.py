import os
import psycopg2
from contextlib import contextmanager


@contextmanager
def get_connection():
    conn = psycopg2.connect(
        host=os.environ.get('PGHOST'),
        port=os.environ.get('PGPORT', '5432'),
        dbname=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
    )
    try:
        yield conn
    finally:
        conn.close()


def obter_ip_cliente(request):
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr


def registrar_processamento(ip_origem, quantidade_notas, status='sucesso'):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO historico_processamento (ip_origem, quantidade_notas, status)
                VALUES (%s, %s, %s)
                """,
                (ip_origem, quantidade_notas, status)
            )
            conn.commit()
