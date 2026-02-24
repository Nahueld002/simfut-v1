# Documentación de Desarrollo

## Requisitos Previos Generales
- Docker y Docker Compose
- Python 3.10+ (si corres backend local)
- Node.js 18+ (si corres frontend local)
- PostgreSQL 16+

## Variables de Entorno
Copia `infra/env.example` como `.env` en la raíz del proyecto. **NUNCA subas archivos`.env` al repositorio**.
Rellena tus contraseñas seguras allí.

```env
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=simfut_db
POSTGRES_PORT=5432
# etc
```

## Levantar todo en Docker
Desde la raíz del proyecto, basta ejecutar:

```bash
docker compose -f infra/compose.yml up --build
```
Esto levantará:
- PostgreSQL (puerto 5432)
- FastApi Backend (puerto 8000)
- Next.js Frontend (puerto 3000)

## Desarrollo Backend (Modo Local)
```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Desarrollo Frontend (Modo Local)
```bash
cd apps/frontend
npm install
npm run dev
```
