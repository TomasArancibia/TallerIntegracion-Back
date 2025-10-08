-- EJECUTAR COMPLETO PARA EL SEEDING EXHAUSTIVO

-- SEEDING DESDE CERO

-- 1. ÁREAS (IDs: 1, 2, 3, 4, 5)
INSERT INTO area (nombre) VALUES 
    ('Mantención'),
    ('Nutrición y alimentación a pacientes'),
    ('Limpieza de habitación, baño o box'),
    ('Asistencia social'),
    ('Acompañamiento espiritual');

-- 2. HOSPITALES (IDs: 1, 2)
INSERT INTO hospital (nombre) VALUES 
    ('Hospital UC Christus Demo'),
    ('Clínica San Lucas');

-- 3. HABITACIONES (IDs: 1-8)
INSERT INTO habitacion (numero, id_hospital) VALUES 
    ('101', 1), ('102', 1), ('103', 1), ('104', 1),  -- Hospital UC Christus Demo
    ('101', 2), ('102', 2), ('103', 2), ('104', 2);  -- Clínica San Lucas

-- 4. CAMAS (IDs: 1-24)
INSERT INTO cama (identificador_qr, id_habitacion, activo) VALUES 
    ('H1-101-A', 1, true), ('H1-101-B', 1, false), ('H1-101-C', 1, true),
    ('H1-102-A', 2, true), ('H1-102-B', 2, true), ('H1-102-C', 2, true),
    ('H1-103-A', 3, true), ('H1-103-B', 3, false), ('H1-103-C', 3, true),
    ('H1-104-A', 4, true), ('H1-104-B', 4, true), ('H1-104-C', 4, true),
    ('H2-101-A', 5, true), ('H2-101-B', 5, true), ('H2-101-C', 5, true),
    ('H2-102-A', 6, true), ('H2-102-B', 6, true), ('H2-102-C', 6, false),
    ('H2-103-A', 7, true), ('H2-103-B', 7, true), ('H2-103-C', 7, true),
    ('H2-104-A', 8, true), ('H2-104-B', 8, true), ('H2-104-C', 8, false);

-- 5. SOLICITUDES DE EJEMPLO
INSERT INTO solicitud (id_cama, id_area, identificador_qr, tipo, descripcion, estado_actual, fecha_creacion)
SELECT 
    c.id_cama, 1, c.identificador_qr, 'BAÑO',
    'BAÑO — ejemplo en ' || hosp.nombre || ' habitación ' || h.numero,
    'pendiente'::estadosolicitud,
    NOW() - INTERVAL '1 day'
FROM cama c
JOIN habitacion h ON c.id_habitacion = h.id_habitacion
JOIN hospital hosp ON h.id_hospital = hosp.id_hospital
WHERE c.activo = true
LIMIT 12;

INSERT INTO solicitud (id_cama, id_area, identificador_qr, tipo, descripcion, estado_actual, fecha_creacion)
SELECT 
    c.id_cama, 1, c.identificador_qr, 'CLIMATIZACIÓN',
    'CLIMATIZACIÓN — ejemplo en ' || hosp.nombre || ' habitación ' || h.numero,
    'en_proceso'::estadosolicitud,
    NOW() - INTERVAL '2 days'
FROM cama c
JOIN habitacion h ON c.id_habitacion = h.id_habitacion
JOIN hospital hosp ON h.id_hospital = hosp.id_hospital
WHERE c.activo = true
LIMIT 12;

-- VERIFICACIÓN FINAL
SELECT 
    'hospital' as tabla, 
    COUNT(*) as registros, 
    MIN(id_hospital) as min_id, 
    MAX(id_hospital) as max_id 
FROM hospital
UNION ALL
SELECT 
    'area' as tabla, 
    COUNT(*) as registros, 
    MIN(id_area) as min_id, 
    MAX(id_area) as max_id 
FROM area
UNION ALL
SELECT 
    'habitacion' as tabla, 
    COUNT(*) as registros, 
    MIN(id_habitacion) as min_id, 
    MAX(id_habitacion) as max_id 
FROM habitacion
UNION ALL
SELECT 
    'cama' as tabla, 
    COUNT(*) as registros, 
    MIN(id_cama) as min_id, 
    MAX(id_cama) as max_id 
FROM cama
UNION ALL
SELECT 
    'solicitud' as tabla, 
    COUNT(*) as registros, 
    MIN(id_solicitud) as min_id, 
    MAX(id_solicitud) as max_id 
FROM solicitud;