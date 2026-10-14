-- =============================================================
-- SAKURA - Etapa 2 de catalogos automaticos desde CV
-- Habilidades y tecnologias
-- =============================================================
-- La importacion reutiliza habilidades normalizadas y solo crea valores
-- declarados en secciones confiables del CV. Estas columnas conservan la
-- trazabilidad sin exigir descripcion ni categoria inventadas.

BEGIN;

ALTER TABLE tbl_habilidad
    ADD COLUMN IF NOT EXISTS hab_creado_automaticamente boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS hab_origen varchar(20),
    ADD COLUMN IF NOT EXISTS hab_origen_candidato_id integer;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_tbl_habilidad_origen_candidato'
          AND conrelid = 'tbl_habilidad'::regclass
    ) THEN
        ALTER TABLE tbl_habilidad
            ADD CONSTRAINT fk_tbl_habilidad_origen_candidato
            FOREIGN KEY (hab_origen_candidato_id)
            REFERENCES tbl_candidato(cand_id)
            ON UPDATE RESTRICT ON DELETE SET NULL;
    END IF;
END $$;

COMMENT ON COLUMN tbl_habilidad.hab_creado_automaticamente IS
'Indica que la habilidad fue creada por la importacion de un CV.';
COMMENT ON COLUMN tbl_habilidad.hab_origen IS
'Origen de la alta automatica; actualmente CV.';
COMMENT ON COLUMN tbl_habilidad.hab_origen_candidato_id IS
'Candidato cuyo CV origino la alta automatica.';

COMMIT;
