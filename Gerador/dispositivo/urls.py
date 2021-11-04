'''
    Neste arquivo temos as URLS que serão usadas no DJANGO
'''
from django.urls import path
from django.conf.urls import url
from .views import home, add, remove

urlpatterns = [
    url("add/$", add, name = 'add'), #rota para adição de dispositivos
    url("remove/$", remove, name = 'remove'), #rota para eliminar um dispositivo, na qual apenas encerramos a thread de envio
    path("", home, name = 'home'), #rota para a interface de interação
]