from flask import Flask, jsonify, request
import requests
from time import sleep
from random import choice,choices
from string import hexdigits
import sys
import cache

IP = sys.argv[2] if(len(sys.argv) >3 ) else "26.181.221.42"
PORT = sys.argv[3] if(len(sys.argv) > 3) else sys.argv[2] if(len(sys.argv) > 2) else 17892

id_server= sys.argv[1] if(len(sys.argv) > 1) else''.join(''.join(choices(hexdigits, k = 15)).upper())
app = Flask(__name__)

@app.route('/pacientes/<quantidade>', methods=['GET'])
def api_get(quantidade):
    '''
        Função que retorna um json contendo os {quantidade} pacientes mais graves do sistema
    '''
    quantidade = int(quantidade)
    try:
<<<<<<< HEAD
        if(cache.quantidade < quantidade):
            print('quantidade atualizada')
            cache.quantidade = quantidade
            cache.CACHE[1] = False
            cache.start_thread_atualizadora()
        dados = cache.get_cache(quantidade)
        while(dados == None):
            sleep(.0001)
            dados = cache.get_cache(quantidade)
        a = jsonify({'pacientes':dados})
=======
        pacientes = SortedList(key=lambda x: -x['gravidade'])
        for fog in fogs:
            for paciente in requests.get('http://'+fogs[fog]['href']+f'/pacientes/{quantidade}').json()['pacientes']:
                paciente["href"] = fogs[fog]["href"]
                pacientes.add(paciente)
        a = jsonify({'pacientes':pacientes[:int(quantidade)]})
>>>>>>> ed59cc8197ff598d2ef63b455e217fda923b8530
        #para libera o ajax pegar os dados
        a.headers["Access-Control-Allow-Origin"] = "*"
        return a,200
    except Exception as e:
        print(f'[API] Erro on process request')
        print(e)
        a = jsonify({'pacientes':[]})
        #para libera o ajax pegar os dados
        a.headers["Access-Control-Allow-Origin"] = "*"
        return a,404


@app.route('/fogs', methods=['GET'])
def api_get_fogs():
    '''
        Função que retorna um json contendo os {quantidade} pacientes mais graves do sistema
    '''
    a = jsonify(cache.fogs)
    a.headers["Access-Control-Allow-Origin"] = "*"
    return a,200

@app.route('/add_fogs/<id>', methods=['POST'])
def api_add_fogs(id):
    if(id not in cache.fogs):
        cache.fogs_list_ids.append(id)
        # print(fogs_list_ids)
    cache.fogs[id] = request.json
    cache.fogs[id]['id'] = id
    # print(fogs)
    a = jsonify({})
    a.headers["Access-Control-Allow-Origin"] = "*"
    return a,200
    
@app.route('/get_fog', methods=['POST'])
def api_get_fog():
    try:
        print(request.json)
        if('codigo' in request.json):
            fog = cache.fogs_list_ids[int(request.json['codigo'])%len(cache.fogs_list_ids)]
        else:
            fog = choice(cache.fogs_list_ids)
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
    if(request.method == "POST"):
        if(request.form['href'] == f'{IP}:{PORT}'):
            return 'Para né',400
        requests.post(f'http://{request.form["href"]}/add_fogs/{id_server}',json={'href':f"{IP}:{PORT}",
                                                                'ip':IP,
                                                                "port":PORT,"is_final":False})
        return 'O request foi enviado',200
    elif(request.method == "GET"):
        return '''<form action="/connect_with_upper_layer" method="POST">
                    <p>Digite o ip:port do servidor, sera adicionado http:// no inicio e a rota enviada é /add_fogs/__id_deste_server__</p>
                    <input type="text" name="href">
                    <button style="width: 80px;" type="submit">Enviar</button>
                </form>''',200
    return 'WTF',200

app.run(host = IP, port = PORT, debug = True)
