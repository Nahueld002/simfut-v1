# Contributing to SimFut

¡Gracias por tu interés en contribuir a SimFut! Este proyecto es mantenible por la comunidad y valoramos todas las contribuciones, desde reportes de bugs hasta nuevas funcionalidades.

## Estructura del Proyecto (Monorepo)
- `apps/backend/`: API y motor (Python/FastAPI).
- `apps/frontend/`: Interfaz de usuario (React/Next.js).
- `infra/`: Configuración de Docker y variables de entorno.
- `database/`: Migraciones y seeds.
- `docs/`: Documentación de arquitectura, API y guías de desarrollo.
- `scripts/`: Herramientas de datos y scripts útiles.
- `data/`: Datasets pequeños y templates.

## Reglas Principales

### 1. Uso de Catálogos
**REGLA DE ORO:** Los catálogos se consumen por `codigo`, no por `id`. 
La lógica del backend y del motor NUNCA debe depender de IDs (ej. `1`, `2`) hardcodeados en la base de datos, sino de sus respectivos códigos estables alfanuméricos (ej. `ACTIVO`, `INACTIVO`).

### 2. Cambios en la Base de Datos
*No se mergea nada que cambie la DB sin su respectiva migración y documentación.*
Si necesitas agregar tablas o columnas:
1. Crea un script en `database/migrations/`.
2. Actualiza la estructura en `docs/database/`.

## Cómo levantar el entorno local
1. Copia `infra/env.example` a `.env` y configura tus variables.
2. Ejecuta `docker compose -f infra/compose.yml up --build` para levantar toda la pila (Base de datos, Backend y Frontend).

Dudas o consultas, abre un Issue en el repositorio.
