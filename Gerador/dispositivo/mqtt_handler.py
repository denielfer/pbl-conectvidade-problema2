
from .my_mqtt import My_mqtt
from json import dumps
from .dispositivo import Dispositivo

# Rotas usadas:
#
# 'dispositivos/set_fog/__id_device__' -> no pacote deve ter uma string contendo a rota que sera usada
#
#
#
#

dispositivo_fog = {}

def __dispositivo_mqtt_handler__(client, userdata, msg):
    print(f'mensage arived {msg.topic}')
    topic_splited=msg.topic.split('/')
    if(topic_splited[1] == 'set_fog'):
        dispositivo_fog[topic_splited[2]] = str(msg.payload)[2:-1]

def start_mqtt():
    global client_mqtt
    client_mqtt = My_mqtt()
    client_mqtt.conect(callback = __dispositivo_mqtt_handler__)
    client_mqtt.subscribe('dispositivos/#')

def get_fog(id_dispositivo):
    client_mqtt.publish(f'main_server/get_fog/{id_dispositivo}', '')

def update_paciente_function(dispositivo:Dispositivo):
    if(dispositivo.id in dispositivo_fog):
        fog = dispositivo_fog[dispositivo.id]
        client_mqtt.publish(f'fogs/{fog}/update_data/{dispositivo.id}/{dispositivo.gravidade}/{dispositivo.old_gravidade}',
                            dumps(dispositivo.get_medicoes()))
    else:
        get_fog(dispositivo.id)
        print(f"[{dispositivo.id}] requesting FOG")
