from django.core.exceptions import ValidationError


def validar_cedula_ecuatoriana(valor):
    # Convertimos el valor a texto y quitamos espacios al inicio o al final
    cedula = str(valor).strip()

    # 1. Comprobar que tenga 10 caracteres y que todos sean números
    if len(cedula) != 10:
        raise ValidationError('La cédula debe tener exactamente 10 dígitos.')

    if not cedula.isdigit():
        raise ValidationError('La cédula debe contener únicamente números.')

    # 2. Comprobar que los dos primeros dígitos correspondan a una provincia válida (01 a 24, o 30)
    codigo_provincia = int(cedula[0:2])
    if (codigo_provincia < 1 or codigo_provincia > 24) and codigo_provincia != 30:
        raise ValidationError('El código de provincia de la cédula no es válido.')

    # 3. Comprobar que el tercer dígito sea menor a 6 (persona natural)
    tercer_digito = int(cedula[2])
    if tercer_digito >= 6:
        raise ValidationError('El tercer dígito de la cédula no corresponde a una persona natural.')

    # 4. Algoritmo oficial módulo 10 usando los primeros 9 dígitos
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma_total = 0

    for posicion in range(9):
        digito_actual = int(cedula[posicion])
        coeficiente_actual = coeficientes[posicion]
        resultado = digito_actual * coeficiente_actual

        if resultado >= 10:
            resultado = resultado - 9

        suma_total = suma_total + resultado

    # 5. Calcular el dígito verificador esperado y compararlo con el último dígito de la cédula
    residuo = suma_total % 10
    if residuo == 0:
        digito_verificador_calculado = 0
    else:
        digito_verificador_calculado = 10 - residuo

    ultimo_digito_cedula = int(cedula[9])
    if digito_verificador_calculado != ultimo_digito_cedula:
        raise ValidationError('La cédula ecuatoriana ingresada no es válida.')


def validar_ruc_ecuatoriano(valor):
    ruc = str(valor).strip()

    if len(ruc) != 13:
        raise ValidationError('El RUC debe tener exactamente 13 dígitos.')

    if not ruc.isdigit():
        raise ValidationError('El RUC debe contener únicamente números.')

    codigo_provincia = int(ruc[0:2])
    if (codigo_provincia < 1 or codigo_provincia > 24) and codigo_provincia != 30:
        raise ValidationError('El código de provincia del RUC no es válido.')

    ultimos_tres_digitos = ruc[10:13]
    if ultimos_tres_digitos == '000':
        raise ValidationError('Los últimos tres dígitos del RUC no pueden ser 000.')


def validar_telefono(valor):
    telefono = str(valor).strip()

    if not telefono.isdigit():
        raise ValidationError('El teléfono debe contener únicamente números.')

    if len(telefono) != 10:
        raise ValidationError('El teléfono debe tener exactamente 10 dígitos.')