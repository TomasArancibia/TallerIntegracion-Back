-- EJECUTAR COMPLETO ANTES DEL SEEDING EXHAUSTIVO
-- Elimina las tablas y tipos existentes para permitir recrear el esquema desde cero.

DROP TABLE IF EXISTS solicitud CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;
DROP TABLE IF EXISTS cama CASCADE;
DROP TABLE IF EXISTS habitacion CASCADE;
DROP TABLE IF EXISTS piso CASCADE;
DROP TABLE IF EXISTS servicio CASCADE;
DROP TABLE IF EXISTS edificio CASCADE;
DROP TABLE IF EXISTS institucion CASCADE;
DROP TABLE IF EXISTS area CASCADE;

DROP TYPE IF EXISTS estado_solicitud CASCADE;
DROP TYPE IF EXISTS tipo_solicitud CASCADE;
DROP TYPE IF EXISTS rol_usuario CASCADE;

SELECT 'Limpieza total completada. Ejecute ahora 02_seed_exhaustive.sql' AS status;
