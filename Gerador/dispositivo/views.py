'''
    Neste arquivo temos as funções que são executadas quando uma das rotas cadastradas é acessada
'''
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from .dispositivo import Dispositivo
import names
from .import request_handler

dispositivos = {}

def home(request):
    '''
        Função que simplesmente retora a página HTML da home page (interface de interação)
    '''
    template = loader.get_template("home.html")
    return HttpResponse(template.render({"dispositivos":[(dispositivos[i].id) for i in dispositivos], "options":[(f'Gravidade {tendencia}', tendencia) for tendencia in request_handler.Dispositivo.GOAL_DADOS_PER_STATE]}, request))

def add(request):
    '''
        Função responsável por adicionar novos dispositivos no sistema
    '''
    if(request.method == "POST"): #se for um POST
        for _ in range(int(request.POST.get('numero_de_dispositivos'))): #para cada dispositivo no campo 'numero_de_dispositivos' presente no request recebido
            #conseguimos um identificador único para este sistema
            id = names.get_full_name()
            while(id in dispositivos):
                id = names.get_full_name()
            #e então criamos um dispositivo com este identificador, passando a tendência indicada no campo 'tendencia_dos_dispositivos'
            dispositivos[id] = Dispositivo(id, request.POST.get('tendencia_dos_dispositivos'), send_function = request_handler.update_paciente_function)
            dispositivos[id].init_thread()
    return redirect('home') #redirecionamos para a interface

def remove(request):
    '''
        Função que encerra a execução de um dispositivo
    '''
    if(request.method == "POST"): #se post
        id = request.POST.get('id') #pegamos o id passado
        if(id in dispositivos): #se o id estiver no sistema
            dispositivos[id].stop() #paramos sua execução
            del(dispositivos[id]) #removemos do sistema
    return redirect('home') #redirecionamos para home
