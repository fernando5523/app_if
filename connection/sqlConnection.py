# En el archivo sqlConnection.py

# import pyodbc

# class sqlConnection:
#     def __init__(self, sqlCredential: dict):
#         self.__erpCredential = sqlCredential

#     def set_connection_database(self):
#         SQL_ATTR_CONNECTION_TIMEOUT = 113

#         # Parámetros de conexión
#         # server = 'DESKTOP-SJI07SK\\SQLEXPRESS' # Nombre del servidor y nombre de la instancia
#         server = 'DESKTOP-JC1U73K\SQLEXPRESS' # Nombre del servidor y nombre de la instancia nueva
#         database = 'Proveedores2'  # Nombre de tu base de datos
#         driver = 'ODBC Driver 17 for SQL Server'  # ODBC Driver específico para SQL Server

#         try:
#             __connection = pyodbc.connect(
#                 f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;",
#                 timeout=1,
#                 attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: 1},
#             )
#         except Exception as e:
#             __connection = None
#             print(
#                 "Error: No se realizo la conexion a la base de datos " + database,
#                 str(e),
#             )

#         return __connection




# # # Paquetes y Librerias
import pyodbc


class sqlConnection:
    def __init__(self, sqlCredential: dict):
        self.__erpCredential = sqlCredential
        print(self.__erpCredential)

    def set_connection_database(self):
        SQL_ATTR_CONNECTION_TIMEOUT = 113

        try:

            __connection = pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server}"
                + ";SERVER="
                + self.__erpCredential["DB_HOST"]
                + ";DATABASE="
                + self.__erpCredential["DB_NAME"]
                + ";UID="
                + self.__erpCredential["DB_USER"]
                + ";PWD="
                + self.__erpCredential["DB_PASS"],
                timeout=10,
                attrs_before={SQL_ATTR_CONNECTION_TIMEOUT: 1},
            )

            print("Conexion exitosa a la base de datos")

        except Exception as e:
            __connection = None
            print(
                "Error: No se realizo la conexion a la base de datos " + self.__erpCredential["DB_NAME"],
                str(e),
            )

        return __connection
