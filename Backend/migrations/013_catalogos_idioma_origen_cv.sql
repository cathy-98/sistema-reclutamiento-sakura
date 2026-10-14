-- =============================================================
-- SAKURA - Etapa 4 de catalogos automaticos desde CV
-- Idiomas creados a partir de una seccion explicita y un nivel resoluble
-- =============================================================
-- El modelo exige nivel para asociar un idioma al candidato. La trazabilidad
-- se agrega al catalogo, pero el importador solo crea el idioma cuando puede
-- persistir tambien una asociacion valida; asi no quedan idiomas huerfanos.

BEGIN;

ALTER TABLE tbl_idioma
    ADD COLUMN IF NOT EXISTS idio_creado_automaticamente boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS idio_origen varchar(20),
    ADD COLUMN IF NOT EXISTS idio_origen_candidato_id integer;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_tbl_idioma_origen_candidato'
          AND conrelid = 'tbl_idioma'::regclass
    ) THEN
        ALTER TABLE tbl_idioma
            ADD CONSTRAINT fk_tbl_idioma_origen_candidato
            FOREIGN KEY (idio_origen_candidato_id)
            REFERENCES tbl_candidato(cand_id)
            ON UPDATE RESTRICT ON DELETE SET NULL;
    END IF;
END $$;

COMMENT ON COLUMN tbl_idioma.idio_creado_automaticamente IS
'Indica que el idioma fue creado por la importacion de un CV.';
COMMENT ON COLUMN tbl_idioma.idio_origen IS
'Origen de la alta automatica; actualmente CV.';
COMMENT ON COLUMN tbl_idioma.idio_origen_candidato_id IS
'Candidato cuyo CV origino la alta automatica.';

COMMIT;
