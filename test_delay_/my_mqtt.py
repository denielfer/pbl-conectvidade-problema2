import paho.mqtt.client as mqtt
import threading

class My_mqtt:
    def __init__(self):
        self.client = mqtt.Client()
        self.topics = []

    def subscribe(self, topic, qos = 1):
        '''
            Função que inscreve esse client em um tópico específico
            por default temos qos = 1
            callback deve receber 3 argumentos: client, userdata, msg
            o tópico e o payload estão dentro de msg

            @param topic: str, tópico no qual o client se increverá
            @param qos: int, qualidade da comunicação
        '''
        self.client.subscribe(topic, qos = qos)

    def __on_connect__(self, client, userdata, flags, rc):
        '''
            Função que é chamada quando o client se comunica ao broker mqtt, assim os parâmetros são os requisitados por tal
        '''
        print("[MY_MQTT] Connected with result code " + str(rc))

    def __on_message__(self, client, userdata, msg):
        '''
            Função que é chamada pelo client quando qualquer mensagem de um tópico que ele está inscrito e 
              ela printa o tópico recebido e a mensagem

            Esta função cria uma thread para lidar com cada mensagem que chega passando o callback

        '''
        print(f'[MY_MQTT] Mensage arived but no callback was seted: {msg.topic}: {msg.payload}')

    def conect(self, ip = "26.181.221.42", port = 1883, keep_alive = 60, callback = None):
        '''
            Conecta com {ip}:{porta}, configura on_connect e on_menssage funções e inicia uma thread 
              para o main_loop do mqtt (thread que vai receber as mensagens e passar para 
              a função que lida com todas as mensagens)
        '''
        while True:
            try:
                self.client.on_connect = self.__on_connect__
                if(callback == None):
                    print('[MY_MQTT] Using defalt callback (print)')
                    self.client.on_message = self.__on_message__
                else:
                    print('[MY_MQTT] Using passed callback')
                    self.client.on_message = callback
                self.client.connect(ip, port, keep_alive)
                self.running_thread = threading.Thread(target = self.__main_loop__)
                self.running_thread.setDaemon(True)
                self.running_thread.start()
                break
            except Exception:
                print(f"Não foi possível se conectar com o broker, tentando novamente...")

    def __main_loop__(self):
        '''
            Função que será passada para o thread do main loop
        '''
        self.client.loop_forever()

    def disconect(self):
        '''
            Desconecta do servidor que estava reconectado
        '''
        self.client.disconect()
    
    def publish(self, topic, payload, qos = 1):
        '''
            Publica {payload} no {topic} com o qos informado

            @param topic: str, tópico no qual a mensagem será publicada
            @param payload: object, objeto que será enviado (ele será transformado em bytes, 
                então, para o caso de objeto propriamente dito garantir que essa transformação 
                exista, para dic ele vira uma string que pode ser serializado por um json) 
            @param qos: int, informa a qualidade do serviço
        '''
        self.client.publish(topic,payload,qos)

    def unsubscribe(self, topic):
        '''
            Desinscreve do tópico informado

            @param topic: str, string informando o tópico que quer se desinscrever
        '''
        self.client.unsubscribe(topic)

if(__name__ == '__main__'):
    print("test")
    client = My_mqtt()
    client.conect()

    def __print__(client, userdata, msg):
        print(msg.payload)

    client.subscribe('oi', __print__)
    print("waiting")
    from time import sleep
    sleep(1)
    client.subscribe('tchau', __print__)
    sleep(30)