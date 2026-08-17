BEGIN;

-- =============================================================
-- MÓDULO 6 - INFORMES, CIERRE Y COMUNICACIONES
-- PostgreSQL / Sakura
-- =============================================================

CREATE TABLE IF NOT EXISTS tbl_categoria_habilidad (
    cthb_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cthb_nombre varchar(100) NOT NULL,
    cthb_descripcion varchar(300),
    CONSTRAINT uq_tbl_categoria_habilidad_nombre UNIQUE (cthb_nombre),
    CONSTRAINT chk_tbl_categoria_habilidad_nombre CHECK (trim(cthb_nombre) <> '')
);

INSERT INTO tbl_categoria_habilidad (cthb_nombre, cthb_descripcion)
VALUES
    ('Lenguajes', 'Lenguajes de programación'),
    ('Frameworks / Librerías', 'Frameworks y librerías de desarrollo'),
    ('Bases de Datos', 'Motores, tecnologías y herramientas de datos'),
    ('Cloud / DevOps', 'Cloud, contenedores, CI/CD y automatización'),
    ('Herramientas', 'Herramientas técnicas generales'),
    ('Metodologías', 'Metodologías, prácticas y marcos de trabajo'),
    ('Otros', 'Conocimientos sin categoría específica')
ON CONFLICT (cthb_nombre) DO NOTHING;

ALTER TABLE tbl_habilidad
    ADD COLUMN IF NOT EXISTS hab_categoria_habilidad_id integer;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_tbl_habilidad_categoria_habilidad'
    ) THEN
        ALTER TABLE tbl_habilidad
            ADD CONSTRAINT fk_tbl_habilidad_categoria_habilidad
            FOREIGN KEY (hab_categoria_habilidad_id)
            REFERENCES tbl_categoria_habilidad(cthb_id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_tbl_habilidad_categoria
    ON tbl_habilidad(hab_categoria_habilidad_id);

-- =============================================================
-- Idiomas del candidato
-- =============================================================
CREATE TABLE IF NOT EXISTS tbl_idioma (
    idio_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    idio_nombre varchar(100) NOT NULL,
    CONSTRAINT uq_tbl_idioma_nombre UNIQUE (idio_nombre),
    CONSTRAINT chk_tbl_idioma_nombre CHECK (trim(idio_nombre) <> '')
);

INSERT INTO tbl_idioma (idio_nombre)
VALUES ('Español'), ('Inglés'), ('Portugués'), ('Francés'), ('Alemán'), ('Italiano'), ('Otro')
ON CONFLICT (idio_nombre) DO NOTHING;

CREATE TABLE IF NOT EXISTS tbl_candidato_idioma (
    cdio_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cdio_candidato_id integer NOT NULL REFERENCES tbl_candidato(cand_id),
    cdio_idioma_id integer NOT NULL REFERENCES tbl_idioma(idio_id),
    cdio_nivel varchar(30) NOT NULL,
    CONSTRAINT uq_tbl_candidato_idioma UNIQUE (cdio_candidato_id, cdio_idioma_id),
    CONSTRAINT chk_tbl_candidato_idioma_nivel CHECK (cdio_nivel IN ('Basico','Intermedio','Avanzado','Nativo'))
);

CREATE INDEX IF NOT EXISTS ix_tbl_candidato_idioma_candidato
    ON tbl_candidato_idioma(cdio_candidato_id);

-- =============================================================
-- Documentos generados
-- =============================================================
CREATE TABLE IF NOT EXISTS tbl_documento_reporte_candidato (
    drcp_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    drcp_solicitud_candidato_id integer NOT NULL REFERENCES tbl_solicitud_candidato(slcd_id),
    drcp_tipo_documento varchar(30) NOT NULL,
    drcp_nombre_archivo varchar(255) NOT NULL,
    drcp_ruta_archivo varchar(1000) NOT NULL,
    drcp_fecha_generacion timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    drcp_usuario_generador_id integer NOT NULL REFERENCES tbl_usuario(usr_id),
    drcp_hash_sha256 varchar(64) NOT NULL,
    drcp_snapshot_json jsonb,
    CONSTRAINT chk_tbl_documento_reporte_tipo CHECK (drcp_tipo_documento IN ('RESUMEN','CV_CORPORATIVO')),
    CONSTRAINT chk_tbl_documento_reporte_nombre CHECK (trim(drcp_nombre_archivo) <> ''),
    CONSTRAINT chk_tbl_documento_reporte_hash CHECK (length(drcp_hash_sha256) = 64)
);

CREATE INDEX IF NOT EXISTS ix_tbl_documento_reporte_postulacion
    ON tbl_documento_reporte_candidato(drcp_solicitud_candidato_id);
CREATE INDEX IF NOT EXISTS ix_tbl_documento_reporte_fecha
    ON tbl_documento_reporte_candidato(drcp_fecha_generacion DESC);

-- =============================================================
-- Plantillas editables de correo
-- =============================================================
CREATE TABLE IF NOT EXISTS tbl_plantilla_notificacion (
    plnt_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plnt_tipo varchar(30) NOT NULL,
    plnt_nombre varchar(100) NOT NULL,
    plnt_asunto varchar(300) NOT NULL,
    plnt_cuerpo text NOT NULL,
    plnt_activa boolean NOT NULL DEFAULT true,
    plnt_fecha_actualizacion timestamp without time zone,
    plnt_usuario_actualizacion_id integer REFERENCES tbl_usuario(usr_id),
    CONSTRAINT uq_tbl_plantilla_notificacion_tipo UNIQUE (plnt_tipo),
    CONSTRAINT chk_tbl_plantilla_notificacion_tipo CHECK (plnt_tipo IN ('RECHAZO','AGRADECIMIENTO','DIRECTIVOS')),
    CONSTRAINT chk_tbl_plantilla_notificacion_nombre CHECK (trim(plnt_nombre) <> ''),
    CONSTRAINT chk_tbl_plantilla_notificacion_asunto CHECK (trim(plnt_asunto) <> ''),
    CONSTRAINT chk_tbl_plantilla_notificacion_cuerpo CHECK (trim(plnt_cuerpo) <> '')
);

INSERT INTO tbl_plantilla_notificacion (plnt_tipo, plnt_nombre, plnt_asunto, plnt_cuerpo, plnt_activa)
VALUES
(
    'RECHAZO',
    'Cierre de proceso - rechazo',
    'Cierre proceso de selección - {cargo}',
    E'Estimado/a {nombre},\n\nAgradecemos sinceramente tu participación en el proceso de selección para el cargo {cargo}, asociado a la solicitud {codigo_solicitud}.\n\nEn esta oportunidad el proceso ha finalizado y no continuaremos con tu postulación. Valoramos el tiempo y disposición demostrados durante las distintas etapas.\n\nEsperamos poder considerarte en futuras oportunidades que se ajusten a tu perfil.\n\nSaludos cordiales,\nEquipo de Reclutamiento ELITSOFT',
    true
),
(
    'AGRADECIMIENTO',
    'Agradecimiento de participación',
    'Gracias por participar - {cargo}',
    E'Estimado/a {nombre},\n\nAgradecemos tu participación en el proceso {codigo_solicitud} para el cargo {cargo}.\n\nSaludos cordiales,\nEquipo de Reclutamiento ELITSOFT',
    true
),
(
    'DIRECTIVOS',
    'Presentación de candidatos aprobados',
    'Candidatos aprobados - {cargo} - {codigo_solicitud}',
    E'Estimados/as,\n\nAdjuntamos los CVs corporativos de los candidatos aprobados para el proceso {codigo_solicitud}, cargo {cargo}, para su revisión y decisión final.\n\nSaludos cordiales,\nEquipo de Reclutamiento ELITSOFT',
    true
)
ON CONFLICT (plnt_tipo) DO NOTHING;

-- =============================================================
-- Trazabilidad de comunicaciones
-- =============================================================
CREATE TABLE IF NOT EXISTS tbl_notificacion_reclutamiento (
    ntfr_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ntfr_solicitud_candidato_id integer NOT NULL REFERENCES tbl_solicitud_candidato(slcd_id),
    ntfr_tipo varchar(30) NOT NULL,
    ntfr_destinatario varchar(2000) NOT NULL,
    ntfr_cc varchar(2000),
    ntfr_asunto varchar(300) NOT NULL,
    ntfr_cuerpo text NOT NULL,
    ntfr_estado varchar(20) NOT NULL,
    ntfr_usuario_id integer NOT NULL REFERENCES tbl_usuario(usr_id),
    ntfr_fecha_creacion timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ntfr_fecha_envio timestamp without time zone,
    ntfr_error text,
    CONSTRAINT chk_tbl_notificacion_tipo CHECK (ntfr_tipo IN ('RECHAZO','AGRADECIMIENTO','DIRECTIVOS')),
    CONSTRAINT chk_tbl_notificacion_estado CHECK (ntfr_estado IN ('BORRADOR','ENVIADO','ERROR')),
    CONSTRAINT chk_tbl_notificacion_destinatario CHECK (trim(ntfr_destinatario) <> ''),
    CONSTRAINT chk_tbl_notificacion_asunto CHECK (trim(ntfr_asunto) <> ''),
    CONSTRAINT chk_tbl_notificacion_cuerpo CHECK (trim(ntfr_cuerpo) <> '')
);

CREATE INDEX IF NOT EXISTS ix_tbl_notificacion_postulacion
    ON tbl_notificacion_reclutamiento(ntfr_solicitud_candidato_id);
CREATE INDEX IF NOT EXISTS ix_tbl_notificacion_fecha
    ON tbl_notificacion_reclutamiento(ntfr_fecha_creacion DESC);
CREATE INDEX IF NOT EXISTS ix_tbl_notificacion_estado
    ON tbl_notificacion_reclutamiento(ntfr_estado);

COMMIT;
