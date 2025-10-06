"use strict";
var KTAuthI18nDemo = function () {
    var e, n, a = {
        "general-progress": {
            English: "Please wait...",
            Spanish: "Procesando...",
        },
        "general-desc": {
            English: "Record of adaptation actions",
            Spanish: "Registro de acciones de adaptación",
        },
        "general-or": {English: "Or", Spanish: "O"},
        "sign-in-title": {
            English: "Sign In",
            Spanish: "Iniciar Sesión",
        },
        "sign-in-input-email": {
            English: "Email",
            Spanish: "Correo electrónico",
        },
        "sign-in-input-password": {
            English: "Password",
            Spanish: "Clave",
        },
        "sign-in-forgot-password": {
            English: "Forgot Password ?",
            Spanish: "Has olvidado tu contraseña ?",
        },
        "sign-in-submit": {
            English: "Sign In",
            Spanish: "Iniciar Sesión",
        },

        "sign-up-head-link": {
            English: "Sign In",
            Spanish: "Iniciar Sesión",
        },

        "sign-up-submit": {
            English: "Submit",
            Spanish: "Iniciar Sesión",
        },

        "sign-in-logout-accept": {
            English: "Yes",
            Spanish: "Sí",
        },

        "sign-in-logout-cancel": {
            English: "No",
            Spanish: "No",
        },
        "title-logout": {
            English: "Are you sure you want to leave?",
            Spanish: "Ud. está seguro que desea salir?",
        },
        "btn-create": {
            English: "New Action",
            Spanish: "Nueva acción",
        },

    }, s = function (e) {
        for (var n in a) if (a.hasOwnProperty(n) && a[n][e]) {
            let s = document.querySelector("[data-kt-translate=" + n + "]");
            null !== s && ("INPUT" === s.tagName ? s.setAttribute("placeholder", a[n][e]) : s.innerHTML = a[n][e])
        }
    }, i = function (n) {
        const a = e.querySelector('[data-kt-lang="' + n + '"]');
        if (null !== a) {
            const e = document.querySelector('[data-kt-element="current-lang-name"]'),
                s = document.querySelector('[data-kt-element="current-lang-flag"]'),
                i = a.querySelector('[data-kt-element="lang-name"]'),
                r = a.querySelector('[data-kt-element="lang-flag"]');
            e.innerText = i.innerText, s.setAttribute("src", r.getAttribute("src")), localStorage.setItem("kt_auth_lang", n)
        }
    };
    return {
        init: function () {
            null !== (e = document.querySelector("#kt_auth_lang_menu")) && (n = KTMenu.getInstance(e), function () {
                if (null !== localStorage.getItem("kt_auth_lang")) {
                    let e = localStorage.getItem("kt_auth_lang");
                    i(e), s(e)
                }
                n.on("kt.menu.link.click", (function (e) {
                    let n = e.getAttribute("data-kt-lang");
                    i(n), s(n)
                }))
            }())
        }
    }
}();
KTUtil.onDOMContentLoaded((function () {
    KTAuthI18nDemo.init()
}));