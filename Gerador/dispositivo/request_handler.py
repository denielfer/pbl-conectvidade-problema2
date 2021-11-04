
from .my_mqtt import My_mqtt
from json import dumps
from .dispositivo import Dispositivo
import requests

import time as TiMe___ 
def millis():
    ''' 
        Função que retorna os milisegundos do intante atual

        @return int, contendo os milisegundos do intante atual
    '''
    return int(round(TiMe___.time() * 1000))

clients = {}
dispositivo_client = {}

def start_mqtt(ip,port):
    ''' 
        Função que cria e inicia um broker mqtt, se conectando no broker presente no <ip> e <porta>

        @param ip: str, string cotnendo o ip do broker que deve se conectar
        @param port: int, inteiro indicando a porta do broker que se deve conectar
        @return My_mqtt, client mqtt do tipo: My_mqtt
    '''
    client_mqtt = My_mqtt()
    client_mqtt.conect(ip=ip,port=port)
    return client_mqtt

def get_fog(id_dispositivo,codigo):
    '''
        Função usada por dispositivo para se conectar ao Servidor Principal e conseguir uma fog para se comunicar

        @param id_dispositivo: string, contendo o identificador do dispositivo
        @param codigo: int, numero que sera usado pelo filtro do servidor para escolher qual fog deve ser direcionado
    '''
    try:# fazemos o request
        response = requests.post('http://26.181.221.42:17892/get_fog',json={'codigo':codigo}).json()
    except:# se der erro fechamos a função
        print(f"[DISPOSITIVO] device: '{id_dispositivo}' was not ablet to reach main server or no fog was returned")
        return
    while( not response['is_final']):# enquanto os dados nao forem de uma fog
        response = requests.post(f'http://{response["href"]}/get_fog',json={'codigo':codigo}).json() # continuamos a fazer os requests ate chegarmos em uma fog
    if(f"{response['ip']}_{response['port']}" not in clients):
        # se ouver resposta e o nao haja um broker sa conectado a esta fog criamos um novo broker, 
        # isso foi feito assim, para economisar processamento do sistema ( nao criando diversos 
        # brokers conectados no mesmo, assim temos 1 broker conectado em cada fog e os dispotivos conectados
        # usam esses brokers de forma compartilhada para enviar os dados )
        client = start_mqtt(response['ip'],response['port'])
        clients[f"{response['ip']}_{response['port']}"] = client
    else:# se ja ouver um broker no sistema conectado a fog alvo, slavamos que este dispositivo deve usar este broker
        client = clients[f"{response['ip']}_{response['port']}"]
    dispositivo_client[id_dispositivo] = (client,response['id'])


def update_paciente_function(dispositivo:Dispositivo):
    ''' Função que define o comportamento de envio de dados do dispositivo
        
        Esta função sera passada para os dispositivos pois ela define como os dados sao enviados pelo mesmo,
            assim esta função recebe um dispositivo como parametro para acessar seus dados
        Caso esta função verifica se o dispositivo ja tem um broker designado, caso contrario chama o metodo 
            'get_fog' para este despositivo. ( assim podendo fazer uma adição recursiva, caso o primeiro servidor
            conectado envie dados de outro servidor e nao de uma FOG )

        @param dispositivo: Dispositivo, dispositivo do qual os dados serao enviados
    '''
    try:
        if(dispositivo.id in dispositivo_client):# caso ja tenha um broker designado pra uso
            #fazemos o envio de dados
            client_mqtt,id = dispositivo_client[dispositivo.id]
            client_mqtt.publish(f'{id}/update_data/{dispositivo.id}/{dispositivo.gravidade}/{dispositivo.old_gravidade}/{millis()}',
                                dumps(dispositivo.get_medicoes()))
        else: # caso nao hava broker
            print(f"[{dispositivo.id}] requesting FOG")
            get_fog(dispositivo.id,dispositivo.codigo) # executamos o procedimento para tentar conseguir 1
    except:
        pass