from my_mqtt import My_mqtt
from time import sleep
import threading

requests_to_process = []
fogs = []
with_fog = -1

def __add_fog__(topic_splited,payload,client):
    fogs.appen(topic_splited[2])

def __get_fog__(topic_splited,payload,client):
    if(len(fogs) != 0):
        with_fog += 1
        print(type(client))
#        client.send_message(topic_splited)

def __update_dados__(topic_splited,payload,client):
    print('updating')
    pass

request_actions = {
    'new_fog':__add_fog__,
    'get_fog':__get_fog__,
    'update_pacientes':__update_dados__,
}

def __queue_requests__(client,userdata,msg):
    print(f'queue {msg.topic}')
    requests_to_process.append((client,userdata,msg))

def __request_handler__():
    while True:
        try:
            if(len(requests_to_process) != 0):
                client,userdata,msg=requests_to_process.pop(0)
                print(msg.topic.split('/'))
                topic_splited = msg.topic.split('/')
                if(topic_splited[1] in request_actions ):
                    request_actions[topic_splited[1]](topic_splited,msg.payload,client=client)
                else:
                    print(f'[REQUEST_HANDLER] Erro on process no action found: {topic_splited[1]}')
            else:
                sleep(.05)
        except Exception as e:
            print()
            print(f'[REQUEST_HANDLER] Erro on process {msg}')
            print(f'[REQUEST_HANDLER] Exception: {e}')
            print()

client = My_mqtt()
request_handler_thread = threading.Thread(target=__request_handler__)
request_handler_thread.setDaemon(True)
request_handler_thread.start()
client.conect("26.181.221.42", 1883)
client.client.max_queued_messages_set(1000000)
client.subscribe('main_server/#',__queue_requests__,qos=1)
input()
