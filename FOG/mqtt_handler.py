from my_mqtt import My_mqtt
import threading
import requests
import json
from sortedcontainers import SortedList

MAIN_SERVER_URL='http://26.181.221.42:17892' # link do main serve que esta fog ira se conectar
HOST = '26.181.221.42' # ip desta maquina que sera usado para upa API e onde é esperado que esteja o Broker MQTT
PORT_API = 18931 #porta onde a API ira ser executada
PORT_BROKER = 1883 #porta onde o broker MQTT se encontra

import time as TiMe___ 
def millis():
    ''' 
        Função que retorna os milisegundos do intante atual

        @return int, contendo os milisegundos do intante atual
    '''
    return int(round(TiMe___.time() * 1000))

my_client = My_mqtt() # client mqtt

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
    delay = millis()-int(topic_splited[5]) # dado usado para medir o delay do tempo de envio
    print(f'{topic_splited[2]} gravidade: {topic_splited[3]} estado: {"Grave" if float(topic_splited[3]) > 100 else "Normal"} delay:{delay}')
    try: # tentamos remover o dado antigo de gravidade do paciente na lista
        pacientes_por_gravidade.pop(pacientes_por_gravidade.index({'id': topic_splited[2], 'gravidade': float(topic_splited[4])}))
    except:
        print(f"[MQTT_HANDLER] Não existe registro anterior do paciente {topic_splited[2]}")
    try: # tentamos decodificar os dados enviados
        dados = json.loads(payload)
    except: # caso nao seja possivel enceramos a função
        print(f'[MQTT_HANDLER] not able to decode payload: {payload}')
        return
    #salvamos os dados
    pacientes_por_gravidade.add({'id': topic_splited[2], 'gravidade': float(topic_splited[3])}) # salvamos o paciente na lista ordenada por prioridade
    dados["time"] = topic_splited[5] # salvamos o tempo que foi enviado os dados
    dados["dalay"] = delay # e o delau para a fog
    pacientes_dados[topic_splited[2]] = dados # salvamos os dados no sistema

request_actions = { # dicionario que define ações que resolvem as mensagens mqtt
    'update_data': __update_data__
}

requests_to_process = [] # fila de requests para processar
requests_count = 0 # variavel para contar quantos requestes ainda existem para processar
requests_count_check_for_thread = 0 # variavel para adicção de novas threads que lidam com os requests

def __request_handler__(is_persistent: bool):
    ''' 
        Função que lida com os requests MQTT que estao na fila para serem tratados

        @param is_persistent: bool, boolean que indica se a thread deve encera sua execução quando a fila de requests
            estiver vazia ( False ) ou se deve continuar existindo ( True )
    '''
    global requests_count
    while True:
        try: # para o caso de existir um erro no processamento a thread nao encerra a sua execução e passar para o proximo request
            if(len(requests_to_process) != 0): # se existir requests para processar
                client, userdata, msg = requests_to_process.pop(0) # pegamos os dados salvos
                #print(msg.topic.split('/')[2])
                topic_splited = msg.topic.split('/') # dividimos os topicos
                if(topic_splited[1] in request_actions): # e procuramos a função, e executamos, que lida com este request
                    request_actions[topic_splited[1]](topic_splited, msg.payload, client = my_client)
                else: # caso contrario informamos que o request nao foi possivel tratar pois nao existe função para a mensagme passada
                    print(f'[MQTT_HANDLER] Erro on process no action found: {topic_splited[1]}')
                requests_count -= 1
            else: # caso a lista de requestes para processar estiver vazia
                if(is_persistent): # se for uma thread persistente volta ao inicio do loop
                    pass
                else: # se nao encerra sua execução
                    #print("thread handler adicional encerada ******************************************************************")
                    break
        except Exception as e:
            print(f'[MQTT_HANDLER] Erro on process {msg.topic}:{msg.payload} Exception: {e}')

def __queue_requests__(client, userdata, msg):
    ''' 
        Função que lida com os requests MQTT que chegaram no sistema adicionando elas numa fila para serem processados
    '''
    requests_to_process.append((client, userdata, msg)) # adicionamos o request na lsita
    #verificação se é nescessario criar uam nova thread e se nescessario cria a mesma
    # em um sistema de nevoa onde existiria uma maquina so com esse programa e o mosquito esse codigo seria comentado para almetna desempenho ( redusindo o numero de thread total do sistema )
    global requests_count
    requests_count += 1
    if(requests_count > 100): # se ouver mais de 100 request na fila
        global requests_count_check_for_thread
        requests_count_check_for_thread+=1
        if(requests_count_check_for_thread > 50): # e isso seja visto pelos ultimos 50 requests
            # criamos uma nova thread
            requests_count_check_for_thread = 0
            #print(f"[MQTT_HANDLER] New Thread created requests count {requests_count} //////////////////////////////////////////")
            _thread = threading.Thread(target = __request_handler__, args=(False,))
            _thread.setDaemon(True)
            _thread.start()

def get_pacientes_por_prioridade(quantidade: int):
    '''
        Retorna uma lista com os <quantidade> pacientes mais graves do sistema
    '''
    quantidade = int(quantidade) # garantimos que a varivel é um inteiro pois se for passado '2' ele nao fazo cast
    return pacientes_por_gravidade[-quantidade:]

fog_name = input("Digite o identificador da fog: ") # pegamos o identificador da fog
my_client.conect(ip = HOST, callback = __queue_requests__) # nos conectamos ao broker
# print('dfc')
request_handler_thread = threading.Thread(target = __request_handler__, args=(True,))
request_handler_thread.setDaemon(True)
request_handler_thread.start()
my_client.subscribe(f'{fog_name}/#', qos = 1)
# request para o main server para ser adicionado como fog
requests.post(MAIN_SERVER_URL+f'/add_fogs/{fog_name}',json={'href':f"{HOST}:{PORT_API}",
                                                                'ip':f"{HOST}",
                                                                "port":PORT_BROKER,"is_final":True})
if(__name__ == '__main__'):
    input()