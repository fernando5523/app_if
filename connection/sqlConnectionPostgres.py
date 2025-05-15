import psycopg2
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde un archivo .env

class SQLConnectionPostgres:
    def __init__(self):
        pass

    @contextmanager
    def set_connection_database(self):
        """
        Context manager to handle the database connection.
        """
        conn = None
        try:
            conn = psycopg2.connect(
                host=os.getenv("APP_DB_TOKEN_HOST"),
                dbname=os.getenv("APP_DB_TOKEN_NAME"),
                user=os.getenv("APP_DB_TOKEN_USER"),
                password=os.getenv("APP_DB_TOKEN_PASS"),
                port=os.getenv("APP_DB_TOKEN_PORT")
            )
            yield conn
        except psycopg2.OperationalError as e:
            print(f"Operational error: {e}")
            raise
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
        finally:
            if conn:
                conn.close()
