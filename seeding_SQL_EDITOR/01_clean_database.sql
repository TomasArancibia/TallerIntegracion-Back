-- EJECUTAR COMPLETO ANTES DEL SEEDING EXHAUSTIVO

-- LIMPIEZA TOTAL CON TRUNCATE (MÁS EFECTIVA)
-- Paso 1: Desactivar triggers de foreign key temporalmente
SET session_replication_role = replica;

-- Paso 2: Usar TRUNCATE en lugar de DELETE (más eficiente)
TRUNCATE TABLE solicitud CASCADE;
TRUNCATE TABLE cama CASCADE;
TRUNCATE TABLE habitacion CASCADE;
TRUNCATE TABLE hospital CASCADE;
TRUNCATE TABLE area CASCADE;

-- Paso 3: Reactivar triggers
SET session_replication_role = DEFAULT;

-- Paso 4: Resetear secuencias de auto-incremento
ALTER SEQUENCE hospital_id_hospital_seq RESTART WITH 1;
ALTER SEQUENCE habitacion_id_habitacion_seq RESTART WITH 1;
ALTER SEQUENCE cama_id_cama_seq RESTART WITH 1;
ALTER SEQUENCE area_id_area_seq RESTART WITH 1;
ALTER SEQUENCE solicitud_id_solicitud_seq RESTART WITH 1;

-- Verificar que todo esté vacío
SELECT 
    'hospital' as tabla, COUNT(*) as registros FROM hospital
UNION ALL
SELECT 'area' as tabla, COUNT(*) as registros FROM area
UNION ALL
SELECT 'habitacion' as tabla, COUNT(*) as registros FROM habitacion
UNION ALL
SELECT 'cama' as tabla, COUNT(*) as registros FROM cama
UNION ALL
SELECT 'solicitud' as tabla, COUNT(*) as registros FROM solicitud;

SELECT 'Limpieza TOTAL completada' as status;