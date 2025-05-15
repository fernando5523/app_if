from dotenv import load_dotenv
import os, pandas
from connection.sqlConnection import sqlConnection

class sqlController:
    """
    Clase para controlar las operaciones con la base de datos SQL.
    """
    
    # Variables Globales
    load_dotenv()

    __APP_DB_HOST = os.getenv("APP_DB_HOST")
    __APP_DB_NAME = os.getenv("APP_DB_NAME")
    __APP_DB_USER = os.getenv("APP_DB_USER")
    __APP_DB_PASS = os.getenv("APP_DB_PASS")

    __API_DB_HOST = os.getenv("API_DB_HOST")
    __API_DB_NAME = os.getenv("API_DB_NAME")
    __API_DB_USER = os.getenv("API_DB_USER")
    __API_DB_PASS = os.getenv("API_DB_PASS")

    def __init__(self, sqlArguments: dict = None):
        """
        Inicializa la clase con los argumentos de la consulta SQL.

        Args:
        sqlArguments (dict): Un diccionario que contiene los argumentos de la consulta SQL.
        """
        self.__sqlArguments = sqlArguments

        if sqlArguments["sqlType"] == "APP":
            __sqlCredential = {
                "DB_HOST": self.__APP_DB_HOST,
                "DB_NAME": self.__APP_DB_NAME,
                "DB_USER": self.__APP_DB_USER,
                "DB_PASS": self.__APP_DB_PASS,
            }

        else:
            __sqlCredential = {
                "DB_HOST": self.__API_DB_HOST,
                "DB_NAME": self.__API_DB_NAME,
                "DB_USER": self.__API_DB_USER,
                "DB_PASS": self.__API_DB_PASS,
            }

        self.__sqlConnection = sqlConnection(__sqlCredential).set_connection_database()

    def set_procedure_insert(self):
        """
        Inserta datos en la base de datos SQL.

        Returns:
        bool: True si la inserción es exitosa, False de lo contrario.
        """
        if self.__sqlConnection is not None:
            __sqlQuery = self.__sqlArguments["sqlQuery"]
            __sqlEntry = self.__sqlArguments["sqlEntry"]

            try:
                __sqlCursor = self.__sqlConnection.cursor()
                __sqlCursor.execute(__sqlQuery, __sqlEntry)
                __sqlData = __sqlCursor.fetchone().RSPDB
                self.__sqlConnection.commit()
                __sqlCursor.close()
                self.__sqlConnection.close()

            except Exception as e:
                __sqlData = None
                print("Error: No se lograron insertar los datos.", str(e))
        else:
            __sqlData = None

        return __sqlData

    def set_procedure_update(self):
        """
        Actualiza datos en la base de datos SQL.

        Returns:
        bool: True si la actualización es exitosa, False de lo contrario.
        """
        if self.__sqlConnection is not None:
            __sqlQuery = self.__sqlArguments["sqlQuery"]
            __sqlEntry = self.__sqlArguments["sqlEntry"]

            try:
                __sqlCursor = self.__sqlConnection.cursor()
                __sqlCursor.execute(__sqlQuery, __sqlEntry)
                __sqlData = __sqlCursor.fetchone().RSPDB
                self.__sqlConnection.commit()
                __sqlCursor.close()
                self.__sqlConnection.close()

            except Exception as e:
                __sqlData = None
                print("Error: No se lograron actualizar los datos.", str(e))
        else:
            __sqlData = None

        return __sqlData

    def get_procedure_select(self):
        """
        Obtiene datos de la base de datos SQL utilizando una consulta almacenada.

        Returns:
        pandas.DataFrame: Un DataFrame de pandas que contiene los datos obtenidos.
        """
        if self.__sqlConnection is not None:
            __sqlColumns = self.__sqlArguments["sqlColumns"]
            __sqlQuery = self.__sqlArguments["sqlQuery"]
            __sqlEntry = self.__sqlArguments["sqlEntry"]

            try:
                __sqlCursor = self.__sqlConnection.cursor()
                __sqlResult = __sqlCursor.execute(__sqlQuery, __sqlEntry).fetchall()
                __sqlData = pandas.DataFrame.from_records(__sqlResult, columns=__sqlColumns)
                __sqlCursor.close()
                self.__sqlConnection.close()

            except Exception as e:
                __sqlData = None
                print("Error: La consulta proporcionada no contiene datos.", str(e))
        else:
            __sqlData = None

        return __sqlData

    def get_statement_select(self):
        """
        Obtiene datos de la base de datos SQL utilizando una consulta directa.

        Returns:
        pandas.DataFrame: Un DataFrame de pandas que contiene los datos obtenidos.
        """
        if self.__sqlConnection is not None:
            __sqlColumns = self.__sqlArguments["sqlColumns"]
            __sqlQuery = self.__sqlArguments["sqlQuery"]

            try:
                __sqlCursor = self.__sqlConnection.cursor()
                __sqlResult = __sqlCursor.execute(__sqlQuery).fetchall()
                __sqlData = pandas.DataFrame.from_records(__sqlResult, columns=__sqlColumns)
                __sqlCursor.close()
                self.__sqlConnection.close()

            except Exception as e:
                __sqlData = None
                print("Error: La consulta proporcionada no contiene datos.", str(e))
        else:
            __sqlData = None

        return __sqlData
