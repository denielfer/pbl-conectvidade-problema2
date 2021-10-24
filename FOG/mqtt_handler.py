from my_mqtt import My_mqtt
import threading
import requests
import json
from sortedcontainers import SortedList

MAIN_SERVER_URL='http://26.181.221.42:17892' # ip do main server para o qual a requisição para adiciona esta fog na sua lista de fogs
HOST = '26.181.221.42' # Este ip é considerado o ip no qual tem o mqtt e no qual a api estara rodando
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
# mantemos um contador atualizado de quantos requestes estao na fila para criar 
# mais thread para lidar com as mensagem caso a fila fique muito grande
requests_count = 0
requests_count_check_for_thread = 0

def __request_handler__(is_persistent: bool):
    '''
        Função que lida com  as mensagens recebidas pelo MQTT

        Esta função estara removendo as mensagens que estao na fila e chamando a função predefinida para lida com os requestes.
        As açoes soa definidas na variavel: 'request_actions' na qual temos um dicionario que mapeia a palavra chave com a função 
            que lida com a mensagem determinada
    '''
    global requests_count
    while True:
        try: # caso ocorra um erro nao queremos que a thread que lida com as mensagens pare
            if(len(requests_to_process) != 0): # caso hajam mensagens para serem lidas
                client, userdata, msg = requests_to_process.pop(0) # pegamos a primeira
                #print(msg.topic.split('/')[2])
                topic_splited = msg.topic.split('/') # quebramos o seus topicos para sabermos qual ação
                if(topic_splited[1] in request_actions): # se a ação estiver no dicionario de ações 
                    request_actions[topic_splited[1]](topic_splited, msg.payload, client = my_client) # fazemos a ação selecionada
                else: # caso contrario printamos que determinada ação nao foi definida
                    print(f'[MQTT_HANDLER] Erro on process no action found: {topic_splited[1]}')
                requests_count -= 1 
            else: # caso nao tenha mais mensagens na fila
                if(is_persistent): # se for uma thread persistente
                    pass # volta a verificar se tem mensagens
                else: # caso contrario ela termina sua execução
                    #print("thread handler adicional encerada ******************************************************************")
                    break
        except Exception as e:
            print(f'[MQTT_HANDLER] Erro on process {msg.topic}:{msg.payload} Exception: {e}')

def __queue_requests__(client, userdata, msg):
    '''
        Função que adiciona mensagens MQTT recebidas na fila de mensagens para serem lidas
    '''
    requests_to_process.append((client, userdata, msg))
    global requests_count
    requests_count += 1
    if(requests_count > 100): # se fila tiver mais de 100 mensagens na fila
        global requests_count_check_for_thread
        requests_count_check_for_thread+=1
        if(requests_count_check_for_thread > 50): # e nos verificamos que existe mais de 100 mensagens na fila nas ultimas 50 adições
            #criamos uma thread nova
            requests_count_check_for_thread = 0
            #print(f"[MQTT_HANDLER] New Thread created requests count {requests_count} //////////////////////////////////////////")
            _thread = threading.Thread(target = __request_handler__, args=(False,))
            _thread.setDaemon(True)
            _thread.start()

def get_pacientes_por_prioridade(quantidade: int):
    '''
        Função que retorna uma lista dos {quantidade} pacientes mais gravez do sistema, ordenados por gavidade de forma decrecente
    '''
    quantidade = int(quantidade)
    return pacientes_por_gravidade[::-1][:quantidade]

fog_name = input("Digite o identificador da fog: ")
my_client.conect(ip=HOST,callback = __queue_requests__)
# print('dfc')
#iniciamos a thread que lida com as respostas da fila de mensagens
request_handler_thread = threading.Thread(target = __request_handler__, args=(True,))
request_handler_thread.setDaemon(True)
request_handler_thread.start()
my_client.subscribe(f'{fog_name}/#', qos = 1) #nos inscrevemos no topico que a fog houve
# e enviamos uma mensagem ao servidor indicando que esta fog esta operante
requests.post(MAIN_SERVER_URL+f'/add_fogs/{fog_name}',json={'href':f"{HOST}:{PORT_API}",
                                                                'ip':f"{HOST}",
                                                                "port":PORT_BROKER,"is_final":True})
if(__name__ == '__main__'):
    input()