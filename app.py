from flask import Flask, render_template, request, redirect, url_for, jsonify
from usuario import usuario
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
import json

sensores_pancs = {
    "sensor1": {"name": "umidade", "value": 0},
    "sensor2": {"name": "temperatura", "value": 0}
}
atuadores_pancs = {
    "atuador1": {"name": "Protecao_Fisica", "value": 0},
}
saude_vacas = {
    "vaca1": {"name": "Mimosa", "value": 0, "peso_historico": []},
}
atuadores_vacas = {
    "atuador1": {"name": "Portao", "value": "FECHADO"},
}

sensores_abelhas = {
    "sensor_umidade": {"name": "Umidade do ar: ", "value": 0},
    "sensor_temperatura_agua": {"name": "Temperatura da água: ", "value": 0},
    "sensor_temperatura_ar": {"name": "Temperatura do ar: ", "value": 0},
    "sensor_nivel_agua": {"name": "Nível da água: ", "value": 0},
    }

sensores_peixes = {
    "Sensor_temp": {"name": "Temperatura da água: ", "value": 0},
    "Sensor_ph": {"name": "PH da água: ", "value": 0},
}

atuadores_abelhas = {
    "bomba": {"name": "Bomba", "value": "LIGADA"},
    "led": {"name": "Led", "value": 0},
}

app = Flask(__name__)

app.register_blueprint(usuario, url_prefix='/')

app.config['MQTT_BROKER_URL'] = 'mqtt-dashboard.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'bagriela'
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5000
app.config['MQTT_TLS_ENABLED'] = False

mqtt_client = Mqtt()
mqtt_client.init_app(app)

# TOPICS
# PANCS
topic_subscribe1 = "pancs/temperatura"
topic_subscribe2 = "pancs/umidade"
topic_subscribe3 = "pancs/atuador"
# VACAS
topic_subscribe4 = "esp32/peso"
topic_subscribe5 = "esp32/servo"
topic_subscribe6 = "esp32/portao"

# ABELHAS
bee_topic1 = "esp32/temperatura_agua"
bee_topic2 = "esp32/umidade_ar"
bee_topic3 = "esp32/temperatura_ar"
bee_topic4 = "esp32/nivel_agua"
bee_topic5 = "esp32/bomba_agua"
bee_topics = [bee_topic1, bee_topic2, bee_topic3, bee_topic4, bee_topic5]
topic_subscribe7 = "esp32/mensagem"

#PEIXES
peixe_topic1 = "esp32/peixes_agua"
peixe_topic2 = "esp32/peixes_ph"
# USER

@app.route("/abelhas")
def abelhas():
    return render_template("abelhas.html", values = sensores_abelhas, atuadores = atuadores_abelhas)

@app.route("/peixes")
def peixes():
    return render_template("peixes.html", values = sensores_peixes)

@app.route("/vacas")
def vacas():
    return render_template("vacas.html", values=saude_vacas, atuadores=atuadores_vacas)

@app.route("/pancs")
def pancs():
    return render_template("pancs.html", values=sensores_pancs, atuadores=atuadores_pancs)

@app.route("/userpage")
def gestaouser():
    return render_template("userpage.html")

# ADMIN

@app.route("/abelhasadm")
def abelhasadm():
    return render_template("abelhasadm.html", values = sensores_abelhas, atuadores = atuadores_abelhas)

@app.route("/peixesadm")
def peixesadm():
    return render_template("peixesadm.html", values = sensores_peixes)

@app.route("/vacasadm")
def vacasadm():
    return render_template("vacasadm.html", values=saude_vacas, atuadores=atuadores_vacas)

@app.route("/pancsadm")
def pancsadm():
    return render_template("pancsadm.html", values=sensores_pancs, atuadores=atuadores_pancs)

@app.route("/admpage")
def admpage():
    return render_template("admpage.html")

@app.route("/add_sensor_atuador_pancs", methods=['GET', 'POST'])
def add_sensor_atuador_pancs():
    if request.method == 'POST':
        item_type = request.form['item_type']
        item_name = request.form['item_name']
        item_value = request.form['item_value']
        if item_type == 'sensor':
            new_sensor_id = f"sensor{len(sensores_pancs)+1}"
            sensores_pancs[new_sensor_id] = {"name": item_name, "value": item_value}
        elif item_type == 'atuador':
            new_atuador_id = f"atuador{len(atuadores_pancs)+1}"
            atuadores_pancs[new_atuador_id] = {"name": item_name, "value": item_value}

    return redirect(url_for('pancsadm'))

@app.route("/del_sensor_pancs", methods=['POST'])
def del_sensor_pancs():
    sensor_name = request.form['sensor_name']
    sensor_key = next((key for key, sensor in sensores_pancs.items() if sensor['name'] == sensor_name), None)
    if sensor_key:
        del sensores_pancs[sensor_key]
    return redirect(url_for('pancsadm'))

@app.route("/del_atuador_pancs", methods=['POST'])
def del_atuador_pancs():
    atuador_name = request.form['atuador_name']
    atuador_key = next((key for key, atuador in atuadores_pancs.items() if atuador['name'] == atuador_name), None)
    if atuador_key:
        del atuadores_pancs[atuador_key]
    return redirect(url_for('pancsadm'))

@app.route('/att_sensor', methods=['GET', 'POST'])
def att_sensor():
    global sensores_pancs, atuadores_pancs
    if request.method == 'POST':
        current_name = request.form['current_sensor']
        new_name = request.form['new_sensor']
        new_value = request.form['configuration']
        if current_name in sensores_pancs:
            sensores_pancs[new_name] = {"name": new_name,"value": new_value}
            if current_name != new_name:
                del sensores_pancs[current_name]
        elif current_name in atuadores_pancs:
            atuadores_pancs[new_name] = {"name": new_name,"value": new_value}
            if current_name != new_name:
                del atuadores_pancs[current_name]
        else:
            return "Sensor ou atuador não encontrado", 404
    else:
        current_name = request.args.get('current_sensor', None)
        new_name = request.args.get('new_sensor', None)
        new_value = request.args.get('configuration', None)
        if current_name and new_name and new_value:
            if current_name in sensores_pancs:
                sensores_pancs[new_name] = {"name": new_name,"value": new_value}
                if current_name != new_name:
                    del sensores_pancs[current_name]
            elif current_name in atuadores_pancs:
                atuadores_pancs[new_name] = {"name": new_name,"value": new_value}
                if current_name != new_name:
                    del atuadores_pancs[current_name]
            else:
                return "Sensor ou atuador não encontrado ou dados inválidos", 404
    return redirect(url_for('pancsadm'))

@app.route("/add_sensor_atuador_abelhas", methods=['GET', 'POST'])
def add_sensor_atuador_abelhas():
    if request.method == 'POST':
        item_type = request.form['item_type']
        item_name = request.form['item_name']
        item_value = request.form['item_value']
        if item_type == 'sensor':
            new_sensor_id = f"sensor{len(sensores_abelhas)+1}"
            sensores_abelhas[new_sensor_id] = {"name": item_name, "value": item_value}
        elif item_type == 'atuador':
            new_atuador_id = f"atuador{len(atuadores_abelhas)+1}"
            atuadores_abelhas[new_atuador_id] = {"name": item_name, "value": item_value}

    return redirect(url_for('abelhasadm'))

@app.route("/del_sensor_abelhas", methods=['POST'])
def del_sensor_abelhas():
    sensor_name = request.form['sensor_name']
    sensor_key = next((key for key, sensor in sensores_abelhas.items() if sensor['name'] == sensor_name), None)
    if sensor_key:
        del sensores_abelhas[sensor_key]
    return redirect(url_for('abelhasadm'))

@app.route("/add_vaca", methods=['POST'])
def add_vaca():
    vaca_name = request.form['vaca_name']
    vaca_peso = request.form['vaca_peso']
    new_vaca_id = f"vaca{len(saude_vacas) + 1}"
    saude_vacas[new_vaca_id] = {
        "name": vaca_name,
        "value": vaca_peso,
        "peso_historico": [vaca_peso]
    }

    return redirect(url_for('vacasadm'))

@app.route("/publish", methods=['POST'])
def control_portao():
    action = request.form['action']
    if action == 'abelhasadm':
        mqtt_client.publish(topic_subscribe7, 'open')
        return redirect(url_for('abelhasadm'))
    elif action == 'abelhas':
        mqtt_client.publish(topic_subscribe7, 'open')
        return redirect(url_for('abelhas'))
    elif action == 'vaca_open_adm':
        mqtt_client.publish(topic_subscribe6, 'ABRIR')
        return redirect(url_for('vacasadm'))
    elif action == 'vaca_close_adm':
        mqtt_client.publish(topic_subscribe6, 'FECHAR')
        return redirect(url_for('vacasadm'))
    elif action == 'vaca_open':
        mqtt_client.publish(topic_subscribe6, 'ABRIR')
        return redirect(url_for('vacas'))
    elif action == 'vaca_close':
        mqtt_client.publish(topic_subscribe6, 'FECHAR')
        return redirect(url_for('vacas'))

    return redirect(url_for('usuario.login'))


# MQTT

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Broker Connected successfully')
        mqtt_client.subscribe(topic_subscribe2)
        mqtt_client.subscribe(topic_subscribe1)
        mqtt_client.subscribe(topic_subscribe3)
        mqtt_client.subscribe(topic_subscribe4)
        mqtt_client.subscribe(topic_subscribe5)
        mqtt_client.subscribe(topic_subscribe6)

        mqtt_client.subscribe(bee_topic1)
        mqtt_client.subscribe(bee_topic2)
        mqtt_client.subscribe(bee_topic3)
        mqtt_client.subscribe(bee_topic4)
        mqtt_client.subscribe(bee_topic5)

        mqtt_client.subscribe(peixe_topic1)
        mqtt_client.subscribe(peixe_topic2)

    else:
        print('Bad connection. Code:', rc)

@mqtt_client.on_disconnect()
def handle_disconnect(client, userdata, rc):
    print("Disconnected from broker")

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    print(message.payload.decode())
    
    if message.topic == topic_subscribe1:
        sensores_pancs["sensor2"]["value"] = message.payload.decode()
    
    if message.topic == topic_subscribe2:
        sensores_pancs["sensor1"]["value"] = message.payload.decode()

    if message.topic == topic_subscribe3:
        atuadores_pancs["atuador1"]["value"] = message.payload.decode()

    if message.topic == topic_subscribe4:
        novo_peso = message.payload.decode()
        saude_vacas["vaca1"]["value"] = novo_peso
        if novo_peso not in saude_vacas["vaca1"]["peso_historico"]:
            saude_vacas["vaca1"]["peso_historico"].append(novo_peso)

    if message.topic == topic_subscribe5:
        atuadores_vacas["atuador1"]["value"] = message.payload.decode()
    
    if message.topic == bee_topic1:
        sensores_abelhas["sensor_temperatura_agua"]["value"] = message.payload.decode()

    if message.topic == bee_topic2:
        sensores_abelhas["sensor_umidade"]["value"] = message.payload.decode()

    if message.topic == bee_topic3:
        sensores_abelhas["sensor_temperatura_ar"]["value"] = message.payload.decode()
        
    if message.topic == bee_topic4:  # Verifique se o tópico correto está sendo usado
        sensores_abelhas["sensor_nivel_agua"]["value"] = message.payload.decode()

    if message.topic == bee_topic5:
        atuadores_abelhas["bomba"]["value"] = message.payload.decode()

    if message.topic == peixe_topic1:
        sensores_peixes["Sensor_temp"]["value"] = message.payload.decode()
    
    if message.topic == peixe_topic2:
        sensores_peixes["Sensor_ph"]["value"] = message.payload.decode()
        
    
     


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
