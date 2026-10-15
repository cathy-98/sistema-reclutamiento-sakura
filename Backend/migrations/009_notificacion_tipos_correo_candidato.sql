-- =============================================================
-- SAKURA - Módulo 6 / Comunicaciones
-- Migración 009: Alinear tipos del historial de notificaciones
-- Fecha: 2026-10-06
--
-- La tabla de plantillas ya contempla los tipos de correo usados por
-- los flujos actuales de candidatos. El historial debe aceptar esas
-- mismas comunicaciones para no rechazar el registro después del envío.
-- =============================================================

BEGIN;

DO $$
BEGIN
    IF to_regclass('public.tbl_notificacion_reclutamiento') IS NULL THEN
        RAISE EXCEPTION
            'No existe public.tbl_notificacion_reclutamiento. Ejecute primero 007_modulo6_informes.sql.';
    END IF;
END $$;

ALTER TABLE tbl_notificacion_reclutamiento
    DROP CONSTRAINT IF EXISTS chk_tbl_notificacion_tipo;

ALTER TABLE tbl_notificacion_reclutamiento
    ADD CONSTRAINT chk_tbl_notificacion_tipo
    CHECK (
        ntfr_tipo IN (
            'RECHAZO',
            'AGRADECIMIENTO',
            'DIRECTIVOS',
            'CONTACTO',
            'INVITACION',
            'AVANCE',
            'SELECCION'
        )
    );

COMMIT;
