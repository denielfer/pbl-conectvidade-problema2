import requests
from my_mqtt import My_mqtt
from time import sleep,time
import threading
import pandas as pd
from random import random, choice
import json

QUANTIDADE_PACIENTES_MAX=1000
NUM_TENTATIVAS = 30
my_client = My_mqtt()  #criamos o cliente mqtt
my_client.conect()  # nos conectamos

SERVER_IP = "26.181.221.42"
SERVER_PORT = 18931

def millis():
    '''
        Função que retorna os milisegundos do instante atual
            (retorna o datetime time em millis atual)
    '''
    return int(round(time() * 1000))

#Funções para gerar novo paciente (mediçoes de um dispositivo) com dados aleatorios
def get_random_modify(goal, value, step = 5):
    return round(((goal-value) * random()) + (choice([-1, 1])) * (step * random()), 2)
    
def get_data_for_new_device():
    return {
        'Temperatura': get_random_modify(35.3,0,15), #número aleatório entre 0 e 35.3 +ou- 0 a 15
        'Frequencia Respiratoria': get_random_modify(30,0,0), #número aleatório entre 0 e 30
        'Frequencia Cardiaca': get_random_modify(120,0,0), #número aleatório entre 0 e 120
        'Oxigenacao': get_random_modify(100,0,0), #número aleatório entre 0 e 100
        'Max Pressao': get_random_modify(120,0,0), #número aleatório entre 0 e 120
    }
#função para avaliar gravidade do paciente ( conseguir a gravidade do mesmo com base nas medições do dispositivo)
def gravidade(dados:dict):
    return round(((100 - dados["Max Pressao"]) * 3 + 
                    (96 - dados["Oxigenacao"]) * 4 + 
                    (dados["Frequencia Respiratoria"] - 20) * 3 + 
                    (dados["Temperatura"] - 38) * 4 + 
                    (dados["Frequencia Cardiaca"] - 100) * 3),2)

resultados_dataframe = pd.DataFrame(columns=[ a for a in range(NUM_TENTATIVAS)])
URL_SEM_ID = f'http://{SERVER_IP}:{SERVER_PORT}/paciente/'
print(URL_SEM_ID)
for id in range(QUANTIDADE_PACIENTES_MAX):
    id = str(id)
    print(f'on device: {id}')
    medições = []
    for medição in range( NUM_TENTATIVAS ):
        print(f'\ton teste: {medição}')
        dados = get_data_for_new_device()
        dados[1] = medição
        payload = json.dumps(dados)
        #enquanto nao tiver resposta com o paciente pedimos novamente pelos daods do paciente
        flag = False
        tempo_recebimento = None
        tempo_de_envio = millis()
        my_client.publish(f'fog/update_data/{id}/0/0/{tempo_de_envio}',payload)
        while not flag:
            r = requests.get(URL_SEM_ID+id)
            tempo_recebimento = millis()
            print('\t\trequesting')
            j = r.json()
            if ('1' in j):
                flag = j['1'] == medição
        print(f'delay: {tempo_recebimento-tempo_de_envio}')
        medições.append(tempo_recebimento-tempo_de_envio)
    resultados_dataframe.loc[id] = medições

import pickle
with open("resultados_paciente.bin",'wb') as file:
    pickle.dump(resultados_dataframe,file)