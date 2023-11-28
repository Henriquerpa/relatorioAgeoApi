import requests
import json
from datetime import datetime
import socket

def enviar_log_para_api( status, erro,hh):
    # Obter a data e a hora atuais
    data_hora_atual = datetime.now()
    # Formatar a data e a hora no formato desejado
    data_hora_formatada = data_hora_atual.strftime("%Y-%m-%d %H:%M:%S")


    url = "http://192.168.1.252:1338/util-api/log-automacao/"
    data_do_evento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formato da data e hora
    nome_da_maquina = socket.gethostname()

    dados = {
        "nome_da_maquina": nome_da_maquina,
        "nome_da_automacao": 'relatório controle saldo AGEO',
        "status": status,
        "erro": erro,
        "vel_download":'0',
        "vel_upload":'0',
        "cpu":'0',
        "memoria":'0',
        "consumo_energetico":'0',
        "hora_homem_minuto": hh,
        "data_do_evento": data_hora_formatada
    }

    response = requests.post(url, json=dados)
    return response.status_code, response.text

# Exemplo de uso da função
resposta = enviar_log_para_api(status='teste',erro='teste',hh=4)

print(resposta)
