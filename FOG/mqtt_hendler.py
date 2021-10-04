from my_mqtt import My_mqtt
from time import sleep
import threading
import json

decoder = json.JSONDecoder()
encoder = json.JSONEncoder()
my_client = My_mqtt()

# Padrao rotas MQTT
# o que tem o padrao "__nome_paciente__" representa variavel entao isso seria substituido pelo nome do pacinete 
# Para atualizar estado do paciente:
#   'fogs/__fog_identificador__/update_data/__identificador_do_paciente__/__prioriade_atual__/__prioridade_antiga__'
# 

prioridades=[{},{},{},{},{}] # lista com dicionarios de priopridade
# em cada posição da lista temos um dicionario contendo os pacientes da prioridade respectiva ao index do dicionario na lista

def __update_data__(topic_splited,payload,client):
    print(f'{topic_splited[3]} prioridade:{topic_splited[4]} estado:{"Grave" if topic_splited[4] != 0 else "Normal"}')
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
    while True:
        try:
            if(len(requests_to_process) != 0):
                client,userdata,msg=requests_to_process.pop(0)
                print(msg.topic.split('/'))
                topic_splited = msg.topic.split('/')
                if(topic_splited[2] in request_actions ):
                    request_actions[topic_splited[2]](topic_splited,msg.payload,client=my_client)
                else:
                    print(f'[MQTT_HANDLER] Erro on process no action found: {topic_splited[2]}')
            else:
                sleep(.05)
        except Exception as e:
            print(f'[MQTT_HANDLER] Erro on process {msg.topic}:{msg.payload} Exception: {e}')

fog_name='fog_1'
my_client.conect(callback=__queue_requests__)
request_handler_thread = threading.Thread(target=__request_handler__)
request_handler_thread.setDaemon(True)
request_handler_thread.start()
my_client.subscribe(f'fogs/{fog_name}/#',qos=1)
my_client.publish(f"main_server/new_fog/{fog_name}",'')
if(__name__ == '__main__'):
    input()