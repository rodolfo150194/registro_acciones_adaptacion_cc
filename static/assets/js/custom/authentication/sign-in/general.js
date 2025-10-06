"use strict";
var KTGeneral = function () {
    var form, submit;
    return {
        init: function () {
            form = document.querySelector("#kt_sign_in_form");
            submit = document.querySelector("#kt_in_submit");

            submit.addEventListener("click", (function (i) {
                i.preventDefault();

                // Mostrar indicador de progreso
                submit.setAttribute("data-kt-indicator", "on");
                submit.disabled = true;

                // Enviar el formulario
                form.submit()
            }));
        }
    }
}();

KTUtil.onDOMContentLoaded((function () {
    KTGeneral.init()
}));