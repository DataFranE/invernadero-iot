import time
import datetime
import random
import json


"""
 Módulo básico de simulación de telemetría IoT para el cultivo de tomate (_Solanum lycopersicum_).
Simula las variables consideradas críticas en su rango probable de variación.
 """

print("Inicializando simulación de invernadero.")
print("-"*50)
print()

try:
    while True:
        #Simulación de las variables agroclimáticas.
        lectura_simulada = {
            "sensor_id": "sensor_simulado",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "activo",
            "telemetry": {
                "temperatura": round(random.uniform(-5.0, 45.0), 2),
                "humedad_relativa": int(random.uniform(0, 100)),
                "humedad_suelo": int(random.uniform(0, 100)),
                "radiacion_par": int(random.uniform(0, 2000)),
                }                  
        }
        
        payload = json.dumps(lectura_simulada)

        print(f"Payload JSON simulado por el sensor: \n {payload}")
        print("-"*50) #Separación visual entre lecturas.

        time.sleep(2)
except KeyboardInterrupt:
    print("\nSimulación finalizada por el usuario.")

