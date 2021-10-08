from flask import Flask,jsonify
from json import JSONDecodeError
import mqtt_handler
from markupsafe import escape

app = Flask(__name__)

@app.route('/<quantidade>', methods=['GET'])
def api_get(quantidade):
    '''
        Funçao que retorna um json contendo os {quantidade} pacientes mais graves do sistema
    '''
    for a in mqtt_handler.fogs:
        mqtt_handler.publish(f'fogs/{a}/get_pacientes/{quantidade}')
        
app.run(host="0.0.0.0", port=17892)
    