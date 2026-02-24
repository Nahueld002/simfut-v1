# Cambios en la Base de Datos

## Control de Versiones / Migraciones

Toda modificación a la estructura de la base de datos (tablas, columnas, restricciones) debe reflejarse mediante un script SQL en `database/migrations/` y documentarse. 

### Migración `0001_add_ciudad_id_to_competencia.sql`
- **Qué cambió**: Se agregó la columna `ciudad_id` a la tabla `futsim.competencia`, que actúa como Foreign Key hacia `futsim.ciudad(ciudad_id)`.
- **Por qué cambió**: Era necesario vincular una competencia con una ciudad en particular para la lógica geográfica del motor.
- **Cómo migrar una DB existente**:
  Para aplicar este cambio en una base de datos antigua que no cuenta con el campo, simplemente ejecuta el script `database/migrations/0001_add_ciudad_id_to_competencia.sql` en tu cliente SQL (DBeaver, psql, etc).

```sql
ALTER TABLE futsim.competencia 
ADD COLUMN IF NOT EXISTS ciudad_id INT REFERENCES futsim.ciudad(ciudad_id);
```
