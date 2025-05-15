var icnError = '/static/img/modals/error-modal.svg';
var tltError = 'Error';
var btnError = 'Cerrar';

var icnWarning = '/static/img/modals/warning-modal.svg';
var tltWarning = 'Advertencia';
var btnWarning = 'Cerrar';

var documentHead = undefined;
var invoiceHead = undefined;
var purchHead = undefined;
var purchList = undefined;
var pdfURL = undefined;
var xmlURL = undefined;

var listaProveedores = undefined;


let  purchHeadResponse;
let  xmlUploadResponse;

let invoiceId;
let invoiceNumber;


let proveedores;
let funcionalidadApp;


/**
 * USUARIOS ASIGNAR
 */
async function cargarUsuarios() {
    const endpoint = '/invoice/get_users';
    try {
        const usuarios = await consultasGet(endpoint);
        const userList = document.getElementById('userList');
        userList.innerHTML = ''; // Limpiar la lista antes de agregar nuevos elementos

        usuarios.forEach(usuario => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center list-group-item-custom';
            li.innerHTML = `
                <div>
                    <i class="bi bi-person-circle me-2 user-icon"></i> <span class="user-name">${usuario.USERNAME}</span>
                </div>
                <button class="btn btn-dark btn-sm btn-custom" onclick="selectUser(${usuario.USERID}, '${usuario.USERNAME}')">Seleccionar</button>
            `;
            userList.appendChild(li);
        });
    } catch (error) {
        console.error('Error al cargar usuarios:', error);
    }
}

// Función para seleccionar usuario
function selectUser(userId, userName) {
    // Guardar usuario seleccionado en cookies
    Cookies.set('selectedUserId', userId);
    Cookies.set('selectedUserName', userName);

    // Actualizar el botón de usuario en la interfaz
    const userButton = document.getElementById('dropdownMenuButton1');
    userButton.innerHTML = `<i class="bi bi-person-circle me-2 user-icon"></i>${userName}`;

    // Mostrar SweetAlert
    Swal.fire({
        title: 'Usuario Seleccionado',
        text: `Has seleccionado a ${userName}`,
        icon: 'success',
        confirmButtonText: 'Aceptar'
    }).then(() => {
        // Cerrar el modal de selección de usuario
        const changeUserModal = bootstrap.Modal.getInstance(document.getElementById('changeUserModal'));
        if (changeUserModal) {
            changeUserModal.hide();
        }
        // Recargar la página
        location.reload();
    });
}


// Función para verificar y mostrar el modal si no hay usuario seleccionado
function checkUserSelection() {
    const selectedUserId = Cookies.get('selectedUserId');
    const selectedUserName = Cookies.get('selectedUserName');

    if (selectedUserId && selectedUserName) {
        // Si hay un usuario seleccionado en cookies, actualizar el botón de usuario
        const userButton = document.getElementById('dropdownMenuButton1');
        userButton.innerHTML = `<i class="bi bi-person-circle me-2 user-icon"></i>${selectedUserName}`;
    } else {
        // Si no hay usuario seleccionado, mostrar el modal de selección de usuario
        const changeUserModal = new bootstrap.Modal(document.getElementById('changeUserModal'));
        changeUserModal.show();

        // Añadir opacidad o deshabilitar el contenido
        document.getElementById('contentWindow').classList.add('blurred');
    }
}

// Llama a cargarUsuarios cuando sea necesario, por ejemplo, cuando se muestra el modal
document.addEventListener('DOMContentLoaded', (event) => {
    cargarUsuarios();
    checkUserSelection();
});

// Interceptar el evento de cierre del modal
document.getElementById('changeUserModal').addEventListener('hide.bs.modal', function (event) {
    const selectedUserId = Cookies.get('selectedUserId');
    const selectedUserName = Cookies.get('selectedUserName');

    if (!selectedUserId || !selectedUserName) {
        event.preventDefault();
        Swal.fire({
            title: 'Advertencia',
            text: 'Debes seleccionar un usuario antes de cerrar el modal.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
    }
});
/**
 * FIN ASIGNAR USUARIOS
 */

// Documento cargado
$(document).ready(async function() {
    try {
        // Mostrar elementos de carga y ocultar contenido
        mostrarLoader();

        // Validar usuarios
        checkUserSelection();

        // otros códigos de inicialización aquí...
    } catch (error) {
        console.error('Error:', error);
    }
});





// Agregar proveedores al select
async function agregarProveedores() {
    const endpoint = '/invoice/get_suppliers';
    try {
        proveedores = await consultasGet(endpoint);
        // console.log(proveedores);

        // para el select de pedidos
        const selectProveedor = $('#supplier').empty();

        selectProveedor.append('<option value="0" selected>Seleccionar el Proveedor</option>');

        proveedores.forEach(proveedor => {
            selectProveedor.append(`<option value="${proveedor.RUC}">${proveedor.BUSINESSNAME}</option>`);
        });
        estilosSelects(selectProveedor);

        // para el select de descargas
        const selectProveedorDescarga = $('#supplierDownload').empty();
        selectProveedorDescarga.append('<option value="0" selected>Seleccionar el Proveedor</option>');
        proveedores.forEach(proveedor => {
            selectProveedorDescarga.append(`<option value="${proveedor.RUC}">${proveedor.BUSINESSNAME}</option>`);
        });
        estilosSelects(selectProveedorDescarga);

    } catch (error) {
        console.error('Error al agregar proveedores:', error);
        alertaError("Proveedores no localizados")
    } finally{
        mostrarContenido()
        
    }
}


// agregar trv
async function agregarTrv(ruc) {
    const endpoint = "/invoice/purch/" + ruc;
    try {
        mostrarLoader()

        const trv = await consultasGet(endpoint);

        const selectTrv = $("#numberPurch");
        selectTrv.empty().append('<option value="0" selected>Seleccionar el número de TRV</option>');

        trv.forEach(item => {
            const optionText = `${item.WAREHOUSEID} - ${item.PURCHID} - ${item.PURCHDATE}`;
            selectTrv.append(`<option value="${item.PURCHID}">${optionText}</option>`);
        });

        estilosSelects("#numberPurch");
    } catch (error) {
        console.error('Error al agregar TRV:', error);
        alertaError("TRV no localizados")
    } finally{
        mostrarContenido()
    }
}

async function handleProveedorChange() {
    resetFields();
    let selectedProveedor = $('#supplier').val();

    if (selectedProveedor == 0) {
        alertaError("TRV no localizados");
        return;
    }



    agregarTrv(selectedProveedor);

}



// manejar la carga de trv por proveedor
async function mostarDatos(){
    mostrarLoader();
    let ruc = $('#supplier').val();
    let trv = $('#numberPurch').val();
    let xmlFile = $('#xmlPurch')[0];
    let jsonText = $('#jsonText').val();


    let endpointPurchHead = `/invoice/purch/head/${ruc}/${trv}`;
    let endpointDataUpload;
    let formData = new FormData();


    // guardar archivo

    if (funcionalidadApp == "XML"){
        endpointDataUpload = '/invoice/xml/upload';
        // datos del xml
        let file = xmlFile.files[0];
        let fileName = file.name;
        
        formData.append('xmlfile', file, fileName);
        formData.append('supplier', ruc);

    } else {
        
        endpointDataUpload = '/invoice/json/upload';
        // datos del json pegado
        try {
            let jsonParsed = JSON.parse(jsonText);
            let jsonRuc = jsonParsed.ruc;
            let jsonSerie = jsonParsed.serie.replace(/\s+/g, '_'); // Reemplazar espacios por guiones bajos
            let fileName = `${jsonRuc}_${jsonSerie}.json`;

            let jsonBlob = new Blob([jsonText], { type: 'application/json' });
            let jsonFile = new File([jsonBlob], fileName, { type: 'application/json' });

            formData.append('jsonfile', jsonFile);
            formData.append('supplier', ruc);
        } catch (error) {
            alertaError("El texto pegado no es un JSON válido");
            ocultarLoader();
            return;
        }
    }

    try {
        // Realizar ambas solicitudes POST simultáneamente
        [purchHeadResponse, xmlUploadResponse] = await Promise.all([
            consultasPost(endpointPurchHead),
            consultasPostData(endpointDataUpload, formData)
        ]);

        // console.log(purchHeadResponse);
        // console.log(xmlUploadResponse);
        
        // obtenemos los datos de purchHeadResponse
        completarDatosGenerales(purchHeadResponse[0], xmlUploadResponse);

        // Procesar la respuesta del endpointXmlUpload si es necesario
        mostrarContenido();
    } catch (error) {
        console.error('Error al obtener los datos del pedido de compra o al cargar el XML:', error);
    }
}

// Completamos el formulario de datos generales
async function completarDatosGenerales(purchHead, invoiceHead){
    $('#purchId').val(purchHead.PURCHID);
    $('#vendorId').val(purchHead.VENDORID);
    $('#vendorName').val(purchHead.VENDORNAME);
    $('#warehouseName').val(purchHead.WAREHOUSEID);
    $('#purchStatus').val(purchHead.PURCHSTATUS + ' - ' + purchHead.DOCUMENTSTATE);
    $('#workerId').val(purchHead.WORKERID);
    $('#workerName').val(purchHead.WORKERNAME);
    $('#purchDate').val(purchHead.PURCHDATE);
    $('#invoiceId').val(invoiceHead.INVOICENUMBER); // No estoy seguro si aquí debe ser purchHead o invoiceHead
    $('#purchCurrency').val(purchHead.PURCHCURRENCY);
    $('#purchPayment').val(purchHead.PURCHPAYMENT);



}



async function validarProductos(){
    mostrarLoader()
    let purchHead = purchHeadResponse[0]
    let invoiceHead= xmlUploadResponse

    let formData = new FormData();

    formData.append('purchId', purchHead.PURCHID);
    formData.append('vendorId', purchHead.VENDORID);
    formData.append('invoiceNumber', invoiceHead.INVOICENUMBER);
    formData.append('invoiceDate', invoiceHead.INVOICEDATE);
    formData.append('purchDate', purchHead.PURCHDATE);
    formData.append('purchCurrency', purchHead.PURCHCURRENCY);
    formData.append('purchPayment', purchHead.PURCHPAYMENT);
    formData.append('siteId', purchHead.SITEID);
    formData.append('warehouseId', purchHead.WAREHOUSEID);
    // formData.append('pdfFile', pdfURL);
    formData.append('xmlFile', invoiceHead.URLFILE);
    formData.append('userId', parseInt(Cookies.get('selectedUserId')))

    
    let endpoint = '/invoice/invoice_create'
    let response = await consultasPostDataCreate(endpoint, formData)


    let idPedidoDataBase = parseInt(response[0]["INVOICEID"])
    let factura = invoiceHead.INVOICENUMBER
    let proveedor = purchHead.VENDORID

    if (idPedidoDataBase > 0) {
        $(location).attr('href', '/purchase/' + idPedidoDataBase + '/' + factura + '/' + proveedor + '/' + funcionalidadApp);
    }
}


function resetFields() {
    $('#xmlPurch').val('');
    $('#purchId').val('');
    $('#vendorId').val('');
    $('#vendorName').val('');
    $('#warehouseName').val('');
    $('#purchStatus').val('');
    $('#workerId').val('');
    $('#workerName').val('');
    $('#purchDate').val('');
    $('#invoiceId').val('');
    $('#purchCurrency').val('');
    $('#purchPayment').val('');
    $('#jsonText').val('');
}


function validarXml(){
    //validamos el xml
    let xmlFile = $('#xmlPurch')[0];
    // nombre del archivo xml
    let fileName = xmlFile.files[0].name;

    // obtenemos el proveedor
    let vendorId = $('#supplier').val();

    // validamos el nombre del archivo con el proveedor
    return fileName.includes(vendorId);

}

function ocultarInputs(){
    $('#jsonField').hide(); // Ocultar campo JSON por defecto
    $('#xmlField').hide();  // Ocultar campo XML por defecto
}


function pegarJson() {
    navigator.clipboard.readText().then(text => {
        try {
            let jsonData = JSON.parse(text);
            
            // Validar si el JSON tiene los campos requeridos
            if (jsonData.ruc && jsonData.serie && jsonData.fecha && jsonData.tipo_moneda && jsonData.items && jsonData.items.length > 0) {
                let item = jsonData.items[0];
                if (item.codigo && item.descripcion && item.cantidad && item.sub_total && item.bonificacion) {
                    $('#jsonText').val(text);
                } else {
                    throw new Error("El JSON no contiene todos los campos requeridos en los items.");
                }
            } else {
                throw new Error("El JSON no contiene todos los campos requeridos.");
            }
        } catch (err) {
            alertaError("El texto seleccionado no es un JSON válido o le faltan campos requeridos.");
            $('#jsonText').val('');
        }
    }).catch(err => {
        console.error('Error al pegar JSON:', err);
        alertaError("Error al acceder al portapapeles");
    });
}


function toggleFields() {
    // obtener el proveedor
    let supplier = $('#supplier').val();

    if ($('#xmlOption').is(':checked')) {
        $('#jsonField').hide();
        $('#xmlField').show();
        funcionalidadApp = "XML"
    } else if ($('#jsonOption').is(':checked')) {
        $('#jsonField').show();
        $('#xmlField').hide();
        funcionalidadApp = "JSON"
    }

    if (supplier == "20100055237") {
        $('#downloadJsonAlicorp').show();
    }else{
        $('#downloadJsonAlicorp').hide();
    }

}


function descargarXml() {
    const proveedor = $('#supplierDownload').val().trim();
    const numeroFactura = $('#invoiceNumberDownload').val().trim();

    if (!proveedor || !numeroFactura) {
        alertaError('Por favor, ingresa el proveedor y el número de factura.');
        return;
    }

    const formData = new FormData();
    formData.append('proveedor', proveedor);
    formData.append('numeroFactura', numeroFactura);

    const endpoint = '/invoice/download_xml';

    fetch(endpoint, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (response.ok) {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/zip')) {
                return response.blob();  // Si la respuesta es un archivo ZIP, obtenerlo como blob
            } else {
                return response.json().then(errorData => {
                    throw new Error(`Error: ${errorData.message || 'Ocurrió un error inesperado.'}`);
                });
            }
        } else {
            return response.json().then(errorData => {
                throw new Error(`Error ${errorData.status_code}: ${errorData.message}`);
            });
        }
    })
    .then(blob => {
        if (blob) {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${proveedor}_${numeroFactura}.zip`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

            alertaCorrecto('Archivo descargado exitosamente.');
            $('#supplierDownload').val('');
            $('#invoiceNumberDownload').val('');
        }
    })
    .catch(error => {
        console.error('Hubo un problema con la descarga:', error.message);
        alertaErrorDescargaXML(`Error al descargar el archivo: ${error.message}`);
    });
}



async function confirmarDescargarJson() {
    let endpoint = "/invoice/download_json_alicorp";
    let serie = $("#serieInput").val().trim();
    let correlativo = $("#correlativoInput").val().trim();

    if (!serie || !correlativo) {
        alertaError("Debe ingresar la serie y el correlativo.");
        return;
    }

    let formData = new FormData();
    formData.append("serie", serie);
    formData.append("correlativo", correlativo);

    try {
        // Mostrar mensaje de descarga
        $("#progressContainer").show();
        $("#btn_footer").hide()
        $("#errorContainer").hide().html("");

        let response = await $.ajax({
            url: endpoint,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false
        });

        console.log(response);
        

        $("#progressContainer").hide();
        $("#btn_footer").show()

        if (response.success) {
            $('#jsonText').val(JSON.stringify(response.data, null, 2));
            $('#jsonModal').modal('hide');
            alertaCorrecto("SE AGREGARON LOS DATOS CORRECTAMENTE AL CAMPO");
            $("#btn_footer").show()
        } else {
            // console.error("Error en la respuesta AJAX:", response);
            $("#errorContainer").show().html(`
                <div class="alert alert-danger">
                    <strong>Error en la descarga:</strong>
                    <pre>${JSON.stringify(response, null, 2)}</pre>
                </div>
            `);
            $("#btn_footer").show()
        }
    } catch (error) {
        $("#progressContainer").hide();
        // console.error("Error al descargar JSON:", error);
        let errorMessage = error.responseJSON ? JSON.stringify(error.responseJSON, null, 2) : JSON.stringify(error, null, 2);

        $("#errorContainer").show().html(`
            <div class="alert alert-danger">
                <strong>Error al descargar JSON:</strong>
                <pre>${errorMessage}</pre>
            </div>
        `);

        $("#btn_footer").show()
    }
}







// Documento cargado
$(document).ready(async function() {
    try {

        // mostrar modal de descargar alicorp
        $("#downloadJsonAlicorp").click(function (e) { 
            e.preventDefault();
            $('#jsonModal').modal('show');
        });

        $("#confirmDownload").click(function (e) { 
            e.preventDefault();
            confirmarDescargarJson()
        });

        // Deshabilitar la entrada manual en el textarea
        $('#jsonText').prop('readonly', true);

        // Mostrar elementos de carga y ocultar contenido
        mostrarLoader()

        // ocultar inputs
        ocultarInputs()

        // Validar usuarios
        checkUserSelection();


        // usuarios
        cargarUsuarios()
        
        // proveedores
        agregarProveedores()

        // Manejar el cambio en el select de proveedores
        $('#supplier').change(handleProveedorChange);

        // Manejar los cambios de xml o json
        toggleFields();
        $('input[name="format"]').change(toggleFields);


        // descarga de xml
        $('#formDownloadFactura').submit(function (e) {
            e.preventDefault();
            descargarXml();
        });

        // mostrar datos generales
        $('#formPurch').submit(function (e) {
            e.preventDefault();
            mostarDatos();
        })

        // validar productos
        $('#formInvoice').submit(function (e) {
            e.preventDefault();
            validarProductos();
        })

        // pegar texto json
        $("#pasteJson").click(function (e) { 
            e.preventDefault();
            pegarJson()
        });

        
    
    } catch (error) {
        console.error('Error:', error);
    }
});


// Llama a checkUserSelection cada vez que el modal se muestra
document.getElementById('changeUserModal').addEventListener('shown.bs.modal', cargarUsuarios);