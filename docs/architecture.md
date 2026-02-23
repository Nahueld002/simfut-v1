# SIMFUT God Mode Architecture

## Overview
SIMFUT God Mode is a "world simulator" for football ecosystems, built on a modern stack.

### Stack
- **Frontend**: Next.js (App Router) + TailwindCSS + TanStack Query.
- **Backend**: FastAPI (Python 3.10+) + SQLAlchemy 2.0 (Async) + Alembic.
- **Database**: PostgreSQL 15+ with JSONB usage for flexible schema parts.

## Database Design (v6.0)
The database structure is located in `app/models/` and matches the `simfut_db.sql` v6.0 schema.
Key Concepts:
- **No Players**: All simulation is based on Team Attributes (`EquipoRatingActual`) and Institutional Attributes (`EquipoInstitucion`).
- **Flexible Competitions**: Using generic structures (`Competencia`, `Edicion`, `Etapa`, `Grupo`, `Ronda`) to support any tournament format.
- **Narrative**: Heavy use of logging (`SimLog`, `HistoriaNarrativa`) and snapshots (`MundoSnapshot`, `SnapshotEquipo`) to track the evolving world.

## Backend Structure
- `app/core`: Configuration and DB connection.
- `app/models`: SQLAlchemy models partitioned by domain (`world`, `geo`, `team`, `competition`, `match`, `narrative`).
- `app/api`: API Endpoints (to be implemented).
- `alembic/`: Database migrations.

## Simulation Flow (Planned)
1. **Engine**: A probabilistic engine takes `EquipoRatingActual` + `PartidoContexto` -> outputs `PartidoResult` + `PartidoStats`.
2. **Update**: Post-match, ELO is updated, fatigue applied, and table standings (`TablaPosiciones`) recalculated.
3. **Narrative**: 'Story Generator' checks for anomalies (upsets, streaks) and creates `Noticia`.
