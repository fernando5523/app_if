import psycopg2
from connection.sqlConnectionPostgres import SQLConnectionPostgres

class sqlControllerPostres:
    def __init__(self):
        self.connection = SQLConnectionPostgres()

    def select_query(self, query):
        """
        Execute a SELECT query and return results.
        """
        try:
            with self.connection.set_connection_database() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
            return results
        except psycopg2.Error as e:
            print(f"Error executing select query: {e}")
            return None
