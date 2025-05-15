from controller.sqlController import sqlController
from utils.dataType import dataType
import json
from flask import jsonify

class adminUserModel():
        # para el seteo de tipos
    __dataType = dataType()

    def get_data(self):
        try:
            __sqlQuery = {
                "sqlColumns": ["ID", "DNI", "USERNAME", "STATE"],
                "sqlQuery": f"SELECT * FROM USERTABLE",
                "sqlType": "APP",
            }
            __resultQuery = sqlController(__sqlQuery).get_statement_select()

            # print(__resultQuery)

            if __resultQuery is not None and len(__resultQuery) > 0:
                self.__dataType.set_column_type_string(__resultQuery, "ID")
                self.__dataType.set_column_type_string(__resultQuery, "DNI")
                self.__dataType.set_column_type_string(__resultQuery, "USERNAME")
                self.__dataType.set_column_type_string(__resultQuery, "STATE")
            
                return __resultQuery
                    
            else:
                return "errorServer"  # Devolver un mensaje de error si no se encuentran datos
        except Exception as e:
                # Manejar cualquier excepción y devolver un mensaje de error
                print(f"Error en get_document_header: {str(e)}")
                return "errorServer"
        


    def save_data(self, document, username):
        __sqlQuery = {
            "sqlQuery": "EXEC UserCreate ?, ?",
            "sqlEntry": (
                document,
                username
            ),
            "sqlType": "APP",
        }

        result_query = sqlController(__sqlQuery).set_procedure_insert()

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
    
    def update_data(self, id, document, username, state):
        __sqlQuery = {
            "sqlQuery": "EXEC UserUpdate ?, ?, ?, ?",
            "sqlEntry": (
                id,
                document,
                username,
                state
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
         