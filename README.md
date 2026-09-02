# Invernadero IoT - Pipeline de Datos (MVP)

Simulador y sistema de adquisición de datos IoT de extremo a extremo para un invernadero inteligente. Este repositorio documenta la evolución arquitectónica del proyecto, comenzando desde un Producto Mínimo Viable (MVP) monolítico hasta una arquitectura robusta orientada a producción.

> **IMPORTANTE**: Debido a que la numerosa cantidad de variables que es posible monitorear dentro de un invernadero, se eligió al tomate( _Solanum lycopersicum_ ) por ser una de las especies más representativas del cultivo bajo cubierta para de delimitar la simulacion a las variables críticas, **en sus rangos probables no en los óptimos**, para esta especie en particular.
> **Es posible que en fases posteriores de desarrollo se opte por modificar las variables analizadas o l cultivo de referencia**

## Arquitectura actual (MVP)

1. **Simulador (src/simulator.py):** Genera telemetría sintética de variables ambientales clave (temperatura, humedad relativa, humedad del suelo y radiación PAR)respetando los rangos máximos de variación admisibles y emite la carga útil (_payload_) en formato JSON, simulando el comportamiento de sensores físicos.
2. **Broker MQTT (broker.hivemq.com):** Gestiona la publicación/suscripción de mensajes mediante tópicos jerárquicos (invernadero/sensores/GH_TOMATO_01).
3. **Consumidor (src/consumer.py):** Se suscribe al tópico en tiempo real, captura los paquetes de red, valida el formato y deserializa la carga JSON para su posterior procesamiento.

## Tecnología y herramientas

* **Lenguaje:** Python 3.12+
* **Protocolo de comunicación:** MQTT v5 / v3.1.1 (vía paho-mqtt v2.x)
* **Broker de pruebas:** hiveMQ
* **Formato de intercambio:** JSON
* **Control de versiones:** Git

## Estructura de la carga útil
El mensaje transmitido por el simulado a travez del broker y recibido por el consumidor responde a la siguiente estructura tipo, la que debería ver impresa tanto en la terminal del simulador y del consumidor.

## Estructura del proyecto

```text
invernadero-iot/
├── README.md
├── requirements.txt   # Dependencias del proyecto
└── src/
    ├── simulator.py       # Simula y publica lecturas de sensores
    └── consumer.py    # Escucha el broker MQTT, captura, valida y deserializa la carga
```

## Instalación y pruebas

1. Clonar el repositorio y configurar el entorno
git clone [https://github.com/DataFranE/invernadero-iot.git](https://github.com/DataFranE/invernadero-iot.git)
cd invernadero-iot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. Iniciar el consumidor
En una terminal:
python3 src/consumer.py

3. Iniciar el simulador
En otra terminal:
python3 src/simulator.py

**NOTA (Estructura de la carga útil):** El mensaje transmitido por el simulado a través del broker y recibido por el consumidor responde a la siguiente estructura tipo, la que debería ver impresa tanto en la terminal del simulador y del consumidor y le permitirá corroborar el correcto funcionamiento del sistema.

```text
{
  "sensor_id": "GH_TOMATO_01",
  "timestamp": "2026-08-31 20:31:34",
  "status": "active",
  "telemetry": {
    "temperature": 21.45,
    "relative_humidity": 65,
    "soil_humidity": 42,
    "par_radiation": 1200
  }
}
```
## Roadmap de escalibilidad (Próximas mejoras)

- [x] Fase 1: MVP de Telemetría IoT (Completado)
- [ ] Fase 2: Infraestructura Local, Persistencia e Ingesta Eficiente
- [ ] Fase 3: Refactorización POO & Simulación Concurrente
- [ ] Fase 4: Observabilidad y Visualización en Tiempo Real

**NOTA 1:** Se encuentra aun en evaluación la posibilidad de agregar una 5ta fase de desarrollo...
- [ ] Fase 5: Bucle de Control y Actuadores (Advanced AgTech)

**NOTA 2:** En el archivo **ROADMAP.md** puede observar un detalle de los hitos a alcanzar en cada una de las fases de desarrollo

## Contribuciones y aprendizaje

Este es mi primer proyecto técnico, el cual busca aplicar criterio electromecánico y agrónomico en la busqueda de soluciones interdiciplinarias en el campo de los cultivos bajo cubierta mientras aprendo el uso de la tecnología y herramientas usadas para la Ingeniería de datos y el IoT. Son bienvenidas las correcciones y sugerencias.
