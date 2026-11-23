from .models import Articulo
# Create your views here.

#VISTAS BASADAS EN FUNCIONES
def listar_articulos(request):
    articulos = Articulo.objects.all()
    print(articulos)