/**
 * Validaciones de frontend y comportamiento de interfaz multiplataforma.
 */

// Algoritmo de Cédula Ecuatoriana (Módulo 10)
function validarCedulaEcuatorianaJS(cedula) {
    if (!/^\d{10}$/.test(cedula)) return false;
    const provincia = parseInt(cedula.substring(0, 2), 10);
    if (!((provincia >= 1 && provincia <= 24) || provincia === 30)) return false;
    const tercerDigito = parseInt(cedula.charAt(2), 10);
    if (tercerDigito >= 6) return false;
    const coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2];
    let suma = 0;
    for (let i = 0; i < 9; i++) {
        let producto = parseInt(cedula.charAt(i), 10) * coeficientes[i];
        if (producto >= 10) producto -= 9;
        suma += producto;
    }
    const verificador = (10 - (suma % 10)) % 10;
    return verificador === parseInt(cedula.charAt(9), 10);
}

function validarEmailJS(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function mostrarError(input, mensaje) {
    input.classList.add('input-invalid');
    const contenedor = input.closest('.form-group');
    if (contenedor) {
        const errorSpan = contenedor.querySelector('.js-error-msg');
        if (errorSpan) errorSpan.textContent = mensaje;
    }
}

function limpiarError(input) {
    input.classList.remove('input-invalid');
    const contenedor = input.closest('.form-group');
    if (contenedor) {
        const errorSpan = contenedor.querySelector('.js-error-msg');
        if (errorSpan) errorSpan.textContent = '';
    }
}

document.addEventListener('DOMContentLoaded', () => {

    /* ----------------------------------------------------------------------
       1. Menú lateral responsivo multiplataforma (Móviles / Tablets)
       ---------------------------------------------------------------------- */
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    if (sidebar && sidebarToggle && sidebarOverlay) {
        const abrirMenu = () => {
            sidebar.classList.add('open');
            sidebarOverlay.classList.add('open');
            document.body.style.overflow = 'hidden'; // Evita scroll de fondo
        };

        const cerrarMenu = () => {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('open');
            document.body.style.overflow = '';
        };

        sidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            if (sidebar.classList.contains('open')) {
                cerrarMenu();
            } else {
                abrirMenu();
            }
        });

        sidebarOverlay.addEventListener('click', cerrarMenu);

        // Cerrar menú al presionar tecla Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sidebar.classList.contains('open')) {
                cerrarMenu();
            }
        });
    }

    /* ----------------------------------------------------------------------
       2. Confirmación para eliminado lógico
       ---------------------------------------------------------------------- */
    document.querySelectorAll('.confirm-delete-form').forEach((form) => {
        form.addEventListener('submit', (e) => {
            const confirmado = window.confirm(
                '¿Deseas desactivar (eliminar lógicamente) este registro?'
            );
            if (!confirmado) e.preventDefault();
        });
    });

    /* ----------------------------------------------------------------------
       3. Validación de formularios (.validated-form)
       ---------------------------------------------------------------------- */
    document.querySelectorAll('.validated-form').forEach((form) => {
        form.addEventListener('submit', (e) => {
            let esValido = true;
            const tipo = form.dataset.formType;
            const campos = form.querySelectorAll('input, select, textarea');

            campos.forEach((campo) => {
                if (campo.type === 'hidden') return;
                limpiarError(campo);
                const valor = campo.value.trim();

                // Campos requeridos
                if (campo.hasAttribute('required') && valor === '') {
                    mostrarError(campo, 'Este campo es obligatorio.');
                    esValido = false;
                    return;
                }

                // Email
                if (campo.type === 'email' && valor !== '' && !validarEmailJS(valor)) {
                    mostrarError(campo, 'Ingresa un correo electrónico con formato válido.');
                    esValido = false;
                }

                // Cédula ecuatoriana
                if (campo.name === 'cedula' && valor !== '' && !validarCedulaEcuatorianaJS(valor)) {
                    mostrarError(campo, 'La cédula ecuatoriana ingresada no es válida.');
                    esValido = false;
                }

                // RUC ecuatoriano
                if (campo.name === 'ruc' && valor !== '' && !/^\d{13}$/.test(valor)) {
                    mostrarError(campo, 'El RUC debe tener exactamente 13 dígitos numéricos.');
                    esValido = false;
                }

                // Teléfono
                if (campo.name === 'telefono' && valor !== '' && !/^\d{10}$/.test(valor)) {
                    mostrarError(campo, 'El teléfono debe contener exactamente 10 dígitos numéricos.');
                    esValido = false;
                }

                // Números mínimos
                if (campo.type === 'number' && valor !== '') {
                    const num = parseFloat(valor);
                    const min = campo.getAttribute('min');
                    if (isNaN(num) || (min !== null && num < parseFloat(min))) {
                        mostrarError(campo, `Ingresa un número válido mayor o igual a ${min}.`);
                        esValido = false;
                    }
                }
            });

            // Reglas específicas para formulario de registro
            if (tipo === 'registro') {
                const pass1 = form.querySelector('#id_password') || form.querySelector('input[name="password"]');
                const pass2 = form.querySelector('#id_confirmar_password') || form.querySelector('input[name="confirmar_password"]') || form.querySelector('input[name="password_confirm"]');
                const fechaNac = form.querySelector('input[name="fecha_nacimiento"]');

                if (pass1 && pass1.value.length < 8) {
                    mostrarError(pass1, 'La contraseña debe tener al menos 8 caracteres.');
                    esValido = false;
                }

                if (pass1 && pass2 && pass1.value !== pass2.value) {
                    mostrarError(pass2, 'Las contraseñas no coinciden.');
                    esValido = false;
                }

                if (fechaNac && fechaNac.value) {
                    const fechaIngresada = new Date(fechaNac.value + 'T00:00:00');
                    const hoy = new Date();
                    if (fechaIngresada >= hoy) {
                        mostrarError(fechaNac, 'La fecha de nacimiento debe ser anterior a hoy.');
                        esValido = false;
                    }
                }
            }

            if (!esValido) {
                e.preventDefault();
            }
        });
    });
});