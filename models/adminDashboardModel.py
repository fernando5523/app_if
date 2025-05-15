from utils.dataType import dataType
import json
from flask import jsonify
import pandas as pd

# Clases Externas
from controller.erpController import erpController
from controller.sqlController import sqlController


class adminDashboardModel():

    __dataType = dataType()

    def get_top_proveedores(self):
        try:
            __sqlQuery = {
                "sqlColumns": ["PROVEEDOR", "CANTIDAD"],
                "sqlQuery": f"SELECT TOP 10 p.businessName, COUNT(i.invoiceId) AS invoiceCount FROM dbo.InvoiceTable i INNER JOIN dbo.Proveedores p ON i.vendorId = p.ruc GROUP BY p.businessName ORDER BY invoiceCount DESC;",
                "sqlType": "APP",
            }
            __resultQuery = sqlController(__sqlQuery).get_statement_select()
            
            if __resultQuery is not None and len(__resultQuery) > 0:
                    self.__dataType.set_column_type_string(__resultQuery, "PROVEEDOR")
                    self.__dataType.set_column_type_integer(__resultQuery, "CANTIDAD")

                    return __resultQuery
            else:
                return "errorServer"  # Devolver un mensaje de error si no se encuentran datos
                 
        except Exception as e:
                # Manejar cualquier excepción y devolver un mensaje de error
                print(f"Error en get_top_proveedores: {str(e)}")
                return "errorServer"

    def get_top_usuarios(self):
        try:
            __sqlQuery = {
                "sqlColumns": ["USUARIO", "CANTIDAD"],
                "sqlQuery": f"SELECT u.userName, COUNT(i.invoiceId) AS numberOfInvoices FROM UserTable u LEFT JOIN InvoiceTable i ON u.userId = i.userCreated GROUP BY u.userId, u.userName ORDER BY numberOfInvoices DESC",
                "sqlType": "APP",
            }
            __resultQuery = sqlController(__sqlQuery).get_statement_select()

            if __resultQuery is not None and len(__resultQuery) > 0:
                    self.__dataType.set_column_type_string(__resultQuery, "USUARIO")
                    self.__dataType.set_column_type_integer(__resultQuery, "CANTIDAD")

                    return __resultQuery
            else:
                return "errorServer"  # Devolver un mensaje de error si no se encuentran datos
        except Exception as e:
            # Manejar cualquier excepción y devolver un mensaje de error
            print(f"Error en get_top_usuarios: {str(e)}")
            return "errorServer"


    def get_ingresos_sql(self, date_init, date_end):
        try:
            desde = "2024-06-01"
            hasta = "2024-06-12"

            sqlQuery = f"""
            SELECT invoiceCreated, COUNT(*) AS cantidadFacturas
            FROM IngresoFacturaDB.dbo.InvoiceTable
            WHERE invoiceCreated BETWEEN '{date_init}' AND '{date_end}'
            GROUP BY invoiceCreated
            ORDER BY invoiceCreated;
            """

            __sqlQuery = {
                "sqlColumns": ["FECHA", "CANTIDAD"],
                "sqlQuery": sqlQuery,
                "sqlType": "APP",
            }
            __resultQuery = sqlController(__sqlQuery).get_statement_select()

            if __resultQuery is not None and len(__resultQuery) > 0:
                    self.__dataType.set_column_type_string(__resultQuery, "FECHA")
                    self.__dataType.set_column_type_integer(__resultQuery, "CANTIDAD")

                    return __resultQuery
            else:
                return "errorServer"  # Devolver un mensaje de error si no se encuentran datos
        except Exception as e:
            # Manejar cualquier excepción y devolver un mensaje de error
            print(f"Error en get_top_usuarios: {str(e)}")
            return "errorServer"
    

    # # complementos en vs de ingresos
    # # proveedor cantidad
    # def get_vs_ingresos_odata_temp(self):
    #     desde = "2024-04-11"
    #     hasta = "2024-04-12"

    #     __erpQuery = {
    #         "odata_entity": "VendPackingSlipJourBiEntities",
    #         "odata_filter": f"$select=OrderAccount,PurchId,DeliveryDate&$filter=DeliveryDate ge {desde}T00:00:00Z and DeliveryDate le {hasta}T23:59:59Z",
    #     }

    #     try:
    #         __resultQuery = erpController(__erpQuery).get_records_odata()

    #         if isinstance(__resultQuery, pd.DataFrame) and not __resultQuery.empty:
    #             # Preparar estructura para almacenar resultados únicos por OrderAccount
    #             order_accounts = {}
                
    #             for index, record in __resultQuery.iterrows():
    #                 order_account = record.get("OrderAccount")
    #                 purch_id = record.get("PurchId")
                    
    #                 if order_account is not None and purch_id is not None:
    #                     # Contar cada OrderAccount y evitar contar PurchId repetidos
    #                     if order_account not in order_accounts:
    #                         order_accounts[order_account] = {
    #                             "OrderAccount": order_account,
    #                             "Cantidad": 0  # Inicializar contador
    #                         }
                        
    #                     # Incrementar contador si el PurchId no ha sido registrado aún
    #                     if purch_id not in order_accounts[order_account]:
    #                         order_accounts[order_account]["Cantidad"] += 1

    #             # Convertir el diccionario a una lista de resultados
    #             unique_results = list(order_accounts.values())
    #             return unique_results

    #         else:
    #             print("No data found or data is not a DataFrame.")
    #             return []

    #     except Exception as e:
    #         print(f"Error en get_vs_ingresos_complementos: {str(e)}")
    #         return []


    # def get_vs_ingresos_odata(self):
    #     desde = "2024-06-01"
    #     hasta = "2024-06-12"

    #     __erpQuery = {
    #         "odata_entity": "VendPackingSlipJourBiEntities",
    #         "odata_filter": f"$select=PurchId,DeliveryDate&$filter=DeliveryDate ge {desde}T00:00:00Z and DeliveryDate le {hasta}T23:59:59Z",
    #     }

    #     try:
    #         __resultQuery = erpController(__erpQuery).get_records_odata()

    #         if isinstance(__resultQuery, pd.DataFrame) and not __resultQuery.empty:
    #             # Preparar estructura para almacenar resultados únicos por fecha
    #             fecha_trv = {}

    #             for index, record in __resultQuery.iterrows():
    #                 delivery_date = record.get("DeliveryDate")
    #                 purch_id = record.get("PurchId")

    #                 if delivery_date is not None and purch_id is not None:
    #                     # Formatear la fecha a formato YYYY-MM-DD
    #                     delivery_date_str = delivery_date.split('T')[0]
                        
    #                     if delivery_date_str not in fecha_trv:
    #                         fecha_trv[delivery_date_str] = {
    #                             "FECHA": delivery_date_str,
    #                             "CANTIDAD": 0,  # Inicializar contador
    #                             "TRV_Unicos": set()  # Utilizar un conjunto para TRV únicos
    #                         }
                        
    #                     # Añadir el PurchId al conjunto de TRV únicos
    #                     fecha_trv[delivery_date_str]["TRV_Unicos"].add(purch_id)
                
    #             # Convertir los conjuntos a listas y contar los TRV únicos
    #             resultados = []
    #             for date in fecha_trv:
    #                 fecha_trv[date]["CANTIDAD"] = len(fecha_trv[date]["TRV_Unicos"])
    #                 del fecha_trv[date]["TRV_Unicos"]  # Eliminar el conjunto después de contar
    #                 resultados.append(fecha_trv[date])

    #             # Convertir la lista de resultados a un DataFrame
    #             df_resultados = pd.DataFrame(resultados)
                
    #             # Ordenar el DataFrame por fecha de manera ascendente
    #             df_resultados = df_resultados.sort_values(by="FECHA", ascending=True)
                
    #             return df_resultados

    #         else:
    #             print("No data found or data is not a DataFrame.")
    #             return pd.DataFrame(columns=["FECHA", "CANTIDAD"])

    #     except Exception as e:
    #         print(f"Error en get_cantidad_trv_por_fecha: {str(e)}")
    #         return pd.DataFrame(columns=["FECHA", "CANTIDAD"])
