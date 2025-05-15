from controller.sqlController import sqlController
from utils.dataType import dataType
import json
from flask import jsonify

class adminModel():
        # para el seteo de tipos
    __dataType = dataType()

    def get_data(self):
        try:
            __sqlQuery = {
                "sqlColumns": ["ID", "RUC", "BUSINESSNAME", "STATE", "READXMLHEADGROUP", "READXMLBODYGROUP", "DATASOURCE"],
                "sqlQuery": f"SELECT ID,RUC,BUSINESSNAME,STATE,READXMLHEADGROUP,READXMLBODYGROUP, DATASOURCE FROM PROVEEDORES",
                "sqlType": "APP",
            }
            __resultQuery = sqlController(__sqlQuery).get_statement_select()

            # print(__resultQuery)

            if __resultQuery is not None and len(__resultQuery) > 0:
                self.__dataType.set_column_type_string(__resultQuery, "ID")
                self.__dataType.set_column_type_string(__resultQuery, "RUC")
                self.__dataType.set_column_type_string(__resultQuery, "BUSINESSNAME")
                self.__dataType.set_column_type_string(__resultQuery, "STATE")
                self.__dataType.set_column_type_string(__resultQuery, "READXMLHEADGROUP")
                self.__dataType.set_column_type_string(__resultQuery, "READXMLBODYGROUP")
                self.__dataType.set_column_type_string(__resultQuery, "DATASOURCE")
            
                return __resultQuery
                    
            else:
                return "errorServer"  # Devolver un mensaje de error si no se encuentran datos
        except Exception as e:
                # Manejar cualquier excepción y devolver un mensaje de error
                print(f"Error en get_document_header: {str(e)}")
                return "errorServer"
    
    def update_data(self,id, ruc, businessname, state,readheadxml, readxmlbody, dataSource):
        __sqlQuery = {
            "sqlQuery": "EXEC ProveedorUpdate ?, ?, ?, ?, ?, ?, ?",
            "sqlEntry": (
                id,
                ruc,
                businessname,
                state,
                readheadxml,
                readxmlbody,
                dataSource
            ),
            "sqlType": "APP",
        }

        result_query = sqlController(__sqlQuery).set_procedure_update()

        if result_query is not None and result_query == "True":
            return jsonify(
                {
                    "success" : True, 
                    "status_code" : 201
                }
            )
        else:
            return jsonify(
                {
                    "success" : False,
                    "status_code" : 504
                }
            )
         