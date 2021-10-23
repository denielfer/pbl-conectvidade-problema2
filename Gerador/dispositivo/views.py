from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from .dispositivo import Dispositivo
from random import choices
from string import hexdigits
from .import mqtt_handler

dispositivos = {}

def get_random_mac_id() -> str:
    return ':'.join(''.join(choices(hexdigits, k = 2)).upper() for _ in range(6))

def home(request):
    template = loader.get_template("home.html")
    return HttpResponse(template.render({"dispositivos":[(dispositivos[a].id) for a in dispositivos], "options":[(f'Prioridade {a}', a) for a in mqtt_handler.Dispositivo.GOAL_DADOS_PER_STATE]},request))

def add(request):
    if(request.method == "POST"):
        for _ in range(int(request.POST.get('numero_de_dispositivos'))):
            id = get_random_mac_id()
            while(id in dispositivos):
                id = get_random_mac_id()
            # while(id not in mqtt_handler.dispositivo_fog):
            #     print("esperando fog")
            #     mqtt_handler.get_fog(id)
            #     sleep(0.5)
            dispositivos[id] = Dispositivo(id,request.POST.get('tendencia_dos_dispositivos'), send_function = mqtt_handler.update_paciente_function)
            dispositivos[id].init_thread()
    return redirect('home')

def remove(request):
    if(request.method == "POST"):
        id = request.POST.get('id')
        if(id in dispositivos):
            dispositivos[id].stop()
            del(dispositivos[id])
    return redirect('home')