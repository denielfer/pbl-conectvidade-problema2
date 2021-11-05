from flask import Flask, jsonify, request
import mqtt_handler
import requests
app = Flask(__name__)

@app.route('/paciente/<id>', methods=['GET'])
def api_get_paciente(id:str):
    '''
        Função que retorna uma reposta json contendo os pacientes do sistema

        @param id:string, identificador do paciente desejado no sistema
    '''
#    print(id)
    if(id in mqtt_handler.pacientes_dados):
        a = jsonify(mqtt_handler.pacientes_dados[id])
        a.headers["Access-Control-Allow-Origin"] = "*"
        return a, 200 #retornamos os dados em um json com o codigo 200
    a = jsonify({"status": f"Paciente {id} não achado"})
    a.headers["Access-Control-Allow-Origin"] = "*"
    return a, 404


@app.route('/pacientes/<quantidade>', methods=['GET'])
def api_get_pacientes(quantidade:int):
    '''
        Função que retorna um json contendo os {quantidade} pacientes mais graves do sistema na seguinte forma:
            {
                'pacientes':[
                    (__id_do_paciente__,__prioridade__),
                    ...
                ]
            }
            no qual __id_do_paciente__ é uma string e __prioridade__ é um number que indica a prioridade do paciente
        
        @param quantidade: int, contendo a quantidade de pacientes desejado
    '''
    #retorna um dicionário com o campo 'pacientes' que tem uma lista com o tamanho solicitado contendo os pacientes mais
    #graves do sistema na seguinte forma: [__id_do_paciente__, {__dados_do_paciente__}]
    #print(quantidade)
    a = mqtt_handler.get_pacientes_por_prioridade(quantidade)
    a = jsonify({'pacientes': a})
    a.headers["Access-Control-Allow-Origin"] = "*"
    return a

@app.route('/connect_with_upper_layer', methods=['GET', 'POST'])
def connect_with_upper_layer():
    '''
        Rota para fazer a conexão entre servidores, adicionando servidores como fogs de outros servidores (para possibilitar pesquisas recursivas de um servidor para outro)
    '''
    if(request.method == "POST"): #se for um post, tentamos fazer o request
        if(request.form['href'] == f'{mqtt_handler.HOST}:{mqtt_handler.PORT_API}'): # caso seja um post sem o 'href' tenha os dados deste servidor geraria uma recurção infinita nas buscas entao bloqueamos que o servidor possar ser adicionado como fog nele mesmo
            return 'Para né',400
        #caso contrário, fazemos um request de adição de fog para o link passado
        requests.post(f'http://{request.form["href"]}/add_fogs/{mqtt_handler.fog_name}',
                                                                json={'href':f"{mqtt_handler.HOST}:{mqtt_handler.PORT_API}",
                                                                'ip':f'{mqtt_handler.HOST}',
                                                                "port":mqtt_handler.PORT_BROKER,"is_final":True},timeout=2)
        return 'O request foi enviado', 200 #informamos q o request foi feito
    elif(request.method == "GET"): #caso seja um get retornamos uma página com um form para ser digitado o '{ip}:{porta}' para onde será feito o request da rota com POST, e um botão para fazer o POST
        return '''<form action="/connect_with_upper_layer" method="POST">
                    <p>Digite o IP:port do servidor, será adicionado http:// no início e a rota enviada é /add_fogs/__id_deste_server__</p>
                    <input type="text" name="href">
                    <button style="width: 80px;" type="submit">Enviar</button>
                </form>''', 200
    return 'WTF', 404 #Essa linha não deve ser alcançada nunca

app.run(host = mqtt_handler.HOST, port = mqtt_handler.PORT_API)