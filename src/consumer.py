import json
import paho.mqtt.client as mqtt

"""
Consumidor MQTT para la telemetría del Invernadero IoT.
Se suscribe a los tópicos MQTT del broker para recibir las lecturas enviadas por los sensores, deserializar las cargas útiles JSON y procesar los eventos entrantes.
"""

#Configuración de la red MQTT
BROKER = "localhost"
PORT = 1883
TOPIC = "invernadero/sensores/#"

#Callback de control de conexión y recepción de mensaje.
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Conectado al broker MQTT: {BROKER}.\nSuscribiendo al tópico.")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Se recibió el payload JSON:\n{payload}")
        print("-"*50)
    except Exception as e:
        print(f"Debido al error: {e} no se pudo procesar el mensaje.")

#Conexión del cliente.
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message


client.connect(BROKER, PORT, 60)

try:
    print("Escuchando los mensajes. Presione [Ctrl + C] para detener.")
    client.loop_forever()
except KeyboardInterrupt:
    print("\nDeteniendo el consumidor.")
    client.disconnect()

