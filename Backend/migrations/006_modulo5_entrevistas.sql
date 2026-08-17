-- ============================================================================
-- SAKURA - MODULO 5 ENTREVISTAS
-- Migracion 006
-- ============================================================================
-- Objetivos:
--  * múltiples tipos por cita (tbl_cita_tipo_entrevista)
--  * entrevistadores asignados por cita + tipo
--  * múltiples evaluaciones por cita: una por usuario + tipo
--  * auditoría básica de cita/evaluación
--  * INT_EVALUATE para Reclutador
--  * compatibilidad con datos históricos existentes
-- ============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Auditoría mínima de la cita
-- ---------------------------------------------------------------------------
ALTER TABLE tbl_cita_entrevista
    ADD COLUMN IF NOT EXISTS ctev_usuario_creador_id integer,
    ADD COLUMN IF NOT EXISTS ctev_fecha_actualizacion timestamp without time zone,
    ADD COLUMN IF NOT EXISTS ctev_motivo_estado character varying(300);

DO $$ BEGIN
    ALTER TABLE tbl_cita_entrevista
        ADD CONSTRAINT fk_tbl_cita_entrevista_usuario_creador
        FOREIGN KEY (ctev_usuario_creador_id) REFERENCES tbl_usuario(usr_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

UPDATE tbl_cita_entrevista
SET ctev_fecha_actualizacion = COALESCE(ctev_fecha_actualizacion, ctev_fecha_creacion, CURRENT_TIMESTAMP)
WHERE ctev_fecha_actualizacion IS NULL;

-- Garantizar la asociación N:M de tipos para datos antiguos.
INSERT INTO tbl_cita_tipo_entrevista (cten_tipo_entrevista_id, cten_cita_entrevista_id)
SELECT ctev_tipo_entrevista_id, ctev_id
FROM tbl_cita_entrevista
WHERE ctev_tipo_entrevista_id IS NOT NULL
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------------
-- 2. Entrevistador por tipo de entrevista
-- ---------------------------------------------------------------------------
ALTER TABLE tbl_usuario_cita_entrevista
    ADD COLUMN IF NOT EXISTS usrce_tipo_entrevista_id integer;

UPDATE tbl_usuario_cita_entrevista uc
SET usrce_tipo_entrevista_id = COALESCE(
    uc.usrce_tipo_entrevista_id,
    ce.ctev_tipo_entrevista_id,
    (
        SELECT MIN(ct.cten_tipo_entrevista_id)
        FROM tbl_cita_tipo_entrevista ct
        WHERE ct.cten_cita_entrevista_id = uc.usrce_cita_entrevista_id
    )
)
FROM tbl_cita_entrevista ce
WHERE ce.ctev_id = uc.usrce_cita_entrevista_id
  AND uc.usrce_tipo_entrevista_id IS NULL;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM tbl_usuario_cita_entrevista WHERE usrce_tipo_entrevista_id IS NULL) THEN
        RAISE EXCEPTION 'M5: existen asignaciones históricas sin tipo de entrevista. Corríjalas antes de continuar.';
    END IF;
END $$;

ALTER TABLE tbl_usuario_cita_entrevista
    ALTER COLUMN usrce_tipo_entrevista_id SET NOT NULL;

DO $$ BEGIN
    ALTER TABLE tbl_usuario_cita_entrevista
        ADD CONSTRAINT fk_tbl_usuario_cita_entrevista_tipo
        FOREIGN KEY (usrce_tipo_entrevista_id) REFERENCES tbl_tipo_entrevista(tpet_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

ALTER TABLE tbl_usuario_cita_entrevista
    DROP CONSTRAINT IF EXISTS pk_tbl_usuario_cita_entrevista;
ALTER TABLE tbl_usuario_cita_entrevista
    ADD CONSTRAINT pk_tbl_usuario_cita_entrevista
    PRIMARY KEY (usrce_cita_entrevista_id, usrce_usuario_id, usrce_tipo_entrevista_id);

-- ---------------------------------------------------------------------------
-- 3. Evaluación identificada por usuario + tipo
-- ---------------------------------------------------------------------------
ALTER TABLE tbl_evaluacion_entrevista
    ADD COLUMN IF NOT EXISTS even_usuario_id integer,
    ADD COLUMN IF NOT EXISTS even_tipo_entrevista_id integer,
    ADD COLUMN IF NOT EXISTS even_fecha_creacion timestamp without time zone,
    ADD COLUMN IF NOT EXISTS even_fecha_actualizacion timestamp without time zone;

-- Backfill seguro cuando la cita histórica posee una única combinación usuario/tipo.
UPDATE tbl_evaluacion_entrevista ev
SET even_usuario_id = x.usrce_usuario_id,
    even_tipo_entrevista_id = x.usrce_tipo_entrevista_id
FROM (
    SELECT usrce_cita_entrevista_id,
           MIN(usrce_usuario_id) AS usrce_usuario_id,
           MIN(usrce_tipo_entrevista_id) AS usrce_tipo_entrevista_id
    FROM tbl_usuario_cita_entrevista
    GROUP BY usrce_cita_entrevista_id
    HAVING COUNT(*) = 1
) x
WHERE ev.even_cita_entrevista_id = x.usrce_cita_entrevista_id
  AND ev.even_usuario_id IS NULL
  AND ev.even_tipo_entrevista_id IS NULL;

UPDATE tbl_evaluacion_entrevista
SET even_fecha_creacion = COALESCE(even_fecha_creacion, CURRENT_TIMESTAMP),
    even_fecha_actualizacion = COALESCE(even_fecha_actualizacion, even_fecha_creacion, CURRENT_TIMESTAMP);

DO $$ BEGIN
    ALTER TABLE tbl_evaluacion_entrevista
        ADD CONSTRAINT fk_tbl_evaluacion_entrevista_usuario
        FOREIGN KEY (even_usuario_id) REFERENCES tbl_usuario(usr_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE tbl_evaluacion_entrevista
        ADD CONSTRAINT fk_tbl_evaluacion_entrevista_tipo
        FOREIGN KEY (even_tipo_entrevista_id) REFERENCES tbl_tipo_entrevista(tpet_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE UNIQUE INDEX IF NOT EXISTS uq_m5_evaluacion_cita_usuario_tipo
    ON tbl_evaluacion_entrevista(even_cita_entrevista_id, even_usuario_id, even_tipo_entrevista_id)
    WHERE even_usuario_id IS NOT NULL AND even_tipo_entrevista_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 4. Índices de consulta
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_m5_cita_slcd ON tbl_cita_entrevista(ctev_solicitud_candidato_id);
CREATE INDEX IF NOT EXISTS idx_m5_cita_estado ON tbl_cita_entrevista(ctev_estado_entrevista_id);
CREATE INDEX IF NOT EXISTS idx_m5_cita_fecha ON tbl_cita_entrevista(ctev_fecha_hora_inicio);
CREATE INDEX IF NOT EXISTS idx_m5_usuario_cita_usuario ON tbl_usuario_cita_entrevista(usrce_usuario_id);
CREATE INDEX IF NOT EXISTS idx_m5_usuario_cita_tipo ON tbl_usuario_cita_entrevista(usrce_tipo_entrevista_id);
CREATE INDEX IF NOT EXISTS idx_m5_eval_cita ON tbl_evaluacion_entrevista(even_cita_entrevista_id);

-- ---------------------------------------------------------------------------
-- 5. Reclutador también puede entrevistar/evaluar
-- ---------------------------------------------------------------------------
INSERT INTO tbl_rol_permiso (rlpm_rol_id, rlpm_permiso_id)
SELECT r.rol_id, p.per_id
FROM tbl_rol r
JOIN tbl_permiso p ON p.per_nombre = 'INT_EVALUATE'
WHERE r.rol_nombre = 'Reclutador'
ON CONFLICT DO NOTHING;

COMMIT;
