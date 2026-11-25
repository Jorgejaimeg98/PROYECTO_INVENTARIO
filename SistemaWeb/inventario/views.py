from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F

from .models import Categoria, Proveedor, Articulo, Entrada, Salida
from .forms import (
    LoginForm,
    RegistroUsuarioForm,
    CategoriaForm,
    ProveedorForm,
    ArticuloForm,
    EntradaForm,
    SalidaForm,
)


def _notificar_errores_formulario(request, form):
    """Determina si el error del formulario corresponde a un registro duplicado o validación general."""
    es_duplicado = False
    for error_list in form.errors.as_data().values():
        for error in error_list:
            if getattr(error, 'code', None) == 'unique':
                es_duplicado = True
                break
    if es_duplicado:
        messages.error(request, 'Registro duplicado.')
    else:
        messages.error(request, 'Error en validación de formulario.')


# ==============================================================================
# AUTENTICACIÓN, REGISTRO Y MENÚ PRINCIPAL
# ==============================================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('menu_principal')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None and user.activo:
                login(request, user)
                return redirect('menu_principal')
            messages.error(request, 'Información incorrecta.')
        else:
            messages.error(request, 'Error en validación de formulario.')
    else:
        form = LoginForm()

    return render(request, 'inventario/login.html', {'form': form})


def registro_view(request):
    if request.user.is_authenticated:
        return redirect('menu_principal')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro creado correctamente.')
            return redirect('login')
        _notificar_errores_formulario(request, form)
    else:
        form = RegistroUsuarioForm()

    return render(request, 'inventario/registro.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def menu_principal(request):
    contexto = {
        'total_articulos': Articulo.objects.filter(activo=True).count(),
        'articulos_bajo_stock': Articulo.objects.filter(
            activo=True, stock_actual__lte=F('stock_minimo')
        ).count(),
        'total_categorias': Categoria.objects.filter(activo=True).count(),
        'total_proveedores': Proveedor.objects.filter(activo=True).count(),
        'total_entradas': Entrada.objects.filter(activo=True).count(),
        'total_salidas': Salida.objects.filter(activo=True).count(),
    }
    return render(request, 'inventario/menu.html', contexto)


# ==============================================================================
# MANTENIMIENTO NÚCLEO: ARTÍCULOS
# ==============================================================================

@login_required
def listar_articulos(request):
    articulos = Articulo.objects.select_related('categoria', 'proveedor').filter(activo=True)
    return render(request, 'inventario/articulos/listar_articulos.html', {'articulos': articulos})


@login_required
def crear_articulos(request):
    if request.method == 'POST':
        form = ArticuloForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro creado correctamente.')
            return redirect('listar_articulos')
        _notificar_errores_formulario(request, form)
    else:
        form = ArticuloForm()

    return render(request, 'inventario/articulos/crear_articulos.html', {'form': form})


@login_required
def editar_articulos(request, pk):
    articulo = Articulo.objects.filter(pk=pk, activo=True).first()
    if not articulo:
        messages.error(request, 'Registro no encontrado.')
        return redirect('listar_articulos')

    if request.method == 'POST':
        form = ArticuloForm(request.POST, instance=articulo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro actualizado correctamente.')
            return redirect('listar_articulos')
        _notificar_errores_formulario(request, form)
    else:
        form = ArticuloForm(instance=articulo)

    return render(request, 'inventario/articulos/editar_articulos.html', {'form': form, 'articulo': articulo})


@login_required
def eliminar_articulos(request, pk):
    articulo = Articulo.objects.filter(pk=pk, activo=True).first()
    if not articulo:
        messages.error(request, 'Registro no encontrado.')
        return redirect('listar_articulos')

    if request.method == 'POST':
        articulo.eliminar_logico()
        messages.success(request, 'Registro eliminado lógicamente de manera exitosa.')
    return redirect('listar_articulos')


# ==============================================================================
# MANTENIMIENTO RELACIONADO 1: CATEGORÍAS
# ==============================================================================

@login_required
def listar_categorias(request):
    categorias = Categoria.objects.filter(activo=True)
    return render(request, 'inventario/categorias/lista.html', {'categorias': categorias})


@login_required
def crear_categorias(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro creado correctamente.')
            return redirect('categoria_lista')
        _notificar_errores_formulario(request, form)
    else:
        form = CategoriaForm()

    return render(request, 'inventario/categorias/crear.html', {'form': form})


@login_required
def editar_categorias(request, pk):
    categoria = Categoria.objects.filter(pk=pk, activo=True).first()
    if not categoria:
        messages.error(request, 'Registro no encontrado.')
        return redirect('categoria_lista')

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro actualizado correctamente.')
            return redirect('categoria_lista')
        _notificar_errores_formulario(request, form)
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'inventario/categorias/editar.html', {'form': form, 'categoria': categoria})


@login_required
def eliminar_categorias(request, pk):
    categoria = Categoria.objects.filter(pk=pk, activo=True).first()
    if not categoria:
        messages.error(request, 'Registro no encontrado.')
        return redirect('categoria_lista')

    if request.method == 'POST':
        categoria.eliminar_logico()
        messages.success(request, 'Registro eliminado lógicamente de manera exitosa.')
    return redirect('categoria_lista')


# ==============================================================================
# MANTENIMIENTO RELACIONADO 2: PROVEEDORES
# ==============================================================================

@login_required
def listar_proveedores(request):
    proveedores = Proveedor.objects.filter(activo=True)
    return render(request, 'inventario/proveedores/lista.html', {'proveedores': proveedores})


@login_required
def crear_proveedores(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro creado correctamente.')
            return redirect('proveedor_lista')
        _notificar_errores_formulario(request, form)
    else:
        form = ProveedorForm()

    return render(request, 'inventario/proveedores/crear.html', {'form': form})


@login_required
def editar_proveedores(request, pk):
    proveedor = Proveedor.objects.filter(pk=pk, activo=True).first()
    if not proveedor:
        messages.error(request, 'Registro no encontrado.')
        return redirect('proveedor_lista')

    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro actualizado correctamente.')
            return redirect('proveedor_lista')
        _notificar_errores_formulario(request, form)
    else:
        form = ProveedorForm(instance=proveedor)

    return render(request, 'inventario/proveedores/editar.html', {'form': form, 'proveedor': proveedor})


@login_required
def eliminar_proveedores(request, pk):
    proveedor = Proveedor.objects.filter(pk=pk, activo=True).first()
    if not proveedor:
        messages.error(request, 'Registro no encontrado.')
        return redirect('proveedor_lista')

    if request.method == 'POST':
        proveedor.eliminar_logico()
        messages.success(request, 'Registro eliminado lógicamente de manera exitosa.')
    return redirect('proveedor_lista')


# ==============================================================================
# MANTENIMIENTO RELACIONADO 3: ENTRADAS
# ==============================================================================

@login_required
def listar_entradas(request):
    entradas = Entrada.objects.select_related('articulo', 'proveedor', 'usuario').filter(activo=True)
    return render(request, 'inventario/entradas/lista.html', {'entradas': entradas})


@login_required
def crear_entradas(request):
    if request.method == 'POST':
        form = EntradaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                entrada = form.save(commit=False)
                entrada.usuario = request.user
                entrada.save()
                articulo = entrada.articulo
                articulo.stock_actual += entrada.cantidad
                articulo.save(update_fields=['stock_actual', 'fecha_actualizacion'])
            messages.success(request, 'Registro creado correctamente.')
            return redirect('entrada_lista')
        _notificar_errores_formulario(request, form)
    else:
        form = EntradaForm()

    return render(request, 'inventario/entradas/crear.html', {'form': form})


@login_required
def editar_entradas(request, pk):
    entrada = Entrada.objects.select_related('articulo').filter(pk=pk, activo=True).first()
    if not entrada:
        messages.error(request, 'Registro no encontrado.')
        return redirect('entrada_lista')

    articulo_anterior = entrada.articulo
    cantidad_anterior = entrada.cantidad

    if request.method == 'POST':
        form = EntradaForm(request.POST, instance=entrada)
        if form.is_valid():
            with transaction.atomic():
                nueva_entrada = form.save(commit=False)
                if articulo_anterior.pk == nueva_entrada.articulo.pk:
                    nuevo_stock = articulo_anterior.stock_actual - cantidad_anterior + nueva_entrada.cantidad
                    if nuevo_stock < 0:
                        messages.error(request, 'Error en validación de formulario.')
                        form.add_error('cantidad', 'El ajuste dejaría el stock del artículo en negativo.')
                        return render(request, 'inventario/entradas/editar.html', {'form': form, 'entrada': entrada})
                    articulo_anterior.stock_actual = nuevo_stock
                    articulo_anterior.save(update_fields=['stock_actual', 'fecha_actualizacion'])
                else:
                    if articulo_anterior.stock_actual < cantidad_anterior:
                        messages.error(request, 'Error en validación de formulario.')
                        form.add_error('articulo', 'No hay stock suficiente en el artículo anterior para revertir esta entrada.')
                        return render(request, 'inventario/entradas/editar.html', {'form': form, 'entrada': entrada})
                    articulo_anterior.stock_actual -= cantidad_anterior
                    articulo_anterior.save(update_fields=['stock_actual', 'fecha_actualizacion'])
                    nueva_entrada.articulo.stock_actual += nueva_entrada.cantidad
                    nueva_entrada.articulo.save(update_fields=['stock_actual', 'fecha_actualizacion'])
                nueva_entrada.save()
            messages.success(request, 'Registro actualizado correctamente.')
            return redirect('entrada_lista')
        _notificar_errores_formulario(request, form)
    else:
        form = EntradaForm(instance=entrada)

    return render(request, 'inventario/entradas/editar.html', {'form': form, 'entrada': entrada})


@login_required
def eliminar_entradas(request, pk):
    entrada = Entrada.objects.select_related('articulo').filter(pk=pk, activo=True).first()
    if not entrada:
        messages.error(request, 'Registro no encontrado.')
        return redirect('entrada_lista')

    if request.method == 'POST':
        with transaction.atomic():
            if entrada.articulo.stock_actual >= entrada.cantidad:
                entrada.articulo.stock_actual -= entrada.cantidad
                entrada.articulo.save(update_fields=['stock_actual', 'fecha_actualizacion'])
            entrada.eliminar_logico()
        messages.success(request, 'Registro eliminado lógicamente de manera exitosa.')
    return redirect('entrada_lista')


# ==============================================================================
# MANTENIMIENTO RELACIONADO 4: SALIDAS
# ==============================================================================

@login_required
def listar_salidas(request):
    salidas = Salida.objects.select_related('articulo', 'usuario').filter(activo=True)
    return render(request, 'inventario/salidas/lista.html', {'salidas': salidas})


@login_required
def crear_salidas(request):
    if request.method == 'POST':
        form = SalidaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                salida = form.save(commit=False)
                salida.usuario = request.user
                salida.save()
                articulo = salida.articulo
                articulo.stock_actual -= salida.cantidad
                articulo.save(update_fields=['stock_actual', 'fecha_actualizacion'])
            messages.success(request, 'Registro creado correctamente.')
            return redirect('salida_lista')
        _notificar_errores_formulario(request, form)
    else:
        form = SalidaForm()

    return render(request, 'inventario/salidas/crear.html', {'form': form})


@login_required
def editar_salidas(request, pk):
    salida = Salida.objects.select_related('articulo').filter(pk=pk, activo=True).first()
    if not salida:
        messages.error(request, 'Registro no encontrado.')
        return redirect('salida_lista')

    articulo_anterior = salida.articulo
    cantidad_anterior = salida.cantidad

    if request.method == 'POST':
        form = SalidaForm(request.POST, instance=salida)
        if form.is_valid():
            with transaction.atomic():
                nueva_salida = form.save(commit=False)
                if articulo_anterior.pk == nueva_salida.articulo.pk:
                    articulo_anterior.stock_actual = (
                        articulo_anterior.stock_actual + cantidad_anterior - nueva_salida.cantidad
                    )
                    articulo_anterior.save(update_fields=['stock_actual', 'fecha_actualizacion'])
                else:
                    articulo_anterior.stock_actual += cantidad_anterior
                    articulo_anterior.save(update_fields=['stock_actual', 'fecha_actualizacion'])
                    nueva_salida.articulo.stock_actual -= nueva_salida.cantidad
                    nueva_salida.articulo.save(update_fields=['stock_actual', 'fecha_actualizacion'])
                nueva_salida.save()
            messages.success(request, 'Registro actualizado correctamente.')
            return redirect('salida_lista')
        _notificar_errores_formulario(request, form)
    else:
        form = SalidaForm(instance=salida)

    return render(request, 'inventario/salidas/editar.html', {'form': form, 'salida': salida})


@login_required
def eliminar_salidas(request, pk):
    salida = Salida.objects.select_related('articulo').filter(pk=pk, activo=True).first()
    if not salida:
        messages.error(request, 'Registro no encontrado.')
        return redirect('salida_lista')

    if request.method == 'POST':
        with transaction.atomic():
            salida.articulo.stock_actual += salida.cantidad
            salida.articulo.save(update_fields=['stock_actual', 'fecha_actualizacion'])
            salida.eliminar_logico()
        messages.success(request, 'Registro eliminado lógicamente de manera exitosa.')
    return redirect('salida_lista')