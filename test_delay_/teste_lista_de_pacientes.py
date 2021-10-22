'''
    Arquivo para testa delay de resposta do servidor conforme mais pacientes sao adicionados

    Neste teste vamos fazer o envio de dados de x pacientes em sequida requisitar ao servidor
        a lista de 1,10,100,250,500,750,1000
    Assim consideraremos este o dalay de resposta do servidor para requestes de n pacientes

    Setup:
        Para este teste funciona é nescessario ter o servidor online e uma fog com identificador 'fog'
'''
import requests
from my_mqtt import My_mqtt
from time import sleep,time
import threading
import pandas as pd
from random import random, choice
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

QUANTIDADE_DE_PACIENTES_ENVIADOS = 0
QUANTIDADE_PACIENTES=[1,10,100,250,500,750,1000]
NUM_TENTATIVAS = 10
my_client = My_mqtt()  #criamos o cliente mqtt
my_client.conect()  # nos conectamos



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


VETOR_DE_DF = []

URL_SEM_ID = f'http://{HOST_TARGET}:{PORT_TARGET}/pacientes/'
print(URL_SEM_ID)
for n,quantidade in enumerate(QUANTIDADE_PACIENTES): # vamos upa 1,10,100,250,500,750,1000 pacientes 
    if QUANTIDADE_DE_PACIENTES_ENVIADOS < quantidade:
        dados = get_data_for_new_device()
        payload = json.dumps(dados)
        my_client.publish(f'fogs/fog/update_data/{quantidade}/{gravidade(dados)}/0/{tempo_de_envio}',payload)
    print(f'Quantitade de pacientes: {quantidade}')
    VETOR_DE_DF[n] = pd.DataFrame(columns=[ a for a in range(NUM_TENTATIVAS)])
    for num_para_pedir in QUANTIDADE_PACIENTES: # a cada um desses valores vamos pedir uma lista com 1,10,100,250,500,750,1000 pacientes
        medições = []    
        num_para_pedir = str(num_para_pedir)
        for medição in range( NUM_TENTATIVAS ): # fazendo 10 tentaticas para cada
            print(f'\tPedindo {num_para_pedir} medição {medição}')
            tempo_de_envio = millis()
            #enquanto nao tiver resposta com o paciente pedimos novamente pelos daods do paciente
            flag = False
            tempo_recebimento = None
            while not flag:
                r = requests.get(URL_SEM_ID+num_para_pedir)
                tempo_recebimento = millis()    
                print('\t\trequesting')
                j = r.json()
                if ('1' in j):
                    flag = j['1'] == medição
            medições.append(tempo_recebimento-tempo_de_envio)
        VETOR_DE_DF[n].loc[num_para_pedir] = medições

import pickle
with open("resultados_com_rios.bin",'wb') as file:
    pickle.dump(VETOR_DE_DF,file)