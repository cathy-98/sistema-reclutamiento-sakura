-- Módulo 2 - Migración de código de solicitud SOL-000001
-- Ejecutar UNA vez sobre la base PostgreSQL existente antes de usar el nuevo backend.

BEGIN;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM public.tbl_solicitud
        WHERE sol_id > 999999
    ) THEN
        RAISE EXCEPTION 'Existen solicitudes con sol_id > 999999. No se puede aplicar el formato SOL-000001.';
    END IF;
END $$;

ALTER TABLE public.tbl_solicitud
    DROP CONSTRAINT IF EXISTS chk_tbl_solicitud_codigo;

ALTER TABLE public.tbl_solicitud
    ALTER COLUMN sol_codigo TYPE character varying(10);

-- Normaliza los códigos existentes usando el ID real de la solicitud.
UPDATE public.tbl_solicitud
SET sol_codigo = 'SOL-' || LPAD(sol_id::text, 6, '0')
WHERE sol_id IS NOT NULL;

ALTER TABLE public.tbl_solicitud
    ADD CONSTRAINT chk_tbl_solicitud_codigo
    CHECK (sol_codigo ~ '^SOL-[0-9]{6}$');

COMMIT;
