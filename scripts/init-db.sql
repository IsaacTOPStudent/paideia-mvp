-- PAIDEIA MVP - Inicialización simple

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS students;
CREATE SCHEMA IF NOT EXISTS diagnostics;
CREATE SCHEMA IF NOT EXISTS evaluations;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

SET timezone = 'America/Bogota';

COMMENT ON SCHEMA auth IS 'Autenticación';
COMMENT ON SCHEMA students IS 'Estudiantes';
COMMENT ON SCHEMA diagnostics IS 'Diagnósticos';
COMMENT ON SCHEMA evaluations IS 'Evaluaciones';

DO $$
BEGIN
  RAISE NOTICE 'Base de datos PAIDEIA inicializada correctamente';
END
$$;