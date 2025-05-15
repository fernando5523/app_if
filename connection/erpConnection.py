import requests

class erpConnection:
    """
    Clase para establecer conexión con Dynamics 365 Finance & Operations mediante OAuth2.
    """

    __ENDPOINT = "https://login.microsoftonline.com/ceb88b8e-4e6a-4561-a112-5cf771712517/oauth2/token"

    def __init__(self, erpCredential: dict):
        """
        Inicializa la clase con las credenciales de Dynamics 365 Finance & Operations.

        Args:
        erpCredential (dict): Un diccionario que contiene las credenciales necesarias para autenticarse en Dynamics 365 Finance & Operations.
        """
        self.__erpCredential = erpCredential
        self.__erpToken = None

    def get_token_erp(self):
        """
        Obtiene el token de acceso para interactuar con Dynamics 365 Finance & Operations.

        Returns:
        str: El token de acceso en formato "Bearer {token}".
        """
        try:
            __request = requests.post(self.__ENDPOINT, self.__erpCredential)

            if __request.status_code == 200:
                self.__erpToken = "Bearer {0}".format(__request.json()["access_token"])

        except Exception as e:
            self.__erpToken = None

            print(
                "Error: No se genero el token para acceder a Dynamics 365 Finance & Operations",
                str(e),
            )

        return self.__erpToken
