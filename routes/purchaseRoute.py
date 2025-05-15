from flask import Blueprint, jsonify, render_template, request
from models.purchaseModel import purchaseModel
import os

purchase = Blueprint('purchase', __name__)
purchaseModel = purchaseModel()

@purchase.route('/<string:id>/<string:factura>/<string:proveedor>/<string:funcionalidadApp>', methods=["GET"])
def index(id, factura, proveedor, funcionalidadApp):
    return render_template("purchase/purchase.html", id=id, factura=factura, proveedor=proveedor, funcionalidadApp=funcionalidadApp)

# carga de los productos xml
@purchase.route('/product/<id>', methods=["GET"])
def purchase_product(id):
    return purchaseModel.get_purchase_lines(id)


# carga de los productos json
@purchase.route('/productJson/<id>', methods=["GET"])
def purchase_product_json(id):
    return purchaseModel.get_ourchase_lines_json(id)


@purchase.route('/upload', methods=["POST"])
def purchase_upload():
    try:
        data = request.json
        # Procesar los 5 elementos directamente, sin partición adicional
        success_count, error_count = purchaseModel.set_purchase_lines(data)

        # Preparar el mensaje de respuesta
        response_message = (
            f"Total de {len(data)} datos procesados.\n"
            f"{success_count} correctos.\n"
            f"{error_count} errores.\n"
        )

        # Crear la respuesta en formato JSON
        response_app = jsonify({
            "msgApp": response_message,
            "success_count": success_count,
            "error_count": error_count
        })
        response_app.status_code = 201
        return response_app

    except Exception as e:
        # Manejo de excepciones y envío de mensaje de error
        return jsonify({
            "msgApp": "Error al procesar la solicitud.",
            "error": str(e)
        }), 500
