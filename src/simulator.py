import time
import datetime
import random
import json
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion as mqtt_version

"""
 Módulo básico de simulación de telemetría IoT para el cultivo de tomate (_Solanum lycopersicum_).
Simula las variables consideradas críticas en su rango probable de variación.
 """
#Configuración de la red MQTT.
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "invernadero/sensores/GH_TOMATO_01"

#Callbaks de control de conexión y publicación.(Firma API v2)
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Conectado con éxito al broker MQTT: {BROKER}.")
    else:
        print("Error de conexión. Código de retorno: {rc}.")

def on_publish(client, userdata, mid, reason_code=None, properties=None):
    pass #Confirmación de la recepción del paquete por parte del BROKER.

#Conexión del cliente.
client = mqtt.Client(callback_api_version=mqtt_version.VERSION2)
client.on_connect = on_connect
client.on_publish = on_publish

client.connect(BROKER, PORT, 60)
client.loop_start()
print("Conectando al servidor... Espere.")
time.sleep(1) 

print("Inicializando simulación de invernadero, para detener precione [Ctrl + C]")
print("-"*50)
print()

try:
    while True:
        #Simulación de las variables agroclimáticas.
        simulated_data = {
            "sensor_id": "GH_TOMATO_01",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active",
            "telemetry": {
                "temperature": round(random.uniform(-5.0, 45.0), 2),
                "relative_humidity": random.randint(0, 100),
                "soil_humidity": random.randint(0, 100),
                "par_radiation": random.randint(0, 2000),
                }                  
        }
        
        payload = json.dumps(simulated_data)
        client.publish(TOPIC, payload)

        print(f"Se envió el payload JSON simulado por el sensor: \n {payload}")
        print("-"*50) #Separación visual entre lecturas.

        time.sleep(2)
        
except KeyboardInterrupt:
    print("\nSimulación finalizada por el usuario.")
finally:
    client.loop_stop()
    client.disconnect()
    print("Se cerró la conección con el servidor.")
