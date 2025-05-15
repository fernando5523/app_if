var tablePurchase = $('#purchaseLines');

let Trv = "TRV";
let PurchaseOrderNumber = undefined;
let ReceivingSiteId = undefined;
let ReceivingWarehouseId = undefined;
let RequestedDeliveryDate = undefined;

let username;
let userId;

let totalDatos = 0;
let totalCorrectos = 0;

function setUser() {
    userId = Cookies.get('selectedUserId');
    username = Cookies.get('selectedUserName');

    // Asignar al h1
    $("#userName").text(username);
}

function diseñoTabla() {
    // Configuración del DataTable
    $('#purchaseProduct').DataTable({
        info: false,
        language: {
            infoEmpty: 'No hay filas para mostrar.',
            zeroRecords: 'No se encontraron resultados.',
        },
        ordering: false,
        paging: false,
        searching: false,
        scrollX: true,
        rowCallback: function(row, data, index) {
            if (index % 2 === 0) {
                $(row).addClass('fila-negra'); // Clase para fila negra
            } else {
                $(row).removeClass('fila-negra'); // Quitar clase para fila negra
            }
        }
    });
}

// Función para obtener los productos de la factura      
async function cargarProductos() {

    let endpoint;

    if (funcionalidad == "XML"){
        endpoint = "/purchase/product/" + id;
    }else{
        endpoint = "/purchase/productJson/" + id;
    }

    let response = await productDataOptimizado(endpoint);
     
    if (!response) {
        return;
    }

    tablePurchase.empty();

    for (let i = 0; i < response.length; i++) {
        productLineSearch(response[i], i, tablePurchase);
    }

    // Asignar variables a los fijos
    PurchaseOrderNumber = response[0].PURCHID;
    RequestedDeliveryDate = new Date(response[0].PURCHDATE);
    ReceivingSiteId = response[0].SITEID;
    ReceivingWarehouseId = response[0].WAREHOUSEID;

    // Nombre del proveedor
    $("#bussines_name").text(response[0].BUSINESSNAME);

    diseñoTabla();

    calculateAmount(response);

    mostrarContenido();
}

// Función para crear el select de empaques
function createEmpaqueSelect(index, empaque, empaque_seleccionado) {
    if (empaque === "") {
        return '<td id="empaque-' + index + '" style="text-align: center; padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="empaque-' + index + '" class="form-control" style="text-align: center !important;font-weight: bold; text-align: justify !important;background-color: red" value="Sin Empaques" disabled></td>';
    }

    let empaqueOptions = empaque.split(',').map(option => option.trim());
    let empaqueSelect = '<select name="empaque-' + index + '" class="form-control design_empaque" style="font-weight: bold; text-align: center; !important;">';

    empaqueOptions.forEach(option => {
        let selected = (option === empaque_seleccionado) ? ' selected' : '';
        empaqueSelect += '<option class="form-control" style="padding: 15px; font-weight: bold; text-align: center; !important;" value="' + option + '"' + selected + '>' + option + '</option>';
    });

    empaqueSelect += '</select>';

    return '<td id="empaque-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;">' + empaqueSelect + '</td>';
}

// Función para completar datos en la tabla
function productLineSearch(dataLine, index, table) {
    index = index + 1;
    let lineaFE = '<tr id="fila-' + index + '"><td id="linea-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="linea-' + index + '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important;" value="' + index + '" disabled></td>';
    let codigoFE = '<td id="codigo-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;">';

    if (dataLine.CODIGO_PROD_DYNAMICS === null) {
        codigoFE += '<input type="text" name="codigo-' + index + '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important; background-color: red;" value="NO" disabled>';
    } else {
        codigoFE += '<input type="text" name="codigo-' + index + '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important;" value="' + dataLine.CODIGO_PROD_DYNAMICS + '" disabled>';
    }

    codigoFE += '</td>';

    let descripcionFE = '<td id="descripcion-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="descripcion-' + index + '" class="form-control" style="font-weight: bold; text-align: justify; width: 636px !important;" value="' + dataLine.DESCRIPTION + '" disabled></td>';
    let empaqueFE = createEmpaqueSelect(index, dataLine.EMPAQUE_LIST, dataLine.EMPAQUE);
    let impuestoFE = '<td id="impuesto-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="impuesto-' + index + '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important;" value="IGV" disabled></td>';
    let cantidadFE = '<td id="cantidad-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="cantidad-' + index + '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important;" value="' + dataLine.PRODUCT_QUANTITY + '" disabled></td>';
    let precioUniFE = '<td id="precio-unit-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="precio-unit-' + index + '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important;" value="' + dataLine.UNIT_PRICE + '" disabled></td>';
    let subTotalFE = '<td id="sub-total-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="sub-total-' + index + '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important;" value="' + dataLine.SUB_TOTAL + '" disabled></td>';
    let igvFE = '<td id="igv-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="igv-' + index + '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important;" value="' + dataLine.IGV + '" disabled></td>';
    let totalFE = '<td id="total-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="total-' + index + '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important;" value="' + dataLine.TOTAL + '" disabled></td>';
    let identificado = '<td id="identificado-' + index + '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="identificado-' + index + '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important; background-color: ' + (dataLine.EN_DYNAMICS === 'NO' ? 'red' : 'white') + '" value="' + dataLine.EN_DYNAMICS + '" disabled></td></tr>';

    table.append(
        lineaFE +
        codigoFE +
        descripcionFE +
        empaqueFE +
        impuestoFE +
        cantidadFE +
        precioUniFE +
        subTotalFE +
        igvFE +
        totalFE +
        identificado
    );
}

function calculateAmount(dataXML) {
    let subAmount = 0.0;
    let impAmount = 0.0;
    let totAmount = 0.0;

    for (let i = 0; i < dataXML.length; i++) {
        subAmount += parseFloat(dataXML[i].SUB_TOTAL);
        impAmount += parseFloat(dataXML[i].IGV);
        totAmount += parseFloat(dataXML[i].TOTAL);
    }

    $('#taxableAmount').val(subAmount.toFixed(2));
    $('#taxAmount').val(impAmount.toFixed(2));
    $('#totalAmount').val(totAmount.toFixed(2));
}



// Función para manejar y mostrar la respuesta del servidor en el preloader
function alertaFinal(response) {
    const messagesLoad = document.getElementById("messagesLoad");

    // Crear un nuevo elemento div para cada respuesta
    const messageDiv = document.createElement("div");

    // Mostrar mensaje de éxito o error
    if (response.success_count !== undefined && response.error_count !== undefined) {
        messageDiv.innerHTML = `
            <div class="alert alert-success">
                ${response.msgApp}
            </div>
        `;

        // Acumular totales globales
        totalDatos += response.success_count + response.error_count;
        totalCorrectos += response.success_count;
    } else {
        messageDiv.innerHTML = `
            <div class="alert alert-danger">
                Error en el procesamiento: ${response.msgApp || "Error desconocido."}
            </div>
        `;
    }

    // Añadir el nuevo mensaje al contenedor
    messagesLoad.appendChild(messageDiv);
}

// Función para mostrar el mensaje final con totales
function mostrarAlertaFinal() {
    const messagesLoad = document.getElementById("messagesLoad");

    // Crear un div grande para mostrar el resumen total
    const resumenDiv = document.createElement("div");
    resumenDiv.innerHTML = `
        <div class="alert alert-info mt-4" style="font-size: 1.5em; text-align: center;">
            <strong>Resumen Final:</strong> <br>
            Total de datos procesados: ${totalDatos} <br>
            Total de ingresos correctos: ${totalCorrectos} <br>
            <a href="/invoice/" class="btn btn-primary mt-3">Inicio</a>
        </div>
    `;

    const spinner = document.querySelector(".preloader-spinner");
    const preloaderText = document.querySelector(".preloader-text");
    spinner.style.display = "none";
    preloaderText.style.display = "none";

    // Añadir el resumen al final del contenedor
    messagesLoad.appendChild(resumenDiv);
}

// Función para dividir un array en subarrays de tamaño fijo
function splitArrayIntoChunks(array, chunkSize) {
    let chunks = [];
    for (let i = 0; i < array.length; i += chunkSize) {
        chunks.push(array.slice(i, i + chunkSize));
    }
    return chunks;
}

// Función para cargar datos de Dynamics y enviarlos en bloques de 5
async function cargarDatosDynamics() {
    // Mostrar loader
    mostrarLoader();

    let data = []; // Array para almacenar los objetos JSON
    let productosNoIdentificados = 0; // Contador para productos no identificados

    $('#purchaseProduct tbody tr').each((index, item) => {
        let linea = item.children[0].children[0].value;
        let codigo = item.children[1].children[0].value;
        // let descripcion = item.children[2].children[0].value;
        let empaque = item.children[3].children[0].value;
        // let impuesto = item.children[4].children[0].value;
        let cantidad = item.children[5].children[0].value;
        let precio_unitario = item.children[6].children[0].value;
        // let sub_total = item.children[7].children[0].value;
        // let igv = item.children[8].children[0].value;
        // let total = item.children[9].children[0].value;
        let identificado = item.children[10].children[0].value;

        // Contar productos no identificados
        if (identificado === 'NO') {
            productosNoIdentificados++;
        }

        // Crear un objeto JSON para cada fila y agregarlo al array
        let rowData = {
            "dataAreaId": Trv,
            "PurchaseOrderNumber": PurchaseOrderNumber,
            "RequestedDeliveryDate": RequestedDeliveryDate,
            "LineNumber": parseInt(linea),
            "ItemNumber": codigo,
            "ReceivingSiteId": ReceivingSiteId,
            "ReceivingWarehouseId": ReceivingWarehouseId,
            "OrderedPurchaseQuantity": parseInt(cantidad),
            "PurchaseUnitSymbol": empaque,
            "PurchasePrice": parseFloat(precio_unitario)
        };


        data.push(rowData);
    });

    // Si hay productos no identificados, mostrar mensaje de alerta
    if (productosNoIdentificados > 0) {
        
        alertaError(`HAY ${productosNoIdentificados} PRODUCTOS NO RECONOCIDOS`)
        mostrarContenido();

        return;
    }

    // Dividir el array data en bloques de 5 elementos
    const chunks = splitArrayIntoChunks(data, 5);

    // Enviar los bloques de datos al backend
    for (const chunk of chunks) {
        // Convertir el chunk en una cadena JSON
        let jsonData = JSON.stringify(chunk);

        console.log(jsonData);

        let endpoint = "/purchase/upload";

        let response;
        try {
            response = await consultasPostDataInsertSocket(endpoint, jsonData);

            // Mostrar contenido de la respuesta
            console.log("Respuesta del servidor:", response);
            alertaFinal(response); // Mostrar resultados acumulados de cada lote
        } catch (error) {
            console.error("Error en la solicitud:", error);
            alertaFinal({ msgApp: `Error en el lote: ${error.message}`, success_count: 0, error_count: chunk.length });
        }
    }

    // Mostrar la alerta final con el resumen
    mostrarAlertaFinal();

    // Ocultar el loader después de procesar todos los bloques
    ocultarLoader();
}

// Función para enviar los datos al backend
async function consultasPostDataInsertSocket(endpoint, jsonData) {
    try {
        const response = await $.ajax({
            url: endpoint,
            type: 'POST',
            data: jsonData,
            processData: false,
            contentType: 'application/json',
        });

        // Devolver la respuesta completa para manejarla en alertaFinal
        return response;

    } catch (error) {
        throw new Error(`Error al realizar la solicitud POST: ${error.message}`);
    }
}



function validarCodigos() {
    let codigoInvalido = false;

    // Verificar cada fila de la tabla para ver si algún código es "NO"
    $('#purchaseProduct tbody tr').each((index, item) => {
        // Buscar la celda que contiene el input del código
        $(item).find('td input[name^="codigo"]').each((i, input) => {
            let codigo = $(input).val(); // Obtener el valor del código
            // console.log(codigo);

            if (codigo === 'NO') {
                codigoInvalido = true;
                return false; // Detener la iteración si se encuentra un código inválido
            }
        });

        if (codigoInvalido) {
            return false; // Detener la iteración de filas si ya se encontró un código inválido
        }
    });

    return codigoInvalido;
}

$(document).ready(function () {
    $('#contentWindow').hide();
    cargarProductos();

    // Asignar usuario
    setUser();

    // Click en cargar líneas
    $("#btnPurchase").click(function (e) { 
        e.preventDefault();
        cargarDatosDynamics();
    });
});
