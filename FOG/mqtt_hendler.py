from my_mqtt import My_mqtt
from time import sleep
import json

decoder = json.JSONDecoder()
encoder = json.JSONEncoder()

# Padrao rotas MQTT
# o que tem o padrao "__nome_paciente__" representa variavel entao isso seria substituido pelo nome do pacinete 
# Para atualizar estado do paciente:
#   'fogs/__fog_identificador__/update_data/__identificador_do_paciente__/__prioriade_atual__/__prioridade_antiga__'
# 

prioridades=[{},{},{},{},{}] # lista com dicionarios de priopridade
# em cada posição da lista temos um dicionario contendo os pacientes da prioridade respectiva ao index do dicionario na lista

def __update_data__(topic_splited,payload):
    if(topic_splited[5] != "none"): # se tive prioridade anterior
        # removemos esse dispositivo da lisda de disposivos na prioridade informada
        del(prioridades[int(topic_splited[5])][topic_splited[3]]) 
    #adicionamos o dispositivo na fila de prioridade informada
    prioridades[int(topic_splited[4])][topic_splited[3]] = decoder.decode(payload) 


request_actions = {
    'update_data':__update_data__,
}

requests_to_process = []
def __queue_requests__(client,userdata,msg):
    requests_to_process.append((client,userdata,msg))

def __request_handler__():
    if(len(requests_to_process) != 0):
        client,userdata,msg=requests_to_process.pop(0)
        topic_splited = msg.topic.split('/')
        if(topic_splited[1] in request_actions ):
            request_actions[topic_splited[1]](topic_splited,msg.payload)
        else:
            print(f'erro on process {client},{userdata},{msg}')
    else:
        sleep(.05)

fog_name=''
client = My_mqtt()
client.conect()
client.subscribe(f'fogs/{fog_name}/#',__queue_requests__,qos=1)
client.publish(f"main_server/new_fog/{fog_name}")
