/*
SCRIPT DE INICIALIZACIÓN DE BASE DE DATOS DEL INVERNADERO IOT
TimescaleDB / PostgreSQL
*/


CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE; --Activación de timescaleDB en la instancia de PostrgresSQL


-- Tabla relacional para separar los metadatos de los valores dinamicos

CREATE TABLE IF NOT EXISTS dispositivos(
    dispositivo_id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion_nave VARCHAR(50) NOT NULL,
    tipo_cultivo VARCHAR(50) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP -- Timestamp con Time Zone para evitar defasajes de zona horarias
);


-- Registro incial de dispositivo del MPV

INSERT INTO dispositivos (dispositivo_id, nombre, ubicacion_nave, tipo_cultivo)
VALUES ('GH_TOMATO_01', 'Nodo Principal Tomate Nave 1', 'Nave_A1', 'Solanum lycopersicum')
ON CONFLICT (dispositivo_id) DO NOTHING; -- No acusa error si se reejecuta el comando


-- Tabla de telemetría y validacion de calidad

CREATE TABLE IF NOT EXISTS telemetria_sensores (
    fecha_hora TIMESTAMPTZ NOT NULL,
    fecha_hora_ingesta TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    dispositivo_id VARCHAR(50) NOT NULL,
    estado VARCHAR(20) DEFAULT 'active',
    temperatura DOUBLE PRECISION,
    humedad_relativa DOUBLE PRECISION,
    humedad_suelo DOUBLE PRECISION,
    radiacion_par DOUBLE PRECISION,
    datos_adicionales JSONB,
    CONSTRAINT fk_dispositivo FOREIGN KEY (dispositivo_id) REFERENCES dispositivos(dispositivo_id),
    CONSTRAINT chk_humedad_relativa CHECK (humedad_relativa IS NOT NULL OR (humedad_relativa >= 0 AND humedad_relativa <=100)),
    CONSTRAINT chk_humedad_suelo CHECK (humedad_suelo IS NULL OR (humedad_suelo >=0 AND humedad_suelo <= 100))
);


-- Conversión a Hypertabla

SELECT create_hypertable(
    'telemetria_sensores',
    'fecha_hora', -- Paritción primaria
    partitioning_column => 'dispositivo_id', -- Particion secundaria
    number_partitions => 2,
    if_not_exists => TRUE
);


-- Indexación para eficientizar las lecturas las consultas por dashboard

CREATE INDEX IF NOT EXISTS idx_telemetria_dispositivo_tiempo
ON telemetria_sensores (dispositivo_id, fecha_hora DESC);


-- Compresión nativa de las series de tiempo

ALTER TABLE telemetria_sensores SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'dispositivo_id', -- Agrupa lecturas por nodo y tuerce la orientación de filas a columnas
    timescaledb.compress_orderby = 'fecha_hora DESC'
);

SELECT add_compression_policy('telemetria_sensores', INTERVAL '7 days', if_not_exists => TRUE); -- Automatiza la compresión cada vez que un chunk supera los 7 dias

