from flask import Flask,jsonify
from json import JSONDecoder
import mqtt_hendler
app = Flask(__name__)
@app.route('/paciente/<id>', methods=['GET'])
def api_get_paciente(id:str):
    '''
        Função que retorna uma reposta json contendo os pacientes do sistema
    '''
    print(id)
    for a in mqtt_hendler.prioridades:
        if( id in a):
            return a[id],200 #retornamos os dados em um json com o codigo 200
    return '{"paciente nao achado":"nao achado"}',404


@app.route('/pacientes/<quantidade>', methods=['GET'])
def api_get_pacientes(quantidade:int):
    '''
        Funçao que retorna um json contendo os {quantidade} pacientes mais graves do sistema na seguinte forma:
            {
                'pacientes':[
                    (__id_do_paciente__,__prioridade__),
                    ...
                ]
            }
            no qual __id_do_paciente__ é uma string e __prioridade__ é um number que indica a prioridade do paciente
    '''
    #retorna um dicionario com o campo 'pacientes' que tem uma lista com tamanho solicitado contendo os pacientes mais
    #   graves do sistema na seguinte forma: [__id_do_paciente__,{__dados_do_paciente__}]
    return {'pacientes':mqtt_hendler.get_pacientes_por_prioridade(quantidade)}
for a in range(5000,15500):
    try:    
        app.run(host="0.0.0.0", port=a)
        break
    except Exception:
        print(f'porta {a} ja usada')
    