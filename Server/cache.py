import requests
from sortedcontainers import SortedList
from threading import Thread, Semaphore
from time import sleep

fogs = {}
fogs_list_ids = []
CACHE = [[],False]
quantidade = 10

def atualizar_cache(quantidade_t):
    while True:
        pacientes = SortedList(key=lambda x: -x['gravidade'])
        try:
            for fog in fogs:
                try: #casso de timeout
                    if(quantidade_t != quantidade):
                        # print("quantidade diferente da desta thread")
                        break
                    for paciente in requests.get('http://'+fogs[fog]['href']+f'/pacientes/{quantidade_t}', timeout=2).json()['pacientes']:
                        paciente["href"] = fogs[fog]['href']
                        pacientes.add(paciente)
                except Exception as e:
                    pass
        except Exception as e: # essa exceção acontece caso uma fog seja adicionada durante o loop entao reiniciamos este loop
            continue
        if(quantidade_t == quantidade):
            CACHE[0] = pacientes
            CACHE[1] = True
        else: # caso quantidade seja atualizada esta thread é encerada pois outra ja foi criada para atualizar com a quantidade certa
            break
        sleep(.5)
    # print("thread encerada")

def start_thread_atualizadora():
    thread = Thread(target=atualizar_cache, args=(quantidade,))
    thread.setDaemon(True)
    thread.start()

def get_cache(quantidade_r):
    return CACHE[0][:quantidade_r] if CACHE[1] else None

start_thread_atualizadora()