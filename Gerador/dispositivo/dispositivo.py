import threading
from random import random, choice, choices
from time import sleep
# dados que serao enviados
SENSORES_NOMES = ['Temperatura', 'Frequencia Respiratoria', 'Frequencia Cardiaca', 'Oxigenacao', 'Max Pressao']

def get_random_modify(goal, value, step = 5):
    '''
        Função que retorna um modificador aleatorio tentando deixa os dados proximos do objetivo ( <goal> )
            tentando deixa estes dados semi-aleatorios
        
        @param goal: int, inteiro representando o numero objetvio que os dados devem esta orbitando envolta
        @param value: int, inteiro que indica o valor atual que sera modificado pelo retorno
        @param step:int, o qual agrecivo sera o fator aleatorio que sera adicionado no modificador
        @return: int, inteiro sendo um modificador aleatorio para sera adicionado ao <value> deixando os dados 
            orbitando entorno do <goal>, deixando dados semi-aleatorios
    '''
    return round(((goal-value) * random()) + (choice([-1, 1])) * (step * random()), 2)
    
def get_data_for_new_device():
    '''
        Função que retorna um dicionario com dados gerados de forma aleatorio
    '''
    return {
    'Temperatura': get_random_modify(35.3,0,15), #número aleatório entre 0 e 35.3 +ou- 0 a 15
    'Frequencia Respiratoria': get_random_modify(30,0,0), #número aleatório entre 0 e 30
    'Frequencia Cardiaca': get_random_modify(120,0,0), #número aleatório entre 0 e 120
    'Oxigenacao': get_random_modify(100,0,0), #número aleatório entre 0 e 100
    'Max Pressao': get_random_modify(120,0,0), #número aleatório entre 0 e 120
    }

def send_function(dispositivo): #id, dados
    ''' 
        função placeholder para função de envio de dados que printa os dados
    '''
    print(f'nome: {dispositivo.id}, dados: {dispositivo.medicoes}')

SEND_FUNCTION_DEFAULT = send_function #para ser fácil de trocar a função, default, que envia os dados

class Dispositivo:
    #variáveis para setar padrões de alteração, padroes ( setup de constantes ) para geração dos dados semi-aleatorios
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
    quantidade_dispositivos = 0 # variavel de classe para indicar a quantiadde de dispositivos no sistema, esta sera usada para dar um codigo unico a cada dispositivo
    def __init__(self, id, tendencia, send_function = SEND_FUNCTION_DEFAULT, dados_dos_sensores = None):
        '''
            Função de inicialização de dispositivo
        '''
        self.codigo = Dispositivo.quantidade_dispositivos
        Dispositivo.quantidade_dispositivos+=1
        self.id = id
        self.send_function = send_function
        self.medicoes = dados_dos_sensores if dados_dos_sensores else get_data_for_new_device()
        self.semaphare = threading.Semaphore(1)
        self.semaphare.acquire()
        self.tendencia = Dispositivo.GOAL_DADOS_PER_STATE[tendencia]
        self.gravidade = -300
        self.update_gravidade()

    def get_medicoes(self):
        ''' 
            Retorna as medições salvas neste dispositivo

            @return: dict, contendo os dados das medições deste dispositivo
        '''
        return self.medicoes

    def update_gravidade(self):
        '''
            Função que atualiza a gravidade salva no dispositivo
        '''
        self.old_gravidade = self.gravidade
        self.gravidade = round(((100 - self.medicoes["Max Pressao"]) * 3 + 
                          (96 - self.medicoes["Oxigenacao"]) * 4 + 
                          (self.medicoes["Frequencia Respiratoria"] - 20) * 3 + 
                          (self.medicoes["Temperatura"] - 38) * 4 + 
                          (self.medicoes["Frequencia Cardiaca"] - 100) * 3)+150,2)

    def altera_medicoes(self, dados_dos_sensores):
        '''
            Função que salva <dados_dos_sensores> no dispositivo

            @param dados_dos_sens: dict, dicionario de medições que sera salvo no dispositivo
        '''
        self.medicoes = dados_dos_sensores

    def init_thread(self):
        '''
            Inicia a thread de simulação do dispositivo
        '''
        thread = threading.Thread(target = self.__thread_function__)
        thread.setDaemon(True)
        thread.start()

    def __update_data__(self):
        '''
            Função que atuliza os dados das medições e a gravidade
        '''
        for b in self.tendencia:
            self.medicoes[b] = round(self.medicoes[b] + get_random_modify(self.tendencia[b][0], self.medicoes[b], self.tendencia[b][1]), 2)
        self.update_gravidade()

    def __thread_function__(self):
        '''
            Função da thread de simulação do dispositivo
        '''
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