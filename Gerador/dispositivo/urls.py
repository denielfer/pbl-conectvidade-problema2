'''
    Neste arquivo temos os URLS que serao usados no DJANGO
'''
from django.urls import path
from django.conf.urls import url
from .views import home, add, remove

urlpatterns = [
    url("add/$", add, name = 'add'), # rota para adição de dispositivos
    url("remove/$", remove, name = 'remove'), # rota para eliminar um dispositivo, na qual apenas terminamos a thread de envio
    path("", home, name = 'home'), # rota para a interfacie de interação
]