from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('listar_articulos/', views.listar_articulos, name='listar_articulos'),
]