from my_mqtt import My_mqtt
import threading
import requests
import json
from sortedcontainers import SortedList

MAIN_SERVER_URL='http://26.181.221.42:17892'
HOST = '26.181.221.42'
PORT_API = 18931
PORT_BROKER = 1883

import time as TiMe___ 
def millis():
    return int(round(TiMe___.time() * 1000))

# decoder = json.JSONDecoder()
# encoder = json.JSONEncoder()
my_client = My_mqtt()

# Padrão rotas MQTT
# o que tem o padrão "__nome_paciente__" representa variável então isso seria substituído pelo nome do paciente 
# Para atualizar estado do paciente:
#   '__fog_id__/update_data/__identificador_do_paciente__/__gravidade__/__gravidade_anterior__/__tempo_que_foi_enviado__'

# para armazenar os pacientes usaremos uma estrutura de dados com o(log(n)) para adição, acesso e 
pacientes_por_gravidade = SortedList(key = lambda x: x['gravidade'])  # guarda uma tupla: {"id":__id_paciente__,"gravidade":__gravidade__}
pacientes_dados = {}  # guarda os dados do paciente com chave id do paciente: {__id_do_paciente__: __dados__}

def __update_data__(topic_splited, payload, client):
    '''
        Função interna para atualizar os dados do paciente salvo

        Salvando o nome e gravidade em uma sorted list que ordena os dados pela gravidade e os dados do paciente em um
            dicionário.
    '''
    delay = millis()-int(topic_splited[5])
    print(f'{topic_splited[2]} gravidade: {topic_splited[3]} estado: {"Grave" if float(topic_splited[3]) > 100 else "Normal"} delay:{delay}')
    try: # tentamos remover o dado antigo de gravidade do paciente na lista
        pacientes_por_gravidade.pop(pacientes_por_gravidade.index({'id': topic_splited[2], 'gravidade': float(topic_splited[4])}))
    except:
        print(f"[MQTT_HANDLER] Não existe registro anterior do paciente {topic_splited[2]}")

    try:
        dados = json.loads(payload)
    except:
        print(f'[MQTT_HANDLER] not able to decode payload: {payload}')
        return
    pacientes_por_gravidade.add({'id': topic_splited[2], 'gravidade': float(topic_splited[3])})
    dados["time"] = topic_splited[5]
    dados["dalay"] = delay
    pacientes_dados[topic_splited[2]] = dados

request_actions = {
    'update_data': __update_data__
}

requests_to_process = []
requests_count = 0
requests_count_check_for_thread = 0

def __request_handler__(is_persistent: bool):
    global requests_count
    while True:
        try:
            if(len(requests_to_process) != 0):
                client, userdata, msg = requests_to_process.pop(0)
                #print(msg.topic.split('/')[2])
                topic_splited = msg.topic.split('/')
                if(topic_splited[1] in request_actions):
                    request_actions[topic_splited[1]](topic_splited, msg.payload, client = my_client)
                else:
                    print(f'[MQTT_HANDLER] Erro on process no action found: {topic_splited[1]}')
                requests_count -= 1
            else:
                if(is_persistent):
                    pass
                else:
                    #print("thread handler adicional encerada ******************************************************************")
                    break
        except Exception as e:
            print(f'[MQTT_HANDLER] Erro on process {msg.topic}:{msg.payload} Exception: {e}')

def __queue_requests__(client, userdata, msg):
    requests_to_process.append((client, userdata, msg))
    global requests_count
    requests_count += 1
    if(requests_count > 100):
        global requests_count_check_for_thread
        requests_count_check_for_thread+=1
        if(requests_count_check_for_thread > 50):
            requests_count_check_for_thread = 0
            #print(f"[MQTT_HANDLER] New Thread created requests count {requests_count} //////////////////////////////////////////")
            _thread = threading.Thread(target = __request_handler__, args=(False,))
            _thread.setDaemon(True)
            _thread.start()

def get_pacientes_por_prioridade(quantidade: int):
    quantidade = int(quantidade)
    return pacientes_por_gravidade[::-1][:quantidade]

fog_name = input("Digite o identificador da fog: ")
my_client.conect(callback = __queue_requests__)
# print('dfc')
request_handler_thread = threading.Thread(target = __request_handler__, args=(True,))
request_handler_thread.setDaemon(True)
request_handler_thread.start()
my_client.subscribe(f'{fog_name}/#', qos = 1)
requests.post(MAIN_SERVER_URL+f'/add_fogs/{fog_name}',json={'href':f"{HOST}:{PORT_API}",
                                                                'ip':f"{HOST}",
                                                                "port":PORT_BROKER,"is_final":True})
if(__name__ == '__main__'):
    input()