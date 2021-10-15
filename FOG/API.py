from flask import Flask, jsonify
from json import JSONDecoder
import mqtt_handler
app = Flask(__name__)

@app.route('/paciente/<id>', methods=['GET'])
def api_get_paciente(id:str):
    '''
        Função que retorna uma reposta json contendo os pacientes do sistema
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
    '''
    #retorna um dicionario com o campo 'pacientes' que tem uma lista com o tamanho solicitado contendo os pacientes mais
    #   graves do sistema na seguinte forma: [__id_do_paciente__, {__dados_do_paciente__}]
    print(quantidade)
    a = mqtt_handler.get_pacientes_por_prioridade(quantidade)
    a = jsonify({'pacientes': a})
    a.headers["Access-Control-Allow-Origin"] = "*"
    return a

app.run(host = mqtt_handler.HOST, port = mqtt_handler.PORT)