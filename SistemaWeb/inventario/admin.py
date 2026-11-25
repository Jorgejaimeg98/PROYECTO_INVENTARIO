from django.contrib import admin
from .models import Usuario, Categoria, Proveedor, Articulo, Entrada, Salida
# Register your models here.

#admin.site.register(Usuario)
#admin.site.register(Categoria)
#admin.site.register(Proveedor)
#admin.site.register(Articulo)
#admin.site.register(Entrada)
#admin.site.register(Salida)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import Usuario, Categoria, Proveedor, Articulo, Entrada, Salida


class UsuarioCreacionAdminForm(BaseUserCreationForm):
    """Formulario nativo de Django para crear usuarios en el panel admin usando correo en lugar de username."""
    class Meta:
        model = Usuario
        fields = (
            'cedula',
            'first_name',
            'last_name',
            'email',
            'telefono',
            'fecha_nacimiento',
            'direccion',
        )


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreacionAdminForm
    form = UserChangeForm
    model = Usuario

    list_display = ('cedula', 'first_name', 'last_name', 'email', 'telefono', 'activo', 'is_staff')
    list_filter = ('activo', 'is_staff', 'is_superuser')
    search_fields = ('cedula', 'first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name')

    fieldsets = (
        ('Credenciales de acceso', {'fields': ('email', 'password')}),
        ('Datos personales', {
            'fields': ('cedula', 'first_name', 'last_name', 'telefono', 'fecha_nacimiento', 'direccion')
        }),
        ('Estado y permisos', {
            'fields': ('activo', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        ('Registro de nuevo usuario', {
            'classes': ('wide',),
            'fields': (
                'cedula',
                'first_name',
                'last_name',
                'email',
                'telefono',
                'fecha_nacimiento',
                'direccion',
                'password1',
                'password2',
                'activo',
                'is_staff',
            ),
        }),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('ruc', 'nombre', 'telefono', 'correo', 'activo')
    list_filter = ('activo',)
    search_fields = ('ruc', 'nombre', 'correo')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'categoria',
        'proveedor',
        'precio_unitario',
        'stock_actual',
        'stock_minimo',
        'activo',
    )
    list_filter = ('activo', 'categoria', 'proveedor')
    search_fields = ('codigo', 'nombre')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = (
        'numero_documento',
        'articulo',
        'proveedor',
        'cantidad',
        'costo_unitario',
        'fecha_entrada',
        'usuario',
        'activo',
    )
    list_filter = ('activo', 'fecha_entrada', 'proveedor')
    search_fields = ('numero_documento', 'articulo__nombre', 'proveedor__nombre')
    ordering = ('-fecha_entrada',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(Salida)
class SalidaAdmin(admin.ModelAdmin):
    list_display = (
        'numero_documento',
        'articulo',
        'cantidad',
        'motivo',
        'fecha_salida',
        'usuario',
        'activo',
    )
    list_filter = ('activo', 'motivo', 'fecha_salida')
    search_fields = ('numero_documento', 'articulo__nombre')
    ordering = ('-fecha_salida',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')