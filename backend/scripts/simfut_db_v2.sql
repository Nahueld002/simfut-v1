-- ==============================================================================
-- SIMFUT GOD MODE ENGINE - FINAL DB SCHEMA (v7.0) [REFACTORED & UNIFIED]
-- Cambios:
--   - Integración de patrón de Catálogos Unificados (cat_dominio / cat_parametro)
--   - Eliminación de tablas satélite pequeñas.
--   - Normalización de FKs en tablas core (competencia, estadio, finanzas).
-- ==============================================================================

BEGIN;

-- ----------------------------------------------------------------------
-- RESET & CONFIG
-- ----------------------------------------------------------------------
DROP SCHEMA IF EXISTS futsim CASCADE;
CREATE SCHEMA futsim;

-- Extensiones
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA futsim;

-- Path
SET search_path TO futsim;

-- ----------------------------------------------------------------------
-- 0) CATÁLOGOS MAESTROS (The "One True Lookup" Pattern)
-- ----------------------------------------------------------------------

-- 1. Dominios (Tipos)
CREATE TABLE cat_dominio (
    dominio_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE, 
    descripcion VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- 2. Parámetros (Valores)
CREATE TABLE cat_parametro (
    parametro_id SERIAL PRIMARY KEY,
    dominio_id INT NOT NULL REFERENCES cat_dominio(dominio_id),
    codigo VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    orden INT DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    metadatos JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT uq_dominio_codigo UNIQUE (dominio_id, codigo)
);

CREATE INDEX idx_parametro_dominio ON cat_parametro(dominio_id);
CREATE INDEX idx_parametro_codigo ON cat_parametro(codigo);

-- ----------------------------------------------------------------------
-- 0.1) SEEDS INICIALES (Necesarios para las FKs siguientes)
-- ----------------------------------------------------------------------
-- Insertamos Dominios Clave
INSERT INTO cat_dominio (codigo, descripcion) VALUES
('COMPETENCIA_TIPO', 'Tipos de torneo'),
('ETAPA_TIPO', 'Fases de torneo'),
('METODO_CLASIFICACION', 'Criterios de clasificación'),
('ESTADO_GENERICO', 'Estados de ciclo de vida'),
('ESTILO_JUEGO', 'Estrategia táctica'),
('TIPO_SALIDA', 'Mecánica de inicio'),
('TRANSICION', 'Comportamiento tras robo'),
('TIPO_PROPIEDAD', 'Modelo dueño de club'),
('TIPO_CESPED', 'Superficie estadio'),
('EVENTO_EQUIPO', 'Narrativa dinámica'),
('NARRATIVA_TIPO', 'Hitos históricos'),
('NOTICIA_TIPO', 'Categorías de noticias'),
('CLIMA_CONDICION', 'Clima de partido');

-- (Nota: Los parámetros específicos se pueden cargar en un script de seed separado 
--  o aquí mismo si quieres que la DB nazca ya poblada. Para mantener este script
--  de estructura limpio, dejaremos la carga masiva para el seed.sql, pero 
--  la estructura ya está lista para recibir FKs).

-- ----------------------------------------------------------------------
-- 1) MEDIA
-- ----------------------------------------------------------------------
CREATE TABLE media_asset (
  media_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  url           TEXT NOT NULL,
  mime_type     TEXT,
  ancho         INT,
  alto          INT,
  bytes         BIGINT,
  checksum      TEXT,
  creado_en     TIMESTAMPTZ NOT NULL DEFAULT now(),
  meta          JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- ----------------------------------------------------------------------
-- 2) MUNDO Y TIEMPO
-- ----------------------------------------------------------------------
CREATE TABLE mundo (
  mundo_id               SERIAL PRIMARY KEY,
  nombre                VARCHAR(100) NOT NULL,
  fecha_actual          DATE NOT NULL DEFAULT CURRENT_DATE,
  semilla_rng           BIGINT,
  configuracion_global  JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE temporada (
  temporada_id      SERIAL PRIMARY KEY,
  mundo_id          INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  nombre           VARCHAR(50) NOT NULL,
  fecha_inicio     DATE NOT NULL,
  fecha_fin        DATE NOT NULL,
  es_actual        BOOLEAN NOT NULL DEFAULT FALSE,
  meta             JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (mundo_id, nombre)
);

CREATE TABLE mundo_snapshot (
  snapshot_id      BIGSERIAL PRIMARY KEY,
  mundo_id         INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  fecha           DATE NOT NULL,
  tick            BIGINT NOT NULL DEFAULT 0,
  payload         JSONB NOT NULL,
  creado_en       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (mundo_id, fecha, tick)
);

CREATE TABLE sim_log (
  log_id           BIGSERIAL PRIMARY KEY,
  mundo_id         INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  tick            BIGINT NOT NULL DEFAULT 0,
  fecha           DATE NOT NULL,
  accion          VARCHAR(100) NOT NULL,
  payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
  creado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_sim_log_mundo_fecha ON sim_log(mundo_id, fecha);

-- ----------------------------------------------------------------------
-- 3) GEOGRAFÍA + CLIMA
-- ----------------------------------------------------------------------
CREATE TABLE confederacion (
  confederacion_id   SERIAL PRIMARY KEY,
  nombre            VARCHAR(150) NOT NULL UNIQUE,
  acronimo          VARCHAR(10) UNIQUE,
  logo_media_id     UUID REFERENCES media_asset(media_id),
  reputacion_base   INT NOT NULL DEFAULT 5000,
  meta              JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE pais (
  pais_id              SERIAL PRIMARY KEY,
  confederacion_id     INT REFERENCES confederacion(confederacion_id),
  nombre              VARCHAR(150) NOT NULL UNIQUE,
  iso_code            VARCHAR(3) NOT NULL UNIQUE,
  gentilicio          VARCHAR(50),
  bandera_media_id    UUID REFERENCES media_asset(media_id),
  nivel_futbolistico  INT NOT NULL DEFAULT 50 CHECK (nivel_futbolistico BETWEEN 1 AND 100),
  poblacion           BIGINT,
  meta                JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE region (
  region_id             SERIAL PRIMARY KEY,
  pais_id               INT NOT NULL REFERENCES pais(pais_id) ON DELETE CASCADE,
  nombre               VARCHAR(100) NOT NULL,
  tipo_region          VARCHAR(50) NOT NULL,
  meta                 JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE(pais_id, nombre)
);

CREATE TABLE perfil_climatico (
  perfil_id               SERIAL PRIMARY KEY,
  nombre                 VARCHAR(50) NOT NULL,
  codigo_koppen          VARCHAR(5),
  temp_promedio_verano   FLOAT,
  temp_promedio_invierno FLOAT,
  altitud_media          INT NOT NULL DEFAULT 0,
  tags                   JSONB NOT NULL DEFAULT '[]'::jsonb,
  ventaja_local_climatica FLOAT NOT NULL DEFAULT 1.0,
  meta                   JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE ciudad (
  ciudad_id              SERIAL PRIMARY KEY,
  region_id              INT NOT NULL REFERENCES region(region_id) ON DELETE CASCADE,
  nombre                VARCHAR(100) NOT NULL,
  perfil_climatico_id   INT REFERENCES perfil_climatico(perfil_id),
  coordenadas           POINT,
  poblacion             INT,
  meta                  JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE(region_id, nombre)
);

CREATE TABLE estadio (
  estadio_id      SERIAL PRIMARY KEY,
  ciudad_id       INT REFERENCES ciudad(ciudad_id),
  nombre          VARCHAR(150) NOT NULL,
  capacidad       INT NOT NULL DEFAULT 0,
  tipo_cesped_id  INT NOT NULL REFERENCES cat_parametro(parametro_id),
  foto_media_id   UUID REFERENCES media_asset(media_id),
  estado_id       INT NOT NULL REFERENCES cat_parametro(parametro_id),
  meta            JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- ----------------------------------------------------------------------
-- 4) ASOCIACIONES
-- ----------------------------------------------------------------------
CREATE TABLE asociacion (
  asociacion_id        SERIAL PRIMARY KEY,
  confederacion_id     INT REFERENCES confederacion(confederacion_id),
  pais_id              INT REFERENCES pais(pais_id),
  nombre              VARCHAR(100) NOT NULL,
  acronimo            VARCHAR(20),
  logo_media_id       UUID REFERENCES media_asset(media_id),
  meta                JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (confederacion_id, nombre)
);

-- ----------------------------------------------------------------------
-- 5) EQUIPOS
-- ----------------------------------------------------------------------
CREATE TABLE equipo (
  equipo_id            SERIAL PRIMARY KEY,
  mundo_id             INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  nombre              VARCHAR(150) NOT NULL,
  codigo_tla          VARCHAR(10),
  anio_fundacion      INT,
  ciudad_sede_id      INT REFERENCES ciudad(ciudad_id),
  pais_origen_id      INT REFERENCES pais(pais_id),
  asociacion_liga_id  INT REFERENCES asociacion(asociacion_id),
  estadio_principal_id INT REFERENCES estadio(estadio_id),
  escudo_media_id     UUID REFERENCES media_asset(media_id),
  colores             JSONB NOT NULL DEFAULT '{}'::jsonb,
  estado_id           INT REFERENCES cat_parametro(parametro_id),
  meta                JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (mundo_id, nombre)
);

CREATE TABLE equipo_estadio_hist (
  equipo_id        INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  estadio_id       INT NOT NULL REFERENCES estadio(estadio_id),
  fecha_inicio    DATE NOT NULL,
  fecha_fin       DATE,
  motivo          VARCHAR(100),
  es_principal    BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (equipo_id, estadio_id, fecha_inicio)
);

-- Rating Actual [REFACTOR: IDs Tácticos]
CREATE TABLE equipo_rating_actual (
  equipo_id         INT PRIMARY KEY REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  elo_actual       FLOAT NOT NULL DEFAULT 1200,
  ataque           INT NOT NULL DEFAULT 50 CHECK (ataque BETWEEN 1 AND 100),
  defensa          INT NOT NULL DEFAULT 50 CHECK (defensa BETWEEN 1 AND 100),
  mediocampo       INT NOT NULL DEFAULT 50 CHECK (mediocampo BETWEEN 1 AND 100),
  moral            INT NOT NULL DEFAULT 50 CHECK (moral BETWEEN 0 AND 100),
  fatiga           INT NOT NULL DEFAULT 0 CHECK (fatiga BETWEEN 0 AND 100),
  cohesion         INT NOT NULL DEFAULT 50 CHECK (cohesion BETWEEN 0 AND 100),
  disciplina       INT NOT NULL DEFAULT 50 CHECK (disciplina BETWEEN 0 AND 100),

  -- [REFACTOR] Columnas tácticas FK
  estilo_id        INT REFERENCES cat_parametro(parametro_id), -- Dominio: ESTILO_JUEGO
  salida_id        INT REFERENCES cat_parametro(parametro_id), -- Dominio: TIPO_SALIDA
  transicion_id    INT REFERENCES cat_parametro(parametro_id), -- Dominio: TRANSICION
  
  -- Valores numéricos tácticos se quedan aquí
  tactica_detalle  JSONB NOT NULL DEFAULT '{}'::jsonb, -- {ritmo:70, anchura:60, presion:50...}
  
  actualizado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE futsim.equipo_institucion (
  equipo_id              INT PRIMARY KEY REFERENCES futsim.equipo(equipo_id) ON DELETE CASCADE,

  potencial_basal        INT NOT NULL DEFAULT 1200,
  volatilidad            INT NOT NULL DEFAULT 10,
  infraestructura        INT NOT NULL DEFAULT 10 CHECK (infraestructura BETWEEN 1 AND 20),
  nivel_scouting         INT NOT NULL DEFAULT 10 CHECK (nivel_scouting BETWEEN 1 AND 20),
  nivel_entrenamiento    INT NOT NULL DEFAULT 10 CHECK (nivel_entrenamiento BETWEEN 1 AND 20),
  nivel_juveniles        INT NOT NULL DEFAULT 10 CHECK (nivel_juveniles BETWEEN 1 AND 20),
  estabilidad_directiva  INT NOT NULL DEFAULT 10 CHECK (estabilidad_directiva BETWEEN 1 AND 20),
  hinchada               INT NOT NULL DEFAULT 10 CHECK (hinchada BETWEEN 1 AND 20),
  reputacion_historica   INT NOT NULL DEFAULT 10 CHECK (reputacion_historica BETWEEN 1 AND 20),
  meta                   JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE futsim.equipo_finanzas (
  equipo_id              INT PRIMARY KEY REFERENCES futsim.equipo(equipo_id) ON DELETE CASCADE,
  moneda_id              INT NOT NULL REFERENCES futsim.cat_parametro(parametro_id),
  presupuesto_fichajes   DECIMAL(18,2) NOT NULL DEFAULT 0,
  presupuesto_salarial   DECIMAL(18,2) NOT NULL DEFAULT 0,
  deuda_total            DECIMAL(18,2) NOT NULL DEFAULT 0,
  poder_economico_base   INT NOT NULL DEFAULT 10 CHECK (poder_economico_base BETWEEN 1 AND 20),
  tipo_propiedad_id      INT REFERENCES futsim.cat_parametro(parametro_id),
  paciencia_directiva    INT NOT NULL DEFAULT 10 CHECK (paciencia_directiva BETWEEN 1 AND 20),
  actualizado_en         DATE NOT NULL DEFAULT CURRENT_DATE,
  meta                   JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE rivalidad (
  rivalidad_id     SERIAL PRIMARY KEY,
  equipo_a_id     INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  equipo_b_id     INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  nombre          VARCHAR(100),
  intensidad      INT NOT NULL DEFAULT 50,
  meta            JSONB NOT NULL DEFAULT '{}'::jsonb,
  CHECK (equipo_a_id < equipo_b_id),
  UNIQUE(equipo_a_id, equipo_b_id)
);

CREATE TABLE historial_enfrentamiento (
  historial_id        SERIAL PRIMARY KEY,
  equipo_a_id        INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  equipo_b_id        INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  partidos_jugados   INT NOT NULL DEFAULT 0,
  victorias_a        INT NOT NULL DEFAULT 0,
  victorias_b        INT NOT NULL DEFAULT 0,
  empates            INT NOT NULL DEFAULT 0,
  goles_a            INT NOT NULL DEFAULT 0,
  goles_b            INT NOT NULL DEFAULT 0,
  ultimo_partido_fecha DATE,
  ultimo_ganador_id   INT REFERENCES equipo(equipo_id),
  meta               JSONB NOT NULL DEFAULT '{}'::jsonb,
  CHECK (equipo_a_id < equipo_b_id),
  UNIQUE(equipo_a_id, equipo_b_id)
);

CREATE TABLE evento_equipo (
  evento_id       SERIAL PRIMARY KEY,
  mundo_id        INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  equipo_id       INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  fecha_inicio   DATE NOT NULL,
  fecha_fin      DATE,
  
  -- [REFACTOR] Apunta a cat_parametro (Dominio: EVENTO_EQUIPO)
  tipo_id        INT REFERENCES cat_parametro(parametro_id),
  
  severidad      INT NOT NULL DEFAULT 1,
  modificadores  JSONB NOT NULL DEFAULT '{}'::jsonb,
  descripcion    TEXT
);
CREATE INDEX idx_evento_equipo_mundo_fecha ON evento_equipo(mundo_id, fecha_inicio, fecha_fin);

-- ----------------------------------------------------------------------
-- 6) COMPETICIONES
-- ----------------------------------------------------------------------
CREATE TABLE competencia (
  competencia_id        SERIAL PRIMARY KEY,
  mundo_id              INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  nombre               VARCHAR(150) NOT NULL,
  
  -- [REFACTOR] Apunta a cat_parametro (Dominio: COMPETENCIA_TIPO)
  tipo_id               INT NOT NULL REFERENCES cat_parametro(parametro_id),

  confederacion_id      INT REFERENCES confederacion(confederacion_id),
  pais_id               INT REFERENCES pais(pais_id),
  region_id             INT REFERENCES region(region_id),
  asociacion_id         INT REFERENCES asociacion(asociacion_id),
  logo_media_id        UUID REFERENCES media_asset(media_id),
  reputacion_base      INT NOT NULL DEFAULT 5000,
  configuracion_base   JSONB NOT NULL DEFAULT '{}'::jsonb,
  meta                 JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (mundo_id, nombre)
);

CREATE TABLE competencia_reputacion (
  competencia_id    INT NOT NULL REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  alcance          VARCHAR(20) NOT NULL,
  temporada_id      INT REFERENCES temporada(temporada_id) ON DELETE CASCADE,
  valor            INT NOT NULL DEFAULT 5000,
  actualizado_en   TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (competencia_id, alcance, temporada_id)
);

CREATE TABLE regla_elegibilidad (
  elegibilidad_id   SERIAL PRIMARY KEY,
  competencia_id    INT NOT NULL REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  regla            JSONB NOT NULL,
  nota             TEXT
);

CREATE TABLE competencia_edicion (
  edicion_id        SERIAL PRIMARY KEY,
  competencia_id    INT NOT NULL REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  temporada_id      INT NOT NULL REFERENCES temporada(temporada_id) ON DELETE CASCADE,
  nombre_display   VARCHAR(100),
  fecha_inicio     DATE,
  fecha_fin        DATE,
  estado_id        INT NOT NULL REFERENCES cat_parametro(parametro_id),  
  reglas_edicion   JSONB NOT NULL DEFAULT '{}'::jsonb,
  meta             JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (competencia_id, temporada_id)
);

CREATE TABLE etapa (
  etapa_id        SERIAL PRIMARY KEY,
  edicion_id      INT NOT NULL REFERENCES competencia_edicion(edicion_id) ON DELETE CASCADE,
  orden          INT NOT NULL,
  
  -- [REFACTOR] Apunta a cat_parametro (Dominio: ETAPA_TIPO)
  tipo_id         INT NOT NULL REFERENCES cat_parametro(parametro_id),
  
  nombre         VARCHAR(100) NOT NULL,
  fecha_inicio   DATE,
  fecha_fin      DATE,
  config_etapa   JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (edicion_id, orden)
);

CREATE TABLE grupo (
  grupo_id       SERIAL PRIMARY KEY,
  etapa_id       INT NOT NULL REFERENCES etapa(etapa_id) ON DELETE CASCADE,
  codigo        VARCHAR(10) NOT NULL,
  nombre        VARCHAR(50),
  meta          JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE(etapa_id, codigo)
);

CREATE TABLE ronda (
  ronda_id        SERIAL PRIMARY KEY,
  etapa_id        INT NOT NULL REFERENCES etapa(etapa_id) ON DELETE CASCADE,
  grupo_id        INT REFERENCES grupo(grupo_id) ON DELETE CASCADE,
  numero         INT NOT NULL,
  pierna         INT NOT NULL DEFAULT 1,
  fecha_programada DATE,
  nombre         VARCHAR(100),
  meta           JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (etapa_id, grupo_id, numero, pierna)
);

CREATE TABLE participante (
  participante_id        SERIAL PRIMARY KEY,
  edicion_id             INT NOT NULL REFERENCES competencia_edicion(edicion_id) ON DELETE CASCADE,
  equipo_id              INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  
  -- [REFACTOR] Apunta a cat_parametro (Dominio: METODO_CLASIFICACION)
  metodo_id              INT REFERENCES cat_parametro(parametro_id),
  
  seed                  INT,
  bombo_sorteo          INT,
  grupo_id_inicial       INT REFERENCES grupo(grupo_id),
  grupo_inicial_texto   VARCHAR(10),
  posicion_final        INT,
  ronda_eliminacion     VARCHAR(50),
  puntos_ranking_ganados FLOAT NOT NULL DEFAULT 0,
  meta                  JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (edicion_id, equipo_id)
);

CREATE TABLE tabla_posiciones (
  edicion_id     INT NOT NULL REFERENCES competencia_edicion(edicion_id) ON DELETE CASCADE,
  etapa_id       INT NOT NULL REFERENCES etapa(etapa_id) ON DELETE CASCADE,
  grupo_id       INT REFERENCES grupo(grupo_id) ON DELETE CASCADE,
  equipo_id      INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  pj           INT NOT NULL DEFAULT 0,
  pg           INT NOT NULL DEFAULT 0,
  pe           INT NOT NULL DEFAULT 0,
  pp           INT NOT NULL DEFAULT 0,
  gf           INT NOT NULL DEFAULT 0,
  gc           INT NOT NULL DEFAULT 0,
  dg           INT NOT NULL DEFAULT 0,
  pts          INT NOT NULL DEFAULT 0,
  forma        VARCHAR(10),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
  meta         JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (edicion_id, etapa_id, grupo_id, equipo_id)
);

-- ----------------------------------------------------------------------
-- 7) SEEDING / BOMBOS
-- ----------------------------------------------------------------------
CREATE TABLE perfil_sorteo (
  perfil_sorteo_id    SERIAL PRIMARY KEY,
  nombre             VARCHAR(100) NOT NULL UNIQUE,
  config             JSONB NOT NULL
);
ALTER TABLE etapa ADD COLUMN perfil_sorteo_id INT REFERENCES perfil_sorteo(perfil_sorteo_id);

-- ----------------------------------------------------------------------
-- 8) PARTIDOS
-- ----------------------------------------------------------------------
-- A) CREATE TABLE partido (refactorizado: estado_id FK a cat_parametro)
CREATE TABLE futsim.partido (
  partido_id        BIGSERIAL PRIMARY KEY,
  edicion_id        INT NOT NULL REFERENCES futsim.competencia_edicion(edicion_id) ON DELETE CASCADE,
  etapa_id          INT NOT NULL REFERENCES futsim.etapa(etapa_id) ON DELETE CASCADE,
  ronda_id          INT REFERENCES futsim.ronda(ronda_id) ON DELETE SET NULL,
  grupo_id          INT REFERENCES futsim.grupo(grupo_id) ON DELETE SET NULL,
  local_equipo_id   INT NOT NULL REFERENCES futsim.equipo(equipo_id),
  visita_equipo_id  INT NOT NULL REFERENCES futsim.equipo(equipo_id),
  estadio_real_id   INT REFERENCES futsim.estadio(estadio_id),
  es_neutral        BOOLEAN NOT NULL DEFAULT FALSE,
  ciudad_id         INT REFERENCES futsim.ciudad(ciudad_id),
  fecha_hora        TIMESTAMP,
  jornada           INT,
  fase_label        VARCHAR(50),
  asistencia        INT,
  goles_local       INT,
  goles_visita      INT,
  penales_local     INT,
  penales_visita    INT,
  estado_id         INT NOT NULL DEFAULT 25 REFERENCES futsim.cat_parametro(parametro_id),
  reporte_motor     JSONB NOT NULL DEFAULT '{}'::jsonb,
  CHECK (local_equipo_id <> visita_equipo_id)
);
CREATE INDEX idx_partido_fecha ON futsim.partido(fecha_hora);

CREATE TABLE partido_clima (
  partido_id       BIGINT PRIMARY KEY REFERENCES partido(partido_id) ON DELETE CASCADE,
  temperatura_c   FLOAT,
  humedad         FLOAT,
  viento_kmh      FLOAT,
  lluvia_mm       FLOAT,
  
  -- [REFACTOR] Apunta a cat_parametro (Dominio: CLIMA_CONDICION)
  condicion_id    INT REFERENCES cat_parametro(parametro_id),
  
  tags            JSONB NOT NULL DEFAULT '[]'::jsonb,
  meta            JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE partido_contexto (
  partido_id            BIGINT PRIMARY KEY REFERENCES partido(partido_id) ON DELETE CASCADE,
  intensidad_hinchada  INT NOT NULL DEFAULT 50,
  viaje_km_visita      INT,
  altitud_m            INT,
  rivalidad_intensidad INT,
  presion              INT NOT NULL DEFAULT 50,
  external             JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE partido_stats_equipo (
  partido_id        BIGINT NOT NULL REFERENCES partido(partido_id) ON DELETE CASCADE,
  equipo_id         INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  es_local         BOOLEAN NOT NULL,
  xg               FLOAT,
  tiros            INT,
  tiros_arco       INT,
  posesion         FLOAT,
  corners          INT,
  faltas           INT,
  amarillas        INT,
  rojas            INT,
  delta_elo        FLOAT,
  payload          JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (partido_id, equipo_id)
);

-- ----------------------------------------------------------------------
-- 9) RANKINGS / COEFICIENTES / CUPOS
-- ----------------------------------------------------------------------
CREATE TABLE sistema_ranking (
  sistema_id       SERIAL PRIMARY KEY,
  mundo_id         INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  nombre          VARCHAR(100) NOT NULL,
  alcance         VARCHAR(30) NOT NULL,
  ventana_anios   INT NOT NULL DEFAULT 5,
  reglas_calculo  JSONB NOT NULL,
  confederacion_id INT REFERENCES confederacion(confederacion_id),
  pais_id          INT REFERENCES pais(pais_id),
  competencia_id   INT REFERENCES competencia(competencia_id),
  meta            JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (mundo_id, nombre)
);

CREATE TABLE ranking_entrada (
  entrada_id        BIGSERIAL PRIMARY KEY,
  sistema_id        INT NOT NULL REFERENCES sistema_ranking(sistema_id) ON DELETE CASCADE,
  temporada_id      INT REFERENCES temporada(temporada_id) ON DELETE CASCADE,
  at_date          DATE NOT NULL DEFAULT CURRENT_DATE,
  equipo_id         INT REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  pais_id           INT REFERENCES pais(pais_id) ON DELETE CASCADE,
  confederacion_id  INT REFERENCES confederacion(confederacion_id) ON DELETE CASCADE,
  competencia_id    INT REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  puntos_totales   FLOAT NOT NULL DEFAULT 0,
  ranking_posicion INT,
  historial_puntos JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX idx_ranking_lookup ON ranking_entrada(sistema_id, at_date, puntos_totales DESC);

CREATE TABLE regla_asignacion_cupos (
  asignacion_id         SERIAL PRIMARY KEY,
  mundo_id              INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  competencia_objetivo_id INT NOT NULL REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  sistema_id            INT NOT NULL REFERENCES sistema_ranking(sistema_id),
  temporada_id          INT REFERENCES temporada(temporada_id) ON DELETE CASCADE,
  regla               JSONB NOT NULL,
  nota                TEXT
);

CREATE TABLE regla_clasificacion (
  clasificacion_id      SERIAL PRIMARY KEY,
  mundo_id              INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  temporada_id          INT REFERENCES temporada(temporada_id) ON DELETE CASCADE,
  competencia_fuente_id INT NOT NULL REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  etapa_fuente_tipo     VARCHAR(30),
  grupo_fuente_codigo   VARCHAR(10),
  posicion_desde        INT,
  posicion_hasta        INT,
  condicion_fuente      JSONB NOT NULL DEFAULT '{}'::jsonb,
  competencia_destino_id INT NOT NULL REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  etapa_destino_tipo     VARCHAR(30),
  hint_ronda_destino     VARCHAR(30),
  
  -- [REFACTOR] Apunta a cat_parametro
  metodo_id               INT REFERENCES cat_parametro(parametro_id),
  
  prioridad              INT NOT NULL DEFAULT 0,
  nota                  TEXT
);

-- ----------------------------------------------------------------------
-- 10) HISTORIA / DASHBOARD
-- ----------------------------------------------------------------------
CREATE TABLE snapshot_equipo (
  snapshot_id            BIGSERIAL PRIMARY KEY,
  equipo_id              INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  fecha                 DATE NOT NULL,
  elo                   FLOAT,
  reputacion            INT,
  presupuesto_fichajes  DECIMAL(18,2),
  presupuesto_salarial  DECIMAL(18,2),
  posicion_estimada     INT,
  meta                  JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (equipo_id, fecha)
);

CREATE TABLE historia_narrativa (
  historia_id            SERIAL PRIMARY KEY,
  mundo_id               INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  fecha_generacion      DATE NOT NULL DEFAULT CURRENT_DATE,
  titulo                VARCHAR(150) NOT NULL,
  
  -- [REFACTOR] Apunta a cat_parametro (Dominio: NARRATIVA_TIPO)
  tipo_id               INT REFERENCES cat_parametro(parametro_id),
  
  importancia           INT NOT NULL DEFAULT 1,
  equipo_id              INT REFERENCES equipo(equipo_id) ON DELETE SET NULL,
  competencia_id         INT REFERENCES competencia(competencia_id) ON DELETE SET NULL,
  pais_id                INT REFERENCES pais(pais_id) ON DELETE SET NULL,
  resumen_texto         TEXT,
  datos_clave           JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE noticia (
  noticia_id             BIGSERIAL PRIMARY KEY,
  mundo_id               INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  fecha_hora            TIMESTAMP NOT NULL DEFAULT now(),
  
  -- [REFACTOR] Apunta a cat_parametro (Dominio: NOTICIA_TIPO)
  tipo_id               INT REFERENCES cat_parametro(parametro_id),
  
  titular               VARCHAR(200) NOT NULL,
  cuerpo                TEXT,
  equipos_relacionados  INT[] NOT NULL DEFAULT '{}'::INT[],
  competencia_id         INT REFERENCES competencia(competencia_id) ON DELETE SET NULL,
  meta                  JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE estadistica_global (
  stat_id                SERIAL PRIMARY KEY,
  mundo_id               INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  fecha                 DATE NOT NULL,
  total_goles           INT NOT NULL DEFAULT 0,
  promedio_goles_partido FLOAT NOT NULL DEFAULT 0,
  partidos_jugados      INT NOT NULL DEFAULT 0,
  distribucion_elo      JSONB NOT NULL DEFAULT '{}'::jsonb,
  meta                  JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (mundo_id, fecha)
);

CREATE TABLE equipo_elo_hist (
  equipo_id          INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,
  fecha             DATE NOT NULL,
  elo               FLOAT NOT NULL,
  potencial_basal   INT NOT NULL,
  volatilidad       INT NOT NULL,
  snapshot          JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (equipo_id, fecha)
);

-- Indices finales
CREATE INDEX idx_equipo_mundo ON equipo(mundo_id);
CREATE INDEX idx_participante_edicion ON participante(edicion_id);

COMMIT;