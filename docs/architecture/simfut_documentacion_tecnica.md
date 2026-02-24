# Documentación técnica — Base de datos **SimFut** (schema `futsim`)

> Objetivo: que **Antigravity** identifique rápidamente **qué tablas** y **qué columnas** usar en cada pantalla/flujo del sistema (CRUD, filtros, fixtures, standings, rankings, historial, etc.).

---

## 1) Convenciones y conceptos base

### 1.1 Schema y extensiones

* Todo vive en el schema: **`futsim`**
* Se usa `pgcrypto` para UUIDs (ej.: `futsim.gen_random_uuid()`), especialmente en **`media_asset`**.

### 1.2 Claves y referencias

* Claves primarias suelen ser `SERIAL` (`*_id`) o `UUID` en assets.
* Muchas tablas “de contenido” cuelgan de **`mundo_id`** (multi-mundo) y/o **`temporada_id`** (multi-temporada).

### 1.3 Jerarquía funcional (lo más importante)

**Mundo → Temporada → Competencia → Edición → Etapa → Grupo/Ronda → Partido**

* **`mundo`**: universo de simulación.
* **`temporada`**: período dentro del mundo.
* **`competencia`**: torneo “base” (definición estable).
* **`competencia_edicion`**: instancia del torneo (para una temporada).
* **`etapa`**: fase dentro de la edición (liga, grupos, eliminación, etc.).
* **`grupo` / `ronda`**: contenedores internos (grupos A/B/C, rondas, ida/vuelta).
* **`partido`**: fixture, resultado y output del motor.

---

## 2) Catálogos Unificados (Patrón v7.0)

A partir de la versión 7.0, el modelo utiliza un **Patrón de Catálogo Unificado** apoyado en dos tablas maestras para gobernar toda la taxonomía y estandarización del sistema, reemplazando a docenas de tablas paramétricas individuales.

### 2.1 `cat_dominio` (La tabla Padre)

Define el universo o categoría del parámetro (ej. `ESTADO_GENERICO`, `COMPETENCIA_TIPO`, `CLIMA_CONDICION`).

* **PK**: `dominio_id`
* Campos clave: `codigo` (UNIQUE, String), `descripcion`

### 2.2 `cat_parametro` (La tabla Hijo)

Almacena todos los valores posibles para cualquier dominio de la aplicación. Cualquier entidad que necesite un estado, tipo o categoría, apuntará mediante una FK a esta tabla.

* **PK**: `parametro_id`
* **FK**: `dominio_id → cat_dominio`
* Campos clave: `codigo` (String constante para lógica en código), `descripcion` (Texto formateado para UI), `meta` (JSONB)

**Uso en el código (Best Practice)**: Nunca se debe consultar directamente por el número `parametro_id`, sino vinculando el dominio y buscando por la constante nominal en el campo `codigo` (ej. Buscar el parámetro donde `codigo` sea `'ACTIVO'` dentro del dominio `'ESTADO_GENERICO'`).

---

## 3) Media / Assets

### 3.1 `media_asset`

Guarda metadatos de imágenes/recursos (escudos, banderas, logos).

* **PK**: `media_id` (UUID, default `futsim.gen_random_uuid()`)
* Campos clave:

  * `url` (TEXT, requerido)
  * `mime_type`, `ancho`, `alto`, `bytes`, `checksum`
  * `creado_en`
  * `meta` (JSONB)

**Usos típicos (UI):**

* Mostrar **escudo** de un equipo (`equipo.escudo_media_id`)
* Mostrar **bandera** de un país (`pais.bandera_media_id`)
* Mostrar **logo** de confederación/asociación/competencia (`*.logo_media_id`)

---

## 4) Geografía y organización futbolística

### 4.1 `confederacion`

CONMEBOL, UEFA, etc.

* **PK**: `confederacion_id`
* Campos: `nombre`, `acronimo`, `logo_media_id`, `reputacion_base`, `meta`

### 4.2 `pais`

* **PK**: `pais_id`
* **FK**: `confederacion_id → confederacion`
* Campos clave:

  * `nombre`, `iso_code`, `gentilicio`
  * `bandera_media_id`
  * `nivel_futbolistico`, `poblacion`
  * `meta`

**Para filtros por confederación**: se obtiene desde `pais.confederacion_id`.

### 4.3 `region`

Región dentro de un país (útil para competencias regionales o segmentación).

* **PK**: `region_id`
* **FK**: `pais_id → pais`
* Campos: `nombre`, `meta`

### 4.4 `perfil_climatico`

Perfiles de clima por ciudad/región (para sim).

* **PK**: `perfil_id`
* Campos: `nombre`, `temperatura_media`, `humedad_media`, `lluvia_prob`, `meta`

### 4.5 `ciudad`

* **PK**: `ciudad_id`
* **FKs**: `pais_id → pais`, `region_id → region`, `perfil_clima_id → perfil_climatico`
* Campos: `nombre`, `lat`, `lon`, `altitud`, `poblacion`, `meta`

### 4.6 `estadio`

* **PK**: `estadio_id`
* **FKs**: `ciudad_id → ciudad`, `pais_id → pais`
* Campos: `nombre`, `capacidad`, `altura_msnm`, `tipo_cesped_id` (FK param), `tipo_propiedad_id` (FK param), `meta`

### 4.7 `asociacion`

Federación/Liga que administra (por país o por confederación).

* **PK**: `asociacion_id`
* **FKs**: `confederacion_id → confederacion`, `pais_id → pais`
* Campos: `nombre`, `acronimo`, `logo_media_id`, `meta`

---

## 5) Equipos y “mundo club”

### 5.1 `equipo`

Entidad principal del club.

* **PK**: `equipo_id`
* **FKs**:

  * `mundo_id → mundo`
  * `ciudad_sede_id → ciudad`
  * `pais_origen_id → pais`
  * `asociacion_liga_id → asociacion`
  * `estadio_principal_id → estadio`
  * `escudo_media_id → media_asset`
* Campos clave:

  * `nombre` (requerido; único por `mundo_id`)
  * `codigo_tla` (sigla corta)
  * `anio_fundacion`
  * `colores` (JSONB) — ejemplo: `{ "primario":"#...", "secundario":"#..." }`
  * `estado_id` (FK a cat_parametro, por defecto el ID de 'ACTIVO')
  * `meta` (JSONB)

**Situaciones UI (muy importante):**

* **Listar equipos**: `equipo` (filtrando por `mundo_id`).
* **Buscar por nombre**: `equipo.nombre ILIKE '%texto%'`.
* **Filtrar por país**: `equipo.pais_origen_id = :paisId`.
* **Filtrar por confederación**: join `equipo → pais` y filtrar por `pais.confederacion_id`.
* **Editar equipo**: actualizar columnas de `equipo`, y si cambia estadio principal reflejar historial (ver 5.2).

### 5.2 `equipo_estadio_hist`

Historial de cambios de estadio principal.

* **PK**: `equipo_estadio_hist_id`
* **FKs**: `equipo_id → equipo`, `estadio_id → estadio`
* Campos: `fecha_inicio`, `fecha_fin`, `motivo`, `meta`

**Uso:** cuando cambias el estadio principal en UI, registrar el cambio aquí.

### 5.3 `equipo_rating_actual`

Rating actual (ELO u otro).

* **PK**: `equipo_id` (1–a–1)
* Campos: `elo`, `ataque`, `defensa`, `forma`, `actualizado_en`, `meta`

### 5.4 `equipo_elo_hist`

Histórico de ELO por fecha.

* Campos clave: `equipo_id`, `fecha`, `elo`, `motivo`, `meta`

### 5.5 `equipo_institucion`

Dimensiones institucionales (infra, juveniles, etc.).

* **PK**: `equipo_id` (1–a–1)
* Campos: `infraestructura`, `nivel_scouting`, `nivel_entrenamiento`, `nivel_juveniles`, `estabilidad_directiva`, `hinchada`, `reputacion_historica`, `meta`

### 5.6 `equipo_finanzas`

Dimensiones económicas.

* **PK**: `equipo_id` (1–a–1)
* Campos: `presupuesto`, `salarios`, `deuda`, `ingresos`, `gastos`, `patrocinio`, `tipo_propiedad_id` (FK param), `meta`

### 5.7 Rivalidades e historial

* **`rivalidad`**: rivalidades declaradas entre equipos (`equipo_a_id`, `equipo_b_id`, `intensidad`, `meta`)
* **`historial_enfrentamiento`**: acumulados/estadísticas de enfrentamientos (para previews).

### 5.8 `evento_equipo`

Bitácora de eventos del club (cambios, sanciones, logros, etc.).

* Campos: `equipo_id`, `fecha`, `tipo`, `descripcion`, `meta`

---

## 6) Mundo y temporadas

### 6.1 `mundo`

* **PK**: `mundo_id`
* Campos clave:

  * `nombre`
  * `fecha_actual` (la fecha del mundo)
  * `semilla_rng`
  * `configuracion_global` (JSONB)

### 6.2 `temporada`

* **PK**: `temporada_id`
* **FK**: `mundo_id → mundo`
* Campos:

  * `nombre`
  * `fecha_inicio`, `fecha_fin`
  * `es_actual` (boolean)
  * `meta`

**UI:** selector de contexto (mundo/temporada) para todo.

### 6.3 `mundo_snapshot`

Snapshot del mundo (para rollback / guardado).

* Campos: `mundo_id`, `fecha`, `payload` (JSONB), `meta`

### 6.4 `sim_log`

Logs del motor de simulación.

* Campos: `mundo_id`, `fecha`, `nivel`, `mensaje`, `contexto` (JSONB)

---

## 7) Competencias (torneos) y estructura de edición

### 7.1 `competencia`

Definición “madre” del torneo (no depende de temporada).

* **PK**: `competencia_id`
* **FKs**:

  * `mundo_id → mundo`
  * `tipo_id → cat_competencia_tipo`
  * alcance opcional: `confederacion_id`, `pais_id`, `region_id`, `asociacion_id`
  * `logo_media_id → media_asset`
* Campos clave:

  * `nombre`
  * `estado_id` (FK param)
  * `reputacion_base`
  * `configuracion_base` (JSONB) — reglas globales del torneo
  * `meta` (JSONB)

**Regla práctica (UI de filtros de torneo):**

* Si es torneo de país → `pais_id`.
* Si es confederacional → `confederacion_id`.
* Si depende de liga/federación → `asociacion_id`.

### 7.2 `competencia_reputacion`

Reputación dinámica.

* Campos: `competencia_id`, `temporada_id` (si aplica), `reputacion`, `meta`

### 7.3 `regla_elegibilidad`

Reglas de elegibilidad (clubes, límites por país, etc.).

* Campos: `competencia_id`, `regla` (JSONB), `meta`

### 7.4 `competencia_edicion`

Instancia concreta del torneo en una temporada.

* **PK**: `edicion_id`
* **FKs**: `competencia_id → competencia`, `temporada_id → temporada`
* Campos clave:

  * `nombre_display`
  * `fecha_inicio`, `fecha_fin`
  * `estado` (ej.: `'PLANIFICADA'`, `'EN_CURSO'`, `'FINALIZADA'`)
  * `reglas_edicion` (JSONB)
  * `meta` (JSONB)

### 7.5 `etapa`

* **PK**: `etapa_id`
* **FK**: `edicion_id → competencia_edicion`, `tipo_id → cat_etapa_tipo`
* Campos: `orden`, `nombre`, `fecha_inicio`, `fecha_fin`, `config_etapa` (JSONB)

### 7.6 `grupo`

* **PK**: `grupo_id`
* **FK**: `etapa_id → etapa`
* Campos: `codigo` (A/B/C), `nombre`, `meta`

### 7.7 `ronda`

* **PK**: `ronda_id`
* **FKs**: `etapa_id → etapa`, `grupo_id → grupo` (opcional)
* Campos: `numero`, `pierna` (ida/vuelta), `fecha_programada`, `nombre`, `meta`

### 7.8 `participante`

Inscripción de equipos en una edición.

* **PK**: `participante_id`
* **FKs**: `edicion_id → competencia_edicion`, `equipo_id → equipo`, `metodo_id → cat_metodo_clasificacion`
* Campos clave:

  * `seed`, `bombo_sorteo`
  * `grupo_id_inicial` (si ya está asignado)
  * `posicion_final`, `ronda_eliminacion`
  * `puntos_ranking_ganados`
  * `meta`

### 7.9 `tabla_posiciones`

Standings por edición/etapa/grupo.

* Clave natural: (`edicion_id`, `etapa_id`, `grupo_id`, `equipo_id`)
* Campos: `pj, pg, pe, pp, gf, gc, dg, pts, forma, actualizado_en, meta`

### 7.10 `perfil_sorteo`

Config para sorteos (bombos, restricciones por país, etc.).

* Campos: `edicion_id`, `payload` (JSONB), `meta`

---

## 8) Partidos y estadísticas

### 8.1 `partido`

Fixture + resultado.

* **PK**: `partido_id`
* **FKs**:

  * `edicion_id → competencia_edicion`
  * `etapa_id → etapa`
  * `ronda_id → ronda` (opcional)
  * `grupo_id → grupo` (opcional)
  * `local_equipo_id → equipo`
  * `visita_equipo_id → equipo`
  * `estadio_real_id → estadio` (si aplica)
  * `ciudad_id → ciudad`
* Campos clave:

  * `fecha_hora`
  * `jornada` (matchday)
  * `fase_label` (texto útil para UI)
  * `goles_local`, `goles_visita`, `penales_local`, `penales_visita`
  * `estado`
  * `reporte_motor` (JSONB)

### 8.2 `partido_clima`

* **FK**: `partido_id → partido`
* Campos: `condicion_id` (FK param), `temperatura`, `humedad`, `lluvia`, `viento`, `meta`

### 8.3 `partido_contexto`

Contexto narrativo/ambiental.

* **FK**: `partido_id → partido`
* Campos: `importancia`, `derby`, `viaje_km`, `meta`

### 8.4 `partido_stats_equipo`

Stats por equipo en el partido.

* **FKs**: `partido_id → partido`, `equipo_id → equipo`
* Campos típicos: tiros, posesión, tarjetas, etc. (o en `meta`)

---

## 9) Rankings y cupos

### 9.1 `sistema_ranking`

Define un sistema de ranking (por confederación, país, etc.).

* **PK**: `sistema_id`
* Campos: `nombre`, `alcance`, `meta`

### 9.2 `ranking_entrada`

Puntajes por equipo/competencia/temporada.

* **FKs**: `sistema_id → sistema_ranking`, `equipo_id → equipo`, `temporada_id → temporada`
* Campos: `puntos`, `detalle` (JSONB), `meta`

### 9.3 `regla_asignacion_cupos`

Define cómo se asignan cupos a ediciones.

* Campos: `competencia_id`, `sistema_id`, `regla` (JSONB), `meta`

### 9.4 `regla_clasificacion`

Reglas de clasificación dentro de edición/etapa.

* Campos: `edicion_id`/`etapa_id`, `regla` (JSONB), `meta`

---

## 10) Historia, noticias y estadísticas globales

### 10.1 `snapshot_equipo`

Snapshots por equipo (timeline).

* Campos: `equipo_id`, `fecha`, `payload` (JSONB), `meta`

### 10.2 `historia_narrativa`

Narrativa tipo “FM”.

* Campos: `mundo_id`, `fecha`, `titulo`, `cuerpo`, `meta`

### 10.3 `noticia`

Noticias cortas.

* Campos: `mundo_id`, `fecha`, `titulo`, `contenido`, `tipo`, `meta`

### 10.4 `estadistica_global`

KPIs agregados por mundo/temporada.

* Campos: `mundo_id`, `temporada_id`, `codigo`, `valor`, `meta`

---

# 11) Recetas rápidas — qué tabla/columna usar en cada situación

## 11.1 CRUD **Equipos** (`/teams`)

### Listado base

* Tabla: **`equipo`**
* Columnas mínimas:

  * `equipo_id`, `nombre`, `pais_origen_id`, `ciudad_sede_id`, `asociacion_liga_id`, `escudo_media_id`, `estado`

### Filtro por confederación

* Se filtra por `confederacion.confederacion_id`
* Join:

  * `equipo.pais_origen_id → pais.pais_id → pais.confederacion_id`
* Criterio:

  * `pais.confederacion_id = :confederacionId`

### Filtro por país

* `equipo.pais_origen_id = :paisId`

### Buscador por nombre

* `equipo.nombre ILIKE '%' || :q || '%'`

### Mostrar “país” y “confederación” en card

* Join:

  * `pais.nombre`, `confederacion.nombre`
  * `pais.bandera_media_id` (opcional)
  * `equipo.escudo_media_id` (para mostrar el escudo)

### Botón “Editar”

* Update sobre `equipo`
* Si cambia `estadio_principal_id`:

  * registrar cambio en `equipo_estadio_hist`

---

## 11.2 Filtros de **Torneos** (`/competitions` o selector dentro de /teams)

Tabla base: **`competencia`**

### Torneos por confederación (si ya filtraste confederación)

* `competencia.confederacion_id = :confederacionId`
* Alternativa (si el torneo está a nivel país):

  * filtrar países por `pais.confederacion_id` y luego `competencia.pais_id IN (...)`

### Torneos por país (si ya filtraste país)

* `competencia.pais_id = :paisId`
* y/o `competencia.asociacion_id` si querés mostrar por asociación del país.

### Torneos “del país dentro de una confederación”

* 1. Listar países: `pais.confederacion_id = :confederacionId`
* 2. Luego:

  * `competencia.pais_id IN (...)` **o**
  * `competencia.confederacion_id = :confederacionId`

---

## 11.3 Ver una **edición** de torneo (por temporada)

* Tabla: **`competencia_edicion`**
* Filtros:

  * `temporada_id = :temporadaId`
  * opcional: `competencia_id = :competenciaId`

## 11.4 Ver **participantes** de una edición

* Tabla: **`participante`**
* Filtro: `edicion_id = :edicionId`
* Join: `participante.equipo_id → equipo` para nombre/escudo

## 11.5 Ver **fixture/resultados**

* Tabla: **`partido`**
* Filtro: `edicion_id = :edicionId`
* Dentro de una etapa:

  * `partido.etapa_id = :etapaId`
* Dentro de un grupo:

  * `partido.grupo_id = :grupoId`

## 11.6 Ver **tabla de posiciones**

* Tabla: **`tabla_posiciones`**
* Filtro:

  * `edicion_id = :edicionId`
  * `etapa_id = :etapaId`
  * `grupo_id = :grupoId` (si aplica)

## 11.7 Rankings (cupos, reputación, accesos)

* Sistema: `sistema_ranking`
* Entradas: `ranking_entrada` (por temporada)
* Reglas de cupos: `regla_asignacion_cupos`

---

## 12) Notas prácticas para Antigravity (frontend/back)

* **Siempre incluir `mundo_id`** en queries base, para no mezclar universos.
* Dropdowns encadenados:

  * Confederación → País: `pais.confederacion_id`
  * País → Asociaciones: `asociacion.pais_id`
  * Confederación/País → Competencias: `competencia.confederacion_id`, `competencia.pais_id`, `competencia.asociacion_id`
* `meta` (JSONB) es el “escape hatch” para features nuevas sin migración inmediata; pero para UI estable, priorizar campos estructurados.

---

## Apéndice A — Tablas del schema

`cat_dominio`, `cat_parametro`, `media_asset`, `mundo`, `temporada`, `mundo_snapshot`, `sim_log`, `confederacion`, `pais`, `region`, `perfil_climatico`, `ciudad`, `estadio`, `asociacion`, `equipo`, `equipo_estadio_hist`, `equipo_rating_actual`, `equipo_institucion`, `equipo_finanzas`, `rivalidad`, `historial_enfrentamiento`, `evento_equipo`, `competencia`, `competencia_reputacion`, `regla_elegibilidad`, `competencia_edicion`, `etapa`, `grupo`, `ronda`, `participante`, `tabla_posiciones`, `perfil_sorteo`, `partido`, `partido_clima`, `partido_contexto`, `partido_stats_equipo`, `sistema_ranking`, `ranking_entrada`, `regla_asignacion_cupos`, `regla_clasificacion`, `snapshot_equipo`, `historia_narrativa`, `noticia`, `estadistica_global`, `equipo_elo_hist`
