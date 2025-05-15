// Función para inicializar un gráfico de barras
function createBarChart(selector, categories, data, colors = ['#008FFB']) {
    var options = {
        series: [{
            data: data
        }],
        chart: {
            type: 'bar',
            height: 350
        },
        plotOptions: {
            bar: {
                borderRadius: 4,
                borderRadiusApplication: 'end',
                horizontal: true,
            }
        },
        colors: colors,  // Aplicar colores personalizados
        dataLabels: {
            enabled: true
        },
        xaxis: {
            categories: categories,
        }
    };

    var chart = new ApexCharts(document.querySelector(selector), options);
    chart.render();
}



function createAreaChart(dataOdata, serieOdata, dataSql, serieSql) {
    var options = {
        series: [{
            name: 'Ingreso Manual',
            data: dataOdata
        }, {
            name: 'Ingreso App',
            data: dataSql
        }],
        chart: {
            height: 350,
            type: 'area'
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'smooth'
        },
        xaxis: {
            type: 'datetime',
            categories: serieOdata  // Use serieOdata or serieSql if they are aligned
        },
        tooltip: {
            x: {
                format: 'yyyy-MM-dd'
            }
        }
    };

    var chart = new ApexCharts(document.querySelector("#chart-vs"), options);
    chart.render();
}

function graficarFacturas(fechas, cantidades) {
    let options = {
        chart: {
            type: "area",
            height: 350
        },
        series: [{
            name: "Facturas",
            data: cantidades
        }],
        xaxis: {
            categories: fechas,
            title: { text: "Fecha" }
        },
        yaxis: {
            title: { text: "Cantidad de Facturas" }
        },
        stroke: {
            curve: "smooth"
        },
        // title: {
        //     text: "Cantidad de Facturas por Día",
        //     align: "center"
        // }
    };

    let chart = new ApexCharts(document.querySelector("#chart-ingresos"), options);
    chart.render();
}




// Función asíncrona para cargar los datos desde el servidor
async function fetchData(endpoint) {
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

        return await response.json();
    } catch (error) {
        console.error("Error fetching data: ", error);
        return { "msgApp": "errorServer" };
    }
}

// Función principal para cargar y renderizar los datos
async function cargarDatos() {
    try {
        // Cargar y renderizar datos de proveedores
        let responseProveedores = await fetchData("/adminDashboard/get_proveedores");
        if (responseProveedores.msgApp === "selectDB") {
            let { cantidades: cantidadesProveedores, proveedores } = responseProveedores;
            createBarChart("#chart_proveedores", proveedores, cantidadesProveedores, ['#FF5733']);  // Cambiar el color para proveedores
        } else {
            console.error("Error en el servidor de proveedores");
        }

        // Cargar y renderizar datos de usuarios
        let responseUsuarios = await fetchData("/adminDashboard/get_users");
        if (responseUsuarios.msgApp === "selectDB") {
            let { cantidades: cantidadesUsuarios, usuarios } = responseUsuarios;
            createBarChart("#chart-users", usuarios, cantidadesUsuarios, ['#33FF57']);  // Cambiar el color para usuarios
        } else {
            console.error("Error en el servidor de usuarios");
        }
    } catch (error) {
        console.error("Error al cargar los datos: ", error);
    }
}

async function cargarDatosVs() { 

    // obtrener los valores de fechas
    let date_init = document.getElementById("date_init").value;
    let date_end = document.getElementById("date_end").value;

    try {
        let responseProveedores = await fetchData("/adminDashboard/get_ingresos/"+date_init+"/"+date_end);
        if (responseProveedores.msgApp === "selectDB") {
            console.log(responseProveedores);
            graficarFacturas(responseProveedores.fechas, responseProveedores.cantidades);
        } else {
            console.error("Error en el servidor de proveedores");
        }
    } catch (error) {
        console.error("Error al cargar los datos: ", error);
    }
}




// Inicializar la carga de datos cuando el documento esté listo
$(document).ready(function () {
    cargarDatos();
    // cargarDatosVs();

    $("#btn_cargar_datos").click(function (e) { 
        e.preventDefault();
        cargarDatosVs()
    });
    // createAreaChart()
});
