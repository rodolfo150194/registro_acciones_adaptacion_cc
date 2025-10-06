$(function () {
    const locale_flatpickr = {
        firstDayOfWeek: 1,
        weekdays: {
            shorthand: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'],
            longhand: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        },
        months: {
            shorthand: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Оct', 'Nov', 'Dic'],
            longhand: ['Enero', 'Febrero', 'Мarzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        },
    };

    const e = document.querySelector("#kt_fecha_inicio_flatpickr");
    const e_2 = document.querySelector("#kt_fecha_fin_flatpickr");
    n = $(e).flatpickr({
        altInput: !0,
        altFormat: "d/m/Y",
        dateFormat: "Y-m-d",
        defaultDate:  "",
        //onChange: function (e) {
        //   a(e, t, n)
        //{,
        locale: locale_flatpickr
    });
    n_1 = $(e_2).flatpickr({
        altInput: !0,
        altFormat: "d/m/Y",
        dateFormat: "Y-m-d",
        defaultDate:'',
        //onChange: function (e) {
        //   a(e, t, n)
        //{,
        locale: locale_flatpickr
    });


})