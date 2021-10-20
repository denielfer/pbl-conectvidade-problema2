from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from . import cache

_cache = cache.cache

SERVER_ADRS='http://26.181.221.42:17892'

def lista_de_pacientes(request):
    template = loader.get_template("home.html")
    return HttpResponse(template.render({
                            # 'server_url_pacientes': SERVER_ADRS+"/pacientes/"
                            'server_url_pacientes': "/pacientes/",
                        },request))

def ver_single_pacientes(request,id,from_fog):
    template = loader.get_template("paciente_view.html")
    d = _cache.get("paciente",id=id,fog=from_fog)[id]
    return HttpResponse(template.render({
                            'server_url_paciente': f"/paciente_/{id}/{from_fog}",
                            'keys' : [a for a in d],
                            'id':id,
                            'fog':from_fog
                        },request))

@csrf_exempt
def get_pacientes(request,quantidade):
    return JsonResponse( _cache.get('pacientes',quantidade=quantidade) )


@csrf_exempt
def get_paciente(request,id, from_fog):
    return JsonResponse( _cache.get('paciente',id=id,fog=from_fog) )

@csrf_exempt
def get_paciente_(request,id):
    return get_paciente(request,id,from_fog='all_fogs')