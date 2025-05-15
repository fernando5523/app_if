# Libraries Packages
import datetime
import os


class urlFile:
    def get_upload_folder():
        __dateNow = datetime.date.today().strftime("%d/%m/%Y").split("/")

        __uri1 = os.path.abspath("static/uploads/" + __dateNow[2])
        __uri2 = os.path.abspath(__uri1 + "/" + __dateNow[1])
        __uri3 = os.path.abspath(__uri2 + "/" + __dateNow[0])

        # Crear las carpetas si no existen
        if not os.path.exists(__uri1):
            os.makedirs(__uri1)

        if not os.path.exists(__uri2):
            os.makedirs(__uri2)

        if not os.path.exists(__uri3):
            os.makedirs(__uri3)

        return __uri3
