import json
from datetime import datetime
import pandas as pd

class jsonRead:
   
    def readHead(self, urlFile):
        try:
            # Abrir y leer el archivo JSON con codificación UTF-8 para manejar caracteres especiales
            with open(urlFile, 'r', encoding='utf-8') as file:
                data = json.load(file)
           
            # Extraer los campos requeridos del JSON
            ruc = data.get("ruc", "")
            serie = data.get("serie", "")
            fecha = data.get("fecha", "")
            tipo_moneda = data.get("tipo_moneda", "")

            # Validar que los campos no estén vacíos
            if not all([ruc, serie, fecha, tipo_moneda]):
                raise ValueError("Campos vacíos o nulos encontrados en el archivo JSON.")

            return {
                "VENDORID": ruc,
                "INVOICENUMBER": serie,
                "INVOICEDATE": fecha,
                "INVOICECURRENCY": tipo_moneda,
                "URLFILE": urlFile
            }
        except json.JSONDecodeError:
            print(f"Error en readHead: El archivo {urlFile} no tiene un formato JSON válido.")
            return None
        except FileNotFoundError:
            print(f"Error en readHead: El archivo {urlFile} no se encontró.")
            return None
        except ValueError as ve:
            print(f"Error en readHead: {str(ve)}")
            return None
        except Exception as e:
            print(f"Error inesperado en readHead: {str(e)}")
            return None

    def readJsonGrupo1(self, urlFile):
        try:
            # Abrir y leer el archivo JSON con codificación UTF-8 para manejar caracteres especiales
            with open(urlFile, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            products = data.get("items", [])
            
            # Verificar que haya productos en el JSON
            if not products:
                raise ValueError("No se encontraron productos en el archivo JSON.")
            
            # Estructura para almacenar datos procesados
            __jsonData = {
                "COD_PRODUCT": [],
                "PRODUCT_QUANTITY": [],
                "DESCRIPTION": [],
                "UNIT_PRICE": [],
                "SUB_TOTAL": [],
                "IGV": [],
                "TOTAL": []
            }
            
            # Recorrer items y procesar la información
            for product in products:
                codigo = product.get("codigo", "")
                cantidad = float(product.get("cantidad", 0))  # Convertir cantidad a float
                descripcion = product.get("descripcion", "")
                sub_total = float(product.get("sub_total", 0.00))  # Convertir sub_total a float
                isc = float(product.get("ISC", 0))  # Convertir ISC a float
                
                # Ajustar sub_total si hay ISC
                if isc != 0:
                    sub_total += isc
                
                # Calcular precio unitario
                val_unit = sub_total / cantidad if cantidad != 0 else 0
                igv = sub_total * 0.18
                total = sub_total + igv
                
                # Añadir los datos al diccionario
                __jsonData["COD_PRODUCT"].append(codigo)
                __jsonData["PRODUCT_QUANTITY"].append(round(cantidad, 4))
                __jsonData["DESCRIPTION"].append(descripcion)
                __jsonData["UNIT_PRICE"].append(round(val_unit, 4))
                __jsonData["SUB_TOTAL"].append(round(sub_total, 4))
                __jsonData["IGV"].append(round(igv, 4))
                __jsonData["TOTAL"].append(round(total, 4))
            
            # Convertir el diccionario a DataFrame
            df = pd.DataFrame(__jsonData)
            return df
        
        except json.JSONDecodeError:
            print(f"Error en readJsonGrupo1: El archivo {urlFile} no tiene un formato JSON válido.")
            return None
        except FileNotFoundError:
            print(f"Error en readJsonGrupo1: El archivo {urlFile} no se encontró.")
            return None
        except ValueError as ve:
            print(f"Error en readJsonGrupo1: {str(ve)}")
            return None
        except Exception as e:
            print(f"Error inesperado en readJsonGrupo1: {str(e)}")
            return None
