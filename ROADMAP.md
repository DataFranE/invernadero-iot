# Roadmap de Evolución Arquitectónica - Invernadero IoT

Este documento detalla los hitos técnicos y la hoja de ruta planificada para transformar el sistema de adquisición de telemetría IoT desde un prototipo funcional hasta una arquitectura de datos robusta, aplicando buenas prácticas y patrones propios de entornos de producción AgTech.

---

## Fase 1: Prototipo de Comunicación en Tiempo Real (Completado)
* **Objetivo:** Establecer la comunicación desacoplada y validada entre emisor y receptor en tiempo real.
* **Hitos:**
  - [x] Desarrollo del simulador monolítico (`src/simulator.py`) que genera lecturas agroclimáticas sintéticas respetando variaciones ambientales continuas.
  - [x] Conexión y publicación en broker público MQTT (HiveMQ) con payload serializado en JSON.
  - [x] Consumidor en tiempo real (`src/consumer.py`) con deserialización, validación de estructura de datos y manejo defensivo de excepciones de red.
  - [x] Versionado inicial en Git y documentación base de arquitectura.

---

## Fase 2: Infraestructura Local, Persistencia e Ingesta Eficiente (Completado)
* **Objetivo:** Contenerizar el stack técnico, migrar a un broker dedicado y asegurar la ingesta de series temporales en base de datos.
* **Hitos:**
  - [x] Creación del entorno contenerizado utilizando Docker y `docker-compose.yml`.
  - [x] Despliegue de broker **EMQX** local para eliminar dependencia de brokers públicos y habilitar monitoreo administrativo.
  - [x] Despliegue de **TimescaleDB** (PostgreSQL) con extensión Time-Series.
  - [x] Diseño del DDL/SQL de inicialización: creación de tablas relacionales, conversión a *Hypertable* e implementación de políticas de **compresión nativa de datos**.
  - [x] Reescritura del consumidor en Python para persistencia en BD utilizando **procesamiento en lote (batch processing)** con `executemany`y patrón de **Auto-Descubrimiento**.

---

## Fase 3: Refactorización POO & Simulación Concurrente
* **Objetivo:** Evolucionar el simulador hacia un modelo de objetos escalable que replique una red de múltiples sensores.
* **Hitos:**
  - [ ] Rediseño Orientado a Objetos: Clase base `Sensor` y subclases específicas (`TemperatureSensor`, `SoilHumiditySensor`, etc.).
  - [ ] Implementación de concurrencia (`threading` o `asyncio`) para ejecutar múltiples hilos/instancias de nodos en paralelo.
  - [ ] Desacoplamiento de tópicos por tipo de métrica o sub-zona del invernadero.
  - [ ] Estandarización de cargas útiles individuales y metadatos de calidad de señal (ej. nivel de batería, RSSI).

---

## Fase 4: Observabilidad y Visualización en Tiempo Real
* **Objetivo:** Exponer la telemetría acumulada mediante dashboards analíticos orientados a la toma de decisiones agronómicas.
* **Hitos:**
  - [ ] Integración de **Grafana** al archivo `docker-compose.yml`.
  - [ ] Configuración de la fuente de datos (*DataSource*) conectada a TimescaleDB.
  - [ ] Creación de paneles dinámicos para visualización de series temporales (temperatura, radiación PAR, déficit de presión de vapor - DPV).
  - [ ] Configuración de reglas de alerta visuales ante umbrales de estrés hídrico o térmico.

---

## Fase 5: Bucle de Control y Actuadores (Advanced AgTech)
* **Objetivo:** Implementar automatización y control en bucle cerrado (*Closed-Loop Control*).
* **Hitos:**
  - [ ] Definición de tópicos de comando de red MQTT (ej. `invernadero/actuadores/riego/comandos`).
  - [ ] Implementación de lógica de decisión en el consumidor para disparar eventos automáticos ante anomalías.
  - [ ] Creación de módulos simuladores de actuadores (electroválvulas de riego, extractores de aire, mallas de sombreo) que responden a los comandos enviados.
