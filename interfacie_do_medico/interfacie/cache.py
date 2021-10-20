import requests
import time as TiMe___ 
def millis():
    return int(round(TiMe___.time() * 1000000))

SERVER_ADRS='http://26.181.221.42:17892/'

class Cache:
    def __init__(self):
        self.cache={}
    def get(self, key, *args,**kwargs):
        if(not self.cache[key]['verificação'](self.cache[key],args,kwargs)):
            print(f'[CACHE] updating cache of {key}')
            self.cache[key]['set_dados'](self.cache[key],args,kwargs)
        return self.cache[key]['get_dados'](self.cache[key],args,kwargs)
    def add(self,key,verificação,set_dados,get_dados):
        self.cache[key] = {}
        self.cache[key]['verificação'] = verificação
        self.cache[key]['set_dados'] = set_dados
        self.cache[key]['get_dados'] = get_dados

cache = Cache()
#funções cache pra guarda os dados relacionados a fogs ( identificadores, href )
def set_fogs(dic,*args,**kwargs):
    request =requests.get(f"{SERVER_ADRS}fogs")
    #print(request)
    dic['dados'] = request.json()
    dic['last_time'] = millis()
    #funçõesprint(request.json())
def get_fog(dic,*args,**kwargs):
    fog = args[1]['fog']
    if(fog==None or fog=='all_fogs'):
        return [a for a in dic['dados']]
    return dic['dados'][fog]
def fog_verificação(dic,*args,**kwargs):
    if not 'dados' in dic:
        return False
    return  millis() - dic['last_time'] < 1010
cache.add('fogs',fog_verificação,set_fogs,get_fog)

#Funções para cache de pacientes ( lista de pacientes entregues pelas fogs)
def set_pacientes(dic,*args,**kwargs):
    quantidade = args[1]["quantidade"]
    request =requests.get(f"{SERVER_ADRS}pacientes/{quantidade}")
    dic['dados'] = request.json()['pacientes']
    dic['last_time'] = millis()
    dic['quantidade'] = quantidade
def get_pacientes(dic,*args,**kwargs):
    quantidade = args[1]["quantidade"]
    return {'pacientes':dic['dados'][:quantidade]}
def pacientes_verificação(dic,*args,**kwargs):
    quantidade = args[1]["quantidade"]
    if not "dados" in dic:
        return False
    if(quantidade > dic['quantidade']):
        return False
    return millis() - dic['last_time'] < 1010
cache.add('pacientes',pacientes_verificação,set_pacientes,get_pacientes)

# funções para guarda em cache dados de um paciente especifico
def set_paciente(dic,*args,**kwargs):
    id = args[1]['id']
    founded = False
    try:
        fog = args[1]['fog']
        request =requests.get(f"http://{cache.get('fogs',fog=fog)}/paciente/{id}")
        if(request.status_code == 200):
            founded = True
    except KeyError:
        fog = 'all_fogs'
        for a in cache.get('fogs',fog=fog):
            request =requests.get(f"http://{cache.get('fogs',fog=a)}/paciente/{id}")
            if(request.status_code == 200):
                founded = True
    dic[id] = {'exist':founded}
    if(not founded):
        return
    dic[id]['dados'] = {id:request.json()}
    dic[id]['last_time'] = millis()
def get_paciente(dic,*args,**kwargs):
    id = args[1]['id']
    # print(not dic[id]['exist'])
    if( not dic[id]['exist'] ):
        raise(Exception("Paciente nao encontrado"))
    return dic[id]['dados']
def paciente_verificação(dic,*args,**kwargs):
    id = args[1]['id']
    if not id in dic:
        print(f'[CACHE] Device not found in dict {id}')
        return False
    if not "dados" in dic[id]:
        print(f'[CACHE] Device do not have data {id}')
        return False
    if not dic[id]['exist']:
        print(f'[CACHE] Device do not existe {id}')
        return False
    return millis() - dic[id]['last_time'] < 1010
cache.add('paciente',paciente_verificação,set_paciente,get_paciente)

if(__name__ == '__main__'):
    from time import sleep
    print( cache.get('pacientes',quantidade=10))
    print( cache.get('pacientes',quantidade=10))
    sleep(1)
    print( cache.get('pacientes',quantidade=10))
    print( cache.get('paciente',id='B6:F7:FE:FB:4F:4A'))
    print( cache.get('paciente',id='EC:B7:7D:A0:E8:65',fog = 'fogs'))
    print( cache.get('paciente',id='B6:F7:FE:FB:4F:4A',fog = 'fogs'))
    print( cache.get('paciente',id='EC:B7:7D:A0:E8:65',fog = 'fogs'))
    sleep(1)
    print( cache.get('paciente',id='B6:F7:FE:FB:4F:4A',fog = 'fogs'))
