-- =============================================================
-- SAKURA - Etapa 1 de catalogos automaticos desde CV
-- Empresas y cargos de experiencias laborales
-- =============================================================
-- La importacion reutiliza catalogos existentes y puede crear valores
-- nuevos validos. Estas columnas permiten distinguirlos de registros
-- administrativos y conservar el candidato que origino la alta.

BEGIN;

ALTER TABLE tbl_empresa
    ADD COLUMN IF NOT EXISTS emp_creado_automaticamente boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS emp_origen varchar(20),
    ADD COLUMN IF NOT EXISTS emp_origen_candidato_id integer;

ALTER TABLE tbl_cargo
    ADD COLUMN IF NOT EXISTS crgo_creado_automaticamente boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS crgo_origen varchar(20),
    ADD COLUMN IF NOT EXISTS crgo_origen_candidato_id integer;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_tbl_empresa_origen_candidato'
          AND conrelid = 'tbl_empresa'::regclass
    ) THEN
        ALTER TABLE tbl_empresa
            ADD CONSTRAINT fk_tbl_empresa_origen_candidato
            FOREIGN KEY (emp_origen_candidato_id)
            REFERENCES tbl_candidato(cand_id)
            ON UPDATE RESTRICT ON DELETE SET NULL;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_tbl_cargo_origen_candidato'
          AND conrelid = 'tbl_cargo'::regclass
    ) THEN
        ALTER TABLE tbl_cargo
            ADD CONSTRAINT fk_tbl_cargo_origen_candidato
            FOREIGN KEY (crgo_origen_candidato_id)
            REFERENCES tbl_candidato(cand_id)
            ON UPDATE RESTRICT ON DELETE SET NULL;
    END IF;
END $$;

COMMENT ON COLUMN tbl_empresa.emp_creado_automaticamente IS
'Indica que la empresa fue creada por la importacion de un CV.';
COMMENT ON COLUMN tbl_empresa.emp_origen IS
'Origen de la alta automatica; actualmente CV.';
COMMENT ON COLUMN tbl_empresa.emp_origen_candidato_id IS
'Candidato cuyo CV origino la alta automatica.';

COMMENT ON COLUMN tbl_cargo.crgo_creado_automaticamente IS
'Indica que el cargo fue creado por la importacion de un CV.';
COMMENT ON COLUMN tbl_cargo.crgo_origen IS
'Origen de la alta automatica; actualmente CV.';
COMMENT ON COLUMN tbl_cargo.crgo_origen_candidato_id IS
'Candidato cuyo CV origino la alta automatica.';

COMMIT;
