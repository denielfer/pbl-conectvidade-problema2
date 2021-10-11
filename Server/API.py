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
    try:
        pacientes = SortedList(key=lambda x: x[1])
        for a in mqtt_handler.fogs:
            pacientes.update(requests.get('http://'+mqtt_handler.fogs[a]+f'/pacientes/{quantidade}').json()['pacientes'])
        print(f'[API] resquest 200')
        return {'pacientes':pacientes[::-1][:int(quantidade)]},200
    except:
        print(f'[API] Erro on process request')
        return {'pacientes':[]},200
        
app.run(host="0.0.0.0", port=17892)
    