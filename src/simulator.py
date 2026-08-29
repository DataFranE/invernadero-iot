import time
import random


"""
 Módulo básico de simulación de telemetría IoT para el cultivo de tomate (_Solanum lycopersicum_).
Simula las variables consideradas críticas en su rango probable de variación.
 """

print("Inicializando simulación de invernadero")
print("-"*50)
print()

try:
    while True:
        #Simulación de las variables agroclimáticas.
        temperatura = round(random.uniform(-5.0, 45.0), 2)
        humedad_relativa = int(random.uniform(0, 100))
        humedad_suelo = int(random.uniform(0, 100))
        radiacion_par = int(random.uniform(0, 2000))
        #Lectura en pantalla de los resultados de la simulación.
        print(f"La temperatura es {temperatura} °C")
        print(f"La humedad realativa es de {humedad_relativa} %")
        print(f"La humedad del suelo es de {humedad_suelo} %")
        print(f"La radiación fotosinteticamente activa es de {radiacion_par} μmol/m²/s")
        print("-"*50) #Separación visual entre lecturas.
        time.sleep(2)
except KeyboardInterrupt:
    print("\n Simulación finalizada por el usuario.")

