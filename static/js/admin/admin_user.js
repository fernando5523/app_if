var tablePorveedores = $('#Proveedores');


function diseñoTabla(){

    // Verificar si el DataTable ya está inicializado
    if ($.fn.DataTable.isDataTable('#Proveedores')) {
        // Destruir la instancia existente de DataTable
        $('#Proveedores').DataTable().destroy();
    }

    // Función para cargar la configuración del DataTable
    $('#Proveedores').DataTable({
       info: false,
       language: {
           infoEmpty: 'No hay filas para mostrar.',
           zeroRecords: 'No se encontraron resultados.',
       },
       ordering: false,
       paging: false,
       searching: false,
       scrollX: true,
   });
}




async function cargarUsuarios() { 
    let endpoint = "/adminUser/get_data"
    let response = await consultasGetAdmin(endpoint)


    console.log(response);

    for (let i = 0; i < response.length; i++) {
        proveedorSearch(response[i], i, tablePorveedores)
    }

    diseñoTabla()

 }


async function actualizarUsuario(id) { 
    // Buscar la fila correspondiente al ID
    let filaUsuario = $("#Proveedores tbody tr").filter(function() {
        return $(this).find("input[name='id-" + id + "']").length > 0;
    });

    // Verificar si se encontró la fila
    if (filaUsuario.length > 0) {
        // Obtener los datos del proveedor
        let idUsuario = filaUsuario.find("input[name='id-" + id + "']").val();
        let dniUsuario = filaUsuario.find("input[name='dni-" + id + "']").val();
        let nombreUsuario = filaUsuario.find("input[name='names-" + id + "']").val();
        let estadoUsuario = filaUsuario.find("select[name='estado-" + id + "']").val();

        let data = {
            "id": idUsuario,
            "dni": dniUsuario,
            "name": nombreUsuario,
            "state": estadoUsuario,
        }

        let endpoint = "/adminUser/update_data"

        let response = await $.ajax({
            url: endpoint,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(data),
            contentType: 'application/json'
        });

        if (response.success === true) {
            Swal.fire({
                title: "Actualizacion correcta",
                icon: 'success',
                showDenyButton: false, // Mostrar solo el botón "Ir a inicio"
                showCancelButton: false, // Ocultar el botón de cancelar
                denyButtonText: "Ir a inicio", // Cambiar el texto del botón de negación
              }).then((result) => {
                cargarUsuarios()
              });

        } else {
            alertaError("Error al actualizar")
        }
    }
        
 }


 function proveedorSearch(dataLine, index, table){
    let id =
        '<td style="width: 40px" id="cantidad-' +
        index +
        '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="id-' +
        dataLine.ID  +
        '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important;" value="' +
        dataLine.ID +
        '" disabled></td>';
    
    let dni =
        '<td style="width: 60px" id="cantidad-' +
        index +
        '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="dni-' +
        dataLine.ID +
        '" class="form-control" style="font-weight: bold; text-align: center; width: 200px !important;" value="' +
        dataLine.DNI +
        '" ></td>';
    
    let name =
        '<td style="width: 650px" id="cantidad-' +
        index +
        '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="names-' +
        dataLine.ID +
        '" class="form-control" style="font-weight: bold; text-align: center; !important;" value="' +
        dataLine.USERNAME +
        '" ></td>';

    let state =
        '<td style="width: 30px" style="padding-left: 5px !important; padding-right: 5px !important;">' +
        '<select name="estado-' + dataLine.ID + '" class="form-select" style="font-weight: bold; text-align: center; width: 180px !important;">' +
        '<option value="1" ' + (dataLine.STATE === "1" ? "selected" : "") + '>ACTIVO</option>' +
        '<option value="0" ' + (dataLine.STATE === "0" ? "selected" : "") + '>INACTIVO</option>' +
        '</select>' +
        '</td>';
    
    let btn_Actualizar =
        '<td style="padding-left: 5px !important; padding-right: 5px !important;">' +
        '<button type="button" class="btn btn-dark" onclick="actualizarUsuario(' + dataLine.ID + ')">Actualizar</button>' +
        '</td>';
    
   
    
    table.append(
        '<tr>' + id + dni + name + state + btn_Actualizar + '</tr>'
    );
 }


function cleanForm(){
    $("#user_dni").val("");
    $("#user_name").val("");
}



async function saveUser(){
    let dni = $("#user_dni").val();
    let name = ($("#user_name").val()).toUpperCase();

    let data = {
        "dni": dni,
        "name": name
    }


    let endpoint = "/adminUser/save_data"
    // enviar al backend
    let response = await $.ajax({
        url: endpoint,
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(data),
        contentType: 'application/json'
    });

    if (response.success === true) {
        cleanForm()
        Swal.fire({
            title: "Registro correcto",
            icon: 'success',
            showDenyButton: false, // Mostrar solo el botón "Ir a inicio"
            showCancelButton: false, // Ocultar el botón de cancelar
            denyButtonText: "Ir a inicio", // Cambiar el texto del botón de negación
          }).then((result) => {
            window.location.href = "/adminUser"
          });
    } else {
        alertaError("Error al actualizar")
    }

}


$(document).ready(function () {
    try {
        cargarUsuarios()
    } catch (error) {
        console.log(error);
    }

    // save user
    $("#btn_guardar").click(function () {
        saveUser()
    })

});