from flask import Flask, jsonify, request
import requests
from random import choice
from sortedcontainers import SortedList

fogs = {}
fogs_list_ids = []
index_next_fog = 0
index = 0
app = Flask(__name__)

@app.route('/pacientes/<quantidade>', methods=['GET'])
def api_get(quantidade):
    '''
        Função que retorna um json contendo os {quantidade} pacientes mais graves do sistema
    '''
    try:
        pacientes = SortedList(key=lambda x: x['gravidade'])
        for a in fogs:
            for b in requests.get('http://'+fogs[a]+f'/pacientes/{quantidade}').json()['pacientes']:
                b["href"] = fogs[a]
                pacientes.add(b)
        a = jsonify({'pacientes':pacientes[::-1][:int(quantidade)]})
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
    a = jsonify(fogs)
    a.headers["Access-Control-Allow-Origin"] = "*"
    return a,200

@app.route('/add_fogs/<id>', methods=['POST'])
def api_add_fogs(id):
    if(id not in fogs):
        fogs_list_ids.append(id)
        # print(fogs_list_ids)
    fogs[id] = request.json
    fogs[id]['id'] = id
    # print(fogs)
    a = jsonify({})
    a.headers["Access-Control-Allow-Origin"] = "*"
    return a,200
    
@app.route('/get_fog', methods=['GET'])
def api_get_fog():
    try:
        fog = choice(fogs_list_ids)
        # index_next_fog+=1
        # if(index_next_fog >=len(fogs_list_ids)):
        #   index_next_fog=0
        a = jsonify(fogs[fog])
        a.headers["Access-Control-Allow-Origin"] = "*"
        return a,200
    except:
        return '',404

app.run(host = "26.181.221.42", port = 17892, debug = True)
    