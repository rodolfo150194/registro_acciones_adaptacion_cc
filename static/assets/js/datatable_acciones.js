"use strict";

// Función para obtener el CSRF token desde la cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Class definition
var KTDatatablesExample = function () {
    // Shared variables
    var table;
    var datatable;

    // Private functions
    var initDatatable = function () {
        // Set date data order
        const tableRows = table.querySelectorAll('tbody tr');

        var groupColumn = 3;
        // Init datatable --- more info on datatables: https://datatables.net/manual/
        datatable = $(table).DataTable({
                // "responsive": true,
                "scrollX": true,
                'info': false,
                'responsive': true,
                "columnDefs": [
                    // {visible: false, targets: groupColumn},
                    {orderable: false, targets: [0, -1]}
                ],
                "order": [[groupColumn, 'asc']],
                "pageLength": 10,
                "language": {
                    "processing": "Procesando...",
                    "lengthMenu": "Mostrar _MENU_ registros",
                    "zeroRecords": "No se encontraron resultados",
                    "emptyTable": "No hay acciones registradas",
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
                // "drawCallback": function (settings) {
                //     var api = this.api();
                //     var rows = api.rows({page: 'current'}).nodes();
                //     var last = null;
                //
                //     api.column(groupColumn, {page: 'current'})
                //         .data()
                //         .each(function (group, i) {
                //             if (last !== group) {
                //                 $(rows).eq(i).before(
                //                     '<tr class="text-center fs-5 text-gray-900 bg-light-primary"><td colspan="5">' +
                //                     group +
                //                     '</td></tr>'
                //                 );
                //
                //                 last = group;
                //             }
                //         });
                // }
            }
        );
    }

// Hook export buttons
    var exportButtons = () => {
        const documentTitle = 'Reporte de acciones de adaptación para el cambio climático.';
        var buttons = new $.fn.dataTable.Buttons(table, {
            buttons: [
                {
                    extend: 'copyHtml5',
                    title: documentTitle,
                    exportOptions: {
                        columns: [1, 2, 4]
                    },
                },
                {
                    extend: 'excelHtml5',
                    title: documentTitle,
                    exportOptions: {
                        columns: [1, 2, 4]
                    },
                },
                {
                    extend: 'csvHtml5',
                    title: documentTitle,
                    exportOptions: {
                        columns: [1, 2, 4]
                    },
                },
                {
                    extend: 'pdfHtml5',
                    title: documentTitle,
                    exportOptions: {
                        columns: [1, 2, 3, 4]
                    },
                    customize: function (doc) {
                        // Personalizar los estilos
                        doc.styles.title = {
                            color: 'gray',
                            fontSize: '20',
                            alignment: 'center'
                        };
                        doc.styles.tableHeader = {
                            bold: true,
                            fontSize: 11,
                            color: 'white',
                            fillColor: '#1B84FF',
                            alignment: 'center'
                        };

                        doc.content[1].table.widths = Array(doc.content[1].table.body[0].length + 1).join('*').split('');
                        doc.content[1].table.body.forEach(function (row) {
                            row.forEach(function (cell) {
                                cell.alignment = 'center';
                            });
                        });
                        // Cambiar el ancho de las columnas
                        var objLayout = {};
                        objLayout['paddingLeft'] = function (i) {
                            return 8;
                        };
                        objLayout['paddingRight'] = function (i) {
                            return 8;
                        };
                        objLayout['paddingTop'] = function (i) {
                            return 8;
                        };
                        objLayout['paddingBottom'] = function (i) {
                            return 8;
                        };
                        objLayout['hLineWidth'] = function (i) {
                            return .5;
                        };
                        objLayout['vLineWidth'] = function (i) {
                            return .5;
                        };
                        objLayout['hLineColor'] = function (i) {
                            return '#aaa';
                        };
                        objLayout['vLineColor'] = function (i) {
                            return '#aaa';
                        };
                        objLayout['paddingLeft'] = function (i) {
                            return 4;
                        };
                        objLayout['paddingRight'] = function (i) {
                            return 4;
                        };
                        doc.content[1].layout = objLayout;

                    }
                }
            ]
        }).container().appendTo($('#kt_datatable_example_buttons'));

        // Hook dropdown menu click event to datatable export buttons
        const exportButtons = document.querySelectorAll('#kt_datatable_example_export_menu [data-kt-export]');
        exportButtons.forEach(exportButton => {
            exportButton.addEventListener('click', e => {
                e.preventDefault();

                // Get clicked export value
                const exportValue = e.target.getAttribute('data-kt-export');
                const target = document.querySelector('.dt-buttons .buttons-' + exportValue);

                // Trigger click event on hidden datatable export buttons
                target.click();
            });
        });
    }

// Search Datatable --- official docs reference: https://datatables.net/reference/api/search()
    var handleSearchDatatable = () => {
        const filterSearch = document.querySelector('[data-kt-filter="search"]');
        filterSearch.addEventListener('keyup', function (e) {
            datatable.search(e.target.value).draw();
        });
    }
    // Handle rating filter dropdown
    var handleStatusFilter = () => {
        const filterStatus = document.querySelector('[data-kt-accion-adaptacion-filter="estado_accion"]');
        $(filterStatus).on('change', e => {
            let value = e.target.value;
            if (value === 'Todos') {
                value = '';
            }
            datatable.column(4).search(value).draw();
        });
    }
    // Eliminar fila con confirmación Swal

    // Eliminar múltiples filas seleccionadas
    var handleDeleteAll = () => {
        const deleteAllBtn = document.getElementById('delete_all');
        if (!deleteAllBtn) return;
        deleteAllBtn.addEventListener('click', function () {
            // Obtener todas las filas seleccionadas
            const selectedRows = table.querySelectorAll('tbody tr');
            const rowsToDelete = [];
            selectedRows.forEach(row => {
                const checkbox = row.querySelector('td .form-check-input[type="checkbox"]');
                if (checkbox && checkbox.checked) {
                    rowsToDelete.push(row);
                }
            });
            if (rowsToDelete.length === 0) {
                Swal.fire({
                    text: 'Debe seleccionar al menos una acción para eliminar.',
                    icon: 'warning',
                    confirmButtonText: 'Ok',
                    customClass: {confirmButton: 'btn fw-bold btn-primary'}
                });
                return;
            }
            Swal.fire({
                text: `¿Está seguro que desea eliminar ${rowsToDelete.length} acción(es) seleccionada(s)?`,
                icon: "warning",
                showCancelButton: true,
                buttonsStyling: false,
                confirmButtonText: "Sí, eliminar!",
                cancelButtonText: "No, cancelar",
                customClass: {
                    confirmButton: "btn fw-bold btn-danger",
                    cancelButton: "btn fw-bold btn-active-light-primary"
                }
            }).then(function (result) {
                if (result.value) {
                    let eliminadas = 0;
                    let errores = 0;
                    let total = rowsToDelete.length;
                    // Eliminar en bucle
                    rowsToDelete.forEach(row => {
                        const idAccion = row.getAttribute('data-id');
                        fetch(`   /acciones/eliminar/${idAccion}/`, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken'),
                                'X-Requested-With': 'XMLHttpRequest',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                datatable.row($(row)).remove().draw();
                                eliminadas++;
                            } else {
                                errores++;
                            }
                            if (eliminadas + errores === total) {
                                Swal.fire({
                                    text: `Eliminadas: ${eliminadas}. Errores: ${errores}.`,
                                    icon: errores === 0 ? 'success' : 'warning',
                                    confirmButtonText: 'Ok',
                                    customClass: {confirmButton: 'btn fw-bold btn-primary'}
                                });
                            }
                        })
                        .catch(() => {
                            errores++;
                            if (eliminadas + errores === total) {
                                Swal.fire({
                                    text: `Eliminadas: ${eliminadas}. Errores: ${errores}.`,
                                    icon: 'warning',
                                    confirmButtonText: 'Ok',
                                    customClass: {confirmButton: 'btn fw-bold btn-primary'}
                                });
                            }
                        });
                    });
                }
            });
        });
    }

// Public methods
    return {
        init: function () {
            table = document.querySelector('#kt_datatable_acciones_adaptacion');

            if (!table) {
                return;
            }

            initDatatable();
            exportButtons();
            handleSearchDatatable();
            handleStatusFilter();
            handleDeleteAll();
        }
    };
}
();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesExample.init();
});
