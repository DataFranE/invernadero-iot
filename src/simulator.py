import time
import random

while True:
	temperatura = round(random.uniform(-5.0, 45.0), 2)
	humedad_relativa = round(random.uniform(0.0, 100.0))
	print(f"La temperatura es {temperatura} °C")
	print(f"La Humedad realativa es de {humedad_relativa} %")
	
	time.sleep(2)


