import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# ===============================
# Cargar variables de entorno
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '..', 'docker', '.env')

load_dotenv(ENV_PATH)

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD")
}

# ===============================
# Conexión
# ===============================
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# ===============================
# Ejecutar queries
# ===============================
def execute_query(query, params=None, fetch=True):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                result = cur.fetchall()
            else:
                conn.commit()
                result = None
        return result
    finally:
        conn.close()
