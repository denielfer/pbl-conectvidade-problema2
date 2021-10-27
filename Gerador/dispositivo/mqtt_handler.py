
from .my_mqtt import My_mqtt
from json import dumps
from .dispositivo import Dispositivo
import requests

import time as TiMe___ 
def millis():
    return int(round(TiMe___.time() * 1000))

# Rotas usadas:
#
# 'dispositivos/set_fog/__id_device__' -> no pacote deve ter uma string contendo a rota que será usada
clients = {}
dispositivo_client = {}

def start_mqtt(ip,port):
    client_mqtt = My_mqtt()
    client_mqtt.conect(ip=ip,port=port)
    return client_mqtt

def get_fog(id_dispositivo,codigo):
    try:
        response = requests.post('http://26.181.221.42:17892/get_fog',json={'codigo':codigo}).json()
    except:
        print(f"[DISPOSITIVO] device: '{id_dispositivo}' was not ablet to reach main server or no fog was returned")
        return
    if(f"{response['ip']}_{response['port']}" not in clients):
        client = start_mqtt(response['ip'],response['port'])
        clients[f"{response['ip']}_{response['port']}"] = client
    else:
        client = clients[f"{response['ip']}_{response['port']}"]
    dispositivo_client[id_dispositivo] = (client,response['id'])


def update_paciente_function(dispositivo:Dispositivo):
    ''' Função que define o comportamento de envio de dados do dispositivo
        função que recebe um dispositivo e a    
    '''
    if(dispositivo.id in dispositivo_client):
        client_mqtt,id = dispositivo_client[dispositivo.id]
        client_mqtt.publish(f'{id}/update_data/{dispositivo.id}/{dispositivo.gravidade}/{dispositivo.old_gravidade}/{millis()}',
                            dumps(dispositivo.get_medicoes()))
    else:
        print(f"[{dispositivo.id}] requesting FOG")
        get_fog(dispositivo.id,dispositivo.codigo)
