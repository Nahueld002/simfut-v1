-- Migration: 0001_add_ciudad_id_to_competencia
-- Objeto: Reflejar los cambios realizados en alter_db.py donde se agregó la vinculación de ciudad a la competencia.

ALTER TABLE futsim.competencia 
ADD COLUMN IF NOT EXISTS ciudad_id INT REFERENCES futsim.ciudad(ciudad_id);
