from flask import Flask,jsonify
from json import JSONDecodeError
import mqtt_handler
import requests
from sortedcontainers import SortedList

app = Flask(__name__)

@app.route('/<quantidade>', methods=['GET'])
def api_get(quantidade):
    '''
        Funçao que retorna um json contendo os {quantidade} pacientes mais graves do sistema
    '''
    pacientes = SortedList(key = lambda x: x[1])
    for a in mqtt_handler.fogs:
        print(quantidade)
        print()
        print()
        print()
        print()
        print()
        print()
        pacientes.update(requests.get(mqtt_handler.fogs[a]+f'/pacientes/{quantidade}').json['pacientes'])
    return {'pacientes':pacientes.sort(key=lambda x: x[1],reverse=True)[:quantidade]}
        
app.run(host="0.0.0.0", port=17892)
    