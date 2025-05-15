# Libraries Packages
import hashlib


class textEncrypt:
    def set_encrypt_password(self, text: str):
        __passwordEncrypt = hashlib.new("sha256", text.encode("utf-8"))

        return __passwordEncrypt.hexdigest()
