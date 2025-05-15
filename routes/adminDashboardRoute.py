from flask import Blueprint, jsonify, render_template, request
from models.adminDashboardModel import adminDashboardModel
# from models.adminUserModel import adminUserModel

adminModel = adminDashboardModel()


adminDashboard = Blueprint('adminDashboard', __name__)

@adminDashboard.route('/', methods=['GET'])
def index():
    return render_template('admin/admin_dashboard.html')


@adminDashboard.route('/get_proveedores', methods=['GET'])
def get_proveedores():
    try:
        response_server = adminModel.get_top_proveedores()

        if isinstance(response_server, str):
            response_app = jsonify({"msgApp": "errorServer"})
            response_app.status_code = 504
        else:
            # Convertir el DataFrame a una lista de diccionarios
            response_list = response_server.to_dict(orient="records")
            
            # Separar los datos en dos listas
            cantidades = [item['CANTIDAD'] for item in response_list]
            proveedores = [item['PROVEEDOR'] for item in response_list]

            response_app = jsonify({
                "msgApp": "selectDB",
                "cantidades": cantidades,
                "proveedores": proveedores
            })
            response_app.status_code = 200
        return response_app
    except Exception as e:
        # Manejar cualquier excepción y devolver un mensaje de error
        print(f"Error en get_proveedores: {str(e)}")
        return jsonify({"msgApp": "errorServer"}), 500
    
@adminDashboard.route('/get_users', methods=['GET'])
def get_users():
    try:
        response_server = adminModel.get_top_usuarios()

        if isinstance(response_server, str):
            response_app = jsonify({"msgApp": "errorServer"})
            response_app.status_code = 504
        else:
            # Convertir el DataFrame a una lista de diccionarios
            response_list = response_server.to_dict(orient="records")
            
            # Separar los datos en dos listas
            cantidades = [item['CANTIDAD'] for item in response_list]
            proveedores = [item['USUARIO'] for item in response_list]

            response_app = jsonify({
                "msgApp": "selectDB",
                "cantidades": cantidades,
                "usuarios": proveedores
            })
            response_app.status_code = 200
        return response_app
    except Exception as e:
        # Manejar cualquier excepción y devolver un mensaje de error
        print(f"Error en get_users ruta: {str(e)}")
        return jsonify({"msgApp": "errorServer"}), 500


@adminDashboard.route('/get_ingresos/<string:date_init>/<string:date_end>', methods=['GET'])
def get_ingresos(date_init, date_end):
    try:
        # Obtener datos de SQL Server y OData
        response_server = adminModel.get_ingresos_sql(date_init, date_end)

        if isinstance(response_server, str):
            response_app = jsonify({"msgApp": "errorServer"})
            response_app.status_code = 504
        else:
            # Convertir el DataFrame a una lista de diccionarios
            response_list = response_server.to_dict(orient="records")
            
            # Separar los datos en dos listas
            fechas = [item['FECHA'] for item in response_list]
            cantidades = [item['CANTIDAD'] for item in response_list]

            response_app = jsonify({
                "msgApp": "selectDB",
                "fechas": fechas,
                "cantidades": cantidades
            })
            response_app.status_code = 200
        return response_app
    except Exception as e:
        # Manejar cualquier excepción y devolver un mensaje de error
        print(f"Error en get_users ruta: {str(e)}")
        return jsonify({"msgApp": "errorServer"}), 500