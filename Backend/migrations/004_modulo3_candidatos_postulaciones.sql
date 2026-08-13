BEGIN;

-- M3: rutas/URLs de CV. Se permiten varias separadas por ';'.
ALTER TABLE public.tbl_candidato
    ADD COLUMN IF NOT EXISTS cand_cv_urls character varying(2000);

-- Un candidato solo puede estar una vez en la misma solicitud.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_tbl_solicitud_candidato_solicitud_candidato'
    ) THEN
        ALTER TABLE public.tbl_solicitud_candidato
        ADD CONSTRAINT uq_tbl_solicitud_candidato_solicitud_candidato
        UNIQUE (slcd_solicitud_id, slcd_candidato_id);
    END IF;
END $$;

-- Una habilidad no debe repetirse dentro del perfil de un candidato.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_tbl_candidato_habilidad_candidato_habilidad'
    ) THEN
        ALTER TABLE public.tbl_candidato_habilidad
        ADD CONSTRAINT uq_tbl_candidato_habilidad_candidato_habilidad
        UNIQUE (cdhb_candidato_id, cdhb_habilidad_id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_tbl_candidato_email_lower
    ON public.tbl_candidato (lower(cand_email));

CREATE INDEX IF NOT EXISTS ix_tbl_solicitud_candidato_solicitud_estado
    ON public.tbl_solicitud_candidato (slcd_solicitud_id, slcd_estado_solicitud_candidato_id);

COMMIT;
