from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import json, math, os, pandas, requests
from connection.erpConnection import erpConnection

class erpController:
    """
    Clase para controlar las operaciones con datos de Dynamics 365 Finance & Operations.
    """

    # Variables Globales
    load_dotenv()

    __APP_MODE = os.getenv("APP_MODE")
    __APP_WORKERS = int(os.getenv("APP_WORKERS"))

    print("ERP Controller | APP_MODE: {0}".format(__APP_MODE))

    if __APP_MODE == "Debug":
        __ERP_CREDENTIAL = {
            "client_id": os.getenv("ERP_CLIENT_ID"),
            "client_secret": os.getenv("ERP_CLIENT_SECRET"),
            "resource": os.getenv("ERP_DEBUG"),
            "grant_type": "client_credentials",
        }
    else:
        __ERP_CREDENTIAL = {
            "client_id": os.getenv("ERP_CLIENT_ID"),
            "client_secret": os.getenv("ERP_CLIENT_SECRET"),
            "resource": os.getenv("ERP_PRODUCTION"),
            "grant_type": "client_credentials",
        }

    __ERP_CONNECTION = erpConnection(__ERP_CREDENTIAL)

    def __init__(self, erpQuery: dict = None):
        """
        Inicializa la clase con la consulta a la entidad de Dynamics 365 Finance & Operations.

        Args:
        erpQuery (dict): Un diccionario que contiene la consulta a la entidad de Dynamics 365 Finance & Operations.
        """
        self.__erpQuery = erpQuery
        self.__erpResult = None

    def __set_url_general(self):
        """
        Establece la URL base para la consulta de la entidad.

        Returns:
        str: La URL base para la consulta de la entidad.
        """
        __link = None

        if self.__erpQuery["odata_entity"] is not None:
            __link = "{0}/data/{1}/$count".format(
                self.__ERP_CREDENTIAL["resource"],
                self.__erpQuery["odata_entity"],
            )
            if self.__erpQuery["odata_filter"] is not None:
                __link += "?{0}".format(self.__erpQuery["odata_filter"])
        else:
            print("Error: La entidad en la consulta proporcionada es None")

        return __link

    def __set_url_parts(self):
        """
        Establece las partes de la URL para dividir la consulta en lotes.

        Returns:
        list: Una lista de URLs para la consulta dividida en lotes.
        """
        __link = None
        __payload = {}
        __urls, __iterator = [], []
        __collect, __multiple, __lote = 0, 0, 10000

        __url = self.__set_url_general()

        if __url is not None:
            __headers = {
                "Authorization": self.__ERP_CONNECTION.get_token_erp(),
                "Content-Type": "application/json",
            }
            __rows = int(requests.request("GET", __url, headers=__headers, data=__payload).text.replace("ï»¿", ""))

            if __rows > 0:
                __iterator = list(range(math.ceil(__rows / __lote)))
                __multiple = __rows % __lote
                __link = "{0}/data/{1}".format(
                    self.__ERP_CREDENTIAL["resource"],
                    self.__erpQuery["odata_entity"],
                )

                if self.__erpQuery["odata_filter"] is not None:
                    __link += "?$skip=rvar_s&$top=rvar_t&{0}".format(self.__erpQuery["odata_filter"])
                else:
                    __link += "?$skip=rvar_s&$top=rvar_t"

                for i in __iterator:
                    j = __link.replace("rvar_s", str(__collect))

                    if i != __iterator[-1]:
                        k = j.replace("rvar_t", str(__lote))
                    else:
                        k = j.replace("rvar_t", str(__multiple))

                    __urls.append(k)
                    __collect += __lote
            else:
                print("Error: La consulta proporcionada para la entidad " + self.__erpQuery["odata_entity"] + " no contiene datos")
        else:
            print("Error: La url no fue generada para la consulta de la entidad " + self.__erpQuery["odata_entity"])

        return __urls

    def __set_records_entity(self, url: str):
        """
        Obtiene los registros de la entidad a partir de una URL.

        Args:
        url (str): La URL para obtener los registros de la entidad.

        Returns:
        pandas.DataFrame: Un DataFrame de pandas que contiene los registros de la entidad.
        """
        __json = None
        __payload = {}

        __headers = {
            "Authorization": self.__ERP_CONNECTION.get_token_erp(),
            "Content-Type": "application/json",
        }

        __rows = requests.request("GET", url, headers=__headers, data=__payload)

        if __rows.status_code == 401:
            __headers["Authorization"] = self.__ERP_CONNECTION.get_token_erp()
            __rows = requests.request("GET", url, headers=__headers, data=__payload)

        __rows.encoding = "utf-8"
        __json = __rows.json()["value"]
        __data = pandas.DataFrame.from_dict(__json, orient="columns")

        return __data

    def get_records_odata(self):
        """
        Obtiene los registros de la entidad de Dynamics 365 Finance & Operations.

        Returns:
        pandas.DataFrame: Un DataFrame de pandas que contiene los registros de la entidad.
        """
        __data = []
        __url = self.__set_url_parts()

        with ThreadPoolExecutor(max_workers=self.__APP_WORKERS) as pool:
            __rows = pool.map(self.__set_records_entity, __url)

        for row in __rows:
            __data.append(row)

        if len(__data) > 0:
            self.__erpResult = pandas.concat(__data)
            
        print("Consulta de la entidad " + self.__erpQuery["odata_entity"] + " realizada con éxito")

        return self.__erpResult

    def set_records_odata(self):
        """
        Inserta registros en la entidad de Dynamics 365 Finance & Operations.

        Returns:
        bool: True si la inserción es exitosa, False de lo contrario.
        """
        __link = "{0}/data/{1}/".format(
            self.__ERP_CREDENTIAL["resource"],
            self.__erpQuery["odata_entity"],
        )

        __payload = json.dumps(self.__erpQuery["odata_object"])

        __headers = {
            "Authorization": self.__ERP_CONNECTION.get_token_erp(),
            "Content-Type": "application/json",
        }

        try:
            __response = requests.request("POST", __link, headers=__headers, data=__payload)
            if __response.status_code == 201:
                # Registro exitoso
                return True
            else:
                print(f"Error: {__response.text}")
                return False
        except requests.RequestException as e:
            # Manejo de errores de conexión
            print(f"Request failed: {e}")
            return False
