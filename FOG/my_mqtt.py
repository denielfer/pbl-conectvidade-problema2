import paho.mqtt.client as mqtt
import threading

class My_mqtt:
    def __init__(self):
        self.mqtt_actions= {}
        self.client = mqtt.Client()
        self.topics = []
    def subscribe(self,topic,callback,qos=1):
        '''
            Função que inscreve esse cliente em um topico especifico, chamando a função callback para processar a mensagem quando chegar
            por default temos qos como 1
            callback deve receber 3 argumentos: client,userdata,msg
            o topico e o payload estao dentro de msg

            @param topic: str, topico no qual o cliente se increvera
            @param callback: function, função que lida com a mensagem no {topic}
            @param qos: int, qualidade da comunicação
        '''
        self.mqtt_actions[topic] = callback
        self.client.subscribe(topic,qos=qos)

    def __on_connect__(self,client, userdata, flags, rc):
        '''
            Função que é chamada quando o cliente se comunica ao broker mqtt assim os parametros sao os requisitados la
        '''
        print("Connected with result code "+str(rc))

    def __on_message__(self,client, userdata, msg):
        '''
            Função que é chamada pelo cliente quando qualquer mensagem de um topico que ele esta inscrito chega
            os parametros sao so requeridos pela função que o chamada

            Esta função cria uma thread para lidar com cada mensagem que chega passando o callback

        '''
        if( msg.topic in self.mqtt_actions):
            t = threading.Thread(target=self.mqtt_actions[msg.topic],args=(client,userdata,msg))
            t.setDaemon(True)
            t.start()
        else:
            print(f'Mensage arived but no callback was seted: {msg.topic}: {msg.payload}')
            print(msg.topic+" "+str(msg.payload))
    def conect(self,ip="localhost",port=1883,keep_alive=60):
        '''
            conecta com {ip}:{porta}, configura on_connect e on_menssage funções e inicia uma thread 
              para o main_loop do mqtt ( thread que vai receber as mensagens e passa para 
              amensagem que lida com todas as mensagens)
        '''
        self.client.on_connect = self.__on_connect__
        self.client.on_message = self.__on_message__
        self.client.connect(ip, port, keep_alive)
        self.running_thread = threading.Thread(target=self.__main_loop__)
        self.running_thread.setDaemon(True)
        self.running_thread.start()

    def __main_loop__(self):
        '''
            FUnção que sera passada para o thread do main loop
        '''
        self.client.loop_forever()

    def disconect(self):
        '''
            disconecta do servidor que estava reconectado
        '''
        self.client.disconect()
    
    def publish(self,topic,payload,qos=1):
        '''
            publica {payload} no {topic} com o qos informado

            @param topic: str, topico no qual a mensagem sera publicada
            @param payload: object, obejeto que sera enviado ( ele sera transformado em bytes, 
                entao para o caso de objeto propriamente dito garantir que essa transformação 
                exista, para dic ele vira uma string que pode ser serealizado por um json) 
            @param qos: int, informa a qualidade do serviço
        '''
        self.client.publish(topic,payload,qos)

    def unsubscribe(self, topic):
        '''
            Desiscreve do topico informado

            @param topic: str, string informando o topico que quer se desiscrever
        '''
        if(topic in self.mqtt_actions):
            self.client.unsubscribe(topic)
            del(self.mqtt_actions[topic])
        else:
            print(f"Nao esta inscrito em {topic}")

if(__name__ == '__main__'):
    print("test")
    client = My_mqtt()
    client.conect('26.181.221.42')

    def __print__(client, userdata, msg):
        print(msg.payload)

    client.subscribe('oi',__print__)
    print("waiting")
    from time import sleep
    sleep(1)
    client.subscribe('tchau',__print__)
    sleep(30)