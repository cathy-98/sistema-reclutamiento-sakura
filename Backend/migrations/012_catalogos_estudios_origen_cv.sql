-- =============================================================
-- SAKURA - Etapa 3 de catalogos automaticos desde CV
-- Instituciones educativas y carreras
-- =============================================================
-- El importador solo crea nombres obtenidos en contexto academico explicito;
-- no inventa nivel, tipo de institucion ni descripciones.

BEGIN;

ALTER TABLE tbl_institucion
    ADD COLUMN IF NOT EXISTS inst_creado_automaticamente boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS inst_origen varchar(20),
    ADD COLUMN IF NOT EXISTS inst_origen_candidato_id integer;

ALTER TABLE tbl_carrera
    ADD COLUMN IF NOT EXISTS crra_creado_automaticamente boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS crra_origen varchar(20),
    ADD COLUMN IF NOT EXISTS crra_origen_candidato_id integer;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_tbl_institucion_origen_candidato'
          AND conrelid = 'tbl_institucion'::regclass
    ) THEN
        ALTER TABLE tbl_institucion
            ADD CONSTRAINT fk_tbl_institucion_origen_candidato
            FOREIGN KEY (inst_origen_candidato_id)
            REFERENCES tbl_candidato(cand_id)
            ON UPDATE RESTRICT ON DELETE SET NULL;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_tbl_carrera_origen_candidato'
          AND conrelid = 'tbl_carrera'::regclass
    ) THEN
        ALTER TABLE tbl_carrera
            ADD CONSTRAINT fk_tbl_carrera_origen_candidato
            FOREIGN KEY (crra_origen_candidato_id)
            REFERENCES tbl_candidato(cand_id)
            ON UPDATE RESTRICT ON DELETE SET NULL;
    END IF;
END $$;

COMMENT ON COLUMN tbl_institucion.inst_creado_automaticamente IS
'Indica que la institucion fue creada por la importacion de un CV.';
COMMENT ON COLUMN tbl_institucion.inst_origen IS
'Origen de la alta automatica; actualmente CV.';
COMMENT ON COLUMN tbl_institucion.inst_origen_candidato_id IS
'Candidato cuyo CV origino la alta automatica.';

COMMENT ON COLUMN tbl_carrera.crra_creado_automaticamente IS
'Indica que la carrera fue creada por la importacion de un CV.';
COMMENT ON COLUMN tbl_carrera.crra_origen IS
'Origen de la alta automatica; actualmente CV.';
COMMENT ON COLUMN tbl_carrera.crra_origen_candidato_id IS
'Candidato cuyo CV origino la alta automatica.';

COMMIT;
