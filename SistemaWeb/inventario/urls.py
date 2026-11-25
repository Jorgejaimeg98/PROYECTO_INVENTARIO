from django.urls import path
from . import views

urlpatterns = [
    # Autenticación y menú
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('menu/', views.menu_principal, name='menu_principal'),

    # Núcleo: Artículos
    path('listar_articulos/', views.listar_articulos, name='listar_articulos'),
    path('crear_articulos/', views.crear_articulos, name='crear_articulos'),
    path('editar_articulos/<int:pk>/', views.editar_articulos, name='editar_articulos'),
    path('eliminar_articulos/<int:pk>/', views.eliminar_articulos, name='eliminar_articulos'),

    # Relacionado 1: Categorías
    path('listar_categorias/', views.listar_categorias, name='listar_categorias'),
    path('crear_categorias/', views.crear_categorias, name='crear_categorias'),
    path('editar_categorias/<int:pk>/', views.editar_categorias, name='editar_categorias'),
    path('eliminar_categorias/<int:pk>/', views.eliminar_categorias, name='eliminar_categorias'),

    # Relacionado 2: Proveedores
    path('listar_proveedores/', views.listar_proveedores, name='listar_proveedores'),
    path('crear_proveedores/', views.crear_proveedores, name='crear_proveedores'),
    path('editar_proveedores/<int:pk>/', views.editar_proveedores, name='editar_proveedores'),
    path('eliminar_proveedores/<int:pk>/', views.eliminar_proveedores, name='eliminar_proveedores'),

    # Relacionado 3: Entradas
    path('listar_entradas/', views.listar_entradas, name='listar_entradas'),
    path('crear_entradas/', views.crear_entradas, name='crear_entradas'),
    path('editar_entradas/<int:pk>/', views.editar_entradas, name='editar_entradas'),
    path('eliminar_entradas/<int:pk>/', views.eliminar_entradas, name='eliminar_entradas'),

    # Relacionado 4: Salidas
    path('listar_salidas/', views.listar_salidas, name='listar_salidas'),
    path('crear_salidas/', views.crear_salidas, name='crear_salidas'),
    path('editar_salidas/<int:pk>/', views.editar_salidas, name='editar_salidas'),
    path('eliminar_salidas/<int:pk>/', views.eliminar_salidas, name='eliminar_salidas'),
]