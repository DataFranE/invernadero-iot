# Invernadero IoT - Pipeline de Datos de Telemetría

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Containers-blue?logo=docker)
![EMQX](https://img.shields.io/badge/MQTT-EMQX_v5-brightgreen?logo=eclipse-mosquitto)
![TimescaleDB](https://img.shields.io/badge/Database-TimescaleDB-orange?logo=postgresql)

Sistema de adquisición y persistencia de telemetría IoT de extremo a extremo para un invernadero inteligente. Este proyecto documenta la evolución arquitectónica de un pipeline de datos AgTech, desde un prototipo de comunicación elemental hasta una infraestructura contenerizada escalable con ingesta en lote y modelado de series temporales.

> [!IMPORTANT]
> Para acotar el alcance de la simulación a métricas agronómicas reales, se toma como referencia de cultivo al tomate (_Solanum lycopersicum_). Las variables monitoreadas se generan dentro de rangos agrofisiológicos probables y de estrés para esta especie.

---

## Arquitectura del Pipeline

El sistema implementa una arquitectura desacoplada basada en eventos, utilizando el patrón **Publicador/Suscriptor (Pub/Sub)** sobre MQTT y persistencia orientada a series temporales en **TimescaleDB**.

```text
┌────────────────────────┐      MQTT (JSON)      ┌────────────────────────┐
│  Simulador de Sensores │ ───────────────────>  │   Broker EMQX Local    │
│   (src/simulator.py)   │  tópico:              │  (Contenedor Docker)   │
└────────────────────────┘  invernadero/sensores/│   Puerto: 1883         │
                                                 └───────────┬────────────┘
                                                             │
                                                    Suscripción MQTT
                                                             │
                                                             v
┌────────────────────────┐   Batch Insert (psycopg3) ┌────────────────────────┐
│      TimescaleDB       │ <──────────────────────── │   Consumidor Python    │
│  (Hypertable/Postgres) │  - Auto-Descubrimiento    │    (src/consumer.py)   │
│  - Compresión nativa   │  - Capa Anti-Corrupción   │  - Buffer con lote 10  │
└────────────────────────┘                           └────────────────────────┘
```

---

## Componentes y Flujo de Datos

1. **Simulador de Telemetría (`src/simulator.py`)**:
   Genera eventos JSON en tiempo real con datos de temperatura, humedad relativa, humedad de suelo y radiación PAR.
2. **Broker MQTT (EMQX v5)**:
   Servidor de mensajería local desplegado en Docker que gestiona el enrutamiento de tópicos bajo la jerarquía `invernadero/sensores/#`.
3. **Consumidor y Capa Anti-Corrupción (`src/consumer.py`)**:
   * **Capa Anti-Corrupción (ACL)**: Sanea, valida y adapta la estructura JSON entrante a tipos de datos compatibles con la base de datos.
   * **Auto-Registro de Dispositivos (Auto-Discovery)**: Registra dinámicamente dispositivos desconocidos en la tabla relacional `dispositivos` sin interrumpir la ingesta.
   * **Procesamiento por Lotes (Batching)**: Acumula registros en memoria y ejecuta inserciones eficientes (`executemany`) al alcanzar el tamaño de lote configurado o un tiempo límite de inactividad.
4. **Base de Datos de Series Temporales (TimescaleDB)**:
   * **Esquema Relacional / Temporal**: Combina metadatos de dispositivos con métricas de sensores.
   * **Desacoplamiento de Latencia**: Registra la marca temporal en origen (`fecha_hora`) junto con el momento exacto de procesamiento (`fecha_hora_ingesta`) para el cálculo de latencias de red.
   * **Compresión Nativa**: Políticas de compresión automatizadas para optimizar el almacenamiento de datos históricos.

---

## Stack Tecnológico

* **Lenguaje de Programación**: Python 3.12+
* **Protocolo de Comunicación**: MQTT v5 / v3.1.1 (`paho-mqtt` v2.x)
* **Broker MQTT**: EMQX Enterprise/Community (vía Docker)
* **Base de Datos**: TimescaleDB / PostgreSQL 16 (vía Docker)
* **Controlador DB**: `psycopg3` (PostgreSQL adapter for Python)
* **Contenerización**: Docker & Docker Compose
* **Control de Versiones**: Git

---

## Estructura del Proyecto

```text
invernadero-iot/
├── docker-compose.yml   # Orquestación de contenedores (EMQX + TimescaleDB)
├── .env.example         # Plantilla de variables de entorno
├── requirements.txt     # Dependencias de Python
├── README.md            # Documentación del proyecto
├── ROADMAP.md           # Hoja de ruta técnica detallada
├── scripts/
│   └── init.db.sql      # DDL de inicialización, Hypertables y compresión
└── src/
    ├── simulator.py     # Simula y publica lecturas de sensores
    └── consumer.py      # Consumidor con Batching, Auto-Descubrimiento y ACL
```

---

## Guía de Instalación y Ejecución

### 1. Clonar el repositorio y configurar el entorno Python

```bash
git clone https://github.com/DataFranE/invernadero-iot.git
cd invernadero-iot

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Desplegar la Infraestructura en Docker

Asegúrate de tener Docker Engine y Docker Compose instalados. Copia la plantilla de variables de entorno y levanta los servicios:

```bash
cp .env.example .env
docker-compose up -d
```

Esto desplegará:
* **EMQX**: Accesible en `localhost:1883` (Dashboard web en `http://localhost:18083`).
* **TimescaleDB**: Accesible en `localhost:5432` con la base de datos `invernadero_db` inicializada.

### 3. Iniciar el Consumidor de Datos

En una terminal conectada al entorno virtual:

```bash
python3 src/consumer.py
```

### 4. Iniciar el Simulador de Telemetría

En otra ventana de terminal:

```bash
python3 src/simulator.py
```

---

## Verificación de Persistencia en TimescaleDB

Para comprobar el flujo completo de ingesta, puedes realizar una consulta SQL directa al contenedor de TimescaleDB:

```bash
docker exec -it timescaledb_invernadero psql -U agtech_user -d invernadero_db -P pager=off -c "
SELECT fecha_hora, fecha_hora_ingesta, dispositivo_id, temperatura, humedad_relativa, humedad_suelo, radiacion_par 
FROM telemetria_sensores 
ORDER BY fecha_hora DESC 
LIMIT 10;
"
```

---

## Hoja de Ruta (Roadmap)

- [x] **Fase 1**: Prototipo Base de Telemetría IoT (Comunicación Pub/Sub vía MQTT).
- [x] **Fase 2**: Infraestructura Local, Persistencia e Ingesta Eficiente (Docker, EMQX, TimescaleDB, Batching & Auto-Descubrimiento).
- [ ] **Fase 3**: Refactorización POO & Simulación Concurrente (Modelos de clases para sensores y nodos concurrentes).
- [ ] **Fase 4**: Observabilidad y Visualización en Tiempo Real (Dashboards en Grafana para métricas de microclima).
- [ ] **Fase 5**: Bucle de Control y Actuadores (Simulación de actuadores y reglas de automatización AgTech).

---

## Contribuciones y Contexto

Este proyecto forma parte de una transición profesional hacia la **Ingeniería de Datos aplicada al sector AgTech**, combinando bases agronómicas y electromecánicas con arquitectura de sistemas distribuidos, procesamiento de series temporales y desarrollo de software en Python.
