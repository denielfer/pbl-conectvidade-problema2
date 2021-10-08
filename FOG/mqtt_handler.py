from my_mqtt import My_mqtt
from time import sleep
import threading
import json

# decoder = json.JSONDecoder()
# encoder = json.JSONEncoder()
my_client = My_mqtt()

# Padrão rotas MQTT
# o que tem o padrao "__nome_paciente__" representa variável então isso seria substituído pelo nome do paciente 
# Para atualizar estado do paciente:
#   'fogs/__fog_identificador__/update_data/__identificador_do_paciente__/__prioriade_atual__/__prioridade_antiga__'
#   'fogs/__fog_identificador__/get_pacientes/__quantidade__'

# em cada posição da lista temos um dicionário contendo os pacientes da prioridade respectiva ao index do dicionário na lista
pacientes = {}

def __update_data__(topic_splited, payload, client):
    '''
        Função interna para atualizar os dados do paciente salvo
    '''
    print(f'{topic_splited[3]} gravidade:{topic_splited[4]} estado:{"Grave" if topic_splited[4] > 100 else "Normal"}')
    try:
        dados = json.loads(payload)
    except:
        dados = {}
    pacientes[topic_splited[3]] = {'dados': dados, 'gravidade': topic_splited[4]}

request_actions = {
    'update_data': __update_data__
}

requests_to_process = []

def __queue_requests__(client, userdata, msg):
    requests_to_process.append((client, userdata, msg))

def __request_handler__():
    while True:
        try:
            if(len(requests_to_process) != 0):
                client, userdata, msg = requests_to_process.pop(0)
                #print(msg.topic.split('/')[2])
                topic_splited = msg.topic.split('/')
                if(topic_splited[2] in request_actions):
                    request_actions[topic_splited[2]](topic_splited, msg.payload, client = my_client)
                else:
                    print(f'[MQTT_HANDLER] Erro on process no action found: {topic_splited[2]}')
            else:
                sleep(.05)
        except Exception as e:
            print(f'[MQTT_HANDLER] Erro on process {msg.topic}:{msg.payload} Exception: {e}')

def get_pacientes_por_prioridade(quantidade: int):
    quantidade = int(quantidade)
    return [(paciente, pacientes[paciente]["gravidade"]) for paciente in pacientes].sort(key=lambda patient: patient[1], reverse=True)[:quantidade]

fog_name = input("Digite o identificador da fog: ")
my_client.conect(callback = __queue_requests__)
request_handler_thread = threading.Thread(target = __request_handler__)
request_handler_thread.setDaemon(True)
request_handler_thread.start()
my_client.subscribe(f'fogs/{fog_name}/#', qos = 1)
my_client.publish(f"main_server/new_fog/{fog_name}", '')
if(__name__ == '__main__'):
    input()