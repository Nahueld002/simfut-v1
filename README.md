# SimFut v1 (Simulador de Fútbol)

Bienvenido a **SimFut-v1**, un simulador de gestión de fútbol construido para evaluar competiciones matemáticas, torneos y cruces deportivos mediante un engine de algoritmos predictivos (Elo) e inserción masiva de datos. Está diseñado modularmente para admitir extensiones gráficas o complejas bases estadísticas.

---

## 🚀 QuickStart (Levantar con 1 Comando)
La forma más fácil de iniciar el proyecto y empezar a contribuir.

1. **Clona el repo**:
   ```bash
   git clone https://github.com/Nahueld002/simfut-v1.git
   cd simfut-v1
   ```

2. **Copia el ejemplo de entorno**:
   ```bash
   cp infra/env.example .env
   # Edita .env y coloca passwords reales si lo deseas.
   ```

3. **¡Levanta el proyecto con Docker!**:
   ```bash
   docker compose -f infra/compose.yml up --build
   ```
   *El frontend estará en http://localhost:3000, y el backend en http://localhost:8000.*

---

## 🏗️ Mapa del Monorepo

- 📂 [apps/backend/](./apps/backend/): API HTTP en Python (FastAPI).
- 📂 [apps/frontend/](./apps/frontend/): Interfaz en base React (NextJS).
- 📂 [infra/](./infra/): Docker-Compose (`compose.yml`) e infraestructura de despliegues.
- 📂 [database/](./database/): Dumps SQL, Migraciones requeridas y docs de la DB.
  *(Nota: El script integral primario se encuentra actualmente en `apps/backend/scripts/simfut_db_v2.sql`)*
- 📂 [docs/](./docs/): 
  - [Guía de Desarrollo (Dev)](./docs/dev/)
  - [Arquitectura (Architecture)](./docs/architecture/)
  - [Guía de Base de Datos](./docs/database/)
- 📂 [scripts/](./scripts/): Herramientas y scripts auxiliares.
- 📂 [data/](./data/): Archivos template (.xlsx de ejemplo) para carga y testing manual.

## 🤝 Cómo Contribuir
Agradecemos aportes y refactores de toda índole: desde un typo en el README hasta un endpoint enteramente nuevo. 

Por favor, revisa obligatoriamente:
- [CONTRIBUTING.md](./CONTRIBUTING.md) para políticas de Pull Request y Convenciones.
- `database/migrations/` ante cualquier cambio de esquema. No se aceptan cambios a la BD que no pasen por un script de migración referenciado.

## 🛡️ Seguridad
Cualquier filtración encontrada de contraseñas de producción o testing, por favor **sigue nuestro reporte responsable en [SECURITY.md](./SECURITY.md)** y actualiza tus credenciales. 
Nunca comprometas contraseñas reales ni subas archivos `.env`.
