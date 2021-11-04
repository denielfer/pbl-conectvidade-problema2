import requests
from sortedcontainers import SortedList
from threading import Thread, Semaphore
from time import sleep

fogs = {}
fogs_list_ids = []
CACHE = [[], False]
quantidade = 10

def atualizar_cache(quantidade_t):
    '''  
        Função que atualiza os dados presentes na cache

        @param quantidade_t:int, quantidade de pacientes que será requisitada a cada fog
    '''
    while True:
        try: #esse try é para o caso de adição de fogs enquanto itera pela lista, o que geraria um erro
            pacientes = SortedList(key=lambda x: -x['gravidade']) #lista ordenada de pacientes
            for fog in fogs: #para cada fog
                try: #caso de timeout
                    if(quantidade_t != quantidade): #se a quantidade mudou, nós paramos o loop de requisições
                        # print("quantidade diferente da desta thread")
                        break
                    #para cada paciente na resposta das requisições das fogs, são pedidos os dados com limite de 2 segundos para timeout (Para milhões de dados esse tempo deveria ser aumentado)
                    for paciente in requests.get('http://'+ fogs[fog]['href'] + f'/pacientes/{quantidade_t}', timeout = 2).json()['pacientes']:
                        paciente["href"] = fogs[fog]['href'] #adicionamos referência da fog nos dados
                        pacientes.add(paciente) #e adicionamos ele na lista ordenada
                except Exception as e: #caso ocora exception de timeout vamos para a próxima
                    pass
            if(quantidade_t == quantidade): #se a quantidade de pacientes buscados for igual ao máximo de pacientes que o sistema quer, salvamos os dados na cache
                CACHE[0] = pacientes #salvamos os dados
                CACHE[1] = True #dizemos que o conteúdo da cache é válido
            else: #caso a quantidade seja atualizada, esta thread é encerada pois outra já foi criada para atualizar com a quantidade certa
                break
            sleep(.5)
        except Exception as e: #então caso o erro de iteração aconteça nos recomeçamos as requisições
            continue
    # print("thread encerada")

def start_thread_atualizadora():
    ''' 
        Inicia uma thread que executa a função de atualizar os dados da cache, passando a quantidade que deve ser pedida
            para as fogs
    '''
    thread = Thread(target = atualizar_cache, args = (quantidade,))
    thread.setDaemon(True)
    thread.start()

def get_cache(quantidade):
    ''' 
        Esta função retorna os <quantidade> pacientes mais graves do sistema

        @param quantidade: int, sendo o inteiro representando a quantidade de pacientes desejada
        @return list, retorna uma lista de pacientes com tamanho <quantidade>
    '''
    return CACHE[0][:quantidade] if CACHE[1] else None

start_thread_atualizadora()