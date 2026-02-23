# SIMFUT GOD MODE — Documentación de Base de Datos (Bloque 0–2)

Este documento describe **tablas núcleo** del motor SIMFUT GOD MODE, diseñadas para ser consumidas por un backend Python (API + motor de simulación).
Está escrito para que cualquier desarrollador pueda entender **qué representa cada tabla**, **qué datos se guardan**, y **cómo impactan en la simulación**.

> **Nota de schema:** el SQL del proyecto usa el schema `futsim` (por ejemplo: `SET search_path TO futsim;`).
> En esta documentación se omite el prefijo de schema en los ejemplos por legibilidad. Ajustá tus consultas según el `search_path` de tu instalación.

---

## 0) Catálogos

Los catálogos reemplazan `ENUM` para evitar rigidez (migraciones cada vez que aparece un nuevo tipo de torneo, etapa o estado).
**Regla de oro:** el backend **no debe hardcodear IDs**; debe trabajar por `codigo` y resolver el `*_id` por lookup (cacheable).

### Tabla: `cat_competencia_tipo`

**Uso:** define el tipo general de una competencia.
Se usa en: `competencia.tipo_id`.
Afecta: la forma en que el motor genera fixtures, standings, y reglas por defecto (liga vs copa, etc.).

```sql
CREATE TABLE cat_competencia_tipo (
  tipoid        SERIAL PRIMARY KEY,
  codigo        VARCHAR(30) NOT NULL UNIQUE,   -- 'LIGA','COPA','INTERNACIONAL','SUPERCOPA','AMISTOSO'
  descripcion   TEXT
);
```

**Diccionario de datos**

- **`tipo_id`**: (PK) Identificador interno autoincremental.
- **`codigo`**: string estable para el backend. Ejemplos: `LIGA`, `COPA`, `INTERNACIONAL`, `SUPERCOPA`, `AMISTOSO`.
  - **Uso backend:** ramificar lógica de formato por `codigo`, no por `tipo_id`.
- **`descripcion`**: texto libre para UI/Docs.

**Ejemplo de inserts**

```sql
INSERT INTO cat_competencia_tipo (codigo, descripcion) VALUES
('LIGA', 'Formato liga (round robin)'),
('COPA', 'Eliminación directa o formato mixto')
ON CONFLICT DO NOTHING;
```

---

### Tabla: `cat_etapa_tipo`

**Uso:** define el tipo de una etapa dentro de una edición de torneo (fase regular, grupos, eliminación, etc.).
Se usa en: `etapa.tipo_id`.
Afecta: el algoritmo de fixture (round-robin, knockout ida/vuelta, suizo, split, playoffs).

```sql
CREATE TABLE cat_etapa_tipo (
  tipoid        SERIAL PRIMARY KEY,
  codigo        VARCHAR(30) NOT NULL UNIQUE,   -- 'LEAGUE','GROUPS','KNOCKOUT','SWISS','SPLIT','PLAYOFFS'
  descripcion   TEXT
);
```

**Diccionario de datos**

- **`tipo_id`**: (PK) Identificador interno.
- **`codigo`**: string estable. Ejemplos: `LEAGUE`, `GROUPS`, `KNOCKOUT`, `SWISS`, `SPLIT`, `PLAYOFFS`.
  - **Uso backend:** seleccionar el generador de calendario y la lógica de standings/clasificación.
- **`descripcion`**: texto libre.

**Ejemplo de inserts**

```sql
INSERT INTO cat_etapa_tipo (codigo, descripcion) VALUES
('GROUPS', 'Fase de grupos'),
('KNOCKOUT', 'Eliminación directa')
ON CONFLICT DO NOTHING;
```

---

### Tabla: `cat_metodo_clasificacion`

**Uso:** codifica el método por el que un equipo ingresa a una edición (campeón, ranking, invitado, etc.).
Se usa en: `participante.metodo_id`.
Afecta: la trazabilidad y motor de clasificaciones/cupos (ej. “campeón de copa clasifica a supercopa”).

```sql
CREATE TABLE cat_metodo_clasificacion (
  metodoid      SERIAL PRIMARY KEY,
  codigo        VARCHAR(50) NOT NULL UNIQUE,   -- 'CAMPEON','SUBCAMPEON','RANKING','INVITADO','HOST','PLAYOFF_WINNER','WILD_CARD'
  descripcion   TEXT
);
```

**Diccionario de datos**

- **`metodo_id`**: (PK) Identificador interno.
- **`codigo`**: string estable. Ejemplos: `CAMPEON`, `SUBCAMPEON`, `POSICION_LIGA`, `RANKING`, `INVITADO`, `HOST`, `PLAYOFF_WINNER`, `WILD_CARD`.
  - **Uso backend:** registrar “por qué” entró el equipo, y alimentar reglas de clasificación automáticas.
- **`descripcion`**: texto.

**Ejemplo de inserts**

```sql
INSERT INTO cat_metodo_clasificacion (codigo, descripcion) VALUES
('CAMPEON', 'Campeón de torneo'),
('RANKING', 'Clasifica por ranking/coefficient')
ON CONFLICT DO NOTHING;
```

---

### Tabla: `cat_estado_generico`

**Uso:** catálogo genérico de estados reutilizables en múltiples entidades.
Afecta: flujos de simulación (programado → en curso → finalizado; pendiente → jugado → simulado).

```sql
CREATE TABLE cat_estado_generico (
  estadoid      SERIAL PRIMARY KEY,
  codigo        VARCHAR(30) NOT NULL UNIQUE,   -- 'ACTIVO','INACTIVO','PROGRAMADA','EN_CURSO','FINALIZADA','PENDIENTE','SIMULADO','JUGADO'
  descripcion   TEXT
);
```

**Diccionario de datos**

- **`estado_id`**: (PK) Identificador interno.
- **`codigo`**: string estable. Ejemplos: `ACTIVO`, `INACTIVO`, `PROGRAMADA`, `EN_CURSO`, `FINALIZADA`, `PENDIENTE`, `SIMULADO`, `JUGADO`.
  - **Uso backend:** validaciones de workflow y filtros para UI (mostrar “solo activos”, “solo programados”, etc.).
- **`descripcion`**: texto.

**Ejemplo de inserts**

```sql
INSERT INTO cat_estado_generico (codigo, descripcion) VALUES
('PROGRAMADA', 'Programada'),
('FINALIZADA', 'Finalizada')
ON CONFLICT DO NOTHING;
```

---

### Seeds recomendados (tal como vienen en el SQL)

> Estos inserts son “mínimos” para que el sistema arranque. Podés ampliarlos sin migraciones complejas.

```sql
-- Seeds mínimos (podés ajustar)
INSERT INTO cat_competencia_tipo (codigo, descripcion) VALUES
('LIGA','Formato liga (round robin)'),
('COPA','Eliminación directa o mixta'),
('INTERNACIONAL','Competencia internacional'),
('SUPERCOPA','Supercopa / final única'),
('AMISTOSO','Amistoso / exhibición')
ON CONFLICT DO NOTHING;

INSERT INTO cat_etapa_tipo (codigo, descripcion) VALUES
('LEAGUE','Liga / round-robin'),
('GROUPS','Fase de grupos'),
('KNOCKOUT','Eliminación directa'),
('SWISS','Sistema suizo'),
('SPLIT','Liga con split'),
('PLAYOFFS','Playoffs')
ON CONFLICT DO NOTHING;

INSERT INTO cat_metodo_clasificacion (codigo, descripcion) VALUES
('CAMPEON','Campeón de torneo'),
('SUBCAMPEON','Subcampeón'),
('POSICION_LIGA','Por posición en liga'),
('RANKING','Por ranking/coefficient'),
('INVITADO','Invitado'),
('HOST','Anfitrión'),
('PLAYOFF_WINNER','Ganador de playoff'),
('WILD_CARD','Wild card')
ON CONFLICT DO NOTHING;

INSERT INTO cat_estado_generico (codigo, descripcion) VALUES
('ACTIVO','Entidad activa'),
('INACTIVO','Entidad inactiva'),
('PROGRAMADA','Programada'),
('EN_CURSO','En curso'),
('FINALIZADA','Finalizada'),
('PENDIENTE','Pendiente'),
('SIMULADO','Simulado'),
('JUGADO','Jugado')
ON CONFLICT DO NOTHING;
```

---

## 1) Media

### Tabla: `media_asset`

**Uso:** almacena recursos multimedia (logos, escudos, banderas, fotos de estadios, etc.).
La idea es mantenerlo **simple** (sin relaciones polimórficas) y referenciarlo con `*_media_id` desde tablas como `competencia`, `equipo`, `pais`, `confederacion`, etc.

**Dependencias:** ninguna; es una tabla “base”.

```sql
CREATE TABLE media_asset (
  mediaid       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  url           TEXT NOT NULL,
  mime_type     TEXT,
  ancho         INT,
  alto          INT,
  bytes         BIGINT,
  checksum      TEXT,
  creado_en     TIMESTAMPTZ NOT NULL DEFAULT now(),
  meta          JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

**Diccionario de datos**

- **`media_id`**: (PK) UUID. Generado por `futsim.gen_random_uuid()` (wrapper/función definida en el proyecto).
- **`url`**: URL o ruta del asset (CDN, S3, Git LFS, etc.).
  - **Uso backend:** el API devuelve esto al frontend; el simulador no lo usa para cálculos.
- **`mime_type`**: tipo MIME (`image/png`, `image/svg+xml`, `image/jpeg`).
- **`ancho` / `alto`**: dimensiones (px). Útil para UI y validación.
- **`bytes`**: tamaño del archivo. Útil para auditoría/optimización.
- **`checksum`**: hash (MD5/SHA256) para evitar duplicados o validar cache.
- **`creado_en`**: timestamp de creación.
- **`meta` (JSONB)**: metadatos flexibles.

**JSONB sugerido (`meta`)**

- `source`: `"wikipedia" | "transfermarkt" | "manual_upload" | "generated"`
- `license`: `"CC-BY" | "public_domain" | "all_rights_reserved"`
- `attribution`: texto o URL de atribución
- `tags`: `["escudo","club","paraguay"]`
- `dominant_colors`: `["#0033A0","#D50000"]`
- `storage`: `{"backend":"s3","bucket":"...","key":"..."}`
- `original_filename`: `"escudo.png"`

**Ejemplo de inserts**

```sql
INSERT INTO media_asset (url, mime_type, ancho, alto, bytes, checksum, meta) VALUES
('https://cdn.simfut.org/assets/escudos/olimpia.png', 'image/png', 512, 512, 83412, 'sha256:abc...', '{"source":"manual_upload","tags":["escudo","club"]}'),
('https://cdn.simfut.org/assets/logos/apf.svg', 'image/svg+xml', 0, 0, 12900, 'sha256:def...', '{"source":"wikipedia","license":"CC-BY","tags":["asociacion","logo"]}');
```

---

## 2) Mundo y tiempo

Estas tablas permiten que el motor funcione como “savegame”:

- El **mundo** representa una partida/simulación (config + fecha actual + RNG).
- La **temporada** define ciclos de calendario (inicio/fin) para generar torneos, resetear presupuestos, etc.
- Los **snapshots** permiten guardar estados agregados para dashboards, “rebobinar” o auditoría.
- El **log** permite trazabilidad del motor: qué se simuló, cuándo, y con qué parámetros.

### Tabla: `mundo`

**Uso:** representa una **partida**.Todo lo que “existe” (equipos, torneos, partidos) está colgado de `mundo_id`.El backend Python usará esta tabla para:

- cargar configuración de simulación,
- mantener la fecha actual,
- y reproducir resultados determinísticamente con `semilla_rng` (si se desea).

```sql
CREATE TABLE mundo (
  mundoid               SERIAL PRIMARY KEY,
  nombre                VARCHAR(100) NOT NULL,
  fecha_actual          DATE NOT NULL DEFAULT CURRENT_DATE,
  semilla_rng           BIGINT,
  configuracion_global  JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

**Diccionario de datos**

- **`mundo_id`**: (PK) Identificador del mundo/partida.
- **`nombre`**: nombre humano (“Partida Realista”, “Sandbox Conmebol”, etc.).
- **`fecha_actual`**: fecha en la que está el mundo (avance de calendario).
  - **Uso backend:** seleccionar partidos a simular, ventanas de mercado, fin de temporada.
- **`semilla_rng`**: semilla para aleatoriedad reproducible.
  - **Uso motor:** si querés “replay” idéntico, la semilla es clave (junto con estado RNG).
- **`configuracion_global` (JSONB)**: switches globales del mundo.

**JSONB sugerido (`configuracion_global`)**

- `match_engine`: `{"version":"v1","xg_model":"poisson","home_adv_base":0.04}`
- `volatilidad_global`: `1.0` (multiplicador del “shock”)
- `lesiones`: `true/false` *(si luego agregás jugadores)*
- `sanciones`: `true/false`
- `clima`: `{"enabled":true,"variance":1.0}`
- `finanzas`: `{"enabled":true,"inflation":0.03}`
- `debug`: `{"log_level":"INFO","store_snapshots":true}`

**Ejemplo de inserts**

```sql
INSERT INTO mundo (nombre, fecha_actual, semilla_rng, configuracion_global) VALUES
('Paraguay 2025 - Realista', '2025-01-01', 123456789, '{"match_engine":{"version":"v1"}, "volatilidad_global":1.1}'),
('Sandbox - Caos Total', '2025-01-01', 42, '{"volatilidad_global":2.0, "clima":{"enabled":true,"variance":1.8}, "debug":{"log_level":"DEBUG"}}');
```

---

### Tabla: `temporada`

**Uso:** define un período de calendario dentro de un mundo (por ejemplo “2025”, o “2024/2025”).Sirve como:

- contenedor para ediciones (`competencia_edicion.temporada_id`),
- señal para “fin de temporada” (promedios, ascensos/descensos, reset presupuestos),
- y estructura para dashboards (comparar temporadas).

```sql
CREATE TABLE temporada (
  temporadaid      SERIAL PRIMARY KEY,
  mundoid          INT NOT NULL REFERENCES mundo(mundoid) ON DELETE CASCADE,
  nombre           VARCHAR(50) NOT NULL,          -- "2024/2025"
  fecha_inicio     DATE NOT NULL,
  fecha_fin        DATE NOT NULL,
  es_actual        BOOLEAN NOT NULL DEFAULT FALSE,
  meta             JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (mundoid, nombre)
);
```

**Diccionario de datos**

- **`temporada_id`**: (PK).
- **`mundo_id`**: FK al mundo.
- **`nombre`**: identificador humano (“2024/2025”, “2025”).
- **`fecha_inicio` / `fecha_fin`**: límites del calendario.
- **`es_actual`**: si es la temporada activa del mundo.
- **`meta` (JSONB)**: parámetros extra de calendario y reglas.

**JSONB sugerido (`meta`)**

- `calendar_type`: `"ANUAL" | "APERTURA_CLAUSURA" | "EUROPEO"`
- `breaks`: `[{"from":"2025-06-10","to":"2025-07-05","reason":"interseason"}]`
- `transfer_windows`: `[{"from":"2025-01-01","to":"2025-02-01"}, {"from":"2025-06-15","to":"2025-07-31"}]`
- `promedio_descenso_years`: `3`
- `notes`: texto libre

**Ejemplo de inserts**

```sql
INSERT INTO temporada (mundo_id, nombre, fecha_inicio, fecha_fin, es_actual, meta) VALUES
(1, '2025', '2025-01-01', '2025-12-31', TRUE, '{"calendar_type":"ANUAL","transfer_windows":[{"from":"2025-01-01","to":"2025-02-01"}]}'),
(1, '2026', '2026-01-01', '2026-12-31', FALSE, '{"calendar_type":"ANUAL"}');
```

---

### Tabla: `mundo_snapshot`

**Uso:** snapshots agregados del mundo (“multiverso simple”).No está pensado para guardar TODO el detalle (eso ya vive en tablas normalizadas), sino para:

- dashboards rápidos (KPIs),
- rebobinar / debug,
- auditoría (“cómo estaba el mundo en tal fecha/tick”).

**Dependencias:** `mundo`.

```sql
CREATE TABLE mundo_snapshot (
  snapshotid      BIGSERIAL PRIMARY KEY,
  mundoid         INT NOT NULL REFERENCES mundo(mundoid) ON DELETE CASCADE,
  fecha           DATE NOT NULL,
  tick            BIGINT NOT NULL DEFAULT 0,
  payload         JSONB NOT NULL,
  creado_en       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (mundoid, fecha, tick)
);
```

**Diccionario de datos**

- **`snapshot_id`**: (PK) bigserial.
- **`mundo_id`**: FK.
- **`fecha`**: fecha del snapshot.
- **`tick`**: contador interno de simulación (avanza cada evento).
  - **Uso backend:** ordenar snapshots intra-fecha (varios eventos el mismo día).
- **`payload` (JSONB)**: estado agregado.
- **`creado_en`**: timestamp.
- **UNIQUE (mundo_id, fecha, tick)**: evita duplicados.

**JSONB sugerido (`payload`)**

- `kpis`: `{"partidos_simulados":123,"goles_totales":321,"promedio_goles":2.6}`
- `elo_distribution`: `{"1000-1200":50,"1200-1400":120}`
- `top_teams`: `[{"equipo_id":10,"elo":1550}, ...]`
- `alerts`: `["Crisis en Olimpia","Racha de Libertad"]`
- `rng_state`: opcional si querés reproducibilidad exacta

**Ejemplo de inserts**

```sql
INSERT INTO mundo_snapshot (mundo_id, fecha, tick, payload) VALUES
(1, '2025-03-01', 100, '{"kpis":{"partidos_simulados":48,"promedio_goles":2.4}, "top_teams":[{"equipo_id":3,"elo":1539}]}'),
(1, '2025-03-01', 101, '{"alerts":["Lesión clave en Club X"], "kpis":{"partidos_simulados":49}}');
```

---

### Tabla: `sim_log`

**Uso:** bitácora de acciones del simulador (auditoría + debug).
Cada vez que el motor ejecuta algo relevante (simular partido, generar fixture, fin de temporada),
se registra un evento con un payload.

**Dependencias:** `mundo`.

```sql
CREATE TABLE sim_log (
  logid           BIGSERIAL PRIMARY KEY,
  mundoid         INT NOT NULL REFERENCES mundo(mundoid) ON DELETE CASCADE,
  tick            BIGINT NOT NULL DEFAULT 0,
  fecha           DATE NOT NULL,
  accion          VARCHAR(100) NOT NULL,          -- 'SIM_PARTIDO','FIN_TEMPORADA','GENERAR_FIXTURE', ...
  payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
  creado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Diccionario de datos**

- **`log_id`**: (PK).
- **`mundo_id`**: FK.
- **`tick`**: contador interno (igual concepto que snapshot).
- **`fecha`**: fecha lógica del mundo en el momento del evento.
- **`accion`**: código de acción (string). Ejemplos:
  - `SIM_PARTIDO`
  - `GENERAR_FIXTURE`
  - `ACTUALIZAR_TABLA_POSICIONES`
  - `FIN_TEMPORADA`
  - `RECALCULAR_RANKING`
- **`payload` (JSONB)**: datos del evento.
- **`creado_en`**: timestamp real (cuando se escribió el log).

**JSONB sugerido (`payload`)**

- Para `SIM_PARTIDO`:
  - `partido_id`, `local_id`, `visita_id`, `goles_local`, `goles_visita`
  - `factores`: `{"localia":1.06,"clima":0.98,"fatiga_visita":1.10}`
  - `xg`: `{"local":1.8,"visita":0.9}`
- Para `GENERAR_FIXTURE`:
  - `competencia_edicion_id`, `etapas_creadas`, `partidos_creados`
- Para `FIN_TEMPORADA`:
  - `temporada_id`, `ascensos`, `descensos`, `campeones`, `reputacion_updates`

**Ejemplo de inserts**

```sql
INSERT INTO sim_log (mundo_id, tick, fecha, accion, payload) VALUES
(1, 1200, '2025-05-10', 'SIM_PARTIDO', '{"partido_id":999,"local_id":1,"visita_id":2,"goles_local":2,"goles_visita":1,"factores":{"localia":1.05}}'),
(1, 1300, '2025-12-31', 'FIN_TEMPORADA', '{"temporada_id":1,"ascensos":[10,11],"descensos":[20,21]}');
```

---

## Checklist de implementación backend (Python)

Para estas tablas “núcleo”, el backend suele tener estos módulos:

- **CatalogService**: cachea catálogos por `codigo` (y expone `get_id("LIGA")`).
- **MediaService**: valida `url/mime`, gestiona subida y atribución (`meta`).
- **WorldService**: crea/carga mundos, avanza `fecha_actual`, controla `semilla_rng`.
- **SeasonService**: crea temporadas, valida rangos de fechas, marca `es_actual`.
- **Audit/ReplayService**: escribe `sim_log` y (opcional) `mundo_snapshot` para debug y dashboards.

---

## 3) Geografía y clima

Este bloque define **dónde** existe cada entidad del juego (país/ciudad/estadio) y **qué condiciones ambientales** afectan a la simulación (altura, temperatura media, clima típico).
En el motor, estos datos alimentan:

- **localía** (altura, adaptación climática),
- **fatiga por viaje** (distancia aproximada por coordenadas),
- **probabilidades de clima del partido** (si luego implementás generación de clima diario).

### Tabla: `confederacion`

**Uso:** representa una confederación continental (CONMEBOL, UEFA, AFC, CAF, CONCACAF, OFC).
Se usa para:

- agrupar países bajo un “poder” continental,
- asignar reputación macro (ej. torneos UEFA suelen tener mayor reputación mundial),
- definir organizadores de competiciones internacionales.

**Depende de:** `media_asset` (opcional, por `logo_media_id`).

```sql
CREATE TABLE confederacion (
  confederacionid   SERIAL PRIMARY KEY,
  nombre            VARCHAR(50) NOT NULL UNIQUE,
  acronimo          VARCHAR(10) UNIQUE,
  logo_media_id     UUID REFERENCES media_asset(mediaid),
  reputacion_base   INT NOT NULL DEFAULT 5000,
  meta              JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

**Diccionario de datos**

- **`confederacion_id`**: (PK) ID interno.
- **`nombre`**: nombre único (ej. `"CONMEBOL"`). Usar naming oficial.
- **`acronimo`**: acrónimo único (ej. `"CONMEBOL"`, `"UEFA"`). Útil para UI y slugs.
- **`logo_media_id`**: FK opcional a `media_asset` (logo de la confederación).
- **`reputacion_base`**: reputación base (escala 0–10000 aprox).
  - **Uso backend:** sirve como “peso” para reputación continental y para torneos/reglas que dependan del nivel de la confederación.
- **`meta` (JSONB)**: metadata flexible (sin romper schema).

**JSONB sugerido (`meta`)**

- `website`: URL oficial
- `region_scope`: `"continental"`
- `ranking_system_id`: ID lógico del sistema ranking asociado (si querés enlazar)
- `notes`: texto

**Ejemplo de inserts**

```sql
INSERT INTO confederacion (nombre, acronimo, reputacion_base, meta) VALUES
('CONMEBOL', 'CONMEBOL', 7000, '{"website":"https://www.conmebol.com"}'),
('UEFA', 'UEFA', 9000, '{"website":"https://www.uefa.com","notes":"Mayor peso en reputación mundial"}');
```

---

### Tabla: `pais`

**Uso:** representa un país fútbolístico.Se usa para:

- identidad geográfica de clubes (`equipo.pais_origen_id`),
- elegibilidad por país (reglas de torneos),
- reputación y “calidad de cantera” mediante `nivel_futbolistico`.

**Depende de:** `confederacion`, `media_asset` (bandera opcional).

```sql
CREATE TABLE pais (
  paisid              SERIAL PRIMARY KEY,
  confederacionid     INT REFERENCES confederacion(confederacionid),
  nombre              VARCHAR(100) NOT NULL UNIQUE,
  iso_code            VARCHAR(3) NOT NULL UNIQUE,   -- ARG, BRA
  gentilicio          VARCHAR(50),
  bandera_media_id    UUID REFERENCES media_asset(mediaid),
  nivel_futbolistico  INT NOT NULL DEFAULT 50 CHECK (nivel_futbolistico BETWEEN 1 AND 100),
  poblacion           BIGINT,
  importancia_futbol  INT CHECK (importancia_futbol BETWEEN 1 AND 20),
  meta                JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

**Diccionario de datos**

- **`pais_id`**: (PK).
- **`confederacion_id`**: FK opcional a `confederacion`.
  - Puede ser NULL en datasets incompletos, pero lo ideal es setearlo siempre.
- **`nombre`**: nombre único (“Paraguay”).
- **`iso_code`**: ISO-3166 alfa-3 (ej. `"PRY"`). Se usa como clave estable.
- **`gentilicio`**: “Paraguayo”, “Argentino”.
- **`bandera_media_id`**: FK opcional a `media_asset`.
- **`nivel_futbolistico`**: 1–100.
  - **Idea:** multiplica el “pool” de talento y la competitividad media de clubes del país.
  - **Uso backend:** al generar newgens o asignar potencial de equipos/liga.
- **`poblacion`**: población real aproximada (opcional).
  - **Uso backend:** puede alimentar “fanbase” máxima, mercado, etc.
- **`meta` (JSONB)**: info extra.

**JSONB sugerido (`meta`)**

- `currency`: `"PYG"`, `"USD"`, etc.
- `league_system`: `"apertura_clausura" | "annual"`
- `climate_notes`: texto
- `timezone`: `"America/Asuncion"`
- `fifa_code`: `"PAR"` (si querés diferenciar ISO vs FIFA)
- `colors`: `{"primary":"#..."}` para UI

**Ejemplo de inserts**

```sql
INSERT INTO pais (confederacion_id, nombre, iso_code, gentilicio, nivel_futbolistico, poblacion, meta) VALUES
((SELECT confederacion_id FROM confederacion WHERE acronimo='CONMEBOL'), 'Paraguay', 'PRY', 'Paraguayo', 55, 7000000, '{"currency":"PYG","timezone":"America/Asuncion"}'),
((SELECT confederacion_id FROM confederacion WHERE acronimo='UEFA'), 'España', 'ESP', 'Español', 85, 48000000, '{"currency":"EUR","league_system":"annual"}');
```

---

### Tabla: `region`

**Uso:** subdivisión dentro de un país (departamento, provincia, estado, comunidad autónoma).
Se usa para:

- torneos regionales o estaduales,
- restricciones de elegibilidad (“solo equipos de esta región”),
- organización geográfica más granular que el país.

**Depende de:** `pais`.

```sql
CREATE TABLE region (
  regionid             SERIAL PRIMARY KEY,
  paisid               INT NOT NULL REFERENCES pais(paisid) ON DELETE CASCADE,
  nombre               VARCHAR(100) NOT NULL,
  gentilicio           VARCHAR(50),
  codigo_iso           VARCHAR(10),                 -- "BR-SP"
  reputacion_regional  INT NOT NULL DEFAULT 1000,
  meta                 JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE(paisid, nombre)
);
```

**Diccionario de datos**

- **`region_id`**: (PK).
- **`pais_id`**: FK a `pais`. (ON DELETE CASCADE) → al borrar el país, borra regiones.
- **`nombre`**: nombre de la región (único por país).
- **`tipo_region`**: tipo administrativo (ej. `"DEPARTAMENTO"`, `"PROVINCIA"`, `"ESTADO"`, `"CIUDAD_AUTONOMA"`).
  - **Uso backend:** para UI y para reglas (ej. “torneos estaduales”).
- **`meta` (JSONB)**: metadata.

**JSONB sugerido (`meta`)**

- `code`: `"PY-ASU"` o códigos internos
- `capital_city`: `"Asunción"`
- `population`: número
- `geo`: `{"bbox":[...], "center":[lat,lon]}`
- `notes`: texto

**Ejemplo de inserts**

```sql
INSERT INTO region (pais_id, nombre, tipo_region, meta) VALUES
((SELECT pais_id FROM pais WHERE iso_code='PRY'), 'Central', 'DEPARTAMENTO', '{"code":"PY-11"}'),
((SELECT pais_id FROM pais WHERE iso_code='PRY'), 'Asunción', 'DISTRITO_CAPITAL', '{"code":"PY-ASU"}');
```

---

### Tabla: `perfil_climatico`

**Uso:** define un “perfil” climático reutilizable por ciudades.
La idea es separar:

- **clima típico de la ciudad** (`perfil_climatico`)
  de
- **clima puntual del partido** (que suele guardarse en `partido_clima` o en JSON del partido en otros bloques).

Esto permite que el motor:

- genere clima diario coherente,
- aplique ventajas por adaptación (equipos acostumbrados a altura/lluvia/calor).

**Depende de:** nada.

```sql
CREATE TABLE perfil_climatico (
  perfilid               SERIAL PRIMARY KEY,
  nombre                 VARCHAR(50) NOT NULL,
  codigo_koppen          VARCHAR(5),
  temp_promedio_verano   FLOAT,
  temp_promedio_invierno FLOAT,
  altitud_media          INT NOT NULL DEFAULT 0,
  tags                   JSONB NOT NULL DEFAULT '[]'::jsonb, -- ["altura","lluvioso","calor_extremo"]
  ventaja_local_climatica FLOAT NOT NULL DEFAULT 1.0,
  meta                   JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

**Diccionario de datos**

- **`perfil_id`**: (PK).
- **`nombre`**: nombre del perfil (ej. “Subtropical húmedo urbano”).
- **`codigo_koppen`**: clasificación Köppen (ej. `Cfa`, `Aw`, `BSh`). Opcional.
- **`temp_promedio_verano`**: temperatura media típica en verano (°C).
- **`temp_promedio_invierno`**: media típica en invierno (°C).
- **`altitud_media`**: metros sobre el nivel del mar. **Clave** para altura.
- **`tags` (JSONB array)**: etiquetas cualitativas (ej. `["altura","lluvioso","calor_extremo"]`).
  - **Uso backend:** activar modificadores sin necesidad de nuevas columnas.
- **`ventaja_local_climatica`**: multiplicador (default 1.0).
  - **Idea:** cuánto “pesa” el clima/altura para equipos locales adaptados.
  - **Uso backend:** factor dentro del cálculo de localía o fatiga.
- **`meta` (JSONB)**: parámetros adicionales.

**JSONB sugerido**

- En `tags`:
  - `"altura"`, `"lluvioso"`, `"humedad"`, `"calor_extremo"`, `"frio_extremo"`, `"viento_fuerte"`, `"nieve"`, `"seco_polvo"`, `"tormentas"`.
- En `meta`:
  - `rain_prob`: 0..1 (probabilidad típica de lluvia)
  - `storm_prob`: 0..1
  - `humidity_avg`: 0..100
  - `wind_avg_kmh`: número
  - `pitch_effects`: `{"heavy_pitch":true,"ball_speed_mult":0.95}`

**Ejemplo de inserts**

```sql
INSERT INTO perfil_climatico (nombre, codigo_koppen, temp_promedio_verano, temp_promedio_invierno, altitud_media, tags, ventaja_local_climatica, meta) VALUES
('Subtropical húmedo urbano', 'Cfa', 29.0, 17.0, 80, '["humedad","calor","urbano"]', 1.02, '{"rain_prob":0.35,"humidity_avg":75}'),
('Altura extrema', 'Cwb', 18.0, 5.0, 3600, '["altura","frio","viento_fuerte"]', 1.10, '{"wind_avg_kmh":25,"pitch_effects":{"fatigue_visita_mult":1.12}}');
```

---

### Tabla: `ciudad`

**Uso:** representa una ciudad dentro de una región.Se usa para:

- ubicar estadios,
- ubicar equipos (sede),
- calcular distancias (viaje) mediante `coordenadas`,
- asignar clima típico mediante `perfil_climatico_id`.

**Depende de:** `region`, `perfil_climatico` (opcional).

```sql
CREATE TABLE ciudad (
  ciudadid              SERIAL PRIMARY KEY,
  regionid              INT NOT NULL REFERENCES region(regionid) ON DELETE CASCADE,
  nombre                VARCHAR(100) NOT NULL,
  perfil_climatico_id   INT REFERENCES perfil_climatico(perfilid),
  coordenadas           POINT,       -- (lat, lon)
  poblacion             INT,
  meta                  JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE(regionid, nombre)
);
```

**Diccionario de datos**

- **`ciudad_id`**: (PK).
- **`region_id`**: FK a `region`.
- **`nombre`**: nombre de la ciudad (único por región).
- **`perfil_climatico_id`**: FK opcional. Si es NULL, el motor puede usar un perfil por default.
- **`coordenadas`**: `POINT(lat, lon)` aproximado.
  - **Uso backend:** distancia entre ciudades (para fatiga y logística).
- **`poblacion`**: población aproximada.
- **`meta` (JSONB)**: datos adicionales.

**JSONB sugerido (`meta`)**

- `timezone`: override local
- `altitude_override`: si querés sobreescribir altitud del perfil
- `travel_hub`: true/false (ciudades con aeropuerto grande)
- `derby_tags`: `["capital","industrial"]`

**Ejemplo de inserts**

```sql
INSERT INTO ciudad (region_id, nombre, perfil_climatico_id, coordenadas, poblacion, meta) VALUES
((SELECT region_id FROM region WHERE nombre='Asunción'), 'Asunción',
 (SELECT perfil_id FROM perfil_climatico WHERE nombre='Subtropical húmedo urbano'),
 POINT(-25.2637, -57.5759), 520000, '{"travel_hub":true}'),
((SELECT region_id FROM region WHERE nombre='Central'), 'Luque',
 (SELECT perfil_id FROM perfil_climatico WHERE nombre='Subtropical húmedo urbano'),
 POINT(-25.2667, -57.4900), 300000, '{"notes":"Zona metropolitana"}');
```

---

### Tabla: `estadio`

**Uso:** representa el recinto donde se juegan partidos (capacidad, tipo de césped, estado).
Se usa para:

- localía (asistencia posible, “presión”),
- elecciones de sede neutral,
- restricciones (estadios inactivos por remodelación),
- visuales (foto).

**Depende de:** `ciudad`, `media_asset` (foto opcional).

```sql
CREATE TABLE estadio (
  estadioid             SERIAL PRIMARY KEY,
  ciudadid              INT REFERENCES ciudad(ciudadid),
  nombre                VARCHAR(150) NOT NULL,
  capacidad             INT NOT NULL DEFAULT 0,
  tipo_cesped           VARCHAR(50),  -- NATURAL / SINTETICO / HIBRIDO (validar en app)
  tiene_techo           BOOLEAN NOT NULL DEFAULT FALSE,
  foto_media_id         UUID REFERENCES media_asset(mediaid),
  estado_mantenimiento  INT NOT NULL DEFAULT 100 CHECK (estado_mantenimiento BETWEEN 0 AND 100),
  meta                  JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

**Diccionario de datos**

- **`estadio_id`**: (PK).
- **`ciudad_id`**: FK a `ciudad` (puede ser NULL si es “unknown” en datasets).
- **`nombre`**: nombre del estadio.
- **`capacidad`**: capacidad (int).
  - **Uso backend:** techo de asistencia + presión ambiente.
- **`tipo_cesped`**: string (validar en backend). Sugerido: `NATURAL`, `SINTETICO`, `HIBRIDO`.
  - **Uso motor:** puede modificar velocidad del balón / lesiones / estilo.
- **`foto_media_id`**: FK opcional a `media_asset`.
- **`estado`**: string (default `ACTIVO`). Sugeridos: `ACTIVO`, `REMODELACION`, `CERRADO`, `SANCIONADO`.
  - **Uso backend:** si no está activo, el motor debe buscar sede alternativa o marcar partidos neutrales.
- **`meta` (JSONB)**: datos extra.

**JSONB sugerido (`meta`)**

- `roof`: true/false
- `pitch_quality`: 0–100
- `owner`: `"club" | "municipal" | "private"`
- `address`: texto
- `renovation`: `{"from":"2025-01-01","to":"2025-06-01","reason":"remodelacion"}`

**Ejemplo de inserts**

```sql
INSERT INTO estadio (ciudad_id, nombre, capacidad, tipo_cesped, estado, meta) VALUES
((SELECT ciudad_id FROM ciudad WHERE nombre='Asunción'), 'Estadio Defensores del Chaco', 42000, 'NATURAL', 'ACTIVO', '{"pitch_quality":85}'),
((SELECT ciudad_id FROM ciudad WHERE nombre='Luque'), 'Estadio Feliciano Cáceres', 24000, 'NATURAL', 'REMODELACION', '{"renovation":{"from":"2025-02-01","to":"2025-07-01"}}');
```

---

## 4) Asociaciones (organizadores)

### Tabla: `asociacion`

**Uso:** representa la entidad organizadora (APF, AFA, CBF, MLS, federaciones multinacionales, etc.).
Se usa para:

- definir **dónde compite** un club (`equipo.asociacion_liga_id`),
- soportar ligas “cross-border” (ej. MLS con USA+CAN),
- separar “identidad de país” del club vs “liga donde juega”.

**Depende de:** `confederacion`, `pais`, `media_asset`.

```sql
CREATE TABLE asociacion (
  asociacionid        SERIAL PRIMARY KEY,
  confederacionid     INT REFERENCES confederacion(confederacionid),
  paisid              INT REFERENCES pais(paisid),        -- puede ser NULL si es multinacional
  nombre              VARCHAR(100) NOT NULL,
  acronimo            VARCHAR(20),
  logo_media_id       UUID REFERENCES media_asset(mediaid),
  meta                JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (confederacionid, nombre)
);
```

**Diccionario de datos**

- **`asociacion_id`**: (PK).
- **`confederacion_id`**: FK opcional.
- **`pais_id`**: FK opcional. Puede ser NULL si es multinacional.
- **`nombre`**: nombre (ej. “Asociación Paraguaya de Fútbol”).
- **`acronimo`**: “APF”.
- **`logo_media_id`**: FK opcional a `media_asset`.
- **`meta` (JSONB)**: reglas y notas.

**JSONB sugerido (`meta`)**

- `allowed_countries`: `["PRY"]` o `["USA","CAN"]`
- `discipline_style`: `"strict" | "lenient"`
- `registration_rules`: `{"foreign_limits":5}`
- `notes`: texto

**Ejemplo de inserts**

```sql
INSERT INTO asociacion (confederacion_id, pais_id, nombre, acronimo, meta) VALUES
((SELECT confederacion_id FROM confederacion WHERE acronimo='CONMEBOL'),
 (SELECT pais_id FROM pais WHERE iso_code='PRY'),
 'Asociación Paraguaya de Fútbol', 'APF',
 '{"allowed_countries":["PRY"],"notes":"Organiza ligas APF"}'),
((SELECT confederacion_id FROM confederacion WHERE acronimo='CONMEBOL'),
 NULL,
 'Major League Soccer', 'MLS',
 '{"allowed_countries":["USA","CAN"],"notes":"Liga multinacional"}');
```

---

## 5) Equipos (sin jugadores) + ciclos + relaciones

Estas tablas modelan la “vida” de un club sin entrar aún en jugadores:

- identidad + ubicación + escudo/colores (`equipo`)
- estadio principal y estadios alternativos en el tiempo (`equipo_estadio_hist`)
- rating actual (lo que decide partidos hoy) (`equipo_rating_actual`)
- ADN institucional (tendencia, potencial y volatilidad) (`equipo_institucion`)
- finanzas (presupuesto, deuda) (`equipo_finanzas`)
- rivalidades + H2H (`rivalidad`, `historial_enfrentamiento`)
- eventos externos que modifican el equipo (`evento_equipo`)

### Tabla: `equipo`

**Uso:** representa un club/equipo dentro de un `mundo`.
Es la tabla “identidad” del equipo (nombre, sede, asociación liga, estadio principal, escudo, colores).

**Depende de:** `mundo`, `ciudad`, `pais`, `asociacion`, `estadio`, `media_asset`.

```sql
CREATE TABLE equipo (
  equipoid            SERIAL PRIMARY KEY,
  mundoid             INT NOT NULL REFERENCES mundo(mundoid) ON DELETE CASCADE,

  -- identidad
  nombre              VARCHAR(100) NOT NULL,
  nombre_corto        VARCHAR(50),
  codigo_tla          VARCHAR(3),
  anio_fundacion      INT,

  -- geografía/cross-border
  ciudad_sede_id      INT REFERENCES ciudad(ciudadid),
  pais_origen_id      INT REFERENCES pais(paisid),       -- identidad (Mónaco)
  asociacion_liga_id  INT REFERENCES asociacion(asociacionid), -- dónde compite (ej Francia/MLS org)
  pais_liga_id        INT REFERENCES pais(paisid),       -- opcional (si querés mantener tu enfoque)
  estadio_principal_id INT REFERENCES estadio(estadioid),

  -- media
  escudo_media_id     UUID REFERENCES media_asset(mediaid),
  colores             JSONB NOT NULL DEFAULT '{}'::jsonb, -- {primario:"#...", secundario:"#..."}

  estado              VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
  meta                JSONB NOT NULL DEFAULT '{}'::jsonb,

  UNIQUE (mundoid, nombre)
);
```

**Diccionario de datos**

- **`equipo_id`**: (PK).
- **`mundo_id`**: FK a `mundo`. Permite múltiples partidas con mismos clubes.
- **`nombre`**: nombre del club (único por mundo).
- **`codigo_tla`**: abreviatura (ej. “OLI”, “CCP”). Útil para UI.
- **`anio_fundacion`**: año (opcional).
- **`ciudad_sede_id`**: FK a `ciudad` (donde está la sede).
- **`pais_origen_id`**: FK a `pais` (identidad). Ej: Mónaco.
- **`asociacion_liga_id`**: FK a `asociacion` (dónde compite).
- **`estadio_principal_id`**: FK a `estadio`. “casa” por defecto.
- **`escudo_media_id`**: FK a `media_asset`.
- **`colores` (JSONB)**: paleta para UI y kits.
- **`estado`**: `ACTIVO` por defecto. Sugeridos: `ACTIVO`, `DESAPARECIDO`, `SUSPENDIDO`.
- **`meta` (JSONB)**: flex.

**JSONB sugerido**

- En `colores`:
  - `primario`, `secundario`, `terciario` (hex). Ej: `{"primario":"#D50000","secundario":"#000000"}`
  - `uniforme_local`: `{"camiseta":"#...","short":"#...","medias":"#..."}`
- En `meta`:
  - `aliases`: `["Club Olimpia", "Olimpia Asunción"]`
  - `social`: `{"twitter":"...","instagram":"..."}`
  - `rivalries_hint`: lista de nombres para bootstrap
  - `colors_source`: `"manual"|"scraped"`

**Ejemplo de inserts**

```sql
INSERT INTO equipo (mundo_id, nombre, codigo_tla, anio_fundacion, ciudad_sede_id, pais_origen_id, asociacion_liga_id, estadio_principal_id, colores, estado, meta) VALUES
(1, 'Olimpia', 'OLI', 1902,
 (SELECT ciudad_id FROM ciudad WHERE nombre='Asunción'),
 (SELECT pais_id FROM pais WHERE iso_code='PRY'),
 (SELECT asociacion_id FROM asociacion WHERE acronimo='APF'),
 (SELECT estadio_id FROM estadio WHERE nombre='Estadio Defensores del Chaco'),
 '{"primario":"#FFFFFF","secundario":"#000000"}', 'ACTIVO', '{}'),
(1, 'Cerro Porteño', 'CCP', 1912,
 (SELECT ciudad_id FROM ciudad WHERE nombre='Asunción'),
 (SELECT pais_id FROM pais WHERE iso_code='PRY'),
 (SELECT asociacion_id FROM asociacion WHERE acronimo='APF'),
 (SELECT estadio_id FROM estadio WHERE nombre='Estadio General Pablo Rojas'),
 '{"primario":"#0033A0","secundario":"#D50000","terciario":"#FFFFFF"}', 'ACTIVO', '{}');
```

---

### Tabla: `equipo_estadio_hist`

**Uso:** registra **cambios temporales** de estadio (remodelación, sanción, mudanza, obras).
Permite que un equipo tenga:

- un estadio principal histórico (es_principal=true),
- uno o más estadios alternativos (es_principal=false) durante intervalos.

**Depende de:** `equipo`, `estadio`.

```sql
CREATE TABLE equipo_estadio_hist (
  equipoid        INT NOT NULL REFERENCES equipo(equipoid) ON DELETE CASCADE,
  estadioid       INT NOT NULL REFERENCES estadio(estadioid),
  fecha_inicio    DATE NOT NULL,
  fecha_fin       DATE,
  motivo          VARCHAR(100),
  es_principal    BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (equipoid, estadioid, fecha_inicio)
);
```

**Diccionario de datos**

- **`equipo_id`**: FK.
- **`estadio_id`**: FK.
- **`fecha_inicio`**: desde cuándo aplica esa relación.
- **`fecha_fin`**: hasta cuándo (NULL = vigente).
- **`motivo`**: texto (“Remodelación”, “Sanción”, “Mudanza”, “Venta”).
- **`es_principal`**: true si es “la casa” durante ese período; false si es alternativa/provisoria.
- **PK compuesta** `(equipo_id, estadio_id, fecha_inicio)` evita duplicados.

**Cómo lo consume el backend**

- Para un partido en fecha `X`:
  1) buscar registro vigente `fecha_inicio <= X AND (fecha_fin IS NULL OR fecha_fin >= X)`
  2) elegir el `es_principal=true` si existe; si no, fallback a `equipo.estadio_principal_id`.

**Ejemplo de inserts**

```sql
-- Olimpia: estadio en remodelación → juega provisoriamente en otro
INSERT INTO equipo_estadio_hist (equipo_id, estadio_id, fecha_inicio, fecha_fin, motivo, es_principal) VALUES
((SELECT equipo_id FROM equipo WHERE nombre='Olimpia' AND mundo_id=1),
 (SELECT estadio_id FROM estadio WHERE nombre='Estadio Osvaldo Domínguez Dibb'),
 '1960-01-01', '2024-04-29', 'Hasta remodelación', TRUE),
((SELECT equipo_id FROM equipo WHERE nombre='Olimpia' AND mundo_id=1),
 (SELECT estadio_id FROM estadio WHERE nombre='Estadio Defensores del Chaco'),
 '2024-04-30', NULL, 'Provisorio', FALSE);
```

---

### Tabla: `equipo_rating_actual`

**Uso:** representa el **estado competitivo actual** del equipo (lo que decide partidos hoy).
Debe actualizarse frecuentemente por el motor:

- tras cada partido (ELO, moral, fatiga),
- por eventos (crisis, takeover),
- por descanso/travel.

**Depende de:** `equipo`.

```sql
CREATE TABLE equipo_rating_actual (
  equipoid         INT PRIMARY KEY REFERENCES equipo(equipoid) ON DELETE CASCADE,
  elo_actual       FLOAT NOT NULL DEFAULT 1200,
  ataque           INT NOT NULL DEFAULT 50 CHECK (ataque BETWEEN 1 AND 100),
  defensa          INT NOT NULL DEFAULT 50 CHECK (defensa BETWEEN 1 AND 100),
  mediocampo       INT NOT NULL DEFAULT 50 CHECK (mediocampo BETWEEN 1 AND 100),

  moral            INT NOT NULL DEFAULT 50 CHECK (moral BETWEEN 0 AND 100),
  fatiga           INT NOT NULL DEFAULT 0 CHECK (fatiga BETWEEN 0 AND 100),
  cohesion         INT NOT NULL DEFAULT 50 CHECK (cohesion BETWEEN 0 AND 100),
  disciplina       INT NOT NULL DEFAULT 50 CHECK (disciplina BETWEEN 0 AND 100),

  -- estilo/táctica (flexible)
  tactica          JSONB NOT NULL DEFAULT '{}'::jsonb, -- {estilo:"PRESION_ALTA", ritmo:70, agresividad:60, ...}
  actualizado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Diccionario de datos**

- **`equipo_id`**: PK/FK (1:1 con equipo).
- **`elo_actual`**: rating numérico continuo (ej. 1200–2000).
  - **Uso motor:** base para probabilidades de resultado.
- **`ataque` / `defensa` / `mediocampo`**: 1–100.
  - **Uso motor:** componentes del rendimiento para generar xG/estilo.
- **`moral`**: 0–100. Sube/baja por resultados, crisis, rachas.
- **`fatiga`**: 0–100. Sube por carga de partidos/viajes; baja con descanso.
- **`cohesion`**: 0–100. Afecta consistencia, rendimiento en partidos grandes.
- **`disciplina`**: 0–100. Afecta tarjetas, penales, expulsiones.
- **`tactica` (JSONB)**: configuración flexible del estilo de juego.
- **`actualizado_en`**: timestamp (útil para debugging y jobs).

**JSONB sugerido (`tactica`)**

- `estilo`: `"POSESION"|"CONTRA"|"PRESION_ALTA"|"BLOQUE_BAJO"`
- `ritmo`: 0–100
- `agresividad`: 0–100
- `ancho`: 0–100
- `linea_defensiva`: `"alta"|"media"|"baja"`
- `pases`: `"corto"|"mixto"|"largo"`
- `presion`: 0–100
- `transiciones`: `{"repliegue":70,"salida_rapida":60}`

**Ejemplo de inserts**

```sql
INSERT INTO equipo_rating_actual (equipo_id, elo_actual, ataque, defensa, mediocampo, moral, fatiga, cohesion, disciplina, tactica) VALUES
((SELECT equipo_id FROM equipo WHERE nombre='Olimpia' AND mundo_id=1), 1566, 72, 70, 68, 60, 10, 65, 55, '{"estilo":"POSESION","ritmo":65,"presion":55}'),
((SELECT equipo_id FROM equipo WHERE nombre='Sportivo Ameliano' AND mundo_id=1), 1425, 58, 60, 55, 48, 25, 52, 50, '{"estilo":"CONTRA","ritmo":55,"presion":45}');
```

---

### Tabla: `equipo_institucion`

**Uso:** define el “ADN” del club: tendencia, potencial y estabilidad en el largo plazo.
Esta tabla es clave para tu idea de:

- “un equipo chico puede explotar y consolidarse”
- “un grande puede caer y volver a su basal”
  mediante `potencial_basal` + `volatilidad`.

**Depende de:** `equipo`.

```sql
CREATE TABLE equipo_institucion (
  equipoid              INT PRIMARY KEY REFERENCES equipo(equipoid) ON DELETE CASCADE,
  potencial_basal       INT NOT NULL DEFAULT 1200,
  volatilidad           INT NOT NULL DEFAULT 10 CHECK (volatilidad BETWEEN 1 AND 100),

  infraestructura       INT NOT NULL DEFAULT 10 CHECK (infraestructura BETWEEN 1 AND 20),
  nivel_scouting        INT NOT NULL DEFAULT 10 CHECK (nivel_scouting BETWEEN 1 AND 20),
  nivel_entrenamiento   INT NOT NULL DEFAULT 10 CHECK (nivel_entrenamiento BETWEEN 1 AND 20),
  nivel_juveniles       INT NOT NULL DEFAULT 10 CHECK (nivel_juveniles BETWEEN 1 AND 20),

  estabilidad_directiva INT NOT NULL DEFAULT 10 CHECK (estabilidad_directiva BETWEEN 1 AND 20),
  hinchada              INT NOT NULL DEFAULT 1000,     -- tamaño/impacto
  reputacion_historica  INT NOT NULL DEFAULT 5000,
  meta                  JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

**Diccionario de datos**

- **`equipo_id`**: PK/FK (1:1).
- **`potencial_basal`**: el “equilibrio” al que tiende el club (ELO basal).
  - **Uso motor:** drift/reversion a la media (regresión al basal).
- **`volatilidad`**: 1–100. Cuánto fluctúa el club y qué tan sensibles son sus cambios.
  - Alto = rachas y shocks fuertes; bajo = rendimiento estable.
- **`infraestructura`**: 1–20. “capacidad general” del club (instalaciones).
- **`nivel_scouting`**: 1–20. Afecta descubrimiento de talento (si luego hay mercado/jugadores).
- **`nivel_entrenamiento`**: 1–20. Afecta mejora de atributos, recuperación de fatiga.
- **`nivel_juveniles`**: 1–20. Afecta calidad/frecuencia de canteranos.
- **`estabilidad_directiva`**: 1–20. Afecta continuidad del proyecto (menos crisis, más coherencia táctica).
- **`hinchada`**: “fanbase score” (escala relativa) que impacta localía, presión y potencial económico.
- **`reputacion_historica`**: reputación institucional (no el rendimiento actual).
- **`meta` (JSONB)**: filosofía del club, identidad, etc.

**JSONB sugerido (`meta`)**

- `filosofia`: `"cantera"|"comprar_figuras"|"mixto"`
- `prioridades`: `{"liga":true,"copa":false}`
- `rivalries`: `[{"equipo":"Cerro Porteño","intensity":95}]`
- `finanzas_style`: `"conservador"|"agresivo"`
- `owner_notes`: texto

**Ejemplo de inserts**

```sql
INSERT INTO equipo_institucion (equipo_id, potencial_basal, volatilidad, infraestructura, nivel_scouting, nivel_entrenamiento, nivel_juveniles, estabilidad_directiva, hinchada, reputacion_historica, meta) VALUES
((SELECT equipo_id FROM equipo WHERE nombre='Cerro Porteño' AND mundo_id=1), 1539, 22, 19, 17, 17, 16, 12, 20000, 6000, '{"filosofia":"mixto"}'),
((SELECT equipo_id FROM equipo WHERE nombre='Atlético Tembetary' AND mundo_id=1), 1352, 44, 7, 9, 10, 9, 11, 2500, 1100, '{"filosofia":"cantera"}');
```

---

### Tabla: `equipo_finanzas`

**Uso:** finanzas del club. Se separa del rendimiento para que:

- un club pueda tener dinero pero jugar mal,
- o jugar bien pero estar quebrado.

**Depende de:** `equipo`.

```sql
CREATE TABLE equipo_finanzas (
  equipoid                INT PRIMARY KEY REFERENCES equipo(equipoid) ON DELETE CASCADE,
  moneda                  VARCHAR(3) NOT NULL DEFAULT 'USD',
  presupuesto_fichajes    DECIMAL(18,2) NOT NULL DEFAULT 0,
  presupuesto_salarial    DECIMAL(18,2) NOT NULL DEFAULT 0,
  deuda_total             DECIMAL(18,2) NOT NULL DEFAULT 0,

  poder_economico_base    INT NOT NULL DEFAULT 10 CHECK (poder_economico_base BETWEEN 1 AND 20),
  tipo_propiedad          VARCHAR(50),  -- SOCIOS/EMPRESA/ESTADO/TYCOON (validar en app)
  paciencia_directiva     INT NOT NULL DEFAULT 10 CHECK (paciencia_directiva BETWEEN 1 AND 20),

  actualizado_en          DATE NOT NULL DEFAULT CURRENT_DATE,
  meta                    JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

**Diccionario de datos**

- **`equipo_id`**: PK/FK (1:1).
- **`moneda`**: ISO (USD, EUR, PYG).
- **`presupuesto_fichajes`**: dinero para fichajes.
- **`presupuesto_salarial`**: masa salarial.
- **`deuda_total`**: deuda.
- **`poder_economico_base`**: 1–20. Capacidad “natural” de generar ingresos (mercado + marca).
- **`tipo_propiedad`**: SOCIOS/EMPRESA/ESTADO/TYCOON.
- **`paciencia_directiva`**: 1–20. Qué tan rápido “cortan cabezas” (afecta eventos/crisis).
- **`actualizado_en`**: fecha de última actualización.
- **`meta` (JSONB)**: sponsor, ingresos, etc.

**JSONB sugerido (`meta`)**

- `sponsors`: `[{"name":"X","amount":100000}]`
- `ticket_price_avg`: número
- `merch_income`: número
- `ffp`: `{"enabled":false}`
- `notes`: texto

**Ejemplo de inserts**

```sql
INSERT INTO equipo_finanzas (equipo_id, moneda, presupuesto_fichajes, presupuesto_salarial, deuda_total, poder_economico_base, tipo_propiedad, paciencia_directiva, meta) VALUES
((SELECT equipo_id FROM equipo WHERE nombre='Libertad' AND mundo_id=1), 'USD', 2500000, 1800000, 300000, 18, 'EMPRESA', 14, '{"sponsors":[{"name":"SponsorX","amount":500000}]}'),
((SELECT equipo_id FROM equipo WHERE nombre='General Caballero JLM' AND mundo_id=1), 'USD', 200000, 350000, 100000, 10, 'SOCIOS', 10, '{"notes":"Club austero"}');
```

---

### Tabla: `rivalidad`

**Uso:** rivalidades entre equipos (clásicos, derbys) con intensidad.
Canonización: siempre guardar `equipo_a_id < equipo_b_id` para evitar duplicados invertidos.

**Depende de:** `equipo`.

```sql
CREATE TABLE rivalidad (
  rivalidadid     SERIAL PRIMARY KEY,
  equipo_a_id     INT NOT NULL REFERENCES equipo(equipoid) ON DELETE CASCADE,
  equipo_b_id     INT NOT NULL REFERENCES equipo(equipoid) ON DELETE CASCADE,
  nombre          VARCHAR(100),
  intensidad      INT NOT NULL DEFAULT 50 CHECK (intensidad BETWEEN 0 AND 100),
  meta            JSONB NOT NULL DEFAULT '{}'::jsonb,
  CHECK (equipo_a_id < equipo_b_id),
  UNIQUE(equipo_a_id, equipo_b_id)
);
```

**Diccionario de datos**

- **`rivalidad_id`**: (PK).
- **`equipo_a_id`**, **`equipo_b_id`**: equipos involucrados (orden canónico).
- **`nombre`**: nombre del clásico (“Superclásico”, etc.).
- **`intensidad`**: 0–100. Afecta importancia del partido, presión y eventos.
- **`meta` (JSONB)**: tags y narrativa.

**JSONB sugerido**

- `derby_type`: `"historico"|"regional"|"moderno"`
- `notes`: texto
- `policing_risk`: 0–100 (si luego querés impacto en asistencia)

**Ejemplo de inserts**

```sql
INSERT INTO rivalidad (equipo_a_id, equipo_b_id, nombre, intensidad, meta) VALUES
(LEAST((SELECT equipo_id FROM equipo WHERE nombre='Olimpia' AND mundo_id=1),
       (SELECT equipo_id FROM equipo WHERE nombre='Cerro Porteño' AND mundo_id=1)),
 GREATEST((SELECT equipo_id FROM equipo WHERE nombre='Olimpia' AND mundo_id=1),
          (SELECT equipo_id FROM equipo WHERE nombre='Cerro Porteño' AND mundo_id=1)),
 'Superclásico', 95, '{"derby_type":"historico"}');
```

---

### Tabla: `historial_enfrentamiento`

**Uso:** caché persistente de Head-to-Head (H2H) entre dos equipos.
Se actualiza:

- por trigger al cerrar un partido,
- o por job batch al final de la fecha/temporada.

**Depende de:** `equipo`.

```sql
CREATE TABLE historial_enfrentamiento (
  historialid        SERIAL PRIMARY KEY,
  equipo_a_id        INT NOT NULL REFERENCES equipo(equipoid) ON DELETE CASCADE,
  equipo_b_id        INT NOT NULL REFERENCES equipo(equipoid) ON DELETE CASCADE,

  partidos_jugados   INT NOT NULL DEFAULT 0,
  victorias_a        INT NOT NULL DEFAULT 0,
  victorias_b        INT NOT NULL DEFAULT 0,
  empates            INT NOT NULL DEFAULT 0,
  goles_a            INT NOT NULL DEFAULT 0,
  goles_b            INT NOT NULL DEFAULT 0,

  ultimo_partido_fecha DATE,
  ultimo_ganador_id   INT REFERENCES equipo(equipoid), -- NULL si empate

  meta               JSONB NOT NULL DEFAULT '{}'::jsonb,
  CHECK (equipo_a_id < equipo_b_id),
  UNIQUE(equipo_a_id, equipo_b_id)
);
```

**Diccionario de datos**

- **`historial_id`**: (PK).
- **`equipo_a_id`**, **`equipo_b_id`**: orden canónico (`a < b`).
- **`partidos_jugados`**, **`victorias_a`**, **`victorias_b`**, **`empates`**: acumulados.
- **`goles_a`**, **`goles_b`**: goles acumulados.
- **`ultimo_partido_fecha`**: última fecha que jugaron.
- **`ultimo_ganador_id`**: FK a `equipo` (NULL si empate).
- **`meta` (JSONB)**: stats adicionales.

**JSONB sugerido**

- `streak`: `{"a_unbeaten":5}`
- `last_5`: `["W","D","L","W","W"]`
- `notes`: texto

**Ejemplo de inserts**

```sql
INSERT INTO historial_enfrentamiento (equipo_a_id, equipo_b_id, partidos_jugados, victorias_a, victorias_b, empates, goles_a, goles_b, ultimo_partido_fecha, ultimo_ganador_id, meta) VALUES
(LEAST(1,2), GREATEST(1,2), 10, 4, 3, 3, 12, 11, '2025-05-01', 1, '{"notes":"Duelo parejo"}'),
(LEAST(3,7), GREATEST(3,7), 2, 2, 0, 0, 5, 1, '2025-03-15', 3, '{}');
```

> Nota: en una carga real, reemplazá los IDs `1,2,3,7` por subqueries como en `rivalidad`.

---

### Tabla: `evento_equipo`

**Uso:** eventos externos que afectan al equipo por un período.
Ejemplos:

- `CRISIS` (baja moral/cohesión),
- `TAKEOVER` (sube finanzas y/o reputación),
- `SANCTION` (sin público, sanción de estadio),
- `GOLDEN_ERA` (mejora de rendimiento temporal),
- `INJURY_CRISIS` (si luego agregás jugadores).

**Depende de:** `mundo`, `equipo`.

```sql
CREATE TABLE evento_equipo (
  eventoid       SERIAL PRIMARY KEY,
  mundoid        INT NOT NULL REFERENCES mundo(mundoid) ON DELETE CASCADE,
  equipoid       INT NOT NULL REFERENCES equipo(equipoid) ON DELETE CASCADE,
  fecha_inicio   DATE NOT NULL,
  fecha_fin      DATE,
  tipo           VARCHAR(50) NOT NULL,               -- 'CRISIS','TAKEOVER','GOLDEN_ERA','SANCTION','TRAVEL_ISSUE',...
  severidad      INT NOT NULL DEFAULT 1 CHECK (severidad BETWEEN 1 AND 10),
  modificadores  JSONB NOT NULL DEFAULT '{}'::jsonb, -- afecta moral/fatiga/elo/finanzas/etc.
  descripcion    TEXT
);
```

```sql
CREATE INDEX idx_evento_equipo_mundo_fecha ON evento_equipo(mundoid, fecha_inicio, fecha_fin);
```

**Diccionario de datos**

- **`evento_id`**: (PK).
- **`mundo_id`**: FK.
- **`equipo_id`**: FK.
- **`fecha_inicio`**: inicio del evento.
- **`fecha_fin`**: fin (NULL = vigente).
- **`tipo`**: string del evento (validar en backend).
- **`severidad`**: 1–10.
- **`modificadores` (JSONB)**: define qué cambia y cuánto.
- **`descripcion`**: texto humano.

**JSONB sugerido (`modificadores`)**

- `rating_mult`: `{"ataque":0.95,"defensa":0.98}`
- `elo_delta`: `-30` (shock instantáneo)
- `moral_delta`: `-15`
- `fatiga_mult`: `1.10`
- `finanzas`: `{"presupuesto_fichajes_delta":500000}`
- `localia`: `{"sin_publico":true}`
- `tactica_lock`: `{"estilo_forzado":"BLOQUE_BAJO"}`

**Ejemplo de inserts**

```sql
INSERT INTO evento_equipo (mundo_id, equipo_id, fecha_inicio, fecha_fin, tipo, severidad, modificadores, descripcion) VALUES
(1, (SELECT equipo_id FROM equipo WHERE nombre='Olimpia' AND mundo_id=1), '2025-04-01', '2025-05-15', 'CRISIS', 6,
 '{"moral_delta":-12,"cohesion_delta":-8,"elo_delta":-20}', 'Crisis institucional y malos resultados'),
(1, (SELECT equipo_id FROM equipo WHERE nombre='Libertad' AND mundo_id=1), '2025-07-01', NULL, 'TAKEOVER', 7,
 '{"finanzas":{"presupuesto_fichajes_delta":1500000},"reputacion_delta":300}', 'Nuevo inversor y refuerzo económico');
```

---

## Checklist de implementación backend (Python) — Bloques 3–5

Módulos típicos para consumir estas tablas:

- **GeoService**
  - CRUD de confederaciones/países/regiones/ciudades
  - cálculo de distancias (`ciudad.coordenadas`)
- **ClimateService**
  - lookup de `perfil_climatico` por ciudad
  - generación de clima “del partido” (si lo implementás) usando `tags/meta`
- **StadiumService**
  - estado del estadio (activo/remodelación)
  - selección de sede alternativa (neutral o histórica)
- **AssociationService**
  - validación de ligas cross-border (allowed_countries en `meta`)
- **TeamService**
  - construir “TeamProfile” agregando:
    - identidad (`equipo`)
    - rating actual (`equipo_rating_actual`)
    - ADN (`equipo_institucion`)
    - finanzas (`equipo_finanzas`)
    - estadio vigente (`equipo_estadio_hist`)
- **Rivalry/H2H Service**
  - canonización de pares (LEAST/GREATEST)
  - actualización de `historial_enfrentamiento` tras cada partido
- **EventSystem**
  - aplicar `evento_equipo.modificadores` al simular fechas/partidos
  - expirar eventos por `fecha_fin`

---

## 6) COMPETICIONES + EDICIONES + ETAPAS/GRUPOS/RONDAS + PARTICIPANTES

Este bloque define la **arquitectura de torneos** del simulador. La clave es separar:

* **`competencia`** : el “concepto”/marca del torneo (no depende de temporada).
* **`competencia_edicion`** : una edición del torneo en una temporada (donde vive el fixture y el avance real).
* **`etapa` / `grupo` / `ronda`** : estructura del formato (liga, grupos, eliminación, etc.).
* **`participante`** : qué equipos participan y cómo ingresaron.
* **`tabla_posiciones`** : standings persistido (cache oficial para UI y para reglas).

### Cómo lo consume el backend (visión de módulos)

Un backend Python normalmente organiza esto así:

* **CompetitionService** : CRUD de `competencia` y lectura de `configuracion_base`.
* **EditionService** : crear `competencia_edicion`, controlar `estado` y fechas.
* **EligibilityEngine** : evaluar `regla_elegibilidad.regla` para determinar equipos elegibles.
* **FormatBuilder / FixtureGenerator** : generar etapas/grupos/rondas/partidos desde `config_etapa` (+ `perfil_sorteo` si aplica).
* **MatchService** : simular partidos, persistir `partido` + tablas 1:1, y disparar efectos (elo, fatiga, standings).
* **StandingsService** : mantener `tabla_posiciones` consistente e idempotente.

---

### Tabla: `competencia`

**Uso:** Define el torneo base (ej. “Primera División”, “Copa Paraguay”). Aquí viven identidad, alcance/organizador, reputación base y configuración por defecto.

**Depende de:** `mundo`, `cat_competencia_tipo`, y opcionalmente `confederacion`, `pais`, `region`, `asociacion`, `media_asset`.

```sql
CREATE TABLE competencia (
  competencia_id        SERIAL PRIMARY KEY,
  mundo_id              INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  nombre               VARCHAR(100) NOT NULL,
  tipo_id               INT NOT NULL REFERENCES cat_competencia_tipo(tipo_id),

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
```

**Diccionario de datos (columnas)**

* **`competencia_id`** : PK.
* **`mundo_id`** : FK. Permite replicar el mismo set de torneos en múltiples mundos/partidas.
* **`nombre`** : nombre del torneo (único por mundo).
* **`tipo_id`** : FK a `cat_competencia_tipo` (`LIGA`, `COPA`, etc.). Define el “macro-motor” que se espera.
* **`confederacion_id` / `pais_id` / `region_id` / `asociacion_id`** : alcance/organizador.
  * Reglas recomendadas:
    * Continental → `confederacion_id`
    * Nacional → `pais_id` + `asociacion_id`
    * Regional → `region_id` + `asociacion_id`
* **`logo_media_id`** : FK a `media_asset` (UI).
* **`reputacion_base`** : prestigio “por marca” del torneo. Se usa para narrativa, ranking, atractivo y/o pesos de simulación.
* **`configuracion_base` (JSONB)** : plantilla/parametrización por defecto del torneo.
* **`meta` (JSONB)** : metadata libre (estado, alias, fuentes, notas).

**JSONB sugerido**

* `configuracion_base` (campos típicos):
  * `nivel` (int), `categoria` (string)
  * `formato` (string), `sistema` (string)
  * `equipos_default` (int), `vueltas` (int), `partidos_por_equipo` (int)
  * `puntos`: `{victoria, empate, derrota}`
  * `desempate`: `["puntos","diferencia_gol","goles_favor","enfrentamientos_directos","fair_play"]`
  * `ascenso` / `descenso`: objetos con `aplica`, `cupos_default`, `metodo`, etc.
  * `clasificacion_internacional`: cupos/premios
  * `mercado`: restricciones (ej. `tope_extranjeros_matchday`)
* `meta`:
  * `estado`: `"Activo"|"Extinto"|"Pausado"`
  * `aliases`: `[]`
  * `source`: `"manual"|"import"|"community"`
  * `notes`: texto

**Ejemplos de insert (2 registros)**

```sql
INSERT INTO competencia (
  mundo_id, nombre, tipo_id, pais_id, asociacion_id,
  reputacion_base, configuracion_base, meta
) VALUES
(
  1,
  'Primera División',
  (SELECT tipo_id FROM cat_competencia_tipo WHERE codigo='LIGA'),
  (SELECT pais_id FROM pais WHERE iso_code='PRY'),
  (SELECT asociacion_id FROM asociacion WHERE acronimo='APF'),
  8200,
  '{
    "nivel":1,"categoria":"Profesional","formato":"Liga","sistema":"TodosContraTodos",
    "equipos_default":12,"vueltas":2,
    "puntos":{"victoria":3,"empate":1,"derrota":0},
    "desempate":["puntos","diferencia_gol","goles_favor","enfrentamientos_directos","fair_play"],
    "descenso":{"aplica":true,"cupos_default":2,"metodo":"Promedio","ventana_temporadas":3}
  }'::jsonb,
  '{"estado":"Activo"}'::jsonb
),
(
  1,
  'Copa Paraguay',
  (SELECT tipo_id FROM cat_competencia_tipo WHERE codigo='COPA'),
  (SELECT pais_id FROM pais WHERE iso_code='PRY'),
  (SELECT asociacion_id FROM asociacion WHERE acronimo='APF'),
  6000,
  '{
    "categoria":"Copa Nacional","formato":"EliminacionDirecta",
    "rondas_default":7,"partido_unico":true,
    "desempate":{"prorroga":true,"penales":true},
    "clasificacion_internacional":{"aplica":true,"premio":"CupoSudamericana"}
  }'::jsonb,
  '{"estado":"Activo"}'::jsonb
);
```

### Tabla: `competencia_reputacion`

**Uso:** Reputación variable por **alcance** y opcionalmente por **temporada** . Sirve para modelar cambios a lo largo del tiempo y diferencias “local vs global”.

**Depende de:** `competencia`, `temporada`.

```sql
CREATE TABLE competencia_reputacion (
  competencia_id    INT NOT NULL REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  alcance          VARCHAR(20) NOT NULL,     -- 'WORLD','CONFED','PAIS'
  temporada_id      INT REFERENCES temporada(temporada_id) ON DELETE CASCADE,
  valor            INT NOT NULL DEFAULT 5000,
  actualizado_en   TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (competencia_id, alcance, temporada_id),
  CHECK (alcance IN ('WORLD','CONFED','PAIS'))
);
```

* **`competencia_id`** : FK.
* **`alcance`** : `WORLD`/`CONFED`/`PAIS`.
* **`temporada_id`** : si NULL, interpreta “default general”; si no NULL, override específico de temporada.
* **`valor`** : reputación efectiva.
* **`actualizado_en`** : auditoría.

**Regla de resolución recomendada (backend)**

1. buscar (competencia_id, alcance, temporada_id)
2. si no existe, buscar (competencia_id, alcance, NULL)
3. fallback a `competencia.reputacion_base`

**Ejemplos de insert**

```sql
INSERT INTO competencia_reputacion (competencia_id, alcance, temporada_id, valor) VALUES
(
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Primera División'),
  'PAIS',
  (SELECT temporada_id FROM temporada WHERE mundo_id=1 AND nombre='2025'),
  8200
),
(
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Copa Paraguay'),
  'WORLD',
  NULL,
  3200
);
```

### Tabla: `regla_elegibilidad`

**Uso:** Define elegibilidad de participantes mediante una regla declarativa en JSON. Evita hardcodear reglas por torneo.

**Depende de:** `competencia`.

```sql
CREATE TABLE regla_elegibilidad (
  elegibilidad_id   SERIAL PRIMARY KEY,
  competencia_id    INT NOT NULL REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  regla            JSONB NOT NULL,
  nota             TEXT
);
```

**Diccionario de datos**

* **`elegibilidad_id`** : PK.
* **`competencia_id`** : FK.
* **`regla` (JSONB)** : regla evaluable por `EligibilityEngine`.
* **`nota`** : explicación humana.

**JSONB sugerido (`regla`)**

Recomendación: mini-DSL versionado.

* `version`: 1
* `all`: lista de predicados AND
* `any`: lista de predicados OR
* predicados típicos:
  * `pais_in`: `[pais_id,...]`
  * `asociacion_in`: `[asociacion_id,...]`
  * `region_in`: `[region_id,...]`
  * `estado_equipo`: `"ACTIVO"`
  * `max_por_pais`: int (torneos internacionales)
  * `requiere_campeon_de`: `{competencia_id: X}` (supercopas)

> Nota importante: **no metas subqueries dentro del JSON** en SQL. El backend debe resolver IDs y construir el JSON.

**Ejemplos de insert**

```sql
INSERT INTO regla_elegibilidad (competencia_id, regla, nota) VALUES
(
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Copa Paraguay'),
  '{"version":1,"all":[{"estado_equipo":"ACTIVO"},{"pais_in":[1]}]}'::jsonb,
  'Copa: equipos activos del país (pais_id=1 ejemplo)'
),
(
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Primera División'),
  '{"version":1,"all":[{"estado_equipo":"ACTIVO"},{"asociacion_in":[1]}]}'::jsonb,
  'Liga: equipos activos de la asociación (asociacion_id=1 ejemplo)'
);
```

---

### Tabla: `competencia_edicion`

**Uso:** Edición concreta de un torneo dentro de una temporada. Aquí se define el período real, el estado y overrides.

**Depende de:** `competencia`, `temporada`.

```sql
CREATE TABLE competencia_edicion (
  edicion_id        SERIAL PRIMARY KEY,
  competencia_id    INT NOT NULL REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  temporada_id      INT NOT NULL REFERENCES temporada(temporada_id) ON DELETE CASCADE,
  nombre_display   VARCHAR(100),
  fecha_inicio     DATE,
  fecha_fin        DATE,
  estado           VARCHAR(20) NOT NULL DEFAULT 'PROGRAMADA', -- PROGRAMADA/EN_CURSO/FINALIZADA
  reglas_edicion   JSONB NOT NULL DEFAULT '{}'::jsonb,
  meta             JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (competencia_id, temporada_id),
  CHECK (estado IN ('PROGRAMADA','EN_CURSO','FINALIZADA'))
);
```

**Diccionario de datos**

* **`edicion_id`** : PK.
* **`competencia_id`** : FK al torneo base.
* **`temporada_id`** : FK.
* **`nombre_display`** : etiqueta UI (si NULL, el backend/UI puede componerla).
* **`fecha_inicio`/`fecha_fin`** : período real (puede ser subconjunto de temporada).
* **`estado`** : workflow.
* **`reglas_edicion` (JSONB)** : overrides (seed fixture, desempates, cupos especiales).
* **`meta` (JSONB)** : sponsor, TV deal, notas.

**JSONB sugerido**

* `reglas_edicion`:
  * `fixture_seed`: int
  * `equipos_override`: int
  * `criterios_desempate_override`: `[...]`
  * `calendar`: `{hora_default, dias, ventanas}`
* `meta`: `{sponsor, tv_deal, notes}`

**Ejemplos de insert**

```sql
INSERT INTO competencia_edicion (
  competencia_id, temporada_id, nombre_display, fecha_inicio, fecha_fin, estado, reglas_edicion, meta
) VALUES
(
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Primera División'),
  (SELECT temporada_id FROM temporada WHERE mundo_id=1 AND nombre='2025'),
  'Primera División 2025',
  '2025-02-01','2025-11-30',
  'PROGRAMADA',
  '{"fixture_seed":1234}'::jsonb,
  '{"sponsor":"Banco X"}'::jsonb
),
(
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Copa Paraguay'),
  (SELECT temporada_id FROM temporada WHERE mundo_id=1 AND nombre='2025'),
  'Copa Paraguay 2025',
  '2025-05-01','2025-10-15',
  'PROGRAMADA',
  '{"partido_unico":true}'::jsonb,
  '{"notes":"Incluye UFI"}'::jsonb
);
```

---

### Tabla: `etapa`

**Uso:** Fases dentro de una edición (liga, grupos, knockout, swiss, playoffs, etc.). Es el “contrato” principal del `FixtureGenerator`.

**Depende de:** `competencia_edicion`, `cat_etapa_tipo`.

```sql
CREATE TABLE etapa (
  etapa_id        SERIAL PRIMARY KEY,
  edicion_id      INT NOT NULL REFERENCES competencia_edicion(edicion_id) ON DELETE CASCADE,
  orden          INT NOT NULL,
  tipo_id         INT NOT NULL REFERENCES cat_etapa_tipo(tipo_id),
  nombre         VARCHAR(100) NOT NULL,
  fecha_inicio   DATE,
  fecha_fin      DATE,
  config_etapa   JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (edicion_id, orden)
);
```

* **`orden`** : el motor procesa etapas en orden.
* **`tipo_id`** : define algoritmo (LEAGUE/GROUPS/KNOCKOUT…).
* **`config_etapa` (JSONB)** : parámetros del algoritmo.

**JSONB sugerido (`config_etapa`)**

* LEAGUE: `{vueltas, criterios_desempate, calendario}`
* GROUPS: `{grupos, equipos_por_grupo, clasifican_por_grupo, vueltas_grupo}`
* KNOCKOUT: `{rondas:[...], ida_vuelta, penales, prorroga}`
* SWISS: `{rondas, pairing:"elo|ranking", no_repetir_rival:true}`

**Ejemplos de insert**

```sql
INSERT INTO etapa (edicion_id, orden, tipo_id, nombre, fecha_inicio, fecha_fin, config_etapa) VALUES
(
  (SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Primera División 2025'),
  1,
  (SELECT tipo_id FROM cat_etapa_tipo WHERE codigo='LEAGUE'),
  'Fase Regular',
  '2025-02-01','2025-11-30',
  '{"vueltas":2,"criterios_desempate":["puntos","dg","gf"]}'::jsonb
),
(
  (SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Copa Paraguay 2025'),
  1,
  (SELECT tipo_id FROM cat_etapa_tipo WHERE codigo='KNOCKOUT'),
  'Eliminación',
  '2025-05-01','2025-10-15',
  '{"rondas":["R64","R32","R16","QF","SF","F"],"ida_vuelta":false,"penales":true,"prorroga":true}'::jsonb
);
```

---

### Tabla: `grupo`

**Uso:** Agrupaciones dentro de una etapa (Grupo A/B, Zona 1/2). En ligas sin grupos se puede no usar.

**Depende de:** `etapa`.

```sql
CREATE TABLE grupo (
  grupo_id       SERIAL PRIMARY KEY,
  etapa_id       INT NOT NULL REFERENCES etapa(etapa_id) ON DELETE CASCADE,
  codigo        VARCHAR(10) NOT NULL,          -- 'A','B','1'
  nombre        VARCHAR(50),
  meta          JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE(etapa_id, codigo)
);
```

**Diccionario de datos**

* **`codigo`** : clave corta (A, B, 1…).
* **`meta` (JSONB)** : restricciones/estética/semántica del grupo.

**JSONB sugerido**

* `restricciones`: `{max_por_pais:2, evitar_mismo_pais:true}`
* `color_ui`: `"#..."`

**Ejemplos de insert**

```sql
INSERT INTO grupo (etapa_id, codigo, nombre, meta) VALUES
((SELECT etapa_id FROM etapa WHERE nombre='Eliminación' LIMIT 1), 'A', 'Llave A', '{}'::jsonb),
((SELECT etapa_id FROM etapa WHERE nombre='Eliminación' LIMIT 1), 'B', 'Llave B', '{"color_ui":"#0033A0"}'::jsonb);
```

---

### Tabla: `ronda`

**Uso:** Jornadas en liga / rondas en copa. `pierna` soporta ida/vuelta.

**Depende de:** `etapa`, opcional `grupo`.

```sql
CREATE TABLE ronda (
  ronda_id        SERIAL PRIMARY KEY,
  etapa_id        INT NOT NULL REFERENCES etapa(etapa_id) ON DELETE CASCADE,
  grupo_id        INT REFERENCES grupo(grupo_id) ON DELETE CASCADE,
  numero         INT NOT NULL,
  pierna         INT NOT NULL DEFAULT 1,      -- 1 o 2 (ida/vuelta)
  fecha_programada DATE,
  nombre         VARCHAR(100),
  meta           JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (etapa_id, grupo_id, numero, pierna)
);
```

**Diccionario de datos**

* **`numero`** : secuencia.
* **`fecha_programada`** : referencia para schedule.
* **`meta` (JSONB)** : slots, TV, restricciones.

**Ejemplos de insert**

```sql
INSERT INTO ronda (etapa_id, grupo_id, numero, pierna, fecha_programada, nombre) VALUES
((SELECT etapa_id FROM etapa WHERE nombre='Fase Regular' LIMIT 1), NULL, 1, 1, '2025-02-01', 'Jornada 1'),
((SELECT etapa_id FROM etapa WHERE nombre='Fase Regular' LIMIT 1), NULL, 2, 1, '2025-02-08', 'Jornada 2');
```

---

### Tabla: `participante`

**Uso:** Equipos participantes por edición, con trazabilidad de entrada (método, seed, bombo, grupo inicial) y resultados finales.

**Depende de:** `competencia_edicion`, `equipo`, opcional `cat_metodo_clasificacion`, `grupo`.

```sql
CREATE TABLE participante (
  participante_id        SERIAL PRIMARY KEY,
  edicion_id             INT NOT NULL REFERENCES competencia_edicion(edicion_id) ON DELETE CASCADE,
  equipo_id              INT NOT NULL REFERENCES equipo(equipo_id) ON DELETE CASCADE,

  metodo_id              INT REFERENCES cat_metodo_clasificacion(metodo_id),
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
```

**Diccionario de datos**

* `metodo_id`: útil para supercopas, cupos internacionales, etc.
* `grupo_id_inicial` + `grupo_inicial_texto`: soporta importaciones y luego normalización.
* `puntos_ranking_ganados`: si implementás coeficientes.

**JSONB sugerido (`meta`)**

* `source`: `"import"|"sim"|"manual"`
* `qualifier`: `{competencia_id, temporada_id, posicion}`
* `fair_play_pts`: int

**Ejemplos de insert**

```sql
INSERT INTO participante (edicion_id, equipo_id, metodo_id, seed, bombo_sorteo, meta) VALUES
(
  (SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Primera División 2025'),
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Olimpia'),
  (SELECT metodo_id FROM cat_metodo_clasificacion WHERE codigo='INVITADO'),
  1, 1,
  '{"source":"import"}'::jsonb
),
(
  (SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Primera División 2025'),
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Cerro Porteño'),
  (SELECT metodo_id FROM cat_metodo_clasificacion WHERE codigo='INVITADO'),
  2, 1,
  '{"source":"import"}'::jsonb
);
```

---

### Tabla: `tabla_posiciones`

**Uso:** Standings persistido por edición/etapa/grupo. Es el “estado oficial” para UI y reglas (clasificación, descenso, etc.). Debe ser mantenida por el backend al simular/registrar partidos.

**Depende de:** `competencia_edicion`, `etapa`, `grupo` (opcional), `equipo`.

```sql
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

CREATE INDEX idx_tabla_posiciones_orden
  ON tabla_posiciones(edicion_id, etapa_id, grupo_id, pts DESC, dg DESC, gf DESC);
```

**Diccionario de datos**

* `dg`: recomendable recalcular como `gf - gc` (no confiar en input).
* `forma`: convención fija (ej. últimos 5 resultados “GEPGG” o “G-E-P-G-G”).
* `meta` (JSONB): penalizaciones/fair play/h2h.

**JSONB sugerido (`meta`)**

* `fair_play`: `{amarillas, rojas, puntos}`
* `penalizaciones`: `[{motivo, pts, fecha}]`
* `h2h_cache`: opcional si desempate head-to-head es costoso

**Ejemplos de insert**

```sql
INSERT INTO tabla_posiciones (edicion_id, etapa_id, grupo_id, equipo_id, meta) VALUES
(
  (SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Primera División 2025'),
  (SELECT etapa_id FROM etapa WHERE nombre='Fase Regular' AND edicion_id=(SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Primera División 2025')),
  NULL,
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Olimpia'),
  '{"fair_play":{"amarillas":0,"rojas":0,"puntos":0}}'::jsonb
),
(
  (SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Primera División 2025'),
  (SELECT etapa_id FROM etapa WHERE nombre='Fase Regular' AND edicion_id=(SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Primera División 2025')),
  NULL,
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Cerro Porteño'),
  '{}'::jsonb
);
```

---

## 7) SEEDING / BOMBOS (perfil de sorteo)

### Tabla: `perfil_sorteo`

**Uso:** Define cómo se sortean bombos/grupos y restricciones (máx por país, evitar emparejamientos, etc.). Una etapa puede referenciar un perfil (`etapa.perfil_sorteo_id`) para que el generador aplique esa lógica.

```sql
CREATE TABLE perfil_sorteo (
  perfil_sorteo_id    SERIAL PRIMARY KEY,
  nombre             VARCHAR(100) NOT NULL UNIQUE,
  config             JSONB NOT NULL
);

ALTER TABLE etapa
  ADD COLUMN perfil_sorteo_id INT REFERENCES perfil_sorteo(perfil_sorteo_id);
```

**Diccionario de datos**

* `config` (JSONB): contrato del sorteo.

**JSONB sugerido (`config`)**

* `version`: 1
* `criterio_seed`: `"elo"|"ranking"|"manual"`
* `bombos`: int
* `asignacion_grupos`: `{grupos, equipos_por_grupo}`
* `restricciones`:
  * `max_por_pais`: int
  * `evitar_mismo_grupo`: `{pais:true, asociacion:true}`
  * `pares_prohibidos`: `[{equipo_a, equipo_b}]`

**Ejemplos de insert**

```sql
INSERT INTO perfil_sorteo (nombre, config) VALUES
(
  'Sorteo Básico - 2 Bombos',
  '{"version":1,"criterio_seed":"elo","bombos":2,
    "asignacion_grupos":{"grupos":2,"equipos_por_grupo":4},
    "restricciones":{"max_por_pais":2,"evitar_mismo_grupo":{"pais":true}}}'::jsonb
),
(
  'Sorteo Libre',
  '{"version":1,"criterio_seed":"manual","bombos":1,
    "asignacion_grupos":{"grupos":4,"equipos_por_grupo":4},
    "restricciones":{}}'::jsonb
);
```

---

## 8) PARTIDOS + CLIMA + CONTEXTO + STATS

Este bloque guarda el **fixture** y el **resultado de simulación** , separando:

* core del partido (`partido`)
* clima puntual (`partido_clima`)
* contexto humano/logístico (`partido_contexto`)
* estadísticas por equipo (`partido_stats_equipo`)

### Tabla: `partido`

**Uso:** Entidad principal del match. El backend crea partidos como `PENDIENTE` (fixture) y luego los marca `SIMULADO` o `JUGADO`.

**Depende de:** `competencia_edicion`, `etapa`, `ronda`, `grupo`, `equipo`, `estadio`, `ciudad`.

```sql
CREATE TABLE partido (
  partido_id        BIGSERIAL PRIMARY KEY,
  edicion_id        INT NOT NULL REFERENCES competencia_edicion(edicion_id) ON DELETE CASCADE,
  etapa_id          INT NOT NULL REFERENCES etapa(etapa_id) ON DELETE CASCADE,
  ronda_id          INT REFERENCES ronda(ronda_id) ON DELETE SET NULL,
  grupo_id          INT REFERENCES grupo(grupo_id) ON DELETE SET NULL,

  local_equipo_id   INT NOT NULL REFERENCES equipo(equipo_id),
  visita_equipo_id  INT NOT NULL REFERENCES equipo(equipo_id),

  estadio_real_id  INT REFERENCES estadio(estadio_id),
  es_neutral       BOOLEAN NOT NULL DEFAULT FALSE,
  ciudad_id         INT REFERENCES ciudad(ciudad_id),

  fecha_hora       TIMESTAMP,
  jornada          INT,
  fase_label       VARCHAR(50),

  asistencia       INT,

  goles_local      INT,
  goles_visita     INT,
  penales_local    INT,
  penales_visita   INT,

  estado           VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE', -- PENDIENTE/SIMULADO/JUGADO
  reporte_motor    JSONB NOT NULL DEFAULT '{}'::jsonb,

  CHECK (local_equipo_id <> visita_equipo_id),
  CHECK (estado IN ('PENDIENTE','SIMULADO','JUGADO'))
);

CREATE INDEX idx_partido_fecha ON partido(fecha_hora);
CREATE INDEX idx_partido_equipos ON partido(local_equipo_id, visita_equipo_id);
CREATE INDEX idx_partido_edicion_jornada ON partido(edicion_id, jornada);
CREATE INDEX idx_partido_etapa_grupo_ronda ON partido(etapa_id, grupo_id, ronda_id);
```

**Diccionario de datos**

* `estadio_real_id`: puede diferir del estadio principal por sanciones/mudanzas/neutralidad.
* `reporte_motor` (JSONB): trazabilidad explicable para debugging y para UI.

**JSONB sugerido (`reporte_motor`)**

* `version`: string
* `seed`: int
* `xg`: `{local, visita}`
* `factors`: `{elo_diff, localia, clima, fatiga, presion}`
* `timeline`: lista de eventos (si luego agregás jugadores)
* `notes`: texto

**Ejemplos de insert**

```sql
-- Fixture pendiente
INSERT INTO partido (
  edicion_id, etapa_id, ronda_id, grupo_id,
  local_equipo_id, visita_equipo_id,
  estadio_real_id, es_neutral, ciudad_id,
  fecha_hora, jornada, fase_label, estado
) VALUES
(
  (SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Primera División 2025'),
  (SELECT etapa_id FROM etapa WHERE nombre='Fase Regular' AND edicion_id=(SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Primera División 2025')),
  (SELECT ronda_id FROM ronda WHERE nombre='Jornada 1' LIMIT 1),
  NULL,
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Olimpia'),
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Cerro Porteño'),
  (SELECT estadio_id FROM estadio WHERE nombre='Estadio Defensores del Chaco'),
  false,
  (SELECT ciudad_id FROM ciudad WHERE nombre='Asunción' LIMIT 1),
  '2025-02-01 20:00:00',
  1,
  'Jornada 1',
  'PENDIENTE'
),
(
  (SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Copa Paraguay 2025'),
  (SELECT etapa_id FROM etapa WHERE nombre='Eliminación' AND edicion_id=(SELECT edicion_id FROM competencia_edicion WHERE nombre_display='Copa Paraguay 2025')),
  NULL,
  NULL,
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Libertad'),
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Guaraní'),
  (SELECT estadio_id FROM estadio WHERE nombre='Estadio General Pablo Rojas'),
  true,
  (SELECT ciudad_id FROM ciudad WHERE nombre='Asunción' LIMIT 1),
  '2025-06-15 19:30:00',
  NULL,
  'R16',
  'PENDIENTE'
);
```

---

### Tabla: `partido_clima`

**Uso:** Clima puntual del match (separado del clima típico de la ciudad).

```sql
CREATE TABLE partido_clima (
  partido_id       BIGINT PRIMARY KEY REFERENCES partido(partido_id) ON DELETE CASCADE,
  temperatura_c   FLOAT,
  humedad         FLOAT,
  viento_kmh      FLOAT,
  lluvia_mm       FLOAT,
  condicion       VARCHAR(30),
  tags            JSONB NOT NULL DEFAULT '[]'::jsonb,
  meta            JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

* `tags`: `["lluvia","cancha_pesada","calor_extremo","viento_fuerte"]`
* `meta`: `{source:"simulated|real", pitch_effects:{...}}`

**Ejemplos de insert**

```sql
INSERT INTO partido_clima (partido_id, temperatura_c, humedad, viento_kmh, lluvia_mm, condicion, tags, meta) VALUES
(
  (SELECT partido_id FROM partido ORDER BY partido_id DESC LIMIT 1),
  31, 70, 12, 0,
  'SOLEADO',
  '["calor"]'::jsonb,
  '{"source":"simulated"}'::jsonb
),
(
  (SELECT partido_id FROM partido ORDER BY partido_id DESC OFFSET 1 LIMIT 1),
  24, 88, 18, 12.5,
  'LLUVIA',
  '["lluvia","cancha_pesada"]'::jsonb,
  '{"source":"simulated","pitch_effects":{"ball_speed_mult":0.92}}'::jsonb
);
```

### Tabla: `partido_contexto`

**Uso:** Factores humanos/logísticos que afectan simulación (hinchada, viaje, altitud, rivalidad, presión).

```sql
CREATE TABLE partido_contexto (
  partido_id            BIGINT PRIMARY KEY REFERENCES partido(partido_id) ON DELETE CASCADE,
  intensidad_hinchada  INT NOT NULL DEFAULT 50 CHECK (intensidad_hinchada BETWEEN 0 AND 100),
  viaje_km_visita      INT,
  altitud_m            INT,
  rivalidad_intensidad INT,
  presion              INT NOT NULL DEFAULT 50 CHECK (presion BETWEEN 0 AND 100),
  external             JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

**JSONB sugerido (`external`)**

* `travel`: `{delay:true, sleep_hours:6}`
* `importance`: `{derby:true, tv:true}`
* `evento`: `{tipo:"sin_publico", motivo:"sancion"}`

**Ejemplos de insert**

```sql
INSERT INTO partido_contexto (partido_id, intensidad_hinchada, viaje_km_visita, altitud_m, rivalidad_intensidad, presion, external) VALUES
(
  (SELECT partido_id FROM partido ORDER BY partido_id DESC LIMIT 1),
  85, 15, 80, 95, 80,
  '{"importance":{"derby":true,"tv":true}}'::jsonb
),
(
  (SELECT partido_id FROM partido ORDER BY partido_id DESC OFFSET 1 LIMIT 1),
  55, 280, 180, 20, 40,
  '{"travel":{"delay":true,"sleep_hours":6}}'::jsonb
);
```

---

### Tabla: `partido_stats_equipo`

**Uso:** Stats por equipo por partido (2 filas por partido). Se usa para UI, narrativa, analytics y para persistir `delta_elo`.

```sql
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
```

* `passes`: `{attempted, completed}`
* `tactical`: `{style, press}`
* `ppda`: número
* `shot_map`: lista (si luego extendés)

**Ejemplos de insert**

```sql
INSERT INTO partido_stats_equipo (
  partido_id, equipo_id, es_local, xg, tiros, tiros_arco, posesion, corners, faltas, amarillas, rojas, delta_elo, payload
) VALUES
(
  (SELECT partido_id FROM partido ORDER BY partido_id DESC LIMIT 1),
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Olimpia'),
  TRUE,
  1.8, 14, 6, 58.0, 7, 12, 2, 0,
  8.5,
  '{"passes":{"attempted":520,"completed":455},"tactical":{"style":"POSESION","press":55}}'::jsonb
),
(
  (SELECT partido_id FROM partido ORDER BY partido_id DESC LIMIT 1),
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Cerro Porteño'),
  FALSE,
  0.9, 8, 3, 42.0, 3, 15, 3, 1,
  -8.5,
  '{"passes":{"attempted":380,"completed":300},"tactical":{"style":"CONTRA","press":48}}'::jsonb
);
```

## Checklist backend (Bloques 6–8)

* Generación:
  * crear `competencia_edicion`
  * crear `etapa` (+ `perfil_sorteo_id` si aplica)
  * crear `grupo`/`ronda` según formato
  * crear `participante`
  * inicializar `tabla_posiciones`
  * generar `partido` (PENDIENTE)
* Simulación:
  * actualizar `partido` (goles, estado, reporte_motor)
  * upsert `partido_clima` y `partido_contexto`
  * insertar 2 filas `partido_stats_equipo`
  * actualizar `tabla_posiciones` (transacción)
  * actualizar ELO en `equipo_rating_actual` (y fatiga/moral si corresponde)

---

## 9) RANKINGS / COEFICIENTES / CUPOS

Este bloque modela **sistemas de ranking/coefficient** y su uso para **asignar cupos** (slots) y **clasificar** equipos hacia otras competiciones.
La idea central es **no hardcodear** “los 4 primeros van a X” en el código, sino declarar reglas en BD para que el backend Python:

- calcule rankings con una ventana móvil (por ejemplo 5 años),
- persista el ranking en forma consultable (para UI, historial y decisiones),
- convierta rankings y resultados deportivos en **cupos** y **participantes** de nuevas ediciones.

> ⚙️ Flujo típico en el motor:
>
> 1) Se simulan/registran partidos → se completan ediciones y standings.
> 2) Se recalculan rankings (`sistema_ranking` → `ranking_entrada`).
> 3) Se asignan cupos a una competencia objetivo (`regla_asignacion_cupos`).
> 4) Se generan “clasificados” (participantes) para nuevas ediciones (`regla_clasificacion`).

---

### Tabla: `sistema_ranking`

**Uso:** define un “motor de ranking” configurable. Un sistema puede rankear:

- equipos (club coefficient),
- países (country coefficient),
- confederaciones,
- o incluso competiciones (prestigio relativo).

**Depende de:** `mundo` y opcionalmente `confederacion`, `pais`, `competencia` (para acotar el dominio del ranking).

```sql
CREATE TABLE sistema_ranking (
  sistema_id       SERIAL PRIMARY KEY,
  mundo_id         INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  nombre          VARCHAR(100) NOT NULL,
  alcance         VARCHAR(30) NOT NULL,      -- 'WORLD','CONFED','PAIS','COMPETENCIA'
  ventana_anios   INT NOT NULL DEFAULT 5 CHECK (ventana_anios BETWEEN 1 AND 20),
  reglas_calculo  JSONB NOT NULL,
  confederacion_id INT REFERENCES confederacion(confederacion_id),
  pais_id          INT REFERENCES pais(pais_id),
  competencia_id   INT REFERENCES competencia(competencia_id),
  meta            JSONB NOT NULL DEFAULT '{}'::jsonb,
  CHECK (alcance IN ('WORLD','CONFED','PAIS','COMPETENCIA')),
  UNIQUE (mundo_id, nombre)
);
```

**Diccionario de datos (columnas)**

- **`sistema_id`**: PK.
- **`mundo_id`**: FK. Cada mundo puede tener variantes del mismo ranking (realista vs arcade).
- **`nombre`**: nombre único por mundo (ej. `"Coeficiente CONMEBOL Clubes"`).
- **`alcance`**: define el “scope” de cálculo:
  - `WORLD`: ranking global sin filtro
  - `CONFED`: ranking filtrado/definido por confederación
  - `PAIS`: ranking filtrado por país
  - `COMPETENCIA`: ranking acotado a una competencia (útil para seeding interno)
- **`ventana_anios`**: cantidad de años/temporadas hacia atrás que ponderan (1–20).
  - **Uso motor:** “rolling window” para coeficientes tipo UEFA/CONMEBOL.
- **`reglas_calculo` (JSONB)**: contrato del algoritmo (qué suma, cómo pondera, qué fuentes usa).
- **`confederacion_id` / `pais_id` / `competencia_id`**: filtros opcionales coherentes con `alcance`.
  - Ej: alcance `CONFED` → setear `confederacion_id`.
- **`meta` (JSONB)**: metadata administrativa (estado, versión, notas).

**JSONB sugerido (`reglas_calculo`)**

Recomendación: mini-DSL versionado para que el backend pueda evolucionar sin migraciones.

Campos frecuentes:

- `version`: int (ej. 1)
- `entity`: `"EQUIPO" | "PAIS" | "CONFED" | "COMPETENCIA"` (qué se rankea)
- `sources`: de dónde salen los puntos:
  - por competencia: lista de `competencia_id` y sus pesos
  - por tipo de competición: `competencia_tipo: "INTERNACIONAL"` etc.
- `scoring`:
  - `por_resultado`: `{win:2, draw:1, loss:0}` o similar
  - `bonos_ronda`: `{GROUPS:2, R16:1, QF:2, SF:3, F:4, CAMPEON:6}`
  - `bono_reputacion`: multiplicador por `competencia.reputacion_base`
- `weighting`:
  - `decay`: `{"mode":"linear","per_year":0.2}` (decaimiento por antigüedad)
  - `normalize`: `{"by_matches":true}` (puntos por partido)
- `ties`:
  - `tiebreakers`: `["puntos_totales","puntos_ultimo_anio","reputacion_historica","elo_actual"]`
- `output`:
  - `store_historial`: true/false (si llenar `ranking_entrada.historial_puntos` detallado)

**Ejemplo de inserts (2 sistemas distintos)**

```sql
INSERT INTO sistema_ranking (
  mundo_id, nombre, alcance, ventana_anios, reglas_calculo, confederacion_id, meta
) VALUES
(
  1,
  'Coeficiente CONMEBOL - Clubes',
  'CONFED',
  5,
  '{
    "version":1,
    "entity":"EQUIPO",
    "sources":[
      {"competencia_tipo":"INTERNACIONAL","peso":1.0},
      {"competencia_nombre":"Copa Paraguay","peso":0.2}
    ],
    "scoring":{
      "por_resultado":{"win":2,"draw":1,"loss":0},
      "bonos_ronda":{"GROUPS":2,"R16":1,"QF":2,"SF":3,"F":4,"CAMPEON":6}
    },
    "weighting":{"decay":{"mode":"linear","per_year":0.15}},
    "ties":{"tiebreakers":["puntos_totales","puntos_ultimo_anio","elo_actual"]}
  }'::jsonb,
  (SELECT confederacion_id FROM confederacion WHERE acronimo='CONMEBOL'),
  '{"estado":"Activo","notes":"Coeficiente tipo CONMEBOL/UEFA, configurable."}'::jsonb
),
(
  1,
  'Ranking Paraguay - Seeding Liga',
  'PAIS',
  3,
  '{
    "version":1,
    "entity":"EQUIPO",
    "sources":[{"competencia_nombre":"Primera División","peso":1.0}],
    "scoring":{"por_posicion_liga":{"1":40,"2":35,"3":30,"4":28,"5":26,"6":24,"7":22,"8":20,"9":18,"10":16,"11":14,"12":12}},
    "weighting":{"decay":{"mode":"step","by_year":{"0":1.0,"1":0.7,"2":0.4}}},
    "ties":{"tiebreakers":["puntos_totales","puntos_ultimo_anio","reputacion_historica"]}
  }'::jsonb,
  (SELECT pais_id FROM pais WHERE iso_code='PRY'),
  '{"estado":"Activo"}'::jsonb
);
```

---

### Tabla: `ranking_entrada`

**Uso:** tabla de resultados del ranking en un momento (`at_date`) y opcionalmente asociado a una temporada.
Guarda el valor total, la posición y un historial desglosado (JSON) para explicar de dónde sale el número.

**Depende de:** `sistema_ranking` y opcionalmente `temporada` + exactamente uno de: `equipo` / `pais` / `confederacion` / `competencia`.

```sql
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
  historial_puntos JSONB NOT NULL DEFAULT '{}'::jsonb,

  CHECK (
    (CASE WHEN equipo_id IS NULL THEN 0 ELSE 1 END) +
    (CASE WHEN pais_id IS NULL THEN 0 ELSE 1 END) +
    (CASE WHEN confederacion_id IS NULL THEN 0 ELSE 1 END) +
    (CASE WHEN competencia_id IS NULL THEN 0 ELSE 1 END) = 1
  )
);

CREATE INDEX idx_ranking_lookup
  ON ranking_entrada(sistema_id, at_date, puntos_totales DESC);

CREATE INDEX idx_ranking_pos
  ON ranking_entrada(sistema_id, temporada_id, puntos_totales DESC);
```

**Diccionario de datos (columnas)**

- **`entrada_id`**: PK bigserial.
- **`sistema_id`**: FK al “sistema” que generó la entrada.
- **`temporada_id`**: FK opcional (cuando el ranking se calcula “para una temporada” o cierre de temporada).
- **`at_date`**: fecha de corte del ranking.
  - **Uso backend:** ranking “al día de hoy” para seeding; ranking “al cierre” para cupos.
- **`equipo_id` / `pais_id` / `confederacion_id` / `competencia_id`**:
  - sólo **uno** puede tener valor (por el `CHECK`).
  - **Idea:** reutilizar una tabla para distintos niveles sin duplicar schemas.
- **`puntos_totales`**: puntaje final.
- **`ranking_posicion`**: posición (1..N). Recomendación: recalcular y persistir en batch para evitar costo en queries.
- **`historial_puntos` (JSONB)**: desglose explicable y auditable.

**JSONB sugerido (`historial_puntos`)**

Pensado para dos necesidades:

1) debugging/auditoría del motor,
2) UI (“tu coeficiente subió por semifinal en copa”).

Ejemplos de estructuras útiles:

- `by_season`: `{"2023":12.5,"2024":18.0,"2025":20.0}`
- `by_competition`: `{ "<competencia_id>": {"pts":10,"detail":[...]} }`
- `detail`: lista de eventos (máximo razonable):
  - `[{ "temporada":"2025", "competencia":"Copa Paraguay", "ronda":"SF", "pts":3.0 }]`
- `decay_applied`: `{"2023":0.7,"2024":0.85,"2025":1.0}`

**Ejemplo de inserts (2 entradas distintas)**

```sql
-- Entrada de equipo
INSERT INTO ranking_entrada (
  sistema_id, temporada_id, at_date, equipo_id,
  puntos_totales, ranking_posicion, historial_puntos
) VALUES
(
  (SELECT sistema_id FROM sistema_ranking WHERE mundo_id=1 AND nombre='Ranking Paraguay - Seeding Liga'),
  (SELECT temporada_id FROM temporada WHERE mundo_id=1 AND nombre='2025'),
  '2025-12-15',
  (SELECT equipo_id FROM equipo WHERE mundo_id=1 AND nombre='Olimpia'),
  92.0,
  1,
  '{"by_season":{"2023":20,"2024":30,"2025":42},"detail":[{"temporada":"2025","competencia":"Primera División","pos":1,"pts":42}]}'::jsonb
);

-- Entrada de país (ejemplo si algún sistema rankea países)
INSERT INTO ranking_entrada (
  sistema_id, at_date, pais_id, puntos_totales, ranking_posicion, historial_puntos
) VALUES
(
  (SELECT sistema_id FROM sistema_ranking WHERE mundo_id=1 AND nombre='Coeficiente CONMEBOL - Clubes'),
  '2025-12-15',
  (SELECT pais_id FROM pais WHERE iso_code='PRY'),
  55.5,
  7,
  '{"by_season":{"2021":8.0,"2022":9.5,"2023":10.0,"2024":13.0,"2025":15.0}}'::jsonb
);
```

---

### Tabla: `regla_asignacion_cupos`

**Uso:** declara cómo se asignan cupos hacia una **competencia objetivo** usando un `sistema_ranking`.
Ejemplos:

- “los países top-4 del coeficiente obtienen 4 cupos a Libertadores”
- “los 8 mejores equipos por ranking entran a un torneo invitacional”
- “seeding de grupos basado en ranking”

**Depende de:** `mundo`, `competencia` (objetivo), `sistema_ranking` y opcionalmente `temporada`.

```sql
CREATE TABLE regla_asignacion_cupos (
  asignacion_id         SERIAL PRIMARY KEY,
  mundo_id              INT NOT NULL REFERENCES mundo(mundo_id) ON DELETE CASCADE,
  competencia_objetivo_id INT NOT NULL REFERENCES competencia(competencia_id) ON DELETE CASCADE,
  sistema_id            INT NOT NULL REFERENCES sistema_ranking(sistema_id),
  temporada_id          INT REFERENCES temporada(temporada_id) ON DELETE CASCADE,
  regla               JSONB NOT NULL,
  nota                TEXT
);
```

**Diccionario de datos**

- **`asignacion_id`**: PK.
- **`mundo_id`**: FK.
- **`competencia_objetivo_id`**: FK. A qué torneo aplica la asignación.
- **`sistema_id`**: FK. Qué ranking se usa como base (puntos/posición).
- **`temporada_id`**: si NULL, es regla genérica; si no NULL, override para una temporada.
- **`regla` (JSONB)**: “cómo repartir” cupos y cómo resolver empates.
- **`nota`**: explicación humana.

**JSONB sugerido (`regla`)**

Recomendación: mini-DSL para cupos, también versionado.

Campos habituales:

- `version`: 1
- `scope`: `"PAIS" | "EQUIPO" | "CONFED"` (qué entidad recibe cupos)
- `cupos_total`: int (si aplica)
- `cupos_por_entidad`: objeto (mapa) o fórmula:
  - por ranking_posición de entidad: `{"1":4,"2":4,"3":3,...}`
  - o escalones: `[{"from":1,"to":4,"cupos":4},{"from":5,"to":8,"cupos":3}]`
- `fallback`: reglas si faltan entidades (ej. países sin equipos elegibles)
- `eligibility_filter`: condiciones extra para equipos seleccionables
- `tie_breakers`: para empates en puntos (por defecto hereda del sistema, pero puede override)

**Cómo lo consume el backend**

- El motor calcula/lee `ranking_entrada` del `sistema_id` al `at_date` deseado.
- Aplica la regla para determinar:
  1) cuántos cupos obtiene cada entidad,
  2) qué equipos concretos llenan esos cupos (si scope=PAIS, se necesita sub-regla: top equipos del país).
- Finalmente crea `participante` en la `competencia_edicion` destino correspondiente (normalmente de la siguiente temporada).

**Ejemplo de inserts**

```sql
INSERT INTO regla_asignacion_cupos (
  mundo_id, competencia_objetivo_id, sistema_id, temporada_id, regla, nota
) VALUES
(
  1,
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Copa Paraguay'),
  (SELECT sistema_id FROM sistema_ranking WHERE mundo_id=1 AND nombre='Ranking Paraguay - Seeding Liga'),
  (SELECT temporada_id FROM temporada WHERE mundo_id=1 AND nombre='2025'),
  '{
    "version":1,
    "scope":"EQUIPO",
    "cupos_total":16,
    "seleccion":{"top_n_por_ranking":16},
    "tie_breakers":["puntos_totales","puntos_ultimo_anio","reputacion_historica"]
  }'::jsonb,
  'Ejemplo: armar un cupo de 16 por ranking (invitacional o seeding).'
),
(
  1,
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Primera División'),
  (SELECT sistema_id FROM sistema_ranking WHERE mundo_id=1 AND nombre='Ranking Paraguay - Seeding Liga'),
  NULL,
  '{
    "version":1,
    "scope":"EQUIPO",
    "cupos_total":12,
    "seleccion":{"top_n_por_ranking":12},
    "uso":"seeding",
    "bombo_por_posicion":[
      {"bombo":1,"from":1,"to":4},
      {"bombo":2,"from":5,"to":8},
      {"bombo":3,"from":9,"to":12}
    ]
  }'::jsonb,
  'Ejemplo: definir bombos/seed inicial para sorteo o fixture.'
);
```

---

### Tabla: `regla_clasificacion`

**Uso:** reglas declarativas para convertir **resultados** de una competencia fuente en **clasificados** para otra competencia destino.
Es el bloque que permite modelar:

- cupos internacionales desde liga/copa,
- supercopas,
- playoffs de ascenso/descenso,
- ligas regionales que clasifican a un torneo nacional.

**Depende de:** `mundo`, y en la práctica se evalúa contra `tabla_posiciones`, `participante`, y/o resultados de ediciones.

```sql
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
  metodo_id               INT REFERENCES cat_metodo_clasificacion(metodo_id),
  prioridad              INT NOT NULL DEFAULT 0,

  nota                  TEXT
);

CREATE INDEX idx_regla_clasif_fuente ON regla_clasificacion(competencia_fuente_id);
CREATE INDEX idx_regla_clasif_destino ON regla_clasificacion(competencia_destino_id);
```

**Diccionario de datos (columnas)**

- **`clasificacion_id`**: PK.
- **`mundo_id`**: FK.
- **`temporada_id`**: si NULL, regla permanente; si no NULL, solo aplica en esa temporada.
- **`competencia_fuente_id`**: FK. Torneo que produce clasificados.
- **`etapa_fuente_tipo`**: string (ej. `"LEAGUE"`, `"GROUPS"`, `"KNOCKOUT"`).
  - Nota: es string para no acoplar a `cat_etapa_tipo` por ID, pero se recomienda usar los mismos `codigo`.
- **`grupo_fuente_codigo`**: si la etapa tiene grupos, restringe a un grupo específico (`'A'`, `'B'`, `'1'`).
- **`posicion_desde` / `posicion_hasta`**: rango de posiciones (1..N) en standings o resultado final (según implementación).
- **`condicion_fuente` (JSONB)**: condiciones extra (campeón, subcampeón, mejor acumulativo, fair play, etc.).
- **`competencia_destino_id`**: FK. Torneo destino.
- **`etapa_destino_tipo`**: hint para ubicar al clasificado en una etapa destino (ej. `"GROUPS"`, `"KNOCKOUT"`).
- **`hint_ronda_destino`**: hint de ronda (“GROUP_STAGE”, “R16”, “PLAYOFF”).
- **`metodo_id`**: FK a `cat_metodo_clasificacion` (trazabilidad: campeón, ranking, etc.).
- **`prioridad`**: resuelve conflictos cuando un equipo califica por múltiples vías.
  - Ejemplo: campeón de copa tiene prioridad > posición liga, para no duplicar.
- **`nota`**: texto humano.

**JSONB sugerido (`condicion_fuente`)**

Este JSON se usa como “filtro/selector adicional”. Ejemplos típicos:

- `{"campeon":true}` (tomar sólo el campeón)
- `{"subcampeon":true}`
- `{"fase":"Apertura","campeon":true}` (si modelás Apertura/Clausura como competencias distintas)
- `{"acumulativo":true}` (tabla acumulada)
- `{"fair_play_top":1}` (mejor fair play)
- `{"requiere_no_ya_clasificado":true}` (evitar duplicados antes de aplicar)

**Cómo lo consume el backend (recomendación concreta)**

1) En “cierre de edición” de la competencia fuente:
   - Obtener tabla final (por etapa/grupo) desde `tabla_posiciones` o desde resultados del knockout.
2) Para cada regla aplicable (mundo_id + temporada_id opcional + competencia_fuente_id):
   - Resolver el conjunto de equipos que cumplen:
     - etapa/grupo/rango posición + condicion JSON.
3) Encolar esos equipos como candidatos para el destino, con su `metodo_id` y `prioridad`.
4) Resolver duplicados:
   - para cada equipo, quedarse con la regla de mayor prioridad (y si empata, aplicar tiebreakers definidos en `condicion_fuente` o configuración global).
5) Insertar en `participante` de la edición destino correspondiente, con `metodo_id` y `meta.qualifier`.

**Ejemplos de inserts (2 reglas distintas)**

```sql
-- 1) Desde liga: posiciones 1 a 4 clasifican a un torneo destino (ej. "Libertadores" si existiera en tu dataset).
-- Nota: acá usamos "Copa Paraguay" como destino a modo de ejemplo; en un dataset real sería una competencia internacional.
INSERT INTO regla_clasificacion (
  mundo_id, temporada_id,
  competencia_fuente_id, etapa_fuente_tipo, grupo_fuente_codigo, posicion_desde, posicion_hasta, condicion_fuente,
  competencia_destino_id, etapa_destino_tipo, hint_ronda_destino, metodo_id, prioridad, nota
) VALUES
(
  1,
  (SELECT temporada_id FROM temporada WHERE mundo_id=1 AND nombre='2025'),
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Primera División'),
  'LEAGUE',
  NULL,
  1, 4,
  '{"acumulativo":true}'::jsonb,
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Copa Paraguay'),
  'KNOCKOUT',
  'R64',
  (SELECT metodo_id FROM cat_metodo_clasificacion WHERE codigo='POSICION_LIGA'),
  10,
  'Ejemplo: top 4 de liga clasifican al destino.'
);

-- 2) Desde copa: campeón clasifica a supercopa (destino ficticio o real si existe en tu DB).
INSERT INTO regla_clasificacion (
  mundo_id, temporada_id,
  competencia_fuente_id, etapa_fuente_tipo, posicion_desde, posicion_hasta, condicion_fuente,
  competencia_destino_id, etapa_destino_tipo, hint_ronda_destino, metodo_id, prioridad, nota
) VALUES
(
  1,
  (SELECT temporada_id FROM temporada WHERE mundo_id=1 AND nombre='2025'),
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Copa Paraguay'),
  'KNOCKOUT',
  1, 1,
  '{"campeon":true}'::jsonb,
  (SELECT competencia_id FROM competencia WHERE mundo_id=1 AND nombre='Supercopa Paraguay'),
  'KNOCKOUT',
  'FINAL',
  (SELECT metodo_id FROM cat_metodo_clasificacion WHERE codigo='CAMPEON'),
  100,
  'Campeón de Copa Paraguay clasifica a Supercopa (prioridad máxima).'
);
```

---

## Checklist de implementación backend (Python) — Bloque 9

**Servicios / módulos recomendados:**

1) **RankingEngine**

   - Input: `sistema_ranking` + fuentes (resultados, standings, rondas alcanzadas)
   - Output: upsert batch en `ranking_entrada` para un `at_date` y/o cierre de `temporada_id`
   - Recomendación: cálculo idempotente (si corrés dos veces, mismo output)
2) **CupAllocationService**

   - Lee `regla_asignacion_cupos` y ranking correspondiente
   - Produce una “lista de slots” (por país/equipo) + motivos
   - Puede escribir en `participante` (si ya existe la edición destino) o dejar “propuesta” (tabla futura)
3) **QualificationService**

   - Evalúa `regla_clasificacion` contra:
     - `tabla_posiciones` (ligas/grupos)
     - resultados finales de knockout (campeón/subcampeón)
   - Resuelve conflictos por `prioridad`
   - Inserta `participante` con:
     - `metodo_id`
     - `meta.qualifier` (de dónde viene)
     - `seed` / `bombo_sorteo` si se combina con `perfil_sorteo`
4) **Explainability**

   - Construye `historial_puntos` y lo expone por API para UI (“por qué tengo 92 pts”)
