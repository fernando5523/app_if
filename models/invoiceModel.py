from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import os, pandas
import requests
import base64
import time
from flask import jsonify

# Clases Externas
from controller.erpController import erpController
from controller.sqlController import sqlController
from controller.sqlControllerPostgres import sqlControllerPostres
from utils.dataType import dataType
# from utils.readPdf import pdfRead
from utils.readXml import xmlRead
from utils.readJson import jsonRead
import json
import pytz

class invoiceModel:

    # para el seteo de tipos
    __dataType = dataType()

    # para la lectura de pdf
    # __readPdf = pdfRead()

    # para la lectura de xml
    __readXml = xmlRead()

    # para la lectura de json
    __readJson = jsonRead()

    # para el manejo de erp
    # Variables Globales
    load_dotenv()
    __APP_WORKERS = int(os.getenv("APP_WORKERS"))

    def get_users(self):
        try:
            __sqlQuery = {
                "sqlColumns": ["USERID", "USERNAME"],
                "sqlQuery": f"SELECT USERID, USERNAME FROM UserTable WHERE USERSTATE = '1'",
                "sqlType": "APP",
            }
            __resultQuery = sqlController(__sqlQuery).get_statement_select()

            if __resultQuery is not None and len(__resultQuery) > 0:
                self.__dataType.set_column_type_string(__resultQuery, "USERID")
                self.__dataType.set_column_type_string(__resultQuery, "USERNAME")

                return __resultQuery.reset_index(drop=True)

            else:
                return "errorServer"  # Devolver un mensaje de error si no se encuentran datos
        except Exception as e:
            # Manejar cualquier excepción y devolver un mensaje de error
            print(f"Error en get user: {str(e)}")
            return "errorServer" 

    def get_purch_list(self, ruc: str):
        """
        Obtiene una lista de pedidos de compras.
        """

        __erpQuery = {
            "odata_entity": "PurchaseOrderHeadersV2",
            "odata_filter": f"$select=InvoiceVendorAccountNumber, PurchaseOrderNumber, DefaultReceivingWarehouseId, RequestedDeliveryDate &$filter=InvoiceVendorAccountNumber eq %27{ruc}%27 and PurchaseOrderStatus eq Microsoft.Dynamics.DataEntities.PurchStatus%27Backorder%27 and DocumentApprovalStatus eq Microsoft.Dynamics.DataEntities.VersioningDocumentState%27Approved%27 &$orderby=DefaultReceivingWarehouseId asc",
        }

        __resultQuery = erpController(__erpQuery).get_records_odata()

        if __resultQuery is not None and len(__resultQuery) > 0:
            __resultQuery = __resultQuery.drop(["@odata.etag"], axis=1).rename(
                columns={
                    "InvoiceVendorAccountNumber": "VENDORID",
                    "PurchaseOrderNumber": "PURCHID",
                    "DefaultReceivingWarehouseId": "WAREHOUSEID",
                    "RequestedDeliveryDate": "PURCHDATE",
                }
            )

            self.__dataType.set_column_type_string(__resultQuery, "VENDORID")
            self.__dataType.set_column_type_string(__resultQuery, "PURCHID")
            self.__dataType.set_column_type_string(__resultQuery, "WAREHOUSEID")
            self.__dataType.set_column_type_date(__resultQuery, "PURCHDATE", 3)

            return __resultQuery.reset_index(drop=True)

        else:
            return "errorServer"

    def get_suppliers(self):
        try:
            __sqlQuery = {
                "sqlColumns": ["RUC", "BUSINESSNAME", "DATASOURCE"],
                "sqlQuery": f"SELECT RUC,BUSINESSNAME,DATASOURCE  FROM Proveedores WHERE STATE = 'ENABLED'",
                "sqlType": "APP",
            }
            __resultQuery = sqlController(__sqlQuery).get_statement_select()

            if __resultQuery is not None and len(__resultQuery) > 0:
                self.__dataType.set_column_type_string(__resultQuery, "RUC")
                self.__dataType.set_column_type_string(__resultQuery, "BUSINESSNAME")
                self.__dataType.set_column_type_string(__resultQuery, "DATASOURCE")

                return __resultQuery
                    
            else:
                return "errorServer"  # Devolver un mensaje de error si no se encuentran datos

        except Exception as e:
            # Manejar cualquier excepción y devolver un mensaje de error
            print(f"Error en get_document_header: {str(e)}")
            return "errorServer"

    def get_purch_header(self, ruc: str, trv: str):
        """
            Obtiene el encabezado de compra de un proveedor y un ID de compra específicos.
        """
        
        # datos del pedido de compra
        __erpQuery1 = {
            "odata_entity": "PurchaseOrderHeadersV2",
            "odata_filter": f"$select=PurchaseOrderNumber, InvoiceVendorAccountNumber, PurchaseOrderName, DefaultReceivingSiteId, DefaultReceivingWarehouseId, PurchaseOrderStatus, DocumentApprovalStatus, RequestedDeliveryDate, CurrencyCode, PaymentTermsName &$filter=InvoiceVendorAccountNumber eq %27{ruc}%27 and PurchaseOrderNumber eq %27{trv}%27",
        }

        # datos del worker
        __erpQuery2 = {
            "odata_entity": "VendorsV2",
            "odata_filter": f"$select=MainContactPersonnelNumber &$filter=VendorAccountNumber eq %27{ruc}%27",
        }
        
                
        with ThreadPoolExecutor(max_workers=self.__APP_WORKERS) as pool:
            __resultQuery1 = pool.submit(erpController(__erpQuery1).get_records_odata)
            __resultQuery2 = pool.submit(erpController(__erpQuery2).get_records_odata)

        __resultQuery1 = __resultQuery1.result()
        __resultQuery2 = __resultQuery2.result()

        if (__resultQuery1 is not None and len(__resultQuery1) > 0) and (__resultQuery2 is not None and len(__resultQuery2) > 0):
            __purchData = __resultQuery1.drop(["@odata.etag"], axis=1).rename(
                columns={
                    "PurchaseOrderNumber": "PURCHID",
                    "InvoiceVendorAccountNumber": "VENDORID",
                    "PurchaseOrderName": "VENDORNAME",
                    "DefaultReceivingSiteId": "SITEID",
                    "DefaultReceivingWarehouseId": "WAREHOUSEID",
                    "PurchaseOrderStatus": "PURCHSTATUS",
                    "DocumentApprovalStatus": "DOCUMENTSTATE",
                    "RequestedDeliveryDate": "PURCHDATE",
                    "CurrencyCode": "PURCHCURRENCY",
                    "PaymentTermsName": "PURCHPAYMENT",
                }
            )

            self.__dataType.set_column_type_string(__purchData, "PURCHID")
            self.__dataType.set_column_type_string(__purchData, "VENDORID")
            self.__dataType.set_column_type_string(__purchData, "VENDORNAME")
            self.__dataType.set_column_type_string(__purchData, "SITEID")
            self.__dataType.set_column_type_string(__purchData, "WAREHOUSEID")
            self.__dataType.set_column_type_string(__purchData, "PURCHSTATUS")
            self.__dataType.set_column_type_string(__purchData, "DOCUMENTSTATE")
            self.__dataType.set_column_type_date(__purchData, "PURCHDATE", 3)
            self.__dataType.set_column_type_string(__purchData, "PURCHCURRENCY")
            self.__dataType.set_column_type_string(__purchData, "PURCHPAYMENT")

            __purchData["PURCHID"] = __purchData["PURCHID"].replace(to_replace=r"\n", value="", regex=True)
            __purchData["VENDORID"] = __purchData["VENDORID"].replace(to_replace=r"\n", value="", regex=True)
            __purchData["VENDORNAME"] = __purchData["VENDORNAME"].replace(to_replace=r"\n", value="", regex=True)
            __purchData["SITEID"] = __purchData["SITEID"].replace(to_replace=r"\n", value="", regex=True)
            __purchData["WAREHOUSEID"] = __purchData["WAREHOUSEID"].replace(to_replace=r"\n", value="", regex=True)
            __purchData["PURCHSTATUS"] = __purchData["PURCHSTATUS"].replace(to_replace=r"\n", value="", regex=True)
            __purchData["DOCUMENTSTATE"] = __purchData["DOCUMENTSTATE"].replace(to_replace=r"\n", value="", regex=True)
            __purchData["PURCHCURRENCY"] = __purchData["PURCHCURRENCY"].replace(to_replace=r"\n", value="", regex=True)
            __purchData["PURCHPAYMENT"] = __purchData["PURCHPAYMENT"].replace(to_replace=r"\n", value="", regex=True)

            __purchData["SITEID"] = __purchData.apply(lambda row: "SIN SITIO" if row["SITEID"] == "" else row["SITEID"], axis=1)
            __purchData["WAREHOUSEID"] = __purchData.apply(
                lambda row: "SIN ALMACEN" if row["WAREHOUSEID"] == "" else row["WAREHOUSEID"], axis=1
            )
            __purchData["PURCHSTATUS"] = __purchData.apply(
                lambda row: "PEDIDO ABIERTO" if row["PURCHSTATUS"] == "Backorder" else "SIN ESTADO", axis=1
            )
            __purchData["DOCUMENTSTATE"] = __purchData.apply(
                lambda row: "APROBADO" if row["DOCUMENTSTATE"] == "Approved" else "SIN ESTADO", axis=1
            )

            __workerId = __resultQuery2.drop(["@odata.etag"], axis=1).rename(
                columns={
                    "MainContactPersonnelNumber": "WORKERID",
                }
            )

            self.__dataType.set_column_type_string(__workerId, "WORKERID")

            __erpQuery3 = {
                "odata_entity": "EmployeesV2",
                "odata_filter": "$select=PersonnelNumber, Name &$filter=PersonnelNumber eq %27"
                + __workerId.loc[0, "WORKERID"]
                + "%27 and EmploymentLegalEntityId eq %27TRV%27",
            }

            __resultQuery3 = erpController(__erpQuery3).get_records_odata()

            if __resultQuery3 is not None and len(__resultQuery3) > 0:
                __purchData["WORKERID"] = __workerId.loc[0, "WORKERID"]

                __workerData = __resultQuery3.drop(["@odata.etag"], axis=1).rename(
                    columns={
                        "PersonnelNumber": "WORKERID",
                        "Name": "WORKERNAME",
                    }
                )

                self.__dataType.set_column_type_string(__workerData, "WORKERID")
                self.__dataType.set_column_type_string(__workerData, "WORKERNAME")

                __purchHeader = pandas.merge(__purchData, __workerData, how="inner", on="WORKERID")

                return __purchHeader

            else:
                return "errorServer"
        else:
            return "errorServer"
        
    def get_document_pdf_header(self, ruc, urlFile):
        try:
 
            __sqlQuery = {
                "sqlColumns": ["COORDINATESPDFVALIDATE"],
                "sqlQuery": f"SELECT COORDINATESPDFVALIDATE FROM PROVEEDORES WHERE RUC = '{ruc}'",
                "sqlType": "APP",
            }
            __resultQuery = sqlController(__sqlQuery).get_statement_select()

            if __resultQuery is not None and not __resultQuery.empty:
                self.__dataType.set_column_type_string(__resultQuery, "COORDINATESPDFVALIDATE")
                coordinate_str = __resultQuery.loc[0, "COORDINATESPDFVALIDATE"]
                coordinate_list = [float(x.strip()) for x in coordinate_str.split(',')]
                return self.__readPdf.readHeadPdf(ruc, coordinate_list, urlFile)

            else:
                return "errorServer"  # Devolver un mensaje de error si no se encuentran datos

        except Exception as e:
            # Manejar cualquier excepción y devolver un mensaje de error
            print(f"Error en get_document_header: {str(e)}")
            return "errorServer"
        
    def get_document_xml_header(self, ruc, file):
        try:
            __sqlQuery = {
                "sqlColumns": ["READXMLHEADGROUP"],
                "sqlQuery": f"SELECT READXMLHEADGROUP FROM PROVEEDORES WHERE RUC = '{ruc}'",
                "sqlType": "APP",
            }
            __resultQuery = sqlController(__sqlQuery).get_statement_select()

            if __resultQuery is not None and not __resultQuery.empty:
                self.__dataType.set_column_type_string(__resultQuery, "READXMLHEADGROUP")
                nameGroup = __resultQuery.loc[0, "READXMLHEADGROUP"]

                # Genera el nombre de la función en el formato correcto
                function_name = "readHeadXml" + nameGroup.capitalize()
                functionReadXml = getattr(self.__readXml, function_name)

                # Llama a la función generada y devuelve el resultado
                return functionReadXml(file)
                    
            else:
                return "errorServer"  # Devolver un mensaje de error si no se encuentran datos

        except Exception as e:
            # Manejar cualquier excepción y devolver un mensaje de error
            print(f"Error en get_document_header: {str(e)}")
            return "errorServer"
    
    def get_document_json_header(self, file):
        try:
            data = self.__readJson.readHead(file)

            if data is None or len(data) == 0:
                return "errorServer"
            else:
                return data  # O la función adecuada para procesar el JSON
                    
        except Exception as e:
            # Manejar cualquier excepción y devolver un mensaje de error
            print(f"Error en get_document_header: {str(e)}")
            return "errorServer"
        
    def set_invoice_create(self,
        purchId: str,
        vendorId: str,
        invoiceNumber: str,
        invoiceDate: str,
        purchDate: str,
        purchCurrency: str,
        purchPayment: str,
        siteId: str,
        warehouseId: str,
        xmlFile: str,
        userId: int):

        __sqlQuery1 = {
            "sqlColumns": ["RESPONSEDB"],
            "sqlQuery": "EXEC InvoiceValidate ?, ?, ?",
            "sqlEntry": (purchId, vendorId, invoiceNumber),
            "sqlType": "APP",
        }

        __resultQuery1 = sqlController(__sqlQuery1).get_procedure_select()
        if __resultQuery1 is not None and len(__resultQuery1) > 0:
            __pdfFile = ""
            quantity = 0
            __xmlFile = xmlFile.replace("\\", "/")
            __invoiceDate = datetime.strptime(invoiceDate, "%Y-%m-%d").date()
            __purchDate = datetime.strptime(purchDate, "%d/%m/%Y").date()

            __sqlQuery2 = {
                "sqlColumns": ["INVOICEID"],
                "sqlQuery": f"SELECT INVOICEID FROM InvoiceTable WHERE INVOICESTATE = '1' AND INVOICENUMBER = '{invoiceNumber}' AND PURCHID = '{purchId}' AND VENDORID = '{vendorId}'",
                "sqlType": "APP",
            }

            if __resultQuery1.loc[0, "RESPONSEDB"] == "False":
                __sqlQuery3 = {
                    "sqlQuery": "EXEC InvoiceCreate ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
                    "sqlEntry": (
                        purchId,
                        vendorId,
                        invoiceNumber,
                        __invoiceDate,
                        __purchDate,
                        purchCurrency,
                        purchPayment,
                        siteId,
                        warehouseId,
                        __pdfFile,
                        __xmlFile,
                        userId,
                        quantity
                    ),
                    "sqlType": "APP",
                }

                __resultQuery3 = sqlController(__sqlQuery3).set_procedure_insert()

                if __resultQuery3 is not None and __resultQuery3 == "True":
                    __resultQuery2 = sqlController(__sqlQuery2).get_statement_select()

                    if __resultQuery2 is not None and len(__resultQuery2) > 0:
                        self.__dataType.set_column_type_string(__resultQuery2, "INVOICEID")

                        return __resultQuery2
                    else:
                        return "errorServer"
                else:
                    return "errorServer"
            elif __resultQuery1.loc[0, "RESPONSEDB"] == "True":
                __sqlQuery3 = {
                    "sqlQuery": "EXEC InvoiceUpdate ?, ?, ?, ?, ?, ?, ?",
                    "sqlEntry": (
                        purchId,
                        vendorId,
                        invoiceNumber,
                        __invoiceDate,
                        __pdfFile,
                        __xmlFile,
                        userId
                    ),
                    "sqlType": "APP",
                }

                __resultQuery3 = sqlController(__sqlQuery3).set_procedure_update()

                if __resultQuery3 is not None and __resultQuery3 == "True":
                    __resultQuery2 = sqlController(__sqlQuery2).get_statement_select()

                    if __resultQuery2 is not None and len(__resultQuery2) > 0:
                        self.__dataType.set_column_type_string(__resultQuery2, "INVOICEID")

                        return __resultQuery2
                    else:
                        return "errorServer"
                else:
                    return "errorServer"
        else:
            return "errorServer"        


    # descargar archivo xml desde sunat
    def download_xml_sunat(self, ruc, factura):
        max_retries = 3
        backoff_factor = 2

        authorization_token = "Bearer " + self.get_token_sunat()

        # authorization_token = "Bearer eyJraWQiOiJhcGkuc3VuYXQuZ29iLnBlLmtpZDAwMSIsInR5cCI6IkpXVCIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIyMDYwOTY5OTk4MiIsImF1ZCI6Ilt7XCJhcGlcIjpcImh0dHBzOlwvXC9hcGktY3BlLnN1bmF0LmdvYi5wZVwiLFwicmVjdXJzb1wiOlt7XCJpZFwiOlwiXC92MVwvY29udHJpYnV5ZW50ZVwvY29uc3VsdGFjcGVcIixcImluZGljYWRvclwiOlwiMVwiLFwiZ3RcIjpcIjEwMDEwMFwifSx7XCJpZFwiOlwiXC92MVwvY29udHJpYnV5ZW50ZVwvcGFyYW1ldHJvc1wiLFwiaW5kaWNhZG9yXCI6XCIxXCIsXCJndFwiOlwiMTAwMTAwXCJ9XX1dIiwidXNlcmRhdGEiOnsibnVtUlVDIjoiMjA2MDk2OTk5ODIiLCJ0aWNrZXQiOiIxMjM2MTQ0NzM1MDM1IiwibnJvUmVnaXN0cm8iOiIiLCJhcGVNYXRlcm5vIjoiIiwibG9naW4iOiIyMDYwOTY5OTk4Mk9ORklSQUdPIiwibm9tYnJlQ29tcGxldG8iOiJURVJSQU5PVkEgVFJBRElORyBTLkEuQy4iLCJub21icmVzIjoiVEVSUkFOT1ZBIFRSQURJTkcgUy5BLkMuIiwiY29kRGVwZW5kIjoiMDIzMSIsImNvZFRPcGVDb21lciI6IiIsImNvZENhdGUiOiIiLCJuaXZlbFVPIjowLCJjb2RVTyI6IiIsImNvcnJlbyI6IiIsInVzdWFyaW9TT0wiOiJPTkZJUkFHTyIsImlkIjoiIiwiZGVzVU8iOiIiLCJkZXNDYXRlIjoiIiwiYXBlUGF0ZXJubyI6IiIsImlkQ2VsdWxhciI6bnVsbCwibWFwIjp7ImlzQ2xvbiI6ZmFsc2UsImRkcERhdGEiOnsiZGRwX251bXJ1YyI6IjIwNjA5Njk5OTgyIiwiZGRwX251bXJlZyI6IjAyMzEiLCJkZHBfZXN0YWRvIjoiMDAiLCJkZHBfZmxhZzIyIjoiMDAiLCJkZHBfdWJpZ2VvIjoiMDIwMTAxIiwiZGRwX3RhbWFubyI6IjAxIiwiZGRwX3Rwb2VtcCI6IjM5IiwiZGRwX2NpaXUiOiI1MTIyNSJ9LCJpZE1lbnUiOiIxMjM2MTQ0NzM1MDM1Iiwiam5kaVBvb2wiOiJwMDIzMSIsInRpcFVzdWFyaW8iOiIwIiwidGlwT3JpZ2VuIjoiSVQiLCJwcmltZXJBY2Nlc28iOnRydWV9fSwibmJmIjoxNzI0NDQyNDYyLCJjbGllbnRJZCI6ImNkOGU3YWZiLWEwZTItNDIxNy05MTg3LTg4MjA2ZTRiYTdhZiIsImlzcyI6Imh0dHBzOlwvXC9hcGktc2VndXJpZGFkLnN1bmF0LmdvYi5wZVwvdjFcL2NsaWVudGVzc29sXC9jZDhlN2FmYi1hMGUyLTQyMTctOTE4Ny04ODIwNmU0YmE3YWZcL29hdXRoMlwvdG9rZW5cLyIsImV4cCI6MTcyNDQ0NjA2MiwiZ3JhbnRUeXBlIjoiYXV0aG9yaXphdGlvbl90b2tlbiIsImlhdCI6MTcyNDQ0MjQ2Mn0.dsSy8o7FHspWB-Ik4LJN6sZJNvwLdlCvtJDC6pNoKnWYscal8Sc3cfaHX4Cb92s8VaUX3UalDwBVpe2xa6igVre1TbvJfE_GA9tVOqcngU0kQeiuqwTXYwTDWx-LD3kqw5Ik4LZ_er90WMlOmTbKkOwCKiAlqqE2YAAeH29cvQ8FszemjiHfDaWj5De79LrwthKEnm-IReRxvlU9F2OB3FJ6oksvBjbgxuRqhwdET6y8zPnNK5Z06fQTFnyERN8aD9kMGHMg5yJei7bbLBaIJlUDC-QB9_u4OtcR9663qZCehtmVdmD2P7ggROZemqubIPjBLwadXrQRH-cTwZT63w"
        url = f"https://api-cpe.sunat.gob.pe/v1/contribuyente/consultacpe/comprobantes/{ruc}-01-{factura}-2/02"
        headers = {
            "accept": "application/json, text/plain, */*",
            "authorization": authorization_token,
            "Referer": "https://e-factura.sunat.gob.pe/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        for intento in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    nombre_archivo = data.get('nomArchivo')
                    contenido_base64 = data.get('valArchivo')
                    
                    if nombre_archivo and contenido_base64:
                        contenido_decodificado = base64.b64decode(contenido_base64)
                        return {
                            "success": True,
                            "nombre_archivo": nombre_archivo,
                            "contenido": contenido_decodificado
                        }
                    else:
                        return {
                            "success": False,
                            "status_code": 500,
                            "message": "La respuesta de SUNAT no contiene los datos esperados."
                        }
                
                elif response.status_code == 404:
                    return {
                        "success": False,
                        "status_code": 404,
                        "message": "El comprobante no fue encontrado en SUNAT."
                    }
                
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "status_code": 401,
                        "message": "No autorizado. Verifique su token de autorización."
                    }
                
                else:
                    # Otros errores HTTP
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "message": f"Error al solicitar el comprobante: {response.text}"
                    }

            except requests.exceptions.Timeout:
                if intento < max_retries - 1:
                    time.sleep(backoff_factor)
                    backoff_factor *= 2
                    continue
                else:
                    return {
                        "success": False,
                        "status_code": 408,
                        "message": "La solicitud a SUNAT ha excedido el tiempo de espera."
                    }
            except requests.exceptions.RequestException as e:
                return {
                    "success": False,
                    "status_code": 500,
                    "message": f"Error de conexión: {str(e)}"
                }

        # Si se alcanzan los reintentos máximos sin éxito
        return {
            "success": False,
            "status_code": 500,
            "message": "No se pudo obtener el comprobante después de múltiples intentos."
        }
    
    def download_json_sunat_alicorp(self, serie, correlativo):
        token = self.get_token_sunat_guias()

        if token == False:
            return {"success": False, "error": f"Error de Token, Token venciodo"}

        token = token['token']
        
        url = f"https://api-cpe.sunat.gob.pe/v1/contribuyente/gre/comprobantes/20100055237-09-{serie}-{correlativo}"

        print(url)
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "es-ES,es;q=0.9,en;q=0.8",
            "authorization": f"Bearer {token}",
            "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "Referer": "https://e-factura.sunat.gob.pe/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            response = requests.get(url, headers=headers)

            print(response)

            response.raise_for_status()

            data = response.json()
            ruc = data.get('numRuc', 'N/A')
            fecha = data.get('emision', {}).get('fecEmision', '').split('T')[0]
            bien_info = data.get('traslado', {}).get('bien', [])

            items = []
            for bien in bien_info:
                codBien = bien.get('codBien', 'N/A')
                descripcion_completa = bien.get('desBien', '').encode().decode('unicode_escape')
                descripcion = descripcion_completa.split('@##@')[0] if '@##@' in descripcion_completa else descripcion_completa
                numCantidad = int(bien.get('numCantidad', 0))
                monto_pen = float(descripcion_completa.split('@##@')[2].replace(' PEN', '').strip()) if '@##@' in descripcion_completa else None

                items.append({
                    'codigo': codBien,
                    'descripcion': descripcion,
                    'cantidad': numCantidad,
                    'sub_total': monto_pen,
                    'bonificacion': "no",
                    'ISC': "0"
                })

            factura_data = {
                'ruc': ruc,
                'serie': f"{serie}-{correlativo}",
                'fecha': fecha,
                'tipo_moneda': 'sol',
                'items': items
            }

            return {"success": True, "data": factura_data, "nombre_archivo": f"{serie}-{correlativo}.json"}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Error de conexión: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": "Error inesperado", "details": str(e)}




    def get_token_sunat(self):
        __sqlQuery = {
                "sqlColumns": ["LLAVE"],
                "sqlQuery": f"SELECT TOP 1 LLAVE FROM LLAVES ORDER BY ID DESC",
                "sqlType": "APP",
        }
        __resultQuery = sqlController(__sqlQuery).get_statement_select()

        if __resultQuery is not None and len(__resultQuery) > 0:
            return __resultQuery.iloc[0]['LLAVE']
        else:
            return None
        
    
    def get_token_sunat_postgress(self):
        query = "select llave from public.llaves order by id desc limit 1"
        try:
            controller = sqlControllerPostres()
            return controller.select_query(query)

        except Exception as e:
            print(f"Error al obtener memorándums: {e}")
            return None
    
    def get_token_sunat_guias(self):
        """
        Función para obtener el token llamando a la ruta /getToken
        y verificar si la fecha del token es válida.
        """
        try:
            # Obtener la URL base desde las variables de entorno
            BASE_URL = os.getenv("BASE_URL_RRHH")
            if not BASE_URL:
                print("Error: BASE_URL_RRHH no está configurada.")
                return False
            
            endpointConsulta = f"{BASE_URL}/guiasRemision/getToken"
            
            # Realizar la solicitud GET para obtener el token
            response = requests.get(endpointConsulta)
            
            # Validar que la respuesta sea exitosa
            if response.status_code == 200:
                data = response.json()
                print(data)  # Imprimir respuesta para depuración

                if data.get("success"):
                    token_data = data["data"][0]  # Asumimos que solo hay un registro
                    token_fecha_str = token_data["fecha"]
                    
                    # Convertir la fecha obtenida a un objeto datetime con zona horaria de Perú
                    lima_tz = pytz.timezone("America/Lima")
                    token_fecha = datetime.strptime(token_fecha_str, "%Y-%m-%d %H:%M:%S")
                    token_fecha = lima_tz.localize(token_fecha)  # Asignar zona horaria a la fecha del token
                    
                    # Obtener la hora actual en la zona horaria de Perú
                    now = datetime.now(lima_tz)
                    
                    # Comparar si la diferencia es menor a 1 hora
                    if (now - token_fecha) < timedelta(hours=1):
                        return token_data
                    else:
                        print("El token ha expirado.")
                        return False
            return False
        except Exception as e:
            print(f"Error al obtener el token: {e}")
            return False