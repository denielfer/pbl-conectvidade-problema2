from my_mqtt import My_mqtt
from time import sleep
import threading

requests_to_process = []
fogs = {}
fog_order = []
with_fog = -1

#
#main_server/new_fog/__id_fog__
#main_server/get_fog/__id_despositivo__
#

def __add_fog__(topic_splited, payload, client):
    try:
        if(topic_splited[2] not in fogs):
            fog_order.append(topic_splited[2])
    #    print(fogs)
            print(f'[MQTT_HANDLER] Fog added {topic_splited[2]}')
        else:
            print(f'[MQTT_HANDLER] Fog already exist {topic_splited[2]}')
        fogs[topic_splited[2]] = str(payload)[2:-1] # salvamos o url informado (caso já tenha algum path, atualizamos ele)
    except Exception as e:
            print(f'[MQTT_HANDLER] Not able to get path from {payload}')
 
def __get_fog__(topic_splited, payload, client):
    global with_fog
    if(len(fog_order) != 0):
        with_fog += 1
        if(with_fog == len(fog_order)):
            with_fog = -1
#        print(type(client))
        print(f'[MQTT_HANDLER] passing device:{topic_splited[2]} to {fog_order[with_fog]}')
        client.publish(f'dispositivos/set_fog/{topic_splited[2]}', f'{fog_order[with_fog]}')
#        client.send_message(topic_splited)

def __update_dados__(topic_splited, payload, client):
    print(f'updating: {payload}')
    pass

request_actions = {
    'new_fog': __add_fog__,
    'get_fog': __get_fog__,
    'update_pacientes': __update_dados__
}

def __queue_requests__(client, userdata, msg):
#    print(f'queue {msg.topic}')
    requests_to_process.append((client, userdata, msg))

def __request_handler__():
    while True:
        try:
            if(len(requests_to_process) != 0):
                client, userdata, msg = requests_to_process.pop(0)
#                print(msg.topic.split('/'))
                topic_splited = msg.topic.split('/')
                if(topic_splited[1] in request_actions):
                    request_actions[topic_splited[1]](topic_splited, msg.payload, client = client)
                else:
                    print(f'[MQTT_HANDLER] Erro on process {msg.topic}:{msg.payload} Exception: {e}')
            else:
                sleep(.05)
        except Exception as e:
            print(f'[MQTT_HANDLER] Erro on process {msg}')
            print(f'[MQTT_HANDLER] Exception: {e}')

client = My_mqtt()
request_handler_thread = threading.Thread(target = __request_handler__)
request_handler_thread.setDaemon(True)
request_handler_thread.start()
client.conect("26.181.221.42", 1883, callback = __queue_requests__)
client.client.max_queued_messages_set(1000000)
client.subscribe('main_server/#', qos = 1)

def publish(topic, mensagem):
    client.publish(topic, mensagem)

if(__name__ == '__main__'):
    input()