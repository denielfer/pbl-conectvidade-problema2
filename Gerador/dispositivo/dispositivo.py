import threading
from random import random, choice, choices
from time import sleep

SENSORES_NOMES = ['Temperatura', 'Frequencia Respiratoria', 'Frequencia Cardiaca', 'Oxigenacao', 'Max Pressao']

def get_random_modify(goal, value, step = 5):
    return round(((goal-value) * random()) + (choice([-1, 1])) * (step * random()), 2)

# DADOS_DEFAULT={
#     'Temperatura':35.3,
#     'Frequencia Respiratoria': 10,
#     'Frequencia Cardiaca': 100,
#     'Oxigenacao':100,
#     'Max Pressao':120,
# }

def get_data_for_new_device():
    return {
    'Temperatura': get_random_modify(35.3,0,15), #número aleatório entre 0 e 35.3 +ou- 0 a 15
    'Frequencia Respiratoria': get_random_modify(30,0,0), #número aleatório entre 0 e 30
    'Frequencia Cardiaca': get_random_modify(120,0,0), #número aleatório entre 0 e 120
    'Oxigenacao': get_random_modify(100,0,0), #número aleatório entre 0 e 100
    'Max Pressao': get_random_modify(120,0,0), #número aleatório entre 0 e 120
    }

def send_function(dispositivo): #id, dados
    print(f'nome: {dispositivo.id}, dados: {dispositivo.medicoes}')
    return

SEND_FUNCTION_DEFAULT = send_function #para ser fácil de trocar a função que envia os dados

class Dispositivo:
    #variáveis para setar padrões de alteração
    GOAL_DADOS_PER_STATE={
        'Grave': {
            'Temperatura': [40,0.5],
            'Frequencia Respiratoria': [25,1],
            'Frequencia Cardiaca': [115,3],
            'Oxigenacao': [25,5],
            'Max Pressao': [70,5],
        },
        'Normal': {
            'Temperatura': [36,0.5],
            'Frequencia Respiratoria': [10,1],
            'Frequencia Cardiaca': [100,3],
            'Oxigenacao': [98,.5],
            'Max Pressao': [120,5],
        }
    }

    def __init__(self, id, tendencia, send_function = SEND_FUNCTION_DEFAULT, dados_dos_sensores = None):
        self.id = id
        self.send_function = send_function
        self.medicoes = dados_dos_sensores if dados_dos_sensores else get_data_for_new_device()
        self.semaphare = threading.Semaphore(1)
        self.semaphare.acquire()
        self.tendencia = Dispositivo.GOAL_DADOS_PER_STATE[tendencia]
        self.gravidade = -300
        self.update_gravidade()

    def get_medicoes(self):
        return self.medicoes

    def update_gravidade(self):
        self.old_gravidade = self.gravidade
        self.gravidade = round(((100 - self.medicoes["Max Pressao"]) * 3 + 
                          (96 - self.medicoes["Oxigenacao"]) * 4 + 
                          (self.medicoes["Frequencia Respiratoria"] - 20) * 3 + 
                          (self.medicoes["Temperatura"] - 38) * 4 + 
                          (self.medicoes["Frequencia Cardiaca"] - 100) * 3),2)

    def altera_medicoes(self, dados_dos_sensores):
        self.medicoes = dados_dos_sensores

    def init_thread(self):
        thread = threading.Thread(target = self.__thread_function__)
        thread.setDaemon(True)
        thread.start()

    def __update_data__(self):
        for b in self.tendencia:
            self.medicoes[b] = round(self.medicoes[b] + get_random_modify(self.tendencia[b][0], self.medicoes[b], self.tendencia[b][1]), 2)
        self.update_gravidade()

    def __thread_function__(self):
        while True:
            if(self.semaphare.acquire(False)):
                break
            self.__update_data__()
            self.send_function(self)
            sleep(2 * random())

    def stop(self):
        self.semaphare.release()


if __name__ == "__main__":
    d = Dispositivo('daniel', "Prioridade_4")
    d.init_thread()
    input()