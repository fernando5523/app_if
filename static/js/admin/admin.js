var tablePorveedores = $('#Proveedores');


function diseñoTabla(){
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


async function actualizarProveedor(id) {  
    // Buscar la fila correspondiente al ID
    let filaProveedor = $("#Proveedores tbody tr").filter(function() {
        return $(this).find("input[name='id-" + id + "']").length > 0;
    });

    // Verificar si se encontró la fila
    if (filaProveedor.length > 0) {
        // Obtener los datos del proveedor
        let idProveedor = filaProveedor.find("input[name='id-" + id + "']").val();
        let rucProveedor = filaProveedor.find("input[name='ruc-" + id + "']").val();
        let nombreProveedor = filaProveedor.find("input[name='nombre-" + id + "']").val();
        let estadoProveedor = filaProveedor.find("select[name='estado-" + id + "']").val();
        let fuente = filaProveedor.find("select[name='fuente-" + id + "']").val();
        let xmlCabeceraProveedor = filaProveedor.find("select[name='cabecera-" + id + "']").val();
        let xmlCuerpoProveedor = filaProveedor.find("select[name='cuerpo-" + id + "']").val();

        // console.log("ID: " + idProveedor);
        // console.log("RUC: " + rucProveedor);
        // console.log("Nombre: " + nombreProveedor);
        // console.log("Estado: " + estadoProveedor);
        // console.log("XML Cabecera: " + xmlCabeceraProveedor);
        // console.log("XML Cuerpo: " + xmlCuerpoProveedor);

        data = {
            "id": idProveedor,
            "ruc": rucProveedor,
            "businessname": nombreProveedor,
            "state": estadoProveedor,
            "readheadxml": xmlCabeceraProveedor,
            "readxmlbody": xmlCuerpoProveedor,
            "dataSource": fuente
        }

        let endpoint = "/admin/update_data"

        // enviar al backend
        let response = await $.ajax({
            url: endpoint,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(data),
            contentType: 'application/json'
        });

        if (response.success === true) {
            alertaActualizacion()
        } else {
            alertaError("Error al actualizar")
        }

    } else {
        alertaError("No se encontró el proveedor con el ID indicado")
    }
}



async function cargarProveedores() { 
    let endpoint = "/admin/get_data"
    let response = await consultasGetAdmin(endpoint)

    for (let i = 0; i < response.length; i++) {
        proveedorSearch(response[i], i, tablePorveedores)
    }

    diseñoTabla()

 }


 function proveedorSearch(dataLine, index, table){
    let id =
        '<td id="cantidad-' +
        index +
        '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="id-' +
        dataLine.ID  +
        '" class="form-control" style="font-weight: bold; text-align: center; width: 120px !important;" value="' +
        dataLine.ID +
        '" disabled></td>';
    
    let ruc =
        '<td id="cantidad-' +
        index +
        '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="ruc-' +
        dataLine.ID +
        '" class="form-control" style="font-weight: bold; text-align: center; width: 200px !important;" value="' +
        dataLine.RUC +
        '" ></td>';
    
    let nombre =
        '<td id="cantidad-' +
        index +
        '" style="padding-left: 5px !important; padding-right: 5px !important;"><input type="text" name="nombre-' +
        dataLine.ID +
        '" class="form-control" style="font-weight: bold; text-align: left; width: 900px !important; background-color: ' + 
        (dataLine.STATE === "PROGRESS" ? "#FFC300;" : dataLine.STATE === "ENABLED" ? "#31D681;" : dataLine.STATE === "DISABLED" ? "#C70039 ;" : "") +
        '" value="' +
        dataLine.BUSINESSNAME +
        '" disabled></td>';
    

    
    
    let estado =
        '<td style="padding-left: 5px !important; padding-right: 5px !important;">' +
        '<select name="estado-' + dataLine.ID + '" class="form-select" style="font-weight: bold; text-align: center; width: 180px !important;">' +
        '<option value="PROGRESS" ' + (dataLine.STATE === "PROGRESS" ? "selected" : "") + '>PROGRESS</option>' +
        '<option value="ENABLED" ' + (dataLine.STATE === "ENABLED" ? "selected" : "") + '>ENABLED</option>' +
        '<option value="DISABLED" ' + (dataLine.STATE === "DISABLED" ? "selected" : "") + '>DISABLED</option>' +
        '</select>' +
        '</td>';

    let fuente =
        '<td style="padding-left: 5px !important; padding-right: 5px !important;">' +
        '<select name="fuente-' + dataLine.ID + '" class="form-select" style="font-weight: bold; text-align: center; width: 180px !important;">' +
        '<option value="XML" ' + (dataLine.DATASOURCE === "XML" ? "selected" : "") + '>XML</option>' +
        '<option value="JSON" ' + (dataLine.DATASOURCE === "JSON" ? "selected" : "") + '>JSON</option>' +
        '</select>' +
        '</td>';

    let xmlHead =
        '<td style="padding-left: 5px !important; padding-right: 5px !important;">' +
        '<select name="cabecera-' + dataLine.ID + '" class="form-select" style="font-weight: bold; text-align: center; width: 120px !important;" ' +
        (dataLine.DATASOURCE === "JSON" ? "disabled" : "") + '>' +
        '<option value="Grupo1" ' + (dataLine.READXMLHEADGROUP === "Grupo1" ? "selected" : "") + '>Grupo1</option>' +
        '<option value="Grupo2" ' + (dataLine.READXMLHEADGROUP === "Grupo2" ? "selected" : "") + '>Grupo2</option>' +
        
        '</select>' +
        '</td>';
        
    let xmlBody =
        '<td style="padding-left: 5px !important; padding-right: 5px !important;">' +
        '<select name="cuerpo-' + dataLine.ID + '" class="form-select" style="font-weight: bold; text-align: center; width: 120px !important;" ' +
        (dataLine.DATASOURCE === "JSON" ? "disabled" : "") + '>' +
        '<option value="Grupo1" ' + (dataLine.READXMLBODYGROUP === "Grupo1" ? "selected" : "") + '>Grupo1</option>' +
        '<option value="Grupo2" ' + (dataLine.READXMLBODYGROUP === "Grupo2" ? "selected" : "") + '>Grupo2</option>' +
        '<option value="Grupo3" ' + (dataLine.READXMLBODYGROUP === "Grupo3" ? "selected" : "") + '>Grupo3</option>' +
        '<option value="Grupo4" ' + (dataLine.READXMLBODYGROUP === "Grupo4" ? "selected" : "") + '>Grupo4</option>' +
        '<option value="Grupo5" ' + (dataLine.READXMLBODYGROUP === "Grupo5" ? "selected" : "") + '>Grupo5</option>' +
        '</select>' +
        '</td>';
        
    let btn_Actualizar =
            '<td style="padding-left: 5px !important; padding-right: 5px !important;">' +
            '<button type="button" class="btn btn-dark" onclick="actualizarProveedor(' + dataLine.ID + ')">Actualizar</button>' +
            '</td>';
    
    table.append(
        '<tr>' + id + ruc + nombre + estado + fuente + xmlHead + xmlBody + btn_Actualizar+ '</tr>'
    );
 }


$(document).ready(function () {
    try {
        cargarProveedores()
    } catch (error) {
        console.log(error);
    }
});