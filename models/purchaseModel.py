# purchaseModel.py
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os, pandas
from controller.erpController import erpController
from controller.sqlController import sqlController
from utils.dataType import dataType
from utils.readXml import xmlRead
from utils.readJson import jsonRead
from flask import jsonify
import time

class purchaseModel:

    load_dotenv()
    __APP_WORKERS = int(os.getenv("APP_WORKERS"))

    __dataType = dataType()

    # para la lectura de xml
    __readXml = xmlRead()

    # para la lectura de json
    __readJson = jsonRead()


    def get_product_lines(self, vendorId: str, product_xml: list):
        """
        Obtiene las líneas de productos de un proveedor específico.

        Args:
            vendorId (str): Identificador del proveedor.
            product_xml (list): Lista de productos del XML a comparar.

        Returns:
            pandas.DataFrame or None: DataFrame con las líneas de productos del proveedor si se pudo obtener, None si no.
        """
        try:
            # Consulta para productos y su código de acuerdo al proveedor
            __erpQuery2 = {
                "odata_entity": "VendorProductDescriptionsV2",
                "odata_filter": (
                    f"$select=ItemNumber,VendorAccountNumber,VendorProductNumber"
                    f" &$filter=VendorAccountNumber eq '{vendorId}' &$orderby=ItemNumber asc"
                ),
            }

            # Ejecutar la primera consulta secuencialmente
            __resultQuery2 = erpController(__erpQuery2).get_records_odata()

            # Validar si la primera consulta devolvió resultados válidos
            if __resultQuery2 is not None and not __resultQuery2.empty:
                # Limpieza y mapeo de los resultados de la segunda consulta
                __resultQuery2 = (
                    __resultQuery2.drop(columns=["@odata.etag"], errors="ignore")
                    .rename(columns={
                        "ItemNumber": "PRODUCTID",
                        "VendorAccountNumber": "VENDORID",
                        "VendorProductNumber": "COD_PRODUCT"
                    })
                    .replace(r"\n", "", regex=True)
                    .fillna({"COD_PRODUCT": "SCP"})
                    .drop_duplicates()
                    .reset_index(drop=True)
                )

                # Dividir filas con "/" en COD_PRODUCT y reorganizar
                if __resultQuery2["COD_PRODUCT"].str.contains("/").any():
                    __resultQuery2 = (
                        __resultQuery2.assign(COD_PRODUCT=__resultQuery2["COD_PRODUCT"].str.split("/"))
                        .explode("COD_PRODUCT")
                        .reset_index(drop=True)
                    )

                # Filtrar productos de proveedores que coinciden con productos del XML
                df_filtered = __resultQuery2[__resultQuery2['COD_PRODUCT'].isin(product_xml)]

                # Verificar si hay productos filtrados
                if not df_filtered.empty:
                    # Listar los PRODUCTID de PROVEEDORES FILTRADOS
                    product_id_list = df_filtered['PRODUCTID'].unique().tolist()

                    # Construir el filtro OData con los PRODUCTID específicos
                    if product_id_list:
                        product_id_filter = ' or '.join([f"ItemNumber eq '{product_id}'" for product_id in product_id_list])

                        __erpQuery1 = {
                            "odata_entity": "ReleasedProductsV2",
                            "odata_filter": f"$select=ItemNumber,PurchaseUnitSymbol&$filter=(ProductLifecycleStateId eq 'ACTIVO' and ProductGroupId eq 'GA001') and ({product_id_filter})&$orderby=ItemNumber asc",
                        }

                        # Ejecutar la segunda consulta secuencialmente
                        __resultQuery1 = erpController(__erpQuery1).get_records_odata()

                        # Validar si la segunda consulta devolvió resultados válidos
                        if __resultQuery1 is not None and not __resultQuery1.empty:
                            __resultQuery1 = (
                                __resultQuery1.drop(columns=["@odata.etag"], errors="ignore")
                                .rename(columns={"ItemNumber": "PRODUCTID", "PurchaseUnitSymbol": "EMPAQUE"})
                                .replace({"PRODUCTID": r"\n"}, {"PRODUCTID": ""}, regex=True)
                                .dropna(subset=["PRODUCTID", "EMPAQUE"])
                                .drop_duplicates()
                                .reset_index(drop=True)
                            )

                            # Unión de las dos consultas
                            __productData = pandas.merge(__resultQuery1, df_filtered, on="PRODUCTID", how="inner")

                            # Filtrado final de columnas y retorno
                            __productData = __productData[["VENDORID", "EMPAQUE", "COD_PRODUCT", "PRODUCTID"]]

                            return __productData

                        else:
                            print("No se encontraron resultados para la consulta de productos activos.")
                            return None
                    else:
                        print("No hay PRODUCTID para filtrar en productos activos.")
                        return None
                else:
                    print("No se encontraron productos de los proveedores que coincidan con los del XML.")
                    return None

            else:
                print("No se encontraron resultados para la consulta de productos del proveedor.")
                return None

        except Exception as e:
            print(f"Error al obtener las líneas de productos: {e}")
            return None

        

    def get_purchase_lines(self, invoiceId: str):
        """
        Obtiene las líneas de compra asociadas a una factura.

        Args:
            invoiceId (str): Identificador de la factura.

        Returns:
            JSON: Respuesta con el estado de la operación y los datos obtenidos.
        """
        try:
            tiempos = {}  # Diccionario para almacenar los tiempos de cada paso

            # PASO 1 : OBTENER DATOS DESDE LA BASE DE DATOS
            # start_time = time.time()
            __sqlQuery = {
                "sqlColumns": [
                    "XMLFILE", "VENDORID", "PURCHID", "PURCHDATE", "SITEID", 
                    "WAREHOUSEID", "READXMLBODYGROUP", "BUSINESSNAME"
                ],
                "sqlQuery": f"""
                    SELECT XMLFILE, VENDORID, PURCHID, PURCHDATE, SITEID, WAREHOUSEID, 
                    (SELECT READXMLBODYGROUP FROM PROVEEDORES WHERE RUC = VENDORID) AS READXMLBODYGROUP, 
                    (SELECT BUSINESSNAME FROM PROVEEDORES WHERE RUC = VENDORID) AS BUSINESSNAME 
                    FROM InvoiceTable WHERE INVOICEID = '{invoiceId}'
                """,
                "sqlType": "APP",
            }

            __resultQuery = sqlController(__sqlQuery).get_statement_select()
            # tiempos['Paso 1 - Obtener datos desde la base de datos'] = time.time() - start_time
            if __resultQuery.empty:
                return self.generate_response(
                    "Error al consultar la base de datos por la factura seleccionada", False, 504
                )

            # PASO 2 : DARLES EL FORMATO
            # start_time = time.time()
            self.format_dataframe_columns(__resultQuery, [
                "XMLFILE", "PURCHID", "PURCHDATE", "VENDORID", 
                "SITEID", "WAREHOUSEID", "READXMLBODYGROUP", "BUSINESSNAME"
            ])
            # tiempos['Paso 2 - Darles el formato'] = time.time() - start_time

            # PASO 3 : ASIGNAR VARIABLES
            # start_time = time.time()
            __xmlFile, __vendorId, __purchId = __resultQuery.loc[0, ["XMLFILE", "VENDORID", "PURCHID"]]
            __purchDate, __siteId, __warehouseId = __resultQuery.loc[0, ["PURCHDATE", "SITEID", "WAREHOUSEID"]]
            __readXmlGroup, __businessName = __resultQuery.loc[0, ["READXMLBODYGROUP", "BUSINESSNAME"]]
            # tiempos['Paso 3 - Asignar variables'] = time.time() - start_time

            # PASO 4 : LEER LOS DATOS DEL XML
            start_time = time.time()
            functionReadXml = getattr(self.__readXml, f"readProductsXml{__readXmlGroup.capitalize()}")
            __productDataXml = functionReadXml(__xmlFile)
            tiempos['Paso 4 - Leer los datos del XML'] = time.time() - start_time
            if __productDataXml is None:
                return self.generate_response(
                    "Error en la lectura del archivo XML", False, 504
                )

            # PASO 5 : LEER PRODUCTOS DESDE DYNAMICS
            # start_time = time.time()

            # listar los COD_PRODUCT de __productDataXml
            __codProductList = __productDataXml["COD_PRODUCT"].unique().tolist()

            __productDataDynamics = self.get_product_lines(__vendorId, __codProductList)
            # tiempos['Paso 5 - Leer productos desde Dynamics'] = time.time() - start_time
            if __productDataDynamics is None:
                return self.generate_response(
                    "Error en la lectura de productos desde Dynamics, puede que el proveedor no contenga productos registrados", 
                    False, 504
                )

            # PASO 6 : COMPARAR PRODUCTOS
            # start_time = time.time()
            __productDataXml = self.compare_products(__productDataXml, __productDataDynamics)
            # tiempos['Paso 6 - Comparar productos'] = time.time() - start_time

            # PASO 7 : AGREGAR EMPAQUES
            # start_time = time.time()
            __invoiceData = self.agregar_empaques_a_dataframe_principal(__productDataXml)
            # tiempos['Paso 7 - Agregar empaques'] = time.time() - start_time
            if __invoiceData is None:
                return self.generate_response(
                    "Error al agregar empaques al DataFrame principal", False, 504
                )

            # PASO 8 : AGREGAR COLUMNAS Y FINALIZAR
            # start_time = time.time()
            __invoiceData = self.finalize_dataframe(__invoiceData, __productDataDynamics, __vendorId, __purchId, __purchDate, __siteId, __warehouseId, __businessName)
            # tiempos['Paso 8 - Agregar columnas y finalizar'] = time.time() - start_time
            
            # Paso 9: Actualizar cantidad de productos en la base de datos
            cantidad_productos = int(len(__invoiceData))  # <-- Asegúrate que sea tipo int

            # Buscar el invoiceId con base en datos ya procesados
            __sqlBuscaFactura = {
                "sqlColumns": ["INVOICEID"],
                "sqlQuery": f"""
                    SELECT INVOICEID FROM InvoiceTable
                    WHERE PURCHID = '{__purchId}'
                    AND VENDORID = '{__vendorId}'
                    AND INVOICESTATE = '1'
                    AND XMLFILE = '{__xmlFile}'
                """,
                "sqlType": "APP"
            }

            __resultFactura = sqlController(__sqlBuscaFactura).get_statement_select()

            if __resultFactura is not None and not __resultFactura.empty:
                invoiceId = int(__resultFactura.loc[0, "INVOICEID"])  # <-- Convertir a int nativo

                # Ejecutar el procedimiento que solo actualiza la cantidad
                __sqlUpdateCantidad = {
                    "sqlQuery": "EXEC InvoiceUpdateQuantity ?, ?",
                    "sqlEntry": (invoiceId, cantidad_productos),  # ambos son int nativos
                    "sqlType": "APP"
                }

                resultadoUpdate = sqlController(__sqlUpdateCantidad).set_procedure_update()

                if resultadoUpdate != "True":
                    return self.generate_response("No se pudo actualizar la cantidad de productos", False, 504)

            # Retorno de la respuesta con tiempos de ejecución
            response_data = {
                "data": __invoiceData.to_dict(orient="records"),
                # "tiempos": {k: f"{v:.2f} segundos" for k, v in tiempos.items()}
            }
            return self.generate_response(response_data, True, 200)

        except Exception as e:
            return self.generate_response(
                f"Error inesperado: {str(e)}", False, 500
            )

        
    def format_dataframe_columns(self, dataframe, columns):
        """
        Formatea las columnas del DataFrame a tipo string.

        Args:
            dataframe (pandas.DataFrame): DataFrame a formatear.
            columns (list): Lista de nombres de columnas.
        """
        for column in columns:
            self.__dataType.set_column_type_string(dataframe, column)


    def compare_products(self, xml_df, dynamics_df):
        """
        Compara productos entre XML y Dynamics y agrega la columna de identificación.

        Args:
            xml_df (pandas.DataFrame): DataFrame de productos del XML.
            dynamics_df (pandas.DataFrame): DataFrame de productos de Dynamics.

        Returns:
            pandas.DataFrame: DataFrame actualizado con comparación de productos.
        """
        def find_product_info(codigo):
            match = dynamics_df[dynamics_df["COD_PRODUCT"] == str(codigo)]
            return (match.iloc[0]["PRODUCTID"], "SI") if not match.empty else (None, "NO")
        
        xml_df["CODIGO_PROD_DYNAMICS"], xml_df["EN_DYNAMICS"] = zip(*xml_df["COD_PRODUCT"].apply(find_product_info))
        return xml_df


    def finalize_dataframe(self, invoice_data, dynamics_df, vendor_id, purch_id, purch_date, site_id, warehouse_id, business_name):
        """
        Agrega empaques, columnas finales y prepara el DataFrame para la respuesta.

        Args:
            invoice_data (pandas.DataFrame): DataFrame de la factura.
            dynamics_df (pandas.DataFrame): DataFrame de productos de Dynamics.

        Returns:
            pandas.DataFrame: DataFrame finalizado con todas las columnas agregadas.
        """
        invoice_data = invoice_data.merge(
            dynamics_df[['COD_PRODUCT', 'EMPAQUE']], on='COD_PRODUCT', how='left'
        )
        invoice_data.fillna('', inplace=True)
        invoice_data["VENDORID"] = vendor_id
        invoice_data["PURCHID"] = purch_id
        invoice_data["PURCHDATE"] = purch_date
        invoice_data["SITEID"] = site_id
        invoice_data["WAREHOUSEID"] = warehouse_id
        invoice_data["BUSINESSNAME"] = business_name
        return invoice_data


    def generate_response(self, message, success, status_code):
        """
        Genera una respuesta JSON uniforme para todos los returns.

        Args:
            message (str or list): Mensaje o datos a retornar.
            success (bool): Indicador de éxito o error.
            status_code (int): Código de estado HTTP.

        Returns:
            JSON: Respuesta formateada.
        """
        return jsonify({
            "msgApp": message,
            "success": success,
            "status_code": status_code
        })
        


    def get_ourchase_lines_json(self, invoiceId):
        try:
            __sqlQuery = {
                "sqlColumns": [
                    "JSONFILE",
                    "VENDORID",
                    "PURCHID",
                    "PURCHDATE",
                    "SITEID",
                    "WAREHOUSEID",
                    "BUSINESSNAME"
                ],
                "sqlQuery": f"SELECT XMLFILE, VENDORID, PURCHID, PURCHDATE, SITEID, WAREHOUSEID, (SELECT BUSINESSNAME FROM PROVEEDORES WHERE RUC = VENDORID)  AS BUSINESSNAME FROM InvoiceTable WHERE INVOICEID = '{invoiceId}'",
                "sqlType": "APP",
            }

            # print(__sqlQuery['sqlQuery'])

            __resultQuery = sqlController(__sqlQuery).get_statement_select()

            # print(__resultQuery)

            # mostrar avance
            if __resultQuery is None and len(__resultQuery) > 0:

                response_app = jsonify(
                    {
                        "msgApp": "Error al consultar la base de datos por la factura seleccionada",
                        "purchaseApp": False,
                        "success": False,
                        "status_code": 504})
                return response_app

            if __resultQuery is not None and len(__resultQuery) > 0:
                # Configuración de tipos de datos
                self.__dataType.set_column_type_string(__resultQuery, "JSONFILE")
                self.__dataType.set_column_type_string(__resultQuery, "PURCHID")
                self.__dataType.set_column_type_string(__resultQuery, "PURCHDATE")
                self.__dataType.set_column_type_string(__resultQuery, "VENDORID")
                self.__dataType.set_column_type_string(__resultQuery, "SITEID")
                self.__dataType.set_column_type_string(__resultQuery, "WAREHOUSEID")
                self.__dataType.set_column_type_string(__resultQuery, "BUSINESSNAME")

                # Asignación de variables
                __jsonFile = __resultQuery.loc[0, "JSONFILE"]
                __vendorId = __resultQuery.loc[0, "VENDORID"]
                __purchId = __resultQuery.loc[0, "PURCHID"]
                __purchDate = __resultQuery.loc[0, "PURCHDATE"]
                __siteId = __resultQuery.loc[0, "SITEID"]
                __warehouseId = __resultQuery.loc[0, "WAREHOUSEID"]
                __businessName = __resultQuery.loc[0, "BUSINESSNAME"]

                # Leer data del archivo JSON
                __productDataJson = self.__readJson.readJsonGrupo1(__jsonFile)

                if __productDataJson is None:
                    return jsonify({
                        "msgApp": "Error en la lectura del archivo JSON",
                        "purchaseApp": False,
                        "success": False,
                        "status_code": 504
                    })

            # listar los COD_PRODUCT de __productDataXml
            __codProductList = __productDataJson["COD_PRODUCT"].unique().tolist()
            __productDataDynamics = self.get_product_lines(__vendorId, __codProductList)
            # tiempos['Paso 5 - Leer productos desde Dynamics'] = time.time() - start_time
            if __productDataDynamics is None:
                return self.generate_response(
                    "Error en la lectura de productos desde Dynamics, puede que el proveedor no contenga productos registrados", 
                    False, 504
                )
            
            # PASO 6 : COMPARAR PRODUCTOS
            start_time = time.time()
            __productDataJson = self.compare_products(__productDataJson, __productDataDynamics)

            # PASO 7 : AGREGAR EMPAQUES
            __invoiceData = self.agregar_empaques_a_dataframe_principal(__productDataJson)
            # tiempos['Paso 7 - Agregar empaques'] = time.time() - start_time
            if __invoiceData is None:
                return self.generate_response(
                    "Error al agregar empaques al DataFrame principal", False, 504
                )
            
            # PASO 8 : AGREGAR COLUMNAS Y FINALIZAR
            __invoiceData = self.finalize_dataframe(__invoiceData, __productDataDynamics, __vendorId, __purchId, __purchDate, __siteId, __warehouseId, __businessName)
            # tiempos['Paso 8 - Agregar columnas y finalizar'] = time.time() - start_time
            
            # PASO 9: ACTUALIZAR CANTIDAD DE PRODUCTOS EN BD
            cantidad_productos = int(len(__invoiceData))  # aseguramos tipo int

            # Ejecutar procedimiento de actualización (ya tenemos invoiceId como argumento inicial del método)
            invoiceId_int = int(invoiceId)

            __sqlUpdateCantidad = {
                "sqlQuery": "EXEC InvoiceUpdateQuantity ?, ?",
                "sqlEntry": (invoiceId_int, cantidad_productos),
                "sqlType": "APP"
            }

            resultadoUpdate = sqlController(__sqlUpdateCantidad).set_procedure_update()

            if resultadoUpdate != "True":
                return self.generate_response("No se pudo actualizar la cantidad de productos", False, 504)

            # PASO 10: RESPUESTA FINAL
            response_data = {
                "data": __invoiceData.to_dict(orient="records"),
            }
            return self.generate_response(response_data, True, 200)

        except Exception as e:
            return self.generate_response(
                f"Error inesperado: {str(e)}", False, 500
            )
            
    def agregar_empaques_a_dataframe_principal(self, df_productos):

        try:
            # Obtención de los empaques optimizados y con posible caché
            codigos_dynamics = df_productos['CODIGO_PROD_DYNAMICS'].unique().tolist()
            data_empaques = self.get_empaques(codigos_dynamics)

            # Optimizar las columnas necesarias antes del join
            if not data_empaques.empty:
                # Solo trabajamos con las columnas necesarias
                data_empaques = data_empaques[['CODIGO_PROD_DYNAMICS', 'EMPAQUE_LIST']]
                data_empaques.set_index('CODIGO_PROD_DYNAMICS', inplace=True)
                df_productos.set_index('CODIGO_PROD_DYNAMICS', inplace=True)

                # Combinar utilizando join, es más rápido que merge cuando se usan índices
                df_final = df_productos.join(data_empaques, how='left')

                # Reemplazar NaN por vacío de forma directa sin condiciones innecesarias
                df_final['EMPAQUE_LIST'] = df_final['EMPAQUE_LIST'].fillna('')

                # Restaurar índice si es necesario para otras operaciones posteriores
                df_final.reset_index(inplace=True)
            else:
                # Si no hay datos de empaques, devolver el dataframe original sin cambios
                df_final = df_productos.copy()
                df_final['EMPAQUE_LIST'] = ''

            return df_final
        except Exception as e:
            print(f"Error en agregar empaques: {e}")
            return None

    def get_empaques(self, codigos_dynamics):
        # Construir filtro OData correctamente utilizando `or`
        odata_filter = "$select=ProductNumber,FromUnitSymbol,ToUnitSymbol"
        if codigos_dynamics:
            # Construir el filtro con `or` para cada ProductNumber
            codigos_filter = ' or '.join([f"ProductNumber eq '{code}'" for code in codigos_dynamics])
            odata_filter += f"&$filter={codigos_filter}"

        __erpQuery = {
            "odata_entity": "ProductUnitOfMeasureConversions",
            "odata_filter": odata_filter,
        }

        __resultQuery = erpController(__erpQuery).get_records_odata()

        if __resultQuery is not None and not __resultQuery.empty:
            try:
                # Filtrar y procesar los resultados como antes
                __resultQuery.drop(columns=["@odata.etag"], inplace=True, errors='ignore')
                __resultQuery = __resultQuery[__resultQuery['ToUnitSymbol'].str.endswith('.')]

                # Agrupar y concatenar los empaques necesarios
                __resultQuery = (
                    __resultQuery.groupby('ProductNumber', as_index=False)
                    .agg({'FromUnitSymbol': ','.join})
                    .rename(columns={'FromUnitSymbol': 'EMPAQUE_LIST', 'ProductNumber': 'CODIGO_PROD_DYNAMICS'})
                )

            except Exception as e:
                print(f"Error al procesar empaques: {e}")
                return None

        return __resultQuery

    
    def set_purchase_lines(self, jsonPurchase):
        """
        Establece las líneas de compra utilizando datos en formato JSON.

        Args:
            jsonPurchase: Datos de compra en formato JSON.

        Returns:
            Tuple: Cantidad de inserciones exitosas y fallidas.
        """
        success_count = 0
        error_count = 0
        for purchase_data in jsonPurchase:
            __erpQuery = {"odata_entity": "PurchaseOrderLinesV2", "odata_object": purchase_data}
            __response = erpController(__erpQuery).set_records_odata()
            if __response:
                success_count += 1
            else:
                error_count += 1
        return success_count, error_count