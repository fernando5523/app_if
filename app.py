from flask import Flask, redirect
from flask_cors import CORS

# Importar tus rutas
from routes.invoiceRoute import invoice
from routes.purchaseRoute import purchase
from routes.adminRoute import admin
from routes.adminUserRoute import adminUser
from routes.adminDashboardRoute import adminDashboard

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


# Registrar blueprints
app.register_blueprint(invoice, url_prefix='/invoice')
app.register_blueprint(purchase, url_prefix='/purchase')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(adminUser, url_prefix='/adminUser')
app.register_blueprint(adminDashboard, url_prefix='/adminDashboard')

# Definir una ruta de redireccionamiento por defecto a '/invoice'
@app.route('/')
def default():
    return redirect('/invoice')

if __name__ == '__main__':
    app.run(host="0.0.0.0")

