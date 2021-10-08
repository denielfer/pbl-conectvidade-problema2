import threading
from random import random,choice,choices
from time import sleep

SENSORES_NOMES = ['Temperatura','Frequencia Respiratoria','Oxigenação','Max Preção']

def get_random_modify(goal,value,step =5):
    return round(((goal-value)*random())+(choice([-1,1]))*(step*random()),2)

# DADOS_DEFAULT={
#     'Temperatura':35.3,
#     'Frequencia Respiratoria': 10,
#     'Oxigenação':100,
#     'Max Preção':120,
# }

def get_data_for_new_device():
    return {
    'Temperatura':get_random_modify(35.3,0,15),#numero aleatorio entre 0 e 35.3 +ou- 0 a 15
    'Frequencia Respiratoria': get_random_modify(30,0,0),#numero aleatorio entre 0 e 30
    'Oxigenação':get_random_modify(100,0,0),#numero aleatorio entre 0 e 100
    'Max Preção':get_random_modify(120,0,0),#numero aleatorio entre 0 e 120
    }

def send_function(dispositivo):#id,dados
    print(f'nome: {dispositivo.id}, dados : {dispositivo.medições}')
    return

SEND_FUNCTION_DEFAULT=send_function#para ser facil de troca a função que envia os dados

class Dispositivo:
    #variaveis para seta padraoes de alteração
    GOAL_DADOS_PER_STATE={
        'Grave':{
            'Temperatura':[40,0.5],
            'Frequencia Respiratoria': [25,1],
            'Oxigenação':[25,5],
            'Max Preção':[70,5],
        },
        'Normal':{
            'Temperatura':[36,0.5],
            'Frequencia Respiratoria': [10,1],
            'Oxigenação':[98,.5],
            'Max Preção':[120,5],
        },
    }
    def __init__(self,id,tendencia,send_function = SEND_FUNCTION_DEFAULT,dados_dos_sensores=None):
        self.id = id
        self.send_function = send_function
        self.medições = dados_dos_sensores if dados_dos_sensores else get_data_for_new_device()
        self.semaphare = threading.Semaphore(1)
        self.semaphare.acquire()
        tendencia = int(tendencia)
        ruim_em = choices(SENSORES_NOMES, k=tendencia)
        print(ruim_em)
        self.prioridade = tendencia
        self.tendencia = {}
        for a in SENSORES_NOMES:
            self.tendencia[a] = Dispositivo.GOAL_DADOS_PER_STATE['Grave'][a] if a in ruim_em else Dispositivo.GOAL_DADOS_PER_STATE['Normal'][a]
        self.prioridade_anteiror = 0
        self.prioriade_atual = 0

    def get_medições(self):
        return self.medições

    def update_prioridade_atual(self):
        self.prioridade_anteiror = self.prioriade_atual
        cont = 0
        if (self.medições["Max Preção"]<100):
            cont+=1
        if(self.medições["Oxigenação"]<96):
            cont+=1
        if(self.medições["Frequencia Respiratoria"]>20):
            cont+=1
        if(self.medições["Temperatura"]>38.0):
            cont+=1
        self.prioriade_atual = cont

    def altera_medições(self,dados_dos_sensore):
        self.medições= dados_dos_sensore
    def init_thread(self):
        thread = threading.Thread(target=self.__thread_function__,)
        thread.setDaemon(True)
        thread.start()
    def __update_data__(self):
        for b in self.tendencia:
            self.medições[b]= round( self.medições[b]+get_random_modify(self.tendencia[b][0],self.medições[b],self.tendencia[b][1]),2)
        self.update_prioridade_atual()
    def __thread_function__(self):
        while True:
            if(self.semaphare.acquire(False)):
                break
            self.__update_data__()
            self.send_function(self)
            sleep(2*random())
    def stop(self):
        self.semaphare.release()


if __name__ == "__main__":
    d = Dispositivo('daniel',"Prioridade_4")
    d.init_thread()
    input()