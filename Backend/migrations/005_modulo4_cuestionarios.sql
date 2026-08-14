BEGIN;

ALTER TABLE public.tbl_candidato_cuestionario
    ADD COLUMN IF NOT EXISTS cdcu_fecha_inicio timestamp without time zone;

ALTER TABLE public.tbl_candidato_cuestionario
    ADD COLUMN IF NOT EXISTS cdcu_fecha_vencimiento timestamp without time zone;

-- Compatibilidad para registros históricos existentes.
UPDATE public.tbl_candidato_cuestionario
   SET cdcu_fecha_vencimiento = COALESCE(
       cdcu_fecha_vencimiento,
       cdcu_fecha_asignacion + interval '30 days'
   )
 WHERE cdcu_fecha_vencimiento IS NULL;

ALTER TABLE public.tbl_candidato_cuestionario
    ALTER COLUMN cdcu_fecha_vencimiento SET NOT NULL;

ALTER TABLE public.tbl_candidato_cuestionario
    ALTER COLUMN cdcu_permitir_reintento SET DEFAULT false;

UPDATE public.tbl_candidato_cuestionario
   SET cdcu_permitir_reintento = false
 WHERE cdcu_permitir_reintento IS NULL;

ALTER TABLE public.tbl_candidato_cuestionario
    ALTER COLUMN cdcu_permitir_reintento SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
         WHERE conname = 'uq_tbl_pregunta_cuestionario'
    ) THEN
        ALTER TABLE public.tbl_pregunta_cuestionario
            ADD CONSTRAINT uq_tbl_pregunta_cuestionario
            UNIQUE (prcu_cuestionario_id, prcu_pregunta_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
         WHERE conname = 'uq_tbl_candidato_cuestionario_candidato_cuestionario'
    ) THEN
        ALTER TABLE public.tbl_candidato_cuestionario
            ADD CONSTRAINT uq_tbl_candidato_cuestionario_candidato_cuestionario
            UNIQUE (cdcu_candidato_id, cdcu_cuestionario_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
         WHERE conname = 'uq_tbl_respuesta_asignacion_pregunta'
    ) THEN
        ALTER TABLE public.tbl_respuesta_pregunta
            ADD CONSTRAINT uq_tbl_respuesta_asignacion_pregunta
            UNIQUE (rspr_candidato_cuestionario_id, rspr_pregunta_cuestionario_id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_tbl_candidato_cuestionario_estado
    ON public.tbl_candidato_cuestionario(cdcu_estado_cuestionario_candidato_id);

CREATE INDEX IF NOT EXISTS idx_tbl_candidato_cuestionario_candidato
    ON public.tbl_candidato_cuestionario(cdcu_candidato_id);

CREATE INDEX IF NOT EXISTS idx_tbl_candidato_cuestionario_cuestionario
    ON public.tbl_candidato_cuestionario(cdcu_cuestionario_id);

CREATE INDEX IF NOT EXISTS idx_tbl_respuesta_asignacion
    ON public.tbl_respuesta_pregunta(rspr_candidato_cuestionario_id);

-- El diseño funcional acordó que Reclutador también puede crear cuestionarios
-- y mantener el banco. Se reutiliza CUEST_CREATE; no se crea un permiso nuevo.
INSERT INTO public.tbl_rol_permiso (rlpm_rol_id, rlpm_permiso_id)
SELECT r.rol_id, p.per_id
  FROM public.tbl_rol r
 CROSS JOIN public.tbl_permiso p
 WHERE LOWER(r.rol_nombre) = LOWER('Reclutador')
   AND p.per_nombre = 'CUEST_CREATE'
   AND NOT EXISTS (
       SELECT 1
         FROM public.tbl_rol_permiso rp
        WHERE rp.rlpm_rol_id = r.rol_id
          AND rp.rlpm_permiso_id = p.per_id
   );

COMMIT;
