## Descrição ##
Projeto para a 2° PBL da diciplina TEC502 - MI - CONCORRÊNCIA E CONECTIVIDADE. A descrição do problema pode ser vista [aqui]()

Para solução deste problema foi desenvolvido um sistema descentralizado, com a ultilização de micro-sistemas, para possibilitar uma melhor escalabilidade e desempenho. Assim o sistema é composto de 2 sub-sistemas principais e 1 sub-sistema auxiliar ( para testes ) que podem ser executados de forma distribuida, sendo nescessario altera apenas algumas configurações.

---

##Sistema##

Como dito o sistema esta dividido em 3 partes: Servidor ( ou Servidor Principal ), FOG ( ou Servidor Intermediario ) e Gerador ( o que fara a simulação dos dispositivos ).
Assim temos Dispositivos, que são simulados no gerador, se comunicam com o Servidor pedindo uma FOG para se conectar, passando a enviar os dados das medições simuadas para esta.
O Servidor principal funciona como uma API que conecta Dispositivos e FOGs, bem como disponibiliza alguns dados, sendo possivel requisitar os N pacientes mais graves do sistema.
A Fog é onde os dados são guardados, Dispositivos fazem o envio constante destes dados atravez do MQTT, e estes sao disponibilidados atravez de uma API, na qual é possivel pedir os N pacientes mais graves ( presentes nesta FOG ) e os dados de um paciente especifico. 

---

## Configuração ##

Para ultilização deste sistema é nescessario ter o [Python](https://www.python.org/) instalado em todas as maquinas que serao usadas, bem como acesso a um broker MQTT para ultilização de cada fog ( existe suporte para 2 FOGs no mesmo broker, porém por requesito de sistema é usado um broker unico para cada FOG assim os dispositivos se conectariam na FOG mais proxima a eles, assim cada fog teria um broker proprio ), sendo ultilizado por nois servidor MQTT local com o [mosquitto](https://mosquitto.org/).
Tabem para os testes locais foi usado o [Radmin](https://www.radmin-vpn.com/br/) para simulação de uma rede naqual os testes foram feitos durante o desenvolvimento.
Assim para configurar o sistema é feito o seguinte passo a passo:

#Iniciar o Servidor#

Para iniciarmos a execução do sistema é executado o sub-sistema do [Servidor](https://github.com/denielfer/pbl-conectvidade-problema2/tree/main/Server) ( estando na sua pasta na maquina na qual ele sera executado ), para tal precisamos ter um ambiente virtual com os requirements instalados para tal criamos um ambiente virtual python com o comando:

			python -m venv env

e em seguida instalamos os requisitos atravez de:

			python -m pip install -r requirements.txt

por fim precisamos configurar ip e porta no qual a API sera executada para tal pode ser feito alterando o ip e porta deixados como default no arquivo [API.py](https://github.com/denielfer/pbl-conectvidade-problema2/blob/main/Server/API.py) nas linhas 9 e 10, confome imagem

![Alt Text](imagens/server_ip_porta.png)

podendo passar a porta na qual a API sera executada como parametro conforme de arquivo:

				python API.py __identificador_do_servidor__ __porta_para_API__


no qual '__identificador_do_servidor__' e '__porta_para_API__' sao parametros opicionais ( que caso desejado passar ) o primeiro sera usado como identificador do servidor ( uma string unica para indicar este servidor no sistema ) e o segundo sera usado como a porta na qual a API sera executada.

#Iniciar FOG ( ou Servidor Intermediario )#

Com o Servidor em funcionamento executamos quantas FOGs forem desejadas, para tal, na maquina que sera executada a FOG iniciamos o MQTT que sera usado ( caso seja usado um MQTT local ), e entao na pasta da [FOG](https://github.com/denielfer/pbl-conectvidade-problema2/tree/main/FOG) configuraremos no arquivo [mqtt_handler.py](https://github.com/denielfer/pbl-conectvidade-problema2/blob/main/FOG/mqtt_handler.py) o endereço do Servidor que esta fog se conectara, ip e porta da api e porta do broker ( esta solução usa um broker local entao é assumido que o broker esta na mesma maquina que esta FOG sera executada entao o IP da API e o IP do broker são 1 so no sistema ) ( que se encontram nas linhas 7 a 10 ). Comforme a imagem:

![Alt Text](imagens/FOG.png)

Entao na pasta da [FOG](https://github.com/denielfer/pbl-conectvidade-problema2/tree/main/FOG) vamos criar um ambiente virtual python e instala os requesitos atraves de:

			python -m venv env
			python -m pip install -r requirements.txt

Por fim podemos iniciar o sub-sistema usando:

			python API.py

#Iniciar Gerador#

Para iniciarmos o gerador é nescessario no arquivo [request_handler.py](https://github.com/denielfer/pbl-conectvidade-problema2/blob/main/Gerador/dispositivo/request_handler.py) na linhas 39 substituir o link presente na request POST pelo link do seu servidor, confome a imagem:

![Alt Text](imagens/gerador.png)

Entao na pasta do [Gerador](https://github.com/denielfer/pbl-conectvidade-problema2/tree/main/Gerador) vamos criar um ambiente virtual python e instala os requesitos executando:

			python -m venv env
			python -m pip install -r requirements.txt

Por fim podemos iniciar o sub-sistema usando:

			python manage.py runserver

---

## Observações ##

Para usar o [mosquitto](https://mosquitto.org/) como broker é nescessario usar um arquivo de configuração. Nos arquivos de configuração usados as configurações usadas são:
'''
	auto_id_prefix auto-
	max_inflight_messages 0
	max_keepalive 65535
	max_queued_bytes 0
	max_queued_messages 10000000
	listener __port__ __ip__
	allow_anonymous true
'''
no qual __port__ e __ip__ sao substituidos respectivamente pela porta na qual o broker estara operando e o ip da maquina no qual o broker esta sendo executado.
