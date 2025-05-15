from flask import Blueprint, jsonify, render_template, request
from models.adminUserModel import adminUserModel

adminUsModel = adminUserModel()


adminUser = Blueprint('adminUser', __name__)

@adminUser.route('/', methods=['GET'])
def index():
    
    return render_template('admin/admin_user.html')


@adminUser.route('/get_data', methods=['GET'])
def get_data():
    try:
        response_server = adminUsModel.get_data()

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
    


@adminUser.route('/save_data', methods=['POST'])
def save_data():
    data = request.json

    dni = data['dni']
    name = data['name'] 

    return adminUsModel.save_data(dni, name)





@adminUser.route('/update_data', methods=['POST'])
def update_data():
    data = request.json

    id = data['id']
    dni = data['dni']
    name = data['name']
    state = data['state']

    return adminUsModel.update_data(id, dni, name, state)

