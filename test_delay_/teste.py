'''
    Arquivo para testa delay do update de dados do dispositivo na fog

    Neste teste vamos fazer o envio de dados e em sequida requisitar os dados deste paciente
        continuamente ate a fog responder com ele.
    Assim consideraremos este o dalay de ponta a ponta do sistema, pois este estaria fazendo 
        o request com o menor delay do envio de dados do paciente.

    Setup:
        Para este teste funciona é nescessario uma fog com identificador: 'fog'
'''

import requests
from my_mqtt import My_mqtt
from time import sleep,time
import threading
import pandas as pd
import json

#definimos aqui o ip e porta da api da fog
HOST_TARGET = '26.181.221.42'
PORT_TARGET = 17892

def millis():
    '''
        Função que retorna os milisegundos do instante atual
            (retorna o datetime time em millis atual)
    '''
    return int(round(time() * 1000))

NUM_DISPOSITIVOS = 1000
NUM_TENTATIVAS = 10
my_client = My_mqtt()  #criamos o cliente mqtt
my_client.conect()  # nos conectamos

resultados_dataframe = pd.DataFrame(columns=[ a for a in range(NUM_TENTATIVAS)])

URL_SEM_ID = f'http://{HOST_TARGET}:{PORT_TARGET}/paciente/'
print(URL_SEM_ID)
for id in range(NUM_DISPOSITIVOS):
    id = str(id)
    print(f'on device: {id}')
    medições = []
    for medição in range( NUM_TENTATIVAS ):
        print(f'\ton teste: {medição}')
        tempo_de_envio = millis()
        payload = json.dumps({1:medição})
        my_client.publish(f'fogs/fog/update_data/{id}/0/0/{tempo_de_envio}',payload)
        #enquanto nao tiver resposta com o paciente pedimos novamente pelos daods do paciente
        flag = False
        tempo_recebimento = None
        while not flag:
            r = requests.get(URL_SEM_ID+id)
            tempo_recebimento = millis()    
            print('\t\trequesting')
            j = r.json()
            if ('1' in j):
                flag = j['1'] == medição
        medições.append(tempo_recebimento-tempo_de_envio)
    resultados_dataframe.loc[id] = medições

import pickle
with open("resultados_com_rios.bin",'wb') as file:
    pickle.dump(resultados_dataframe,file)