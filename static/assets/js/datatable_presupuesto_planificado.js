"use strict";
var accion = accion;
// Class definition
var KTDatatablesExample = function () {
    // Shared variables
    var table;
    var datatable;
    console.log()
    // Private functions
    var initDatatable = function () {
        // Set date data order
        const tableRows = table.querySelectorAll('tbody tr');
        var groupColumn = 0;
        // Init datatable --- more info on datatables: https://datatables.net/manual/
        datatable = $(table).DataTable({
                // "responsive": true,
                "scrollX": true,
                'info': false,
                "columnDefs": [{visible: false, targets: groupColumn}],
                "order": [[groupColumn, 'asc']],
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
                "drawCallback": function (settings) {
                    var api = this.api();
                    var rows = api.rows({page: 'current'}).nodes();
                    var last = null;

                    api.column(groupColumn, {page: 'current'})
                        .data()
                        .each(function (group, i) {
                            if (last !== group) {
                                $(rows).eq(i).before(
                                    '<tr class="text-center fs-5 text-gray-900 bg-light-primary" style=""><td colspan="5">' +
                                    group +
                                    '</td></tr>'
                                );

                                last = group;
                            }
                        });
                }
            }
        );
    }

// Hook export buttons
    var exportButtons = () => {
        const documentTitle = `Financiamiento`;
        var buttons = new $.fn.dataTable.Buttons(table, {
            buttons: [
                {
                    extend: 'copyHtml5',
                    title: documentTitle,
                    exportOptions: {
                        columns: [0, 1, 2, 3]
                    },
                },
                {
                    extend: 'excelHtml5',
                    title: documentTitle,
                    exportOptions: {
                        columns: [0, 1, 2, 3]
                    },
                },
                {
                    extend: 'csvHtml5',
                    title: documentTitle,
                    exportOptions: {
                        columns: [0, 1, 2, 3]
                    },
                },
                {
                    extend: 'pdfHtml5',
                    title: documentTitle,
                    exportOptions: {
                        columns: [0, 1, 2, 3]
                    },
                    customize: function (doc) {
                        const data = datatable.rows({search: 'applied'}).data().toArray();
                        const groupedData = {};
                        const groupIndex = 0; // índice de la columna de grupo
                        const valueIndex = 3; // columna a sumar

                        // Agrupar y sumar
                        data.forEach(row => {
                            const group = row[groupIndex];
                            const rawValue = row[valueIndex].toString().replace(/,/g, '');
                            const value = parseFloat(rawValue) || 0;
                            if (!groupedData[group]) {
                                groupedData[group] = {
                                    rows: [],
                                    total: 0
                                };
                            }
                            groupedData[group].rows.push(row);
                            groupedData[group].total += value;
                        });

                        // Armar nueva tabla con agrupación y totales
                        const body = [];

                        for (const group in groupedData) {
                            body.push([{
                                text: group,
                                colSpan: 4,
                                alignment: 'center',
                                fillColor: '#d1e7dd',
                                color: '#000000',
                                bold: true
                            }, {}, {}, {}]);

                            groupedData[group].rows.forEach(row => {
                                body.push([
                                    {text: row[0]},
                                    {text: row[1]},
                                    {text: row[2]},
                                    {text: row[3].toString(), alignment: 'center'}
                                ]);
                            });

                            body.push([
                                {text: 'Total', colSpan: 3, alignment: 'center', bold: true}, {}, {},
                                {text: groupedData[group].total.toFixed(2), alignment: 'center', bold: true}
                            ]);
                        }

                        doc.content[1].table.body = body;


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

                        // Ajustar a todo el ancho disponible
                        const columnCount = body[0].length;
                        doc.content[1].table.widths = Array(columnCount).fill('*');

                        // Layout personalizado
                        doc.content[1].layout = {
                            paddingLeft: () => 4,
                            paddingRight: () => 4,
                            paddingTop: () => 8,
                            paddingBottom: () => 8,
                            hLineWidth: () => 0.5,
                            vLineWidth: () => 0.5,
                            hLineColor: () => '#aaa',
                            vLineColor: () => '#aaa'
                        };

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
        const filterStatus = document.querySelector('[data-kt-accion-adaptacion-filter="estado_presupuesto"]');
        $(filterStatus).on('change', e => {
            let value = e.target.value;
            if (value === 'Todos') {
                value = '';
            }
            datatable.column(1).search(value).draw();
        });
    }

// Public methods
    return {
        init: function () {
            table = document.querySelector('#kt_datatable_presupuestos_planificados_adaptacion');

            if (!table) {
                return;
            }

            initDatatable();
            handleSearchDatatable();
            handleStatusFilter();
            exportButtons();
        }
    };
}
();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTDatatablesExample.init();
});

