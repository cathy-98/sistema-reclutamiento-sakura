-- =============================================================
-- SAKURA - Módulo 6 / Perfil de Candidato
-- Migración 008: Normalización del nivel de idioma
-- Fecha: 2026-08-18
--
-- Objetivo:
--   1. Crear el catálogo tbl_nivel_idioma.
--   2. Reemplazar tbl_candidato_idioma.cdio_nivel (VARCHAR)
--      por tbl_candidato_idioma.cdio_nivel_idioma_id (FK).
--   3. Preservar fielmente los niveles históricos genéricos:
--        Basico       -> BAS
--        Intermedio   -> INT
--        Avanzado     -> AVA
--        Nativo       -> NAT
--      SIN inventar una equivalencia CEFR específica.
--   4. Incorporar niveles CEFR A1, A2, B1, B2, C1 y C2 para
--      nuevos registros y futura extracción automática desde CV.
--
-- Requisitos:
--   - Debe haberse ejecutado 007_modulo6_informes.sql.
--   - PostgreSQL.
--
-- La migración es idempotente en lo posible y se ejecuta en
-- una única transacción.
-- =============================================================

BEGIN;

-- =============================================================
-- 1. Catálogo de niveles de idioma
-- =============================================================
CREATE TABLE IF NOT EXISTS tbl_nivel_idioma (
    nvid_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nvid_codigo varchar(20) NOT NULL,
    nvid_nombre varchar(100) NOT NULL,
    nvid_grupo varchar(30) NOT NULL,
    nvid_es_generico boolean NOT NULL DEFAULT false,
    nvid_orden integer NOT NULL,
    nvid_descripcion varchar(255),
    nvid_activo boolean NOT NULL DEFAULT true,

    CONSTRAINT uq_tbl_nivel_idioma_codigo UNIQUE (nvid_codigo),
    CONSTRAINT uq_tbl_nivel_idioma_nombre UNIQUE (nvid_nombre),

    CONSTRAINT chk_tbl_nivel_idioma_codigo
        CHECK (trim(nvid_codigo) <> ''),

    CONSTRAINT chk_tbl_nivel_idioma_nombre
        CHECK (trim(nvid_nombre) <> ''),

    CONSTRAINT chk_tbl_nivel_idioma_grupo
        CHECK (nvid_grupo IN ('Basico', 'Intermedio', 'Avanzado', 'Nativo')),

    CONSTRAINT chk_tbl_nivel_idioma_orden
        CHECK (nvid_orden > 0)
);

COMMENT ON TABLE tbl_nivel_idioma IS
'Catálogo normalizado de niveles de dominio de idiomas. Incluye niveles genéricos históricos y niveles CEFR.';

COMMENT ON COLUMN tbl_nivel_idioma.nvid_codigo IS
'Código estable del nivel. Ejemplos: BAS, A1, A2, INT, B1, B2, AVA, C1, C2, NAT.';

COMMENT ON COLUMN tbl_nivel_idioma.nvid_grupo IS
'Grupo funcional resumido utilizado por Sakura: Basico, Intermedio, Avanzado o Nativo.';

COMMENT ON COLUMN tbl_nivel_idioma.nvid_es_generico IS
'TRUE cuando el nivel representa una clasificación general sin precisión CEFR.';

-- =============================================================
-- 2. Seeds
--
-- Los niveles genéricos permiten migrar los valores históricos
-- sin inventar precisión CEFR.
-- Los niveles A1-C2 permiten registrar niveles exactos.
-- =============================================================
INSERT INTO tbl_nivel_idioma (
    nvid_codigo,
    nvid_nombre,
    nvid_grupo,
    nvid_es_generico,
    nvid_orden,
    nvid_descripcion,
    nvid_activo
)
VALUES
    (
        'BAS',
        'Básico',
        'Basico',
        true,
        10,
        'Nivel básico genérico. Utilizado cuando la fuente no permite determinar A1 o A2.',
        true
    ),
    (
        'A1',
        'Básico A1',
        'Basico',
        false,
        11,
        'CEFR A1 - Usuario básico inicial.',
        true
    ),
    (
        'A2',
        'Básico A2',
        'Basico',
        false,
        12,
        'CEFR A2 - Usuario básico.',
        true
    ),
    (
        'INT',
        'Intermedio',
        'Intermedio',
        true,
        20,
        'Nivel intermedio genérico. Utilizado cuando la fuente no permite determinar B1 o B2.',
        true
    ),
    (
        'B1',
        'Intermedio B1',
        'Intermedio',
        false,
        21,
        'CEFR B1 - Usuario independiente intermedio.',
        true
    ),
    (
        'B2',
        'Intermedio B2',
        'Intermedio',
        false,
        22,
        'CEFR B2 - Usuario independiente intermedio alto.',
        true
    ),
    (
        'AVA',
        'Avanzado',
        'Avanzado',
        true,
        30,
        'Nivel avanzado genérico. Utilizado cuando la fuente no permite determinar C1 o C2.',
        true
    ),
    (
        'C1',
        'Avanzado C1',
        'Avanzado',
        false,
        31,
        'CEFR C1 - Usuario competente avanzado.',
        true
    ),
    (
        'C2',
        'Avanzado C2',
        'Avanzado',
        false,
        32,
        'CEFR C2 - Usuario competente con dominio pleno.',
        true
    ),
    (
        'NAT',
        'Nativo',
        'Nativo',
        false,
        40,
        'Idioma nativo o de dominio equivalente a lengua materna.',
        true
    )
ON CONFLICT (nvid_codigo) DO UPDATE
SET
    nvid_nombre = EXCLUDED.nvid_nombre,
    nvid_grupo = EXCLUDED.nvid_grupo,
    nvid_es_generico = EXCLUDED.nvid_es_generico,
    nvid_orden = EXCLUDED.nvid_orden,
    nvid_descripcion = EXCLUDED.nvid_descripcion,
    nvid_activo = EXCLUDED.nvid_activo;

CREATE INDEX IF NOT EXISTS ix_tbl_nivel_idioma_grupo
    ON tbl_nivel_idioma(nvid_grupo);

CREATE INDEX IF NOT EXISTS ix_tbl_nivel_idioma_activo_orden
    ON tbl_nivel_idioma(nvid_activo, nvid_orden);

-- =============================================================
-- 3. Validar existencia de tabla M6 previa
-- =============================================================
DO $$
BEGIN
    IF to_regclass('public.tbl_candidato_idioma') IS NULL THEN
        RAISE EXCEPTION
            'No existe public.tbl_candidato_idioma. Ejecute primero 007_modulo6_informes.sql.';
    END IF;
END $$;

-- =============================================================
-- 4. Agregar nueva FK nullable durante la migración
-- =============================================================
ALTER TABLE tbl_candidato_idioma
    ADD COLUMN IF NOT EXISTS cdio_nivel_idioma_id integer;

-- =============================================================
-- 5. Migrar datos históricos desde cdio_nivel
--
-- Se usa SQL dinámico porque en una segunda ejecución la columna
-- antigua puede haber sido eliminada.
-- =============================================================
DO $$
DECLARE
    v_sin_mapear integer;
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'tbl_candidato_idioma'
          AND column_name = 'cdio_nivel'
    ) THEN

        EXECUTE $sql$
            UPDATE tbl_candidato_idioma ci
            SET cdio_nivel_idioma_id = ni.nvid_id
            FROM tbl_nivel_idioma ni
            WHERE ci.cdio_nivel_idioma_id IS NULL
              AND ni.nvid_codigo =
                  CASE
                      WHEN lower(trim(ci.cdio_nivel)) IN ('basico', 'básico', 'basic')
                          THEN 'BAS'
                      WHEN lower(trim(ci.cdio_nivel)) IN ('intermedio', 'intermediate')
                          THEN 'INT'
                      WHEN lower(trim(ci.cdio_nivel)) IN ('avanzado', 'advanced')
                          THEN 'AVA'
                      WHEN lower(trim(ci.cdio_nivel)) IN ('nativo', 'native')
                          THEN 'NAT'

                      -- Soporte defensivo por si existieran datos
                      -- introducidos fuera del CHECK original.
                      WHEN upper(trim(ci.cdio_nivel)) = 'A1' THEN 'A1'
                      WHEN upper(trim(ci.cdio_nivel)) = 'A2' THEN 'A2'
                      WHEN upper(trim(ci.cdio_nivel)) = 'B1' THEN 'B1'
                      WHEN upper(trim(ci.cdio_nivel)) = 'B2' THEN 'B2'
                      WHEN upper(trim(ci.cdio_nivel)) = 'C1' THEN 'C1'
                      WHEN upper(trim(ci.cdio_nivel)) = 'C2' THEN 'C2'
                      ELSE NULL
                  END
        $sql$;

        EXECUTE $sql$
            SELECT count(*)
            FROM tbl_candidato_idioma
            WHERE cdio_nivel_idioma_id IS NULL
        $sql$
        INTO v_sin_mapear;

        IF v_sin_mapear > 0 THEN
            RAISE EXCEPTION
                'Migración 008 abortada: existen % registro(s) de tbl_candidato_idioma cuyo nivel no pudo mapearse. Revise cdio_nivel antes de reintentar.',
                v_sin_mapear;
        END IF;
    END IF;
END $$;

-- =============================================================
-- 6. Crear FK hacia catálogo
-- =============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_tbl_candidato_idioma_nivel'
          AND conrelid = 'tbl_candidato_idioma'::regclass
    ) THEN
        ALTER TABLE tbl_candidato_idioma
            ADD CONSTRAINT fk_tbl_candidato_idioma_nivel
            FOREIGN KEY (cdio_nivel_idioma_id)
            REFERENCES tbl_nivel_idioma(nvid_id)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_tbl_candidato_idioma_nivel
    ON tbl_candidato_idioma(cdio_nivel_idioma_id);

-- =============================================================
-- 7. Exigir nivel para todo candidato-idioma
--
-- Si la tabla está vacía también queda NOT NULL correctamente.
-- =============================================================
DO $$
DECLARE
    v_nulos integer;
BEGIN
    SELECT count(*)
    INTO v_nulos
    FROM tbl_candidato_idioma
    WHERE cdio_nivel_idioma_id IS NULL;

    IF v_nulos > 0 THEN
        RAISE EXCEPTION
            'Migración 008 abortada: quedan % registro(s) sin cdio_nivel_idioma_id.',
            v_nulos;
    END IF;

    ALTER TABLE tbl_candidato_idioma
        ALTER COLUMN cdio_nivel_idioma_id SET NOT NULL;
END $$;

-- =============================================================
-- 8. Eliminar CHECK antiguo y columna VARCHAR antigua
-- =============================================================
ALTER TABLE tbl_candidato_idioma
    DROP CONSTRAINT IF EXISTS chk_tbl_candidato_idioma_nivel;

ALTER TABLE tbl_candidato_idioma
    DROP COLUMN IF EXISTS cdio_nivel;

COMMENT ON COLUMN tbl_candidato_idioma.cdio_nivel_idioma_id IS
'Nivel normalizado del idioma del candidato. FK a tbl_nivel_idioma.';

COMMIT;

-- =============================================================
-- CONSULTAS DE VERIFICACIÓN POST-MIGRACIÓN
-- =============================================================

-- 1) Catálogo generado
SELECT
    nvid_id,
    nvid_codigo,
    nvid_nombre,
    nvid_grupo,
    nvid_es_generico,
    nvid_orden,
    nvid_activo
FROM tbl_nivel_idioma
ORDER BY nvid_orden, nvid_id;

-- 2) Estructura normalizada de idiomas del candidato
SELECT
    ci.cdio_id,
    ci.cdio_candidato_id,
    i.idio_id,
    i.idio_nombre,
    ni.nvid_id,
    ni.nvid_codigo,
    ni.nvid_nombre,
    ni.nvid_grupo
FROM tbl_candidato_idioma ci
JOIN tbl_idioma i
    ON i.idio_id = ci.cdio_idioma_id
JOIN tbl_nivel_idioma ni
    ON ni.nvid_id = ci.cdio_nivel_idioma_id
ORDER BY ci.cdio_candidato_id, i.idio_nombre;

-- 3) Esta consulta debe devolver 0 filas.
SELECT
    ci.cdio_id,
    ci.cdio_candidato_id,
    ci.cdio_idioma_id,
    ci.cdio_nivel_idioma_id
FROM tbl_candidato_idioma ci
LEFT JOIN tbl_nivel_idioma ni
    ON ni.nvid_id = ci.cdio_nivel_idioma_id
WHERE ni.nvid_id IS NULL;
