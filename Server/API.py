from flask import Flask,jsonify
from json import JSONDecodeError
import mqtt_handler
import requests
from sortedcontainers import SortedList

app = Flask(__name__)

@app.route('/pacientes/<quantidade>', methods=['GET'])
def api_get(quantidade):
    '''
        Função que retorna um json contendo os {quantidade} pacientes mais graves do sistema
    '''
    # try:
    pacientes = SortedList(key=lambda x: x['gravidade'])
    for a in mqtt_handler.fogs:
        for b in requests.get('http://'+mqtt_handler.fogs[a]+f'/pacientes/{quantidade}').json()['pacientes']:
            b["href"] = 'http://'+mqtt_handler.fogs[a]+f'/paciente/{b["id"]}'
            pacientes.add(b)
    print(f'[API] resquest 200')
    a = jsonify({'pacientes':pacientes[::-1][:int(quantidade)]})
    a.headers["Access-Control-Allow-Origin"] = "*"
    return a,200
    # except Exception as e:
    #    print(f'[API] Erro on process request')
    #     print(e)
    #     a = jsonify({'pacientes':[]})
    #     a.headers["Access-Control-Allow-Origin"] = "*"
    #     return a,200
        
app.run(host="26.181.221.42", port=17892,debug=True)
    