import json
import logging
import paho.mqtt.client as mqtt
import os
import psycopg
import time
from dotenv import load_dotenv
from datetime import datetime, timezone

"""
Consumidor MQTT para la telemetría del Invernadero IoT.
-Se suscribe a los tópicos MQTT del broker para recibir las lecturas enviadas por los sensores.
-Deserializa las cargas útiles JSON y procesar los eventos entrantes adaptándolos al esquema DDL de TimescaleDB.
-Registra automáticamente nuevos dispositivos en la tabla 'dispositivos'.
-Inserta las métricas almacenadas por lotes (Batching) y metadatos dinámicos JSONB.
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

#Configuraciín de Batching.
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))
BATCH_TIMEOUT_SECONDS = float(os.getenv("BATCH_TIMEOUT_SECONDS", 5.0))

data_buffer = []
last_flush_time = time.time()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


def get_db_connection():
    """Establece conexión sincrónica con PostgreSQL/TimescaleDB usando psycopg3. """
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


def sanitize_and_parse(payload: dict) -> tuple:
    """
    Saneamiento y desacoplamiento de la carga útil JSON (Capa Anti-Corrupción / ACL).
    Devuelve una tupla ordenada compatible con el esquema de 'telemetria_sensores'.
    """
    sensor_id = payload.get("sensor_id")
    telemetry = payload.get("telemetry", {})

    if not sensor_id or not isinstance(telemetry, dict):
        logging.warning("Payload ignorado por formato inválido: %s", payload)
        return None

    raw_timestamp = payload.get("timestamp")
    try:
        origin_ts = datetime.strptime(raw_timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        origin_ts = datetime.now(timezone.utc)

    ingested_at = datetime.now(timezone.utc)

    estado = payload.get("status","active")

    temp = telemetry.get("temperature")
    rel_hum = telemetry.get("relative_humidity")
    soil_hum = telemetry.get("soil_humidity")
    par_rad = telemetry.get("par_radiation")

    datos_adicionales = {}
    
    for key, value in telemetry.items():
        if key not in ["temperature", "relative_humidity", "soil_humidity", "par_radiation"]:
            datos_adicionales[key] = value

    return (
        origin_ts,
        ingested_at,
        sensor_id,
        estado,
        temp,
        rel_hum,
        soil_hum,
        par_rad,
        json.dumps(datos_adicionales)
    )


def flush_buffer_to_db():
    """Registra dispositivos desconocidos (Auto-Descubrimiento) y liquida el buffer en TimescaleDB. """
    global data_buffer, last_flush_time

    if not data_buffer:
        return

    #Extrae IDs de dispositivos únicos en el lote.
    dispositivos_unicos = list(set(record[2] for record in data_buffer))

    query_dispositivo = """ 
        INSERT INTO dispositivos (dispositivo_id, nombre, ubicacion_nave, tipo_cultivo)
        VALUES (%s, %s, 'Nave_AutoDescubrimiento', 'Desconocido / Auto-Registrado')
        ON CONFLICT (dispositivo_id) DO NOTHING;
    """

    query = """
        INSERT INTO telemetria_sensores
        (fecha_hora, fecha_hora_ingesta, dispositivo_id, estado, temperatura, humedad_relativa, humedad_suelo, radiacion_par, datos_adicionales)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """


    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                #Registro automático de nuevos dispositivos en la tabla relacional.
                for dev_id in dispositivos_unicos:
                    cur.execute(query_dispositivo, (dev_id, f"Nodo {dev_id}"))

                #Inserción de métricas por lotes en la hypertabla de series temporales.
                cur.executemany(query, data_buffer)

            conn.commit()
            logging.info("BATCH FLUSH: Insertados %d regsitros en TimescaleDB con éxito.", len(data_buffer))
            data_buffer.clear()
            last_flush_time = time.time()
        except psycopg.Error as e:
            logging.error("Error al ejecutar batch insert em DB: %s",e)
            conn.rollback()
        finally:
            conn.close()
    else:
        logging.error("No se pudo vaciar el buffer: Sin conexión a la base de datos.")

#Callback de control de conexión y recepción de mensaje.
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logging.info("Conectado al broker EMQX local(%s:%d)", BROKER, PORT)
        client.subscribe(TOPIC)
    else:
        logging.error("Error de conexión al broker MQTT. Código de retorno: %s", rc)

def on_message(client, userdata, msg):
    global data_buffer, last_flush_time

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        record = sanitize_and_parse(payload)

        if record:
            data_buffer.append(record)
            logging.info("Mensaje acumulado en buffer [%d/%d] - Nodo: %s", len(data_buffer), BATCH_SIZE, record[2])

        current_time = time.time()
        if len(data_buffer) >= BATCH_SIZE or (current_time - last_flush_time) >= BATCH_TIMEOUT_SECONDS:
            flush_buffer_to_db()

    except json.JSONDecodeError:
        logging.error("Error al deserealizar el JSON desde el tópico: %s", msg.topic)
    except Exception:
        logging.exception("Excepción no esperada al procesar mensaje")


def main():
    logging.info("Iniciando Consumidor con Batching (Lote: %d | Timeout: %.1fs)", BATCH_SIZE, BATCH_TIMEOUT_SECONDS)

    #Conexión del cliente.
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        logging.info("Deteniendo el consumidor debido a una interrupción del usuario...")
        if data_buffer:
            logging.info("Guardando registros pendientes en el buffer antes del cierre...")
            flush_buffer_to_db()
    finally:
        client.disconnect()
        logging.info("Consumidor detenido.")

if __name__ == "__main__":
    main()
