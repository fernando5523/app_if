from flask import Blueprint, jsonify, render_template, request, send_file
from models.invoiceModel import invoiceModel
from utils.urlFile import urlFile
import os
from io import BytesIO
import zipfile

invoice = Blueprint('invoice', __name__)


invoice_model = invoiceModel()

urlFolder = urlFile.get_upload_folder()


# para la plantilla de inicio
@invoice.route('/', methods=["GET"])
def index():
    return render_template("invoice/invoice.html")


# Ruta para obtener la lista de compras por proveedor
@invoice.route('/purch/<string:vendorId>', methods=["GET"])
def get_purchases(vendorId):
    try:
        response_server = invoice_model.get_purch_list(vendorId)
        
        if isinstance(response_server, str):
            response_app = jsonify({"msgApp": "errorServer"})
            response_app.status_code = 504
        else:
            response_app = jsonify({"msgApp": "selectDB", "purchApp": response_server.to_dict(orient="records")})
            response_app.status_code = 200
    except Exception as e:
        response_app = jsonify({"msgApp": "error", "error": str(e)})
        response_app.status_code = 500
    
    return response_app


# Ruta para obtener la lista de compras por proveedor
@invoice.route('/get_suppliers', methods=["GET"])
def get_supplier():
    try:
        response_server = invoice_model.get_suppliers()
        
        if isinstance(response_server, str):
            response_app = jsonify({"msgApp": "errorServer"})
            response_app.status_code = 504
        else:
            response_app = jsonify({"msgApp": "selectDB", "purchApp": response_server.to_dict(orient="records")})
            response_app.status_code = 200
    except Exception as e:
        response_app = jsonify({"msgApp": "error", "error": str(e)})
        response_app.status_code = 500
    
    return response_app



# ruta para cargar datos del trv
@invoice.route('/purch/head/<string:ruc>/<string:trv>', methods=["POST", "GET"])
def invoice_purch_head(ruc,trv):
    try:
        response_server = invoice_model.get_purch_header(ruc,trv)

        if isinstance(response_server, str):
            response_app = jsonify({"msgApp": "errorServer"})
            response_app.status_code = 504
        else:
            response_app = jsonify({"msgApp": "selectDB", "purchApp": response_server.to_dict(orient="records")})
            response_app.status_code = 200
    except Exception as e:
        response_app = jsonify({"msgApp": "error", "error": str(e)})
        response_app.status_code = 500

    return response_app


# ruta para cargar pdf 
@invoice.route('/pdf/upload', methods=["POST", "GET"])
def invoice_pdf_upload():
    try:
        ruc = request.form["supplier"]
        pdfFile = request.files["pdfFile"]

        if pdfFile:
            urlFile = os.path.join(urlFolder, pdfFile.filename)
            pdfFile.save(urlFile)

            responseServer = invoice_model.get_document_pdf_header(ruc, urlFile)

            if isinstance(responseServer, str):
                responseApp = jsonify({"msgApp": "errorServer"})
                responseApp.status_code = 504
            else:
                responseApp = jsonify({"msgApp": "selectDB", "pdfApp": responseServer})
                responseApp.status_code = 200
        else:
            responseApp = jsonify({"msgApp": "savePDF"})
            responseApp.status_code = 400

        return responseApp

    except Exception as e:
        responseApp = jsonify({"msgApp": "error", "error": str(e)})
        responseApp.status_code = 500

        return responseApp

# ruta para cargar el xml
@invoice.route('/xml/upload', methods=["POST", "GET"])
def invoice_xml_upload():
    try:
        ruc = request.form["supplier"]
        pdfFile = request.files["xmlfile"]

        if pdfFile:
            urlFile = os.path.join(urlFolder, pdfFile.filename)
            pdfFile.save(urlFile)

            responseServer = invoice_model.get_document_xml_header(ruc, urlFile)

            if isinstance(responseServer, str):
                responseApp = jsonify({"msgApp": "errorServer"})
                responseApp.status_code = 504
            else:
                responseApp = jsonify({"msgApp": "selectDB", "xmlApp": responseServer})
                responseApp.status_code = 200
        else:
            responseApp = jsonify({"msgApp": "saveXML"})
            responseApp.status_code = 400

        return responseApp

    except Exception as e:
        print("error", str(e))
        responseApp = jsonify({"msgApp": "error", "error": str(e)})
        responseApp.status_code = 500

        return responseApp
    

@invoice.route('/json/upload', methods=["POST", "GET"])
def invoice_json_upload():
    try:
        ruc = request.form["supplier"]
        jsonFile = request.files["jsonfile"]

        if jsonFile:
            urlFile = os.path.join(urlFolder, jsonFile.filename)
            jsonFile.save(urlFile)


            responseServer = invoice_model.get_document_json_header(urlFile)


            if isinstance(responseServer, str):
                responseApp = jsonify({"msgApp": "errorServer"})
                responseApp.status_code = 504
            else:
                responseApp = jsonify({"msgApp": "selectDB", "xmlApp": responseServer})
                responseApp.status_code = 200
        else:
            responseApp = jsonify({"msgApp": "saveXML"})
            responseApp.status_code = 400

        return responseApp

    except Exception as e:
        print("error", str(e))
        responseApp = jsonify({"msgApp": "error", "error": str(e)})
        responseApp.status_code = 500

        return responseApp


# ruta para crear el pedido
@invoice.route('/invoice_create', methods=["POST", "GET"])
def invoice_create():
    trv = request.form.get("purchId", None) # NUMERO DE TRV
    ruc = request.form.get("vendorId", None) # RUC
    factura = request.form.get("invoiceNumber", None) # ESO NO ESTA
    fechafactura = request.form.get("invoiceDate", None) # ESO NO ESTA
    fechaComPRA = request.form.get("purchDate", None) # Fecha de Creacion
    moneda = request.form.get("purchCurrency", None) # divisa
    metodoPago = request.form.get("purchPayment", None) # Metodo de pago
    idSitio = request.form.get("siteId", None) # no esta
    idAlmacen = request.form.get("warehouseId", None) #
    # pdfFile = request.form.get("pdfFile", None) #
    xmlFile = request.form.get("xmlFile", None) #
    userId = request.form.get("userId", None) #
    
    responseServer = invoice_model.set_invoice_create(
        trv, ruc, factura, fechafactura, fechaComPRA, moneda, metodoPago, idSitio, idAlmacen, xmlFile, userId
    )

    if isinstance(responseServer, str):
        responseApp = jsonify({"msgApp": "errorServer"})
        responseApp.status_code = 504
    else:
        responseApp = jsonify({"msgApp": "createDB", "invoiceApp": responseServer.to_dict(orient="records")})
        responseApp.status_code = 200

    return responseApp




# Ruta para obtener la lista de compras por proveedor
@invoice.route('/get_users', methods=["GET"])
def get_users():
    try:
        response_server = invoice_model.get_users()
        
        if isinstance(response_server, str):
            response_app = jsonify({"msgApp": "errorServer"})
            response_app.status_code = 504
        else:
            response_app = jsonify({"msgApp": "selectDB", "purchApp": response_server.to_dict(orient="records")})
            response_app.status_code = 200
    except Exception as e:
        response_app = jsonify({"msgApp": "error", "error": str(e)})
        response_app.status_code = 500
    
    return response_app

# ruta para descargar xml
@invoice.route('/download_xml', methods=["POST"])
def download_xml():
    try:
        ruc = request.form.get("proveedor")
        factura = request.form.get("numeroFactura")

        if not ruc or not factura:
            return jsonify({
                "success": False,
                "status_code": 400,
                "message": "Los parámetros 'proveedor' y 'numeroFactura' son requeridos."
            }), 400

        result = invoice_model.download_xml_sunat(ruc, factura)

        if result.get("success"):
            contenido = result.get("contenido")
            nombre_archivo = result.get("nombre_archivo")

            return send_file(
                BytesIO(contenido),
                mimetype='application/zip',
                as_attachment=True,
                download_name=nombre_archivo
            )
        else:
            status_code = result.get("status_code", 500)
            message = result.get("message", "Ocurrió un error desconocido.")
            return jsonify({
                "success": False,
                "status_code": status_code,
                "message": message
            }), status_code

    except Exception as e:
        return jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Error interno del servidor: {str(e)}"
        }), 500



# ruta para descargar xml
@invoice.route('/download_json_alicorp', methods=["POST"])
def download_json_alicorp():
    try:
        serie = request.form.get("serie")
        correlativo = request.form.get("correlativo")

        # eliminar los ceros a la izquierda
        correlativo = correlativo.lstrip('0')

        if not serie or not correlativo:
            return jsonify({
                "success": False,
                "status_code": 400,
                "message": "Los parámetros 'serie' y 'correlativo' son requeridos."
            }), 400

        result = invoice_model.download_json_sunat_alicorp(serie, correlativo)

        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "status_code": 500,
                "message": result.get("error", "Error en la obtención del JSON")
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "status_code": 500,
            "message": f"Error interno del servidor: {str(e)}"
        }), 500
