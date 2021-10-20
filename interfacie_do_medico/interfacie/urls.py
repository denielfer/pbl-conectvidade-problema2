from django.urls import path
from django.conf.urls import url
from .views import lista_de_pacientes,get_paciente,get_pacientes,get_paciente_,ver_single_pacientes

app_name = "receptor"

urlpatterns = [
    path('paciente/<str:id>/<str:from_fog>', ver_single_pacientes, name="paciente_from_fog"),
    path('paciente_/<str:id>/<str:from_fog>', get_paciente, name="paciente_from_fog"),
    path('paciente_/<str:id>/', get_paciente_, name="paciente"),
    path('pacientes/<int:quantidade>/', get_pacientes, name="pacientes"),
    url(r'^$', lista_de_pacientes, name="list_pacients"),
]