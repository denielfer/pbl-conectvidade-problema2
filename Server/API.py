from flask import Flask, jsonify, request
import requests
from time import sleep
from random import choice,choices
from string import hexdigits
import sys
import cache

IP =  "26.181.221.42"
PORT = sys.argv[2] if(len(sys.argv) > 2) else 17892

id_server = sys.argv[1] if(len(sys.argv) > 1) else''.join(''.join(choices(hexdigits, k = 15)).upper())
app = Flask(__name__)

@app.route('/pacientes/<quantidade>', methods=['GET'])
def api_get(quantidade):
    '''
        Função que retorna um json contendo os {quantidade} pacientes mais graves do sistema na seguinte forma:
            {
                'pacientes':[
                    (__id_do_paciente__, __prioridade__),
                    ...
                ]
            }
            no qual __id_do_paciente__ é uma string e __prioridade__ é um número que indica a prioridade do paciente
        
        @param quantidade: int, contendo a quantidade de pacientes desejado
    '''
    quantidade = int(quantidade)
    try:
        if(cache.quantidade < quantidade):
            cache.quantidade = quantidade
            cache.CACHE[1] = False
            cache.start_thread_atualizadora()
            print('quantidade atualizada')

        dados = cache.get_cache(quantidade)

        while(dados == None):
            sleep(.0001)
            dados = cache.get_cache(quantidade)

        a = jsonify({'pacientes':dados})
        #libera a entrada para o AJAX pegar os dados
        a.headers["Access-Control-Allow-Origin"] = "*"
        return a, 200
    except Exception as e:
        print(f'[API] Erro on process request')
        print(e)
        a = jsonify({'pacientes':[]})
        #libera a entrada para o AJAX pegar os dados
        a.headers["Access-Control-Allow-Origin"] = "*"
        return a, 404


@app.route('/fogs', methods=['GET'])
def api_get_fogs():
    '''
        Função que retorna um json contendo os dados das fogs presentes no sistema
    '''
    a = jsonify(cache.fogs)
    a.headers["Access-Control-Allow-Origin"] = "*"
    return a,200

@app.route('/add_fogs/<id>', methods=['POST'])
def api_add_fogs(id):
    '''  
        Esta função lida com a roda de adição de fogs no sistema. Assim esta função salva os dados enviados pelas fogs no sistema
    '''
    if(id not in cache.fogs): # caso o id desta fog nao esteja no sistema ainda vamos adicionar ela na lista de fogs
        cache.fogs_list_ids.append(id)
        # print(fogs_list_ids)
    cache.fogs[id] = request.json # salvamos os dados de pacientes, caso ja existam dados eles sao sobreescritos
    cache.fogs[id]['id'] = id #colocamos o id desta fog nos dados salvos tambem
    # print(fogs)
    a = jsonify({})
    a.headers["Access-Control-Allow-Origin"] = "*"
    return a,200
    
@app.route('/get_fog', methods=['POST'])
def api_get_fog():
    '''  
        Função que lida com a rota de escolher uma fog para um dado dispositivo com base nos dados enviados no json
    '''
    try:
        print(request.json)
        if('codigo' in request.json):# se tiver codigo nos dados enviados
            fog = cache.fogs_list_ids[int(request.json['codigo'])%len(cache.fogs_list_ids)] # usamos esse codigo como index para escolher a fog
        else:# caso contrario
            fog = choice(cache.fogs_list_ids)# enviamos uma fog aleatoria
            # index_next_fog+=1
            # if(index_next_fog >=len(fogs_list_ids)):
            #   index_next_fog=0
        a = jsonify(cache.fogs[fog])
        a.headers["Access-Control-Allow-Origin"] = "*"
        return a,200
    except:
        return '',404

@app.route('/connect_with_upper_layer', methods=['GET','POST'])
def connect_with_upper_layer():
    '''
        Rota para fazer a conecção entre servidores, adicionando servidores como fogs de outros servidores ( para possibilitar pesquisas recursivas de um servidor para outro )
    '''
    if(request.method == "POST"):# se for um post tentamos fazer o request
        if(request.form['href'] == f'{IP}:{PORT}'): # caso seja um post sem o 'href' tenha os dados deste servidor geraria uma recurção infinita nas buscas entao bloqueamos que o servidor possar ser adicionado como fog nele mesmo
            return 'Para né',400
        #caso contrario fazemos um request de adicção de fog para o link passado
        requests.post(f'http://{request.form["href"]}/add_fogs/{id_server}',json={'href':f"{IP}:{PORT}",
                                                                'ip':IP,
                                                                "port":PORT,"is_final":False})
        return 'O request foi enviado',200# informamos q o request foi fito
    elif(request.method == "GET"):# caso seja um get retornamos uma pagian com um form para ser digitado o '{ip}:{porta}' para onde sera feito o request da rota com POST, e um butao para fazer o POST
        return '''<form action="/connect_with_upper_layer" method="POST">
                    <p>Digite o ip:port do servidor, sera adicionado http:// no inicio e a rota enviada é /add_fogs/__id_deste_server__</p>
                    <input type="text" name="href">
                    <button style="width: 80px;" type="submit">Enviar</button>
                </form>''',200
    return 'WTF',404 # Essa linha nao deve ser alcançada nunca

app.run(host = IP, port = PORT, debug = True)
