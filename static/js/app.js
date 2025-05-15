
// consultas get
async function consultasGet(endpoint) {
    try {
        const response = await $.ajax({
            url: endpoint,
            type: 'GET',
            dataType: 'json'
        });

        if (response.msgApp === 'selectDB') {
            return response.purchApp;
        }
    } catch (error) {
        throw error;
    }
}


// consultas get
async function consultasGetAdmin(endpoint) {
    try {
        const response = await $.ajax({
            url: endpoint,
            type: 'GET',
            dataType: 'json'
        });

        if (response.msgApp === 'selectDB') {
            return response.purchaseApp;
        }
    } catch (error) {
        throw error;
    }
}

// Simulación de la función consultasGetAdmin
async function consultasGetAdminDasboard(endpoint) {
    try {
        let response = await fetch(endpoint, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        let data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching data: ", error);
        return { "msgApp": "errorServer" };
    }
}


// consulta post
async function consultasPost(endpoint) {
    try {
        const response = await $.ajax({
            url: endpoint,
            type: 'POST',
            dataType: 'json'
        });

        if (response.msgApp === 'selectDB') {
            return response.purchApp;
        }
    } catch (error) {
        throw error;
    }
}

// consulta post
async function consultasPostData(endpoint, formData) {
    try {
        const response = await $.ajax({
            url: endpoint,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
        });

        if (response && response.msgApp === 'selectDB' && response.xmlApp) {

            return response.xmlApp;
        } else {
            throw new Error('La respuesta del servidor no contiene los datos esperados.');
        }
    } catch (error) {
        throw new Error(`Error al realizar la solicitud POST: ${error.message}`);
    }
}

async function consultasPostDataInsert(endpoint, jsonData) {
    try {
        const response = await $.ajax({
            url: endpoint,
            type: 'POST',
            data: jsonData,
            processData: false,
            contentType: false,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        return response.msgApp

    } catch (error) {
        throw new Error(`Error al realizar la solicitud POST: ${error.message}`);
    }
}


// consulta post
async function consultasPostDataCreate(endpoint, formData) {
    try {
        const response = await $.ajax({
            url: endpoint,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
        });

        if (response && response.msgApp === 'createDB') {

            return response.invoiceApp;
            
        } else {
            throw new Error('La respuesta del servidor no contiene los datos esperados.');
        }
    } catch (error) {
        throw new Error(`Error al realizar la solicitud POST: ${error.message}`);
    }
}


// consulta para cargar productos
async function productData(endpoint) {
    try {
        const response = await $.ajax({
            type: 'GET',
            url: endpoint,
            dataType: 'json'
        });

        if (response.msgApp === 'selectDB') {
            return response.purchaseApp;
        } else {
            alertaInicial(response.msgApp);
            return response.purchaseApp
        }
    } catch (error) {
        throw error;
    }
}






// estilos a los selects
function estilosSelects(select) {
    // Configura el plugin Select2 para el select de proveedores
    $(select).select2({
        theme: 'bootstrap-5',
        width: $(this).data('width') ? $(this).data('width') : $(this).hasClass('w-100') ? '100%' : 'style',
        placeholder: $(this).data('placeholder'),
    });
}


// vista de loaders
function mostrarContenido() { 
    $('#preloaderWindow').hide();
    $('#contentWindow').show();
}

function mostrarLoader() {
    $('#preloaderWindow').show();
    $('#contentWindow').hide();
}


// alertas
function alertaCorrecto(mensaje){
    Swal.fire({
        position: "center",
        icon: "success",
        title: mensaje,
        showConfirmButton: false,
        timer: 2000
      });
}

function alertaError(mensaje){
    Swal.fire({
        position: "center",
        icon: "error",
        title: mensaje,
        showConfirmButton: false,
        timer: 2500
      });
}

function alertaErrorDescargaXML(mensaje){
    Swal.fire({
        position: "center",
        icon: "error",
        title: mensaje,
        showConfirmButton: false,
        timer: 5000
      });
}

// function alertaFinal(mensaje){
//     Swal.fire({
//         title: mensaje,
//         showDenyButton: true,
//         showCancelButton: false,
//         confirmButtonText: "Ir a inicio",
//         denyButtonText: `Regresar`
//       }).then((result) => {
//         /* Read more about isConfirmed, isDenied below */
//         if (result.isConfirmed) {
//           window.location.href = "/";
//         } else if (result.isDenied) {
//           mostrarContenido();
//         }
//       });
// }


function alertaInicial(mensaje){
    Swal.fire({
        title: mensaje,
        icon: 'warning',
        showDenyButton: false, // Mostrar solo el botón "Ir a inicio"
        showCancelButton: false, // Ocultar el botón de cancelar
        denyButtonText: "Ir a inicio", // Cambiar el texto del botón de negación
      }).then((result) => {
        window.location.href = "/"
      });
}


function alertaActualizacion(){
    Swal.fire({
        title: "Actualizacion correcta",
        icon: 'success',
        showDenyButton: false, // Mostrar solo el botón "Ir a inicio"
        showCancelButton: false, // Ocultar el botón de cancelar
        denyButtonText: "Ir a inicio", // Cambiar el texto del botón de negación
      }).then((result) => {
        window.location.href = "/admin"
      });
}


async function productDataOptimizado(endpoint) {
    try {
        const response = await $.ajax({
            type: 'GET',
            url: endpoint,
            dataType: 'json'
        });

        // Verificar si la respuesta contiene los datos esperados
        if (response.success && response.status_code === 200) {
            if (response.msgApp && response.msgApp.data) {
                // Mostrar alerta de éxito y retornar los datos
                alertaCorrecto("Datos cargados correctamente.");
                return response.msgApp.data;
            } else {
                // Mostrar alerta de error si los datos no están presentes en el formato esperado
                alertaError("Error: No se encontraron los datos esperados en la respuesta.");
                return null;
            }
        } else {
            // Mostrar alerta de error en caso de una respuesta con estado fallido
            alertaError(response.msgApp || "Error en la respuesta del servidor.");
            return null;
        }
    } catch (error) {
        // Mostrar alerta de error si la petición falla
        alertaError("Error al cargar los datos. Verifique su conexión.");
        console.error("Error en la petición:", error);
        throw error;
    }
}