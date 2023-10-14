import requests
import smtplib
import pytz
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask,jsonify,request
from datetime import datetime


app = Flask(__name__)

# Configurações do servidor SMTP do Gmail
smtp_server = "smtp.gmail.com: 587"
smtp_port = 587

# Configurações de autenticação
smtp_username = "mfl.emocionometro@gmail.com"
smtp_password = "ihtekcmxtnxszihd"

firebase_url = "https://emocionometer02-default-rtdb.firebaseio.com/"
firebase_db_path = "Respostas"


respostas = requests.get(f"{firebase_url}{firebase_db_path}.json").json()



#Consultar todas as respostas
@app.route('/', methods=['GET'])
def obter_respostas():
    return jsonify(respostas)

#Consultar respostas por [id]
@app.route('/Respostas/<id>', methods=['GET'])
def obter_resposta_por_id(id):
    for resposta in respostas:
        if resposta.get('id') == id:
            return jsonify(resposta)

#Editar
@app.route('/Respostas/<int:id>', methods=['PUT'])
def editar_resposta_por_id(id):
    resposta_alterado = request.get_json()
    for indice,resposta in enumerate(respostas):
        if resposta.get('id') == id:
            respostas[indice].update(resposta_alterado)
            return jsonify(respostas[indice])
        
#Criar
@app.route('/Respostas', methods=['POST'])
def incluir_nova_resposta():
    nova_resposta = request.get_json() # Substitua pelos dados que deseja postar
    tz_brasilia = pytz.timezone('America/Sao_Paulo')

    registro = nova_resposta["Registro"]
    equipamento = nova_resposta["Equipamento"]
    local = nova_resposta["Local"]
    agora = datetime.now(tz_brasilia)
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")
    resposta = "Estou bem" if nova_resposta["Resposta"] == "3" else ("Estou preocupado" if nova_resposta["Resposta"] == "2" else "Não estou bem")
    
    # Adiciona os campos abaixo ao json a ser enviado
    nova_resposta["id_lanc"] = agora.microsecond
    nova_resposta["Resposta"] = resposta
    nova_resposta["Data"] = data
    nova_resposta["Hora"] = hora

    # Realiza a solicitação POST para escrever dados
    response = requests.post(f"{firebase_url}{firebase_db_path}.json?auth=AfhEvdfvDTz196KrTiR6VbecylUyezgPApgq6FCi", json=nova_resposta)

    #Se a resposta for diferente de "Estou bem", faz o envio de e-mail
    if resposta!="Estou bem":
        # Criar uma mensagem de e-mail
        mensagem = MIMEMultipart()
        mensagem["From"] = smtp_username
        destinatarios = ["wiliancalmeida01@gmail.com","wilianalmeida@grupomaringa.com.br"]
        mensagem["To"] = ", ".join(destinatarios)
        mensagem["Subject"] = "Alerta - Emocionômetro"

        # Corpo do e-mail
        mensagem.add_header('Content-Type', 'text/html')
        corpo = "Segue para informação que o colaborador de registro "+registro+" informou: "+resposta+""" 
        Equipamento: """+equipamento+"""
        Local: """+local+"""
        """

        # Anexar corpo do e-mail
        mensagem.attach(MIMEText(corpo, "plain"))
        
        # Configurar a conexão SMTP
        server = smtplib.SMTP(smtp_server)
        server.starttls()  # Usando TLS (ou SSL para 465)
        server.login(smtp_username, smtp_password)

        # Enviar o e-mail
        server.sendmail(smtp_username, [mensagem["To"]], mensagem.as_string().encode('utf-8'))
        print("Email enviado")
        # Fechar a conexão
        server.quit()

    return jsonify(respostas)

#Excluir
@app.route('/Respostas/<int:id>', methods=['DELETE'])
def excluir_resposta(id):
    for indice, resposta in enumerate(respostas):
        if resposta.get('id') == id:
            del respostas[indice]

            return jsonify(respostas)


#app.run(port=5000, host='localhost',debug=True)