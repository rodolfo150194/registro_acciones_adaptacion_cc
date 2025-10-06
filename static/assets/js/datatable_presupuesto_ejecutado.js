"use strict";

// Class definition
var KTDatatablesExample = function () {
    // Shared variables
    var table;
    var datatable;

    // Private functions
    var initDatatable = function () {
        // Set date data order
        const tableRows = table.querySelectorAll('tbody tr');
        // Init datatable --- more info on datatables: https://datatables.net/manual/
        datatable = $(table).DataTable({
                // "responsive": true,
                "scrollX": true,
                'info':false,
                "order": [[1, 'asc']],
                "pageLength": 10,
                "language": {
                    "processing": "Procesando...",
                    "lengthMenu": "Mostrar _MENU_ registros",
                    "zeroRecords": "No se encontraron resultados",
                    "emptyTable": "No hay presupuestos planificados registrados",
                    "info": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                    "infoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
                    "infoFiltered": "(filtrado de un total de _MAX_ registros)",
                    "search": "Buscar:",
                    "infoThousands": ",",
                    "loadingRecords": "Cargando...",
                    "paginate": {
                        "first": "Primero",
                        "last": "Último",
                        "next": "Siguiente",
                        "previous": "Anterior"
                    },
                },
            }
        );
    }


// Public methods
    return {
        init: function () {
            table = document.querySelector('#kt_datatable_presupuestos_ejecutados_adaptacion');

            if (!table) {
                return;
            }

            initDatatable();
        }
    };
}
();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesExample.init();
});

