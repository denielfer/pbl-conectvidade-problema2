import requests
from my_mqtt import My_mqtt
from time import sleep,time
import threading
import pandas as pd
from random import random, choice
import json

QUANTIDADE_DE_PACIENTES_ENVIADOS = 0
QUANTIDADE_PACIENTES_REQUISITADOS_NA_INTERFACIE=[1,10,100,250,500,750,1000]
NUM_TENTATIVAS = 30
my_client = My_mqtt()  #criamos o cliente mqtt
my_client.conect()  # nos conectamos

SERVER_IP = "26.181.221.42"
SERVER_PORT = 17892

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

VETOR_DE_DF = []
URL_SEM_ID = f'http://{SERVER_IP}:{SERVER_PORT}/pacientes/'
print(URL_SEM_ID)
for n,quantidade in enumerate(QUANTIDADE_PACIENTES_REQUISITADOS_NA_INTERFACIE): # vamos upa 1,10,100,250,500,750,1000 pacientes 
    while QUANTIDADE_DE_PACIENTES_ENVIADOS < quantidade: # enviamos paciente ate estarmos em cada uma das quantidades
        dados = get_data_for_new_device()
        payload = json.dumps(dados)
        my_client.publish(f'fog/update_data/{str(quantidade)}/{gravidade(dados)}/0/{millis()}',payload)
        QUANTIDADE_DE_PACIENTES_ENVIADOS+=1
    print(f'Quantitade de pacientes: {quantidade}')
    VETOR_DE_DF.append(pd.DataFrame(columns=[ a for a in range(NUM_TENTATIVAS)]))
    for num_para_pedir in QUANTIDADE_PACIENTES_REQUISITADOS_NA_INTERFACIE: # a cada um desses valores vamos pedir uma lista com 1,10,100,250,500,750,1000 pacientes
        medições = []    
        num_para_pedir_s = str(num_para_pedir)
        for medição in range( NUM_TENTATIVAS ): # fazendo 10 tentaticas para cada
            print(f'\tPedindo {num_para_pedir_s} medição {medição}')
            #enquanto nao tiver resposta com o paciente pedimos novamente pelos daods do paciente
            flag = False
            tempo_recebimento = None
            tempo_de_envio = millis()
            while not flag:
                r = requests.get(URL_SEM_ID+num_para_pedir_s)
                tempo_recebimento = millis()    
                print('\t\trequesting')
                j = r.json()
                if ('1' in j):
                    flag = j['1'] == min([QUANTIDADE_DE_PACIENTES_ENVIADOS,num_para_pedir])
            medições.append(tempo_recebimento-tempo_de_envio)
        VETOR_DE_DF[n].loc[num_para_pedir] = medições

import pickle
with open("resultados_pacientes.bin",'wb') as file:
    pickle.dump(VETOR_DE_DF,file)