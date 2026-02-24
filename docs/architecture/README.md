# Arquitectura General

SimFut-v1 está dividido en tres componentes principales que facilitan la escalabilidad, la separación lógica y la contribución comunitaria.

## Diagrama Simple

```text
[Frontend (Next.js / React)] <--- (HTTP/JSON) ---> [Backend (FastAPI / Python)] 
                                                       |
                                                       | (SQLAlchemy / asyncpg)
                                                       v
                                               [Database (PostgreSQL)]
```

## Estructura de Backend (Dominio y API Separados)
- **API (`apps/backend/app/api`)**: Expone endpoints bajo OpenAPI para interactuar con la DB y las Simulaciones.
- **Motor / Dominio (Reglas puras)**: Maneja los motores ELO y la matemática de simulaciones.
- **Infra (Modelos)**: Representa las tablas en DB mediante ORM (`apps/backend/app/models/`).

### Buenas Prácticas de Código
* **Patrón de Catálogo Unificado (v7.0)**: Centralizamos toda la taxonomía de la aplicación en dos tablas maestras: `cat_dominio` (Padre) y `cat_parametro` (Hijo). Esto reemplaza las múltiples tablas diminutas (tipo *tipos de torneo*, *métodos de clasificación*, etc) y mejora la escalabilidad.
* Los parámetros de estos catálogos se interpretan en el código por su constante string `codigo` y no por su ID PK.

## Infraestructura Externa (Docker)
Todo el sistema está encapsulado para su construcción mediante la receta única de `infra/compose.yml`.
