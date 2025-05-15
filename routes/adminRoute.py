from flask import Blueprint, jsonify, render_template, request
from models.adminModel import adminModel

adminModel = adminModel()


admin = Blueprint('admin', __name__)

@admin.route('/', methods=['GET'])
def index():
    
    return render_template('admin/admin.html')


@admin.route('/get_data', methods=['GET'])
def get_data():
    try:
        response_server = adminModel.get_data()

        if isinstance(response_server, str):
            response_app = jsonify({"msgApp": "errorServer"})
            response_app.status_code = 504
        else:
            response_app = jsonify({"msgApp": "selectDB", "purchaseApp": response_server.to_dict(orient="records")})
            response_app.status_code = 200
        return response_app
    except Exception as e:
                # Manejar cualquier excepción y devolver un mensaje de error
                print(f"Error en get_document_header: {str(e)}")
                return "errorServer"

@admin.route('/update_data', methods=['POST'])
def update_data():
    data = request.json

    id = data['id']
    ruc = data['ruc']
    businessname = data['businessname']
    state = data['state']
    readheadxml = data['readheadxml']
    readxmlbody = data['readxmlbody']
    dataSource = data['dataSource']

    return adminModel.update_data(id, ruc, businessname, state, readheadxml, readxmlbody, dataSource)

