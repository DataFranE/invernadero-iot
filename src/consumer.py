import json
import logging
import paho.mqtt.client as mqtt
import os
import psycopg
from dotenv import load_dotenv
from datetime import datetime, timezone

"""
Consumidor MQTT para la telemetría del Invernadero IoT.
Se suscribe a los tópicos MQTT del broker para recibir las lecturas enviadas por los sensores, deserializar las cargas útiles JSON y procesar los eventos entrantes.
"""
#Lectura de variables de entorno y configuración del broker y base de datos.
load_dotenv()

BROKER = os.getenv("MQTT_HOST", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC = os.getenv("MQTT_TOPIC", "invernadero/sensores/#")

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))
DB_NAME = os.getenv("POSTGRES_DB", "invernadero_db")
DB_USER = os.getenv("POSTGRES_USER", "agtech_user")
DB_PASS = os.getenv("POSTGRES_PASS")

if not DB_PASS:
   raise ValueError("CRÍTICO: La variable de entorno POSTGRES_PASS no está configurada.")

logging.basicConfig(
    level=logging.DEBUG, #Nota personal: DEBUG para poder ver salidas en terminal, recordar investigar método dinámico...
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

#Conexión a la base de datos.
def get_db_connection():
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg.Error as e:
        logging.exception("Error al intentar conectar con TimescaleDB: %s", e)
        return None

#Callback de control de conexión y recepción de mensaje.
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logging.info("Conectado al broker EMQX local(%s:%d)", BROKER, PORT)
        client.subscribe(TOPIC)
        logging.info("Suscripto al patrón de tópicos: %s", TOPIC)
        print("-"*50)
    else:
        logging.error("Error de conexión al broker MQTT. Código de retorno: %s", rc)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        sensor_id = payload.get("sensor_id", "DESCONOCIDO")

        received_at_utc = datetime.now(timezone.utc) #Marca de tiempo del momento de consumo.

        logging.info("Mensaje recibido desde el tópico '%s' [Sensor: %s]", msg.topic, sensor_id)
        logging.debug("Payload completo: %s | Recibido en UTC: %s", payload, received_at_utc)
        print("-"*50)

    except json.JSONDecodeError:
        logging.error("Error al deserealizar el JSON desde el tópico: %s", msg.topic)
    except Exception:
        logging.exception("Excepción no esperada al procesar mensaje")


def main():
    logging.info("Verificando conexión con la base de datos TimecaleDB...")
    db_conn = get_db_connection()
    if db_conn:
        logging.info("Conexión exitosa a la base de datos '%s' en %s:%d", DB_NAME, DB_HOST, DB_PORT)
        db_conn.close()
    else:
        logging.warning("No se pudo establecer la conexión con la base de datos.")


    #Conexión del cliente.
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        logging.info("Iniciando servicio Consumidor de Telemetría...")
        client.connect(BROKER, PORT, 60)
        print("... Presionar [Ctrl + C] para detener.")
        client.loop_forever()
    except KeyboardInterrupt:
        logging.info("Deteniendo el consumidor debido a una interrupción del usuario...")
    finally:
        client.disconnect()
        logging.info("Conexión con el broker MQTT cerrada.")

if __name__ == "__main__":
    main()
