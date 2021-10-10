from my_mqtt import My_mqtt
from time import sleep
import threading
import json
from sortedcontainers import SortedList

HOST = '26.181.221.42'
PORT = 18956

# decoder = json.JSONDecoder()
# encoder = json.JSONEncoder()
my_client = My_mqtt()

# Padrão rotas MQTT
# o que tem o padrao "__nome_paciente__" representa variável então isso seria substituído pelo nome do paciente 
# Para atualizar estado do paciente:
#   'fogs/__fog_identificador__/update_data/__identificador_do_paciente__/__gravidade__/__gravidade_anterior__'

# para armazena os pacietnes usaremos uma estrutura de dados com o(log(n)) para adição,acesso e 
pacientes_por_gravidade = SortedList(key=lambda x: x[1])  # guarda uma tupla: (__id_paciente__,__gravidade__)
pacientes_dados = {}  # guarda os dados do paciente com chave id do paciente: __id_do_paciente__:__dados__

def __update_data__(topic_splited, payload, client):
    '''
        Função interna para atualizar os dados do paciente salvo

        Salvando o nome e gravidade em uma sorted list que ordena os dados pela gravidade e os dados do paciente em um
            dicionario.
    '''
    print(f'{topic_splited[3]} gravidade:{topic_splited[4]} estado:{"Grave" if float(topic_splited[4]) > 100 else "Normal"}')
    try: # tentanmos remove o dado antigo de gravidade do paciente na lista
        pacientes_por_gravidade.pop( pacientes_por_gravidade.index( ( topic_splited[3],float(topic_splited[5]) ) ) )
    except:
        print(f"[MQTT_HANDLER] Nao exisre registro anterior do paciente {topic_splited[3]}")

    try:
        dados = json.loads(payload)
    except:
        print(f'[MQTT_HANDLER] not able to decode payload: {payload}')
        return
    pacientes_por_gravidade.add((topic_splited[3],float(topic_splited[4])))
    pacientes_dados[topic_splited[3]] = dados

request_actions = {
    'update_data': __update_data__
}

requests_to_process = []
requests_count = 0
requests_count_check_for_thread =0

def __request_handler__(is_persistent:bool):
    global requests_count
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
                requests_count -=1
            else:
                if(is_persistent):
                    sleep(.05)
                else:
                    #print("thread handler adicional encerada ******************************************************************")
                    break
        except Exception as e:
            print(f'[MQTT_HANDLER] Erro on process {msg.topic}:{msg.payload} Exception: {e}')

def __queue_requests__(client, userdata, msg):
    requests_to_process.append((client, userdata, msg))
    global requests_count
    requests_count+=1
    if(requests_count > 100):
        global requests_count_check_for_thread
        requests_count_check_for_thread+=1
        if(requests_count_check_for_thread > 50):
            requests_count_check_for_thread =0
            #print(f"[MQTT_HANDLER] New Thread created requests count {requests_count} //////////////////////////////////////////")
            _thread = threading.Thread(target = __request_handler__,args=(False,))
            _thread.setDaemon(True)
            _thread.start()

def get_pacientes_por_prioridade(quantidade: int):
    quantidade = int(quantidade)
    return pacientes_por_gravidade[::-1][:quantidade]

fog_name = input("Digite o identificador da fog: ")
my_client.conect(callback = __queue_requests__)
print('dfc')
request_handler_thread = threading.Thread(target = __request_handler__,args=(True,))
request_handler_thread.setDaemon(True)
request_handler_thread.start()
my_client.subscribe(f'fogs/{fog_name}/#', qos = 1)
my_client.publish(f"main_server/new_fog/{fog_name}", '26.181.221.42:18956')
if(__name__ == '__main__'):
    input()