--
-- PostgreSQL database dump
--

\restrict e4rxbFNdid9hG7Ib0ttk9wezOPic8YWeuAG2zCk02O0vdFgbjuP3usmRKYNI9ya

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: elitsoft_admin
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO elitsoft_admin;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: elitsoft_admin
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: tbl_area; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_area (
    area_id integer NOT NULL,
    area_nombre character varying(20),
    area_descripcion character varying(300),
    CONSTRAINT chk_tbl_area_descripcion_vacia CHECK (((area_descripcion IS NULL) OR (TRIM(BOTH FROM area_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_area_nombre_vacio CHECK ((TRIM(BOTH FROM area_nombre) <> ''::text))
);


ALTER TABLE public.tbl_area OWNER TO elitsoft_admin;

--
-- Name: tbl_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_candidato (
    cand_id integer,
    cand_email character varying(20),
    cand_password character varying(20),
    cand_nombres character varying(20),
    cand_apellido_paterno character varying(20),
    cand_apellido_materno character varying(20),
    cand_fecha_nacimiento date,
    cand_telefono character varying(20),
    cand_rut_sin_dv integer,
    cand_dv integer,
    cand_disponibilidad_id integer,
    cand_resumen_profesional character varying(300),
    cand_fecha_creacion timestamp without time zone,
    cand_url_1 character varying(300),
    cand_titulo character varying(300)
);


ALTER TABLE public.tbl_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_candidato_cuestionario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_candidato_cuestionario (
    cdcu_id integer,
    cdcu_candidato_id integer,
    cdcu_cuestionario_id integer,
    cdcu_fecha_asignacion timestamp without time zone,
    cdcu_fecha_resolucion timestamp without time zone,
    cdcu_porcentaje_obtenido numeric(5,2),
    cdcu_estado_cuestionario_candidato_id integer,
    cdcu_tiempo_utilizado integer,
    cdcu_permitir_reintento boolean,
    cdcu_aprobado boolean
);


ALTER TABLE public.tbl_candidato_cuestionario OWNER TO elitsoft_admin;

--
-- Name: tbl_candidato_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_candidato_habilidad (
    cdhb_id integer,
    cdhb_candidato_id integer,
    cdhb_habilidad_id integer,
    cdhb_nivel_habilidad_id integer,
    cdhb_anios_experiencia integer
);


ALTER TABLE public.tbl_candidato_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_cargo; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cargo (
    crgo_id integer NOT NULL,
    crgo_nombre character varying(30),
    crgo_descripcion character varying(300),
    CONSTRAINT chk_tbl_cargo_descripcion_vacia CHECK (((crgo_descripcion IS NULL) OR (TRIM(BOTH FROM crgo_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_cargo_nombre_vacio CHECK ((TRIM(BOTH FROM crgo_nombre) <> ''::text))
);


ALTER TABLE public.tbl_cargo OWNER TO elitsoft_admin;

--
-- Name: tbl_carrera; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_carrera (
    crra_id integer,
    crra_nombre character varying(40)
);


ALTER TABLE public.tbl_carrera OWNER TO elitsoft_admin;

--
-- Name: tbl_cita_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cita_entrevista (
    ctev_id integer,
    ctev_solicitud_candidato_id integer,
    ctev_tipo_entrevista_id integer,
    ctev_estado_entrevista_id integer,
    ctev_fecha_hora_inicio timestamp without time zone,
    ctev_fecha_hora_fin timestamp without time zone,
    ctev_fecha_creacion timestamp without time zone,
    ctev_enlace_reunion character varying(300),
    ctev_comentarios_convocatoria character varying(300),
    ctev_titulo_evento character varying(300)
);


ALTER TABLE public.tbl_cita_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_cita_tipo_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cita_tipo_entrevista (
    cten_tipo_entrevista_id integer,
    cten_cita_entrevista_id integer
);


ALTER TABLE public.tbl_cita_tipo_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_ciudad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_ciudad (
    ciu_id integer NOT NULL,
    ciu_region_id integer,
    ciu_nombre character varying(100),
    CONSTRAINT chk_tbl_ciudad_nombre_vacio CHECK ((TRIM(BOTH FROM ciu_nombre) <> ''::text))
);


ALTER TABLE public.tbl_ciudad OWNER TO elitsoft_admin;

--
-- Name: tbl_cliente; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cliente (
    cli_id integer NOT NULL,
    cli_nombre character varying(30),
    cli_cargo_empresa_id integer,
    cli_area_empresa_id integer,
    cli_email character varying(100),
    cli_email2 character varying(100),
    cli_telefono1 character varying(12),
    cli_telefono2 character varying(12),
    cli_empresa_id integer,
    CONSTRAINT chk_tbl_cliente_email2_formato CHECK (((cli_email2 IS NULL) OR ((cli_email2)::text ~~ '%@%.%'::text))),
    CONSTRAINT chk_tbl_cliente_email_diferentes CHECK (((cli_email2 IS NULL) OR ((cli_email)::text <> (cli_email2)::text))),
    CONSTRAINT chk_tbl_cliente_email_formato CHECK (((cli_email IS NULL) OR ((cli_email)::text ~~ '%@%.%'::text))),
    CONSTRAINT chk_tbl_cliente_nombre_vacio CHECK ((TRIM(BOTH FROM cli_nombre) <> ''::text)),
    CONSTRAINT chk_tbl_cliente_telefono_diferentes CHECK (((cli_telefono2 IS NULL) OR ((cli_telefono1)::text <> (cli_telefono2)::text)))
);


ALTER TABLE public.tbl_cliente OWNER TO elitsoft_admin;

--
-- Name: tbl_comuna; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_comuna (
    com_id integer NOT NULL,
    com_ciudad_id integer,
    com_nombre character varying(100),
    CONSTRAINT chk_tbl_comuna_nombre_vacio CHECK ((TRIM(BOTH FROM com_nombre) <> ''::text))
);


ALTER TABLE public.tbl_comuna OWNER TO elitsoft_admin;

--
-- Name: tbl_cuestionario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cuestionario (
    cues_id integer,
    cues_nombre character varying(300),
    cues_descripcion character varying(300),
    cues_porcentaje_aprobacion numeric(5,2),
    cues_solicitud_id integer
);


ALTER TABLE public.tbl_cuestionario OWNER TO elitsoft_admin;

--
-- Name: tbl_curso; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_curso (
    curs_id integer,
    curs_candidato_id integer,
    curs_nombre_curso character varying(40),
    curs_institucion_id integer,
    curs_es_certificado boolean,
    curs_anio_curso integer
);


ALTER TABLE public.tbl_curso OWNER TO elitsoft_admin;

--
-- Name: tbl_direccion_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_direccion_candidato (
    drcd_id integer,
    drcd_candidato_id integer,
    drcd_comuna_id integer,
    drcd_calle character varying(40),
    drcd_numero integer,
    drcd_dpto_oficina character varying(10)
);


ALTER TABLE public.tbl_direccion_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_disponibilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_disponibilidad (
    disp_id integer,
    disp_nombre character varying(40)
);


ALTER TABLE public.tbl_disponibilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_empresa; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_empresa (
    emp_id integer NOT NULL,
    emp_nombre character varying(30),
    emp_identificacion character varying(15),
    CONSTRAINT chk_tbl_empresa_identificacion_vacia CHECK ((TRIM(BOTH FROM emp_identificacion) <> ''::text)),
    CONSTRAINT chk_tbl_empresa_nombre_vacio CHECK ((TRIM(BOTH FROM emp_nombre) <> ''::text))
);


ALTER TABLE public.tbl_empresa OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_cuestionario_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_cuestionario_candidato (
    escc_id integer,
    escc_nombre character varying(40)
);


ALTER TABLE public.tbl_estado_cuestionario_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_entrevista (
    esev_id integer,
    esev_nombre character varying(40),
    esev_descripcion character varying(300)
);


ALTER TABLE public.tbl_estado_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_solicitud; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_solicitud (
    essl_id integer NOT NULL,
    essl_nombre character varying(20),
    essl_descripcion character varying(300),
    CONSTRAINT chk_tbl_estado_solicitud_descripcion_vacia CHECK (((essl_descripcion IS NULL) OR (TRIM(BOTH FROM essl_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_estado_solicitud_nombre_vacio CHECK ((TRIM(BOTH FROM essl_nombre) <> ''::text))
);


ALTER TABLE public.tbl_estado_solicitud OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_solicitud_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_solicitud_candidato (
    essc_id integer,
    essc_nombre character varying(40),
    essc_descripcion character varying(300)
);


ALTER TABLE public.tbl_estado_solicitud_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_usuario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_usuario (
    esusr_id integer NOT NULL,
    esusr_nombre character varying(20),
    esusr_descripcion character varying(300),
    CONSTRAINT chk_tbl_estado_usuario_descripcion_vacia CHECK (((esusr_descripcion IS NULL) OR (TRIM(BOTH FROM esusr_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_estado_usuario_nombre_vacio CHECK ((TRIM(BOTH FROM esusr_nombre) <> ''::text))
);


ALTER TABLE public.tbl_estado_usuario OWNER TO elitsoft_admin;

--
-- Name: tbl_estudio_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estudio_candidato (
    etcd_id integer,
    etcd_candidato_id integer,
    etcd_nivel_educacional_id integer,
    etcd_institucion_id integer,
    etcd_carrera_id integer,
    etcd_fecha_inicio date,
    etcd_fecha_fin date
);


ALTER TABLE public.tbl_estudio_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_evaluacion_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_evaluacion_entrevista (
    even_id integer,
    even_nombre_resultado_id integer,
    even_observacion character varying(300),
    even_cita_entrevista_id integer
);


ALTER TABLE public.tbl_evaluacion_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_experiencia_laboral; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_experiencia_laboral (
    expl_id integer,
    expl_candidato_id integer,
    expl_empresa_id integer,
    expl_cargo_id integer,
    expl_descripcion_funciones character varying(300),
    expl_fecha_inicio date,
    expl_fecha_fin date
);


ALTER TABLE public.tbl_experiencia_laboral OWNER TO elitsoft_admin;

--
-- Name: tbl_experiencia_laboral_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_experiencia_laboral_habilidad (
    exph_experiencia_laboral_id integer,
    exph_habilidad_id integer
);


ALTER TABLE public.tbl_experiencia_laboral_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_habilidad (
    hab_id integer,
    hab_nombre character varying(20),
    hab_descripcion character varying(300)
);


ALTER TABLE public.tbl_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_historial_solicitud; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_historial_solicitud (
    hsol_id integer NOT NULL,
    hsol_solicitud_id integer,
    hsol_estado_anterior_id integer,
    hsol_estado_actual_id integer,
    hsol_fecha_cambio timestamp without time zone,
    hsol_usuario_id integer,
    hsol_comentario character varying(300),
    CONSTRAINT chk_tbl_historial_solicitud_comentario_vacio CHECK (((hsol_comentario IS NULL) OR (TRIM(BOTH FROM hsol_comentario) <> ''::text))),
    CONSTRAINT chk_tbl_historial_solicitud_estados_diferentes CHECK (((hsol_estado_anterior_id IS NULL) OR (hsol_estado_actual_id IS NULL) OR (hsol_estado_anterior_id <> hsol_estado_actual_id)))
);


ALTER TABLE public.tbl_historial_solicitud OWNER TO elitsoft_admin;

--
-- Name: tbl_institucion; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_institucion (
    inst_id integer,
    inst_nombre character varying(40),
    inst_tipo_institucion_id integer
);


ALTER TABLE public.tbl_institucion OWNER TO elitsoft_admin;

--
-- Name: tbl_modalidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_modalidad (
    mdld_id integer NOT NULL,
    mdld_nombre character varying(20),
    mdld_descripcion character varying(300),
    CONSTRAINT chk_tbl_modalidad_descripcion_vacia CHECK (((mdld_descripcion IS NULL) OR (TRIM(BOTH FROM mdld_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_modalidad_nombre_vacio CHECK ((TRIM(BOTH FROM mdld_nombre) <> ''::text))
);


ALTER TABLE public.tbl_modalidad OWNER TO elitsoft_admin;

--
-- Name: tbl_motivo_rechazo; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_motivo_rechazo (
    mtrc_id integer,
    mtrc_nombre character varying(40),
    mtrc_descripcion character varying(300)
);


ALTER TABLE public.tbl_motivo_rechazo OWNER TO elitsoft_admin;

--
-- Name: tbl_nivel_educacional; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nivel_educacional (
    nved_id integer,
    nved_nombre character varying(40)
);


ALTER TABLE public.tbl_nivel_educacional OWNER TO elitsoft_admin;

--
-- Name: tbl_nivel_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nivel_habilidad (
    nvhb_id integer,
    nvhb_nombre character varying(20),
    nvhb_descripcion character varying(300),
    nvhb_puntaje_base integer,
    nvhb_duracion integer
);


ALTER TABLE public.tbl_nivel_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_nombre_resultado; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nombre_resultado (
    nore_id integer,
    nore_nombre character varying(40)
);


ALTER TABLE public.tbl_nombre_resultado OWNER TO elitsoft_admin;

--
-- Name: tbl_opcion_respuesta; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_opcion_respuesta (
    opcr_id integer,
    opcr_pregunta_id integer,
    opcr_texto_opcion character varying(300),
    opcr_es_correcta boolean
);


ALTER TABLE public.tbl_opcion_respuesta OWNER TO elitsoft_admin;

--
-- Name: tbl_pais; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_pais (
    pais_id integer NOT NULL,
    pais_nombre character varying(100),
    CONSTRAINT chk_tbl_pais_nombre_vacio CHECK ((TRIM(BOTH FROM pais_nombre) <> ''::text))
);


ALTER TABLE public.tbl_pais OWNER TO elitsoft_admin;

--
-- Name: tbl_permiso; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_permiso (
    per_id integer NOT NULL,
    per_nombre character varying(20),
    per_descripcion character varying(300),
    CONSTRAINT chk_tbl_permiso_descripcion_vacia CHECK (((per_descripcion IS NULL) OR (TRIM(BOTH FROM per_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_permiso_nombre_vacio CHECK ((TRIM(BOTH FROM per_nombre) <> ''::text))
);


ALTER TABLE public.tbl_permiso OWNER TO elitsoft_admin;

--
-- Name: tbl_pregunta; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_pregunta (
    preg_id integer,
    preg_texto_pregunta character varying(300),
    preg_habilidad_id integer,
    preg_nivel_habilidad_id integer,
    preg_fecha_creacion timestamp without time zone
);


ALTER TABLE public.tbl_pregunta OWNER TO elitsoft_admin;

--
-- Name: tbl_pregunta_cuestionario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_pregunta_cuestionario (
    prcu_pregunta_id integer,
    prcu_cuestionario_id integer
);


ALTER TABLE public.tbl_pregunta_cuestionario OWNER TO elitsoft_admin;

--
-- Name: tbl_prioridad_solicitud; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_prioridad_solicitud (
    prsol_id integer NOT NULL,
    prsol_nombre character varying(15),
    prsol_descripcion character varying(300),
    CONSTRAINT chk_tbl_prioridad_descripcion_vacia CHECK (((prsol_descripcion IS NULL) OR (TRIM(BOTH FROM prsol_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_prioridad_nombre_vacio CHECK ((TRIM(BOTH FROM prsol_nombre) <> ''::text))
);


ALTER TABLE public.tbl_prioridad_solicitud OWNER TO elitsoft_admin;

--
-- Name: tbl_region; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_region (
    reg_id integer NOT NULL,
    reg_pais_id integer,
    reg_nombre character varying(100),
    CONSTRAINT chk_tbl_region_nombre_vacio CHECK ((TRIM(BOTH FROM reg_nombre) <> ''::text))
);


ALTER TABLE public.tbl_region OWNER TO elitsoft_admin;

--
-- Name: tbl_respuesta_pregunta; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_respuesta_pregunta (
    rspr_id integer,
    rspr_candidato_cuestionario_id integer,
    rspr_es_correcta boolean,
    rspr_puntaje_obtenido integer,
    rspr_opcion_respuesta_id integer,
    rspr_pregunta_cuestionario_id integer
);


ALTER TABLE public.tbl_respuesta_pregunta OWNER TO elitsoft_admin;

--
-- Name: tbl_rol; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_rol (
    rol_id integer NOT NULL,
    rol_nombre character varying(20),
    rol_descripcion character varying(300),
    CONSTRAINT chk_tbl_rol_descripcion_vacia CHECK (((rol_descripcion IS NULL) OR (TRIM(BOTH FROM rol_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_rol_nombre_vacio CHECK ((TRIM(BOTH FROM rol_nombre) <> ''::text))
);


ALTER TABLE public.tbl_rol OWNER TO elitsoft_admin;

--
-- Name: tbl_rol_permiso; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_rol_permiso (
    rlpm_rol_id integer NOT NULL,
    rlmp_permiso_id integer NOT NULL
);


ALTER TABLE public.tbl_rol_permiso OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_solicitud (
    sol_id integer NOT NULL,
    sol_codigo character varying(8),
    sol_titulo character varying(300),
    sol_cargo_id integer,
    sol_descripcion character varying(300),
    sol_prioridad_id integer,
    sol_cantidad_vacantes integer,
    sol_cliente_id integer,
    sol_usuario_creador_id integer,
    sol_usuario_asignado_id integer,
    sol_modalidad_id integer,
    sol_salario_min integer,
    sol_salario_max integer,
    sol_fecha_creacion timestamp without time zone,
    sol_fecha_inicio_busqueda timestamp without time zone,
    sol_fecha_cierre_busqueda timestamp without time zone,
    sol_fecha_inicio_cliente timestamp without time zone,
    sol_estado_solicitud_id integer,
    sol_hora_inicio_jornada time without time zone,
    sol_hora_fin_jornada time without time zone,
    sol_tipo_contrato_id integer,
    sol_observacion character varying(300),
    CONSTRAINT chk_tbl_solicitud_codigo CHECK (((sol_codigo)::text ~ '^SOL-[0-9]{3}$'::text)),
    CONSTRAINT chk_tbl_solicitud_horario CHECK (((sol_hora_inicio_jornada IS NULL) OR (sol_hora_fin_jornada IS NULL) OR (sol_hora_inicio_jornada < sol_hora_fin_jornada))),
    CONSTRAINT chk_tbl_solicitud_salarios CHECK (((sol_salario_min IS NULL) OR (sol_salario_max IS NULL) OR (sol_salario_min <= sol_salario_max))),
    CONSTRAINT chk_tbl_solicitud_vacantes CHECK ((sol_cantidad_vacantes > 0))
);


ALTER TABLE public.tbl_solicitud OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_solicitud_candidato (
    slcd_id integer,
    slcd_candidato_id integer,
    slcd_solicitud_id integer,
    slcd_pretension_renta integer,
    slcd_puntaje_compatibilidad numeric(5,2),
    slcd_estado_solicitud_id integer,
    slcd_fecha_postulacion timestamp without time zone,
    slcd_observaciones character varying(300),
    slcd_motivo_rechazo_id integer
);


ALTER TABLE public.tbl_solicitud_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_solicitud_habilidad (
    solhb_id integer,
    solhb_solicitud_id integer,
    solhb_habilidad_id integer,
    solhb_nivel_habilidad_id integer,
    solhb_anios_experiencia_req integer,
    solhb_es_excluyente boolean
);


ALTER TABLE public.tbl_solicitud_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_tipo_contrato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_tipo_contrato (
    tpct_id integer NOT NULL,
    tpct_nombre character varying(20),
    tpct_descripcion character varying(300),
    CONSTRAINT chk_tbl_tipo_contrato_descripcion_vacia CHECK (((tpct_descripcion IS NULL) OR (TRIM(BOTH FROM tpct_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_tipo_contrato_nombre_vacio CHECK ((TRIM(BOTH FROM tpct_nombre) <> ''::text))
);


ALTER TABLE public.tbl_tipo_contrato OWNER TO elitsoft_admin;

--
-- Name: tbl_tipo_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_tipo_entrevista (
    tpet_id integer,
    tpet_nombre character varying(40),
    tpet_descripcion character varying(300)
);


ALTER TABLE public.tbl_tipo_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_tipo_institucion; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_tipo_institucion (
    tint_id integer,
    tint_tipo_intitucion character varying(40)
);


ALTER TABLE public.tbl_tipo_institucion OWNER TO elitsoft_admin;

--
-- Name: tbl_usuario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_usuario (
    usr_id integer NOT NULL,
    usr_rol_id integer,
    usr_estado_usuario_id integer,
    usr_area_id integer,
    usr_nombres character varying(15),
    usr_apellido_paterno character varying(15),
    usr_apellido_materno character varying(15),
    usr_rut_sin_dv character varying(15),
    usr_dv character varying(1),
    usr_telefono character varying(15),
    usr_email character varying(30),
    usr_contrasena character varying(255),
    CONSTRAINT chk_tbl_usuario_apellido_paterno_vacio CHECK ((TRIM(BOTH FROM usr_apellido_paterno) <> ''::text)),
    CONSTRAINT chk_tbl_usuario_contrasena_vacia CHECK ((TRIM(BOTH FROM usr_contrasena) <> ''::text)),
    CONSTRAINT chk_tbl_usuario_email_formato CHECK (((usr_email)::text ~~ '%@%.%'::text)),
    CONSTRAINT chk_tbl_usuario_nombres_vacio CHECK ((TRIM(BOTH FROM usr_nombres) <> ''::text)),
    CONSTRAINT chk_tbl_usuario_rut_dv CHECK ((((usr_rut_sin_dv IS NULL) AND (usr_dv IS NULL)) OR ((usr_rut_sin_dv IS NOT NULL) AND (usr_dv IS NOT NULL)))),
    CONSTRAINT chk_tbl_usuario_telefono_vacio CHECK (((usr_telefono IS NULL) OR (TRIM(BOTH FROM usr_telefono) <> ''::text)))
);


ALTER TABLE public.tbl_usuario OWNER TO elitsoft_admin;

--
-- Name: tbl_usuario_cita_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_usuario_cita_entrevista (
    usrce_cita_entrevista_id integer,
    usrce_usuario_id integer
);


ALTER TABLE public.tbl_usuario_cita_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_usuario_usr_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_usuario ALTER COLUMN usr_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_usuario_usr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: tbl_area; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_area (area_id, area_nombre, area_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_candidato (cand_id, cand_email, cand_password, cand_nombres, cand_apellido_paterno, cand_apellido_materno, cand_fecha_nacimiento, cand_telefono, cand_rut_sin_dv, cand_dv, cand_disponibilidad_id, cand_resumen_profesional, cand_fecha_creacion, cand_url_1, cand_titulo) FROM stdin;
\.


--
-- Data for Name: tbl_candidato_cuestionario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_candidato_cuestionario (cdcu_id, cdcu_candidato_id, cdcu_cuestionario_id, cdcu_fecha_asignacion, cdcu_fecha_resolucion, cdcu_porcentaje_obtenido, cdcu_estado_cuestionario_candidato_id, cdcu_tiempo_utilizado, cdcu_permitir_reintento, cdcu_aprobado) FROM stdin;
\.


--
-- Data for Name: tbl_candidato_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_candidato_habilidad (cdhb_id, cdhb_candidato_id, cdhb_habilidad_id, cdhb_nivel_habilidad_id, cdhb_anios_experiencia) FROM stdin;
\.


--
-- Data for Name: tbl_cargo; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cargo (crgo_id, crgo_nombre, crgo_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_carrera; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_carrera (crra_id, crra_nombre) FROM stdin;
\.


--
-- Data for Name: tbl_cita_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cita_entrevista (ctev_id, ctev_solicitud_candidato_id, ctev_tipo_entrevista_id, ctev_estado_entrevista_id, ctev_fecha_hora_inicio, ctev_fecha_hora_fin, ctev_fecha_creacion, ctev_enlace_reunion, ctev_comentarios_convocatoria, ctev_titulo_evento) FROM stdin;
\.


--
-- Data for Name: tbl_cita_tipo_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cita_tipo_entrevista (cten_tipo_entrevista_id, cten_cita_entrevista_id) FROM stdin;
\.


--
-- Data for Name: tbl_ciudad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_ciudad (ciu_id, ciu_region_id, ciu_nombre) FROM stdin;
\.


--
-- Data for Name: tbl_cliente; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cliente (cli_id, cli_nombre, cli_cargo_empresa_id, cli_area_empresa_id, cli_email, cli_email2, cli_telefono1, cli_telefono2, cli_empresa_id) FROM stdin;
\.


--
-- Data for Name: tbl_comuna; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_comuna (com_id, com_ciudad_id, com_nombre) FROM stdin;
\.


--
-- Data for Name: tbl_cuestionario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cuestionario (cues_id, cues_nombre, cues_descripcion, cues_porcentaje_aprobacion, cues_solicitud_id) FROM stdin;
\.


--
-- Data for Name: tbl_curso; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_curso (curs_id, curs_candidato_id, curs_nombre_curso, curs_institucion_id, curs_es_certificado, curs_anio_curso) FROM stdin;
\.


--
-- Data for Name: tbl_direccion_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_direccion_candidato (drcd_id, drcd_candidato_id, drcd_comuna_id, drcd_calle, drcd_numero, drcd_dpto_oficina) FROM stdin;
\.


--
-- Data for Name: tbl_disponibilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_disponibilidad (disp_id, disp_nombre) FROM stdin;
\.


--
-- Data for Name: tbl_empresa; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_empresa (emp_id, emp_nombre, emp_identificacion) FROM stdin;
\.


--
-- Data for Name: tbl_estado_cuestionario_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_cuestionario_candidato (escc_id, escc_nombre) FROM stdin;
\.


--
-- Data for Name: tbl_estado_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_entrevista (esev_id, esev_nombre, esev_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_estado_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_solicitud (essl_id, essl_nombre, essl_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_estado_solicitud_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_solicitud_candidato (essc_id, essc_nombre, essc_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_estado_usuario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_usuario (esusr_id, esusr_nombre, esusr_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_estudio_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estudio_candidato (etcd_id, etcd_candidato_id, etcd_nivel_educacional_id, etcd_institucion_id, etcd_carrera_id, etcd_fecha_inicio, etcd_fecha_fin) FROM stdin;
\.


--
-- Data for Name: tbl_evaluacion_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_evaluacion_entrevista (even_id, even_nombre_resultado_id, even_observacion, even_cita_entrevista_id) FROM stdin;
\.


--
-- Data for Name: tbl_experiencia_laboral; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_experiencia_laboral (expl_id, expl_candidato_id, expl_empresa_id, expl_cargo_id, expl_descripcion_funciones, expl_fecha_inicio, expl_fecha_fin) FROM stdin;
\.


--
-- Data for Name: tbl_experiencia_laboral_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_experiencia_laboral_habilidad (exph_experiencia_laboral_id, exph_habilidad_id) FROM stdin;
\.


--
-- Data for Name: tbl_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_habilidad (hab_id, hab_nombre, hab_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_historial_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_historial_solicitud (hsol_id, hsol_solicitud_id, hsol_estado_anterior_id, hsol_estado_actual_id, hsol_fecha_cambio, hsol_usuario_id, hsol_comentario) FROM stdin;
\.


--
-- Data for Name: tbl_institucion; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_institucion (inst_id, inst_nombre, inst_tipo_institucion_id) FROM stdin;
\.


--
-- Data for Name: tbl_modalidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_modalidad (mdld_id, mdld_nombre, mdld_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_motivo_rechazo; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_motivo_rechazo (mtrc_id, mtrc_nombre, mtrc_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_nivel_educacional; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_nivel_educacional (nved_id, nved_nombre) FROM stdin;
\.


--
-- Data for Name: tbl_nivel_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_nivel_habilidad (nvhb_id, nvhb_nombre, nvhb_descripcion, nvhb_puntaje_base, nvhb_duracion) FROM stdin;
\.


--
-- Data for Name: tbl_nombre_resultado; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_nombre_resultado (nore_id, nore_nombre) FROM stdin;
\.


--
-- Data for Name: tbl_opcion_respuesta; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_opcion_respuesta (opcr_id, opcr_pregunta_id, opcr_texto_opcion, opcr_es_correcta) FROM stdin;
\.


--
-- Data for Name: tbl_pais; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_pais (pais_id, pais_nombre) FROM stdin;
\.


--
-- Data for Name: tbl_permiso; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_permiso (per_id, per_nombre, per_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_pregunta; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_pregunta (preg_id, preg_texto_pregunta, preg_habilidad_id, preg_nivel_habilidad_id, preg_fecha_creacion) FROM stdin;
\.


--
-- Data for Name: tbl_pregunta_cuestionario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_pregunta_cuestionario (prcu_pregunta_id, prcu_cuestionario_id) FROM stdin;
\.


--
-- Data for Name: tbl_prioridad_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_prioridad_solicitud (prsol_id, prsol_nombre, prsol_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_region; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_region (reg_id, reg_pais_id, reg_nombre) FROM stdin;
\.


--
-- Data for Name: tbl_respuesta_pregunta; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_respuesta_pregunta (rspr_id, rspr_candidato_cuestionario_id, rspr_es_correcta, rspr_puntaje_obtenido, rspr_opcion_respuesta_id, rspr_pregunta_cuestionario_id) FROM stdin;
\.


--
-- Data for Name: tbl_rol; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_rol (rol_id, rol_nombre, rol_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_rol_permiso; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_rol_permiso (rlpm_rol_id, rlmp_permiso_id) FROM stdin;
\.


--
-- Data for Name: tbl_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_solicitud (sol_id, sol_codigo, sol_titulo, sol_cargo_id, sol_descripcion, sol_prioridad_id, sol_cantidad_vacantes, sol_cliente_id, sol_usuario_creador_id, sol_usuario_asignado_id, sol_modalidad_id, sol_salario_min, sol_salario_max, sol_fecha_creacion, sol_fecha_inicio_busqueda, sol_fecha_cierre_busqueda, sol_fecha_inicio_cliente, sol_estado_solicitud_id, sol_hora_inicio_jornada, sol_hora_fin_jornada, sol_tipo_contrato_id, sol_observacion) FROM stdin;
\.


--
-- Data for Name: tbl_solicitud_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_solicitud_candidato (slcd_id, slcd_candidato_id, slcd_solicitud_id, slcd_pretension_renta, slcd_puntaje_compatibilidad, slcd_estado_solicitud_id, slcd_fecha_postulacion, slcd_observaciones, slcd_motivo_rechazo_id) FROM stdin;
\.


--
-- Data for Name: tbl_solicitud_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_solicitud_habilidad (solhb_id, solhb_solicitud_id, solhb_habilidad_id, solhb_nivel_habilidad_id, solhb_anios_experiencia_req, solhb_es_excluyente) FROM stdin;
\.


--
-- Data for Name: tbl_tipo_contrato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_tipo_contrato (tpct_id, tpct_nombre, tpct_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_tipo_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_tipo_entrevista (tpet_id, tpet_nombre, tpet_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_tipo_institucion; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_tipo_institucion (tint_id, tint_tipo_intitucion) FROM stdin;
\.


--
-- Data for Name: tbl_usuario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_usuario (usr_id, usr_rol_id, usr_estado_usuario_id, usr_area_id, usr_nombres, usr_apellido_paterno, usr_apellido_materno, usr_rut_sin_dv, usr_dv, usr_telefono, usr_email, usr_contrasena) FROM stdin;
\.


--
-- Data for Name: tbl_usuario_cita_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_usuario_cita_entrevista (usrce_cita_entrevista_id, usrce_usuario_id) FROM stdin;
\.


--
-- Name: tbl_usuario_usr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_usuario_usr_id_seq', 1, false);


--
-- Name: tbl_area pk_tbl_area; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_area
    ADD CONSTRAINT pk_tbl_area PRIMARY KEY (area_id);


--
-- Name: tbl_cargo pk_tbl_cargo; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cargo
    ADD CONSTRAINT pk_tbl_cargo PRIMARY KEY (crgo_id);


--
-- Name: tbl_ciudad pk_tbl_ciudad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_ciudad
    ADD CONSTRAINT pk_tbl_ciudad PRIMARY KEY (ciu_id);


--
-- Name: tbl_cliente pk_tbl_cliente; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT pk_tbl_cliente PRIMARY KEY (cli_id);


--
-- Name: tbl_comuna pk_tbl_comuna; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_comuna
    ADD CONSTRAINT pk_tbl_comuna PRIMARY KEY (com_id);


--
-- Name: tbl_empresa pk_tbl_empresa; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_empresa
    ADD CONSTRAINT pk_tbl_empresa PRIMARY KEY (emp_id);


--
-- Name: tbl_estado_solicitud pk_tbl_estado_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud
    ADD CONSTRAINT pk_tbl_estado_solicitud PRIMARY KEY (essl_id);


--
-- Name: tbl_estado_usuario pk_tbl_estado_usuario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_usuario
    ADD CONSTRAINT pk_tbl_estado_usuario PRIMARY KEY (esusr_id);


--
-- Name: tbl_historial_solicitud pk_tbl_historial_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT pk_tbl_historial_solicitud PRIMARY KEY (hsol_id);


--
-- Name: tbl_modalidad pk_tbl_modalidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_modalidad
    ADD CONSTRAINT pk_tbl_modalidad PRIMARY KEY (mdld_id);


--
-- Name: tbl_pais pk_tbl_pais; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pais
    ADD CONSTRAINT pk_tbl_pais PRIMARY KEY (pais_id);


--
-- Name: tbl_permiso pk_tbl_permiso; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_permiso
    ADD CONSTRAINT pk_tbl_permiso PRIMARY KEY (per_id);


--
-- Name: tbl_prioridad_solicitud pk_tbl_prioridad_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_prioridad_solicitud
    ADD CONSTRAINT pk_tbl_prioridad_solicitud PRIMARY KEY (prsol_id);


--
-- Name: tbl_region pk_tbl_region; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_region
    ADD CONSTRAINT pk_tbl_region PRIMARY KEY (reg_id);


--
-- Name: tbl_rol pk_tbl_rol; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol
    ADD CONSTRAINT pk_tbl_rol PRIMARY KEY (rol_id);


--
-- Name: tbl_rol_permiso pk_tbl_rol_permiso; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol_permiso
    ADD CONSTRAINT pk_tbl_rol_permiso PRIMARY KEY (rlpm_rol_id, rlmp_permiso_id);


--
-- Name: tbl_solicitud pk_tbl_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT pk_tbl_solicitud PRIMARY KEY (sol_id);


--
-- Name: tbl_tipo_contrato pk_tbl_tipo_contrato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_contrato
    ADD CONSTRAINT pk_tbl_tipo_contrato PRIMARY KEY (tpct_id);


--
-- Name: tbl_usuario pk_tbl_usuario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT pk_tbl_usuario PRIMARY KEY (usr_id);


--
-- Name: tbl_area uq_tbl_area_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_area
    ADD CONSTRAINT uq_tbl_area_nombre UNIQUE (area_nombre);


--
-- Name: tbl_cargo uq_tbl_cargo_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cargo
    ADD CONSTRAINT uq_tbl_cargo_nombre UNIQUE (crgo_nombre);


--
-- Name: tbl_ciudad uq_tbl_ciudad_region_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_ciudad
    ADD CONSTRAINT uq_tbl_ciudad_region_nombre UNIQUE (ciu_region_id, ciu_nombre);


--
-- Name: tbl_cliente uq_tbl_cliente_email; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT uq_tbl_cliente_email UNIQUE (cli_email);


--
-- Name: tbl_cliente uq_tbl_cliente_email2; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT uq_tbl_cliente_email2 UNIQUE (cli_email2);


--
-- Name: tbl_comuna uq_tbl_comuna_ciudad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_comuna
    ADD CONSTRAINT uq_tbl_comuna_ciudad_nombre UNIQUE (com_ciudad_id, com_nombre);


--
-- Name: tbl_empresa uq_tbl_empresa_identificacion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_empresa
    ADD CONSTRAINT uq_tbl_empresa_identificacion UNIQUE (emp_identificacion);


--
-- Name: tbl_empresa uq_tbl_empresa_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_empresa
    ADD CONSTRAINT uq_tbl_empresa_nombre UNIQUE (emp_nombre);


--
-- Name: tbl_estado_solicitud uq_tbl_estado_solicitud_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud
    ADD CONSTRAINT uq_tbl_estado_solicitud_nombre UNIQUE (essl_nombre);


--
-- Name: tbl_estado_usuario uq_tbl_estado_usuario_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_usuario
    ADD CONSTRAINT uq_tbl_estado_usuario_nombre UNIQUE (esusr_nombre);


--
-- Name: tbl_modalidad uq_tbl_modalidad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_modalidad
    ADD CONSTRAINT uq_tbl_modalidad_nombre UNIQUE (mdld_nombre);


--
-- Name: tbl_pais uq_tbl_pais_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pais
    ADD CONSTRAINT uq_tbl_pais_nombre UNIQUE (pais_nombre);


--
-- Name: tbl_permiso uq_tbl_permiso_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_permiso
    ADD CONSTRAINT uq_tbl_permiso_nombre UNIQUE (per_nombre);


--
-- Name: tbl_prioridad_solicitud uq_tbl_prioridad_solicitud_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_prioridad_solicitud
    ADD CONSTRAINT uq_tbl_prioridad_solicitud_nombre UNIQUE (prsol_nombre);


--
-- Name: tbl_region uq_tbl_region_pais_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_region
    ADD CONSTRAINT uq_tbl_region_pais_nombre UNIQUE (reg_pais_id, reg_nombre);


--
-- Name: tbl_rol uq_tbl_rol_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol
    ADD CONSTRAINT uq_tbl_rol_nombre UNIQUE (rol_nombre);


--
-- Name: tbl_solicitud uq_tbl_solicitud_codigo; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT uq_tbl_solicitud_codigo UNIQUE (sol_codigo);


--
-- Name: tbl_tipo_contrato uq_tbl_tipo_contrato_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_contrato
    ADD CONSTRAINT uq_tbl_tipo_contrato_nombre UNIQUE (tpct_nombre);


--
-- Name: tbl_usuario uq_tbl_usuario_email; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT uq_tbl_usuario_email UNIQUE (usr_email);


--
-- Name: tbl_usuario uq_tbl_usuario_rut; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT uq_tbl_usuario_rut UNIQUE (usr_rut_sin_dv, usr_dv);


--
-- Name: idx_tbl_area_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_area_nombre ON public.tbl_area USING btree (area_nombre);


--
-- Name: idx_tbl_cargo_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cargo_nombre ON public.tbl_cargo USING btree (crgo_nombre);


--
-- Name: idx_tbl_ciudad_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_ciudad_nombre ON public.tbl_ciudad USING btree (ciu_nombre);


--
-- Name: idx_tbl_ciudad_region; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_ciudad_region ON public.tbl_ciudad USING btree (ciu_region_id);


--
-- Name: idx_tbl_cliente_area_empresa; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cliente_area_empresa ON public.tbl_cliente USING btree (cli_area_empresa_id);


--
-- Name: idx_tbl_cliente_cargo_empresa; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cliente_cargo_empresa ON public.tbl_cliente USING btree (cli_cargo_empresa_id);


--
-- Name: idx_tbl_cliente_email; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cliente_email ON public.tbl_cliente USING btree (cli_email);


--
-- Name: idx_tbl_cliente_empresa; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cliente_empresa ON public.tbl_cliente USING btree (cli_empresa_id);


--
-- Name: idx_tbl_cliente_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cliente_nombre ON public.tbl_cliente USING btree (cli_nombre);


--
-- Name: idx_tbl_comuna_ciudad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_comuna_ciudad ON public.tbl_comuna USING btree (com_ciudad_id);


--
-- Name: idx_tbl_comuna_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_comuna_nombre ON public.tbl_comuna USING btree (com_nombre);


--
-- Name: idx_tbl_empresa_identificacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_empresa_identificacion ON public.tbl_empresa USING btree (emp_identificacion);


--
-- Name: idx_tbl_empresa_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_empresa_nombre ON public.tbl_empresa USING btree (emp_nombre);


--
-- Name: idx_tbl_estado_solicitud_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_solicitud_nombre ON public.tbl_estado_solicitud USING btree (essl_nombre);


--
-- Name: idx_tbl_estado_usuario_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_usuario_nombre ON public.tbl_estado_usuario USING btree (esusr_nombre);


--
-- Name: idx_tbl_historial_solicitud_estado_actual; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_historial_solicitud_estado_actual ON public.tbl_historial_solicitud USING btree (hsol_estado_actual_id);


--
-- Name: idx_tbl_historial_solicitud_estado_anterior; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_historial_solicitud_estado_anterior ON public.tbl_historial_solicitud USING btree (hsol_estado_anterior_id);


--
-- Name: idx_tbl_historial_solicitud_fecha_cambio; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_historial_solicitud_fecha_cambio ON public.tbl_historial_solicitud USING btree (hsol_fecha_cambio);


--
-- Name: idx_tbl_historial_solicitud_solicitud; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_historial_solicitud_solicitud ON public.tbl_historial_solicitud USING btree (hsol_solicitud_id);


--
-- Name: idx_tbl_historial_solicitud_usuario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_historial_solicitud_usuario ON public.tbl_historial_solicitud USING btree (hsol_usuario_id);


--
-- Name: idx_tbl_modalidad_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_modalidad_nombre ON public.tbl_modalidad USING btree (mdld_nombre);


--
-- Name: idx_tbl_pais_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pais_nombre ON public.tbl_pais USING btree (pais_nombre);


--
-- Name: idx_tbl_permiso_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_permiso_nombre ON public.tbl_permiso USING btree (per_nombre);


--
-- Name: idx_tbl_prioridad_solicitud_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_prioridad_solicitud_nombre ON public.tbl_prioridad_solicitud USING btree (prsol_nombre);


--
-- Name: idx_tbl_region_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_region_nombre ON public.tbl_region USING btree (reg_nombre);


--
-- Name: idx_tbl_region_pais; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_region_pais ON public.tbl_region USING btree (reg_pais_id);


--
-- Name: idx_tbl_rol_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_rol_nombre ON public.tbl_rol USING btree (rol_nombre);


--
-- Name: idx_tbl_rol_permiso_permiso; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_rol_permiso_permiso ON public.tbl_rol_permiso USING btree (rlmp_permiso_id);


--
-- Name: idx_tbl_rol_permiso_rol; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_rol_permiso_rol ON public.tbl_rol_permiso USING btree (rlpm_rol_id);


--
-- Name: idx_tbl_solicitud_cargo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_cargo ON public.tbl_solicitud USING btree (sol_cargo_id);


--
-- Name: idx_tbl_solicitud_cliente; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_cliente ON public.tbl_solicitud USING btree (sol_cliente_id);


--
-- Name: idx_tbl_solicitud_codigo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_codigo ON public.tbl_solicitud USING btree (sol_codigo);


--
-- Name: idx_tbl_solicitud_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_estado ON public.tbl_solicitud USING btree (sol_estado_solicitud_id);


--
-- Name: idx_tbl_solicitud_fecha_cierre_busqueda; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_fecha_cierre_busqueda ON public.tbl_solicitud USING btree (sol_fecha_cierre_busqueda);


--
-- Name: idx_tbl_solicitud_fecha_creacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_fecha_creacion ON public.tbl_solicitud USING btree (sol_fecha_creacion);


--
-- Name: idx_tbl_solicitud_fecha_inicio_busqueda; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_fecha_inicio_busqueda ON public.tbl_solicitud USING btree (sol_fecha_inicio_busqueda);


--
-- Name: idx_tbl_solicitud_modalidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_modalidad ON public.tbl_solicitud USING btree (sol_modalidad_id);


--
-- Name: idx_tbl_solicitud_prioridad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_prioridad ON public.tbl_solicitud USING btree (sol_prioridad_id);


--
-- Name: idx_tbl_solicitud_tipo_contrato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_tipo_contrato ON public.tbl_solicitud USING btree (sol_tipo_contrato_id);


--
-- Name: idx_tbl_solicitud_usuario_asignado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_usuario_asignado ON public.tbl_solicitud USING btree (sol_usuario_asignado_id);


--
-- Name: idx_tbl_solicitud_usuario_creador; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_usuario_creador ON public.tbl_solicitud USING btree (sol_usuario_creador_id);


--
-- Name: idx_tbl_tipo_contrato_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_tipo_contrato_nombre ON public.tbl_tipo_contrato USING btree (tpct_nombre);


--
-- Name: idx_tbl_usuario_apellidos; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_apellidos ON public.tbl_usuario USING btree (usr_apellido_paterno, usr_apellido_materno);


--
-- Name: idx_tbl_usuario_area; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_area ON public.tbl_usuario USING btree (usr_area_id);


--
-- Name: idx_tbl_usuario_email; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_email ON public.tbl_usuario USING btree (usr_email);


--
-- Name: idx_tbl_usuario_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_estado ON public.tbl_usuario USING btree (usr_estado_usuario_id);


--
-- Name: idx_tbl_usuario_nombre_completo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_nombre_completo ON public.tbl_usuario USING btree (usr_nombres, usr_apellido_paterno, usr_apellido_materno);


--
-- Name: idx_tbl_usuario_rol; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_rol ON public.tbl_usuario USING btree (usr_rol_id);


--
-- Name: tbl_ciudad fk_tbl_ciudad_region; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_ciudad
    ADD CONSTRAINT fk_tbl_ciudad_region FOREIGN KEY (ciu_region_id) REFERENCES public.tbl_region(reg_id);


--
-- Name: tbl_cliente fk_tbl_cliente_area_empresa; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT fk_tbl_cliente_area_empresa FOREIGN KEY (cli_area_empresa_id) REFERENCES public.tbl_area(area_id);


--
-- Name: tbl_cliente fk_tbl_cliente_cargo_empresa; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT fk_tbl_cliente_cargo_empresa FOREIGN KEY (cli_cargo_empresa_id) REFERENCES public.tbl_cargo(crgo_id);


--
-- Name: tbl_cliente fk_tbl_cliente_empresa; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT fk_tbl_cliente_empresa FOREIGN KEY (cli_empresa_id) REFERENCES public.tbl_empresa(emp_id);


--
-- Name: tbl_comuna fk_tbl_comuna_ciudad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_comuna
    ADD CONSTRAINT fk_tbl_comuna_ciudad FOREIGN KEY (com_ciudad_id) REFERENCES public.tbl_ciudad(ciu_id);


--
-- Name: tbl_historial_solicitud fk_tbl_historial_solicitud_estado_actual; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT fk_tbl_historial_solicitud_estado_actual FOREIGN KEY (hsol_estado_actual_id) REFERENCES public.tbl_estado_solicitud(essl_id);


--
-- Name: tbl_historial_solicitud fk_tbl_historial_solicitud_estado_anterior; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT fk_tbl_historial_solicitud_estado_anterior FOREIGN KEY (hsol_estado_anterior_id) REFERENCES public.tbl_estado_solicitud(essl_id);


--
-- Name: tbl_historial_solicitud fk_tbl_historial_solicitud_solicitud; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT fk_tbl_historial_solicitud_solicitud FOREIGN KEY (hsol_solicitud_id) REFERENCES public.tbl_solicitud(sol_id);


--
-- Name: tbl_historial_solicitud fk_tbl_historial_solicitud_usuario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT fk_tbl_historial_solicitud_usuario FOREIGN KEY (hsol_usuario_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_region fk_tbl_region_pais; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_region
    ADD CONSTRAINT fk_tbl_region_pais FOREIGN KEY (reg_pais_id) REFERENCES public.tbl_pais(pais_id);


--
-- Name: tbl_rol_permiso fk_tbl_rol_permiso_permiso; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol_permiso
    ADD CONSTRAINT fk_tbl_rol_permiso_permiso FOREIGN KEY (rlmp_permiso_id) REFERENCES public.tbl_permiso(per_id);


--
-- Name: tbl_rol_permiso fk_tbl_rol_permiso_rol; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol_permiso
    ADD CONSTRAINT fk_tbl_rol_permiso_rol FOREIGN KEY (rlpm_rol_id) REFERENCES public.tbl_rol(rol_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_cargo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_cargo FOREIGN KEY (sol_cargo_id) REFERENCES public.tbl_cargo(crgo_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_cliente; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_cliente FOREIGN KEY (sol_cliente_id) REFERENCES public.tbl_cliente(cli_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_estado FOREIGN KEY (sol_estado_solicitud_id) REFERENCES public.tbl_estado_solicitud(essl_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_modalidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_modalidad FOREIGN KEY (sol_modalidad_id) REFERENCES public.tbl_modalidad(mdld_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_prioridad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_prioridad FOREIGN KEY (sol_prioridad_id) REFERENCES public.tbl_prioridad_solicitud(prsol_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_tipo_contrato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_tipo_contrato FOREIGN KEY (sol_tipo_contrato_id) REFERENCES public.tbl_tipo_contrato(tpct_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_usuario_asignado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_usuario_asignado FOREIGN KEY (sol_usuario_asignado_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_usuario_creador; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_usuario_creador FOREIGN KEY (sol_usuario_creador_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_usuario fk_tbl_usuario_area; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT fk_tbl_usuario_area FOREIGN KEY (usr_area_id) REFERENCES public.tbl_area(area_id);


--
-- Name: tbl_usuario fk_tbl_usuario_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT fk_tbl_usuario_estado FOREIGN KEY (usr_estado_usuario_id) REFERENCES public.tbl_estado_usuario(esusr_id);


--
-- Name: tbl_usuario fk_tbl_usuario_rol; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT fk_tbl_usuario_rol FOREIGN KEY (usr_rol_id) REFERENCES public.tbl_rol(rol_id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: elitsoft_admin
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict e4rxbFNdid9hG7Ib0ttk9wezOPic8YWeuAG2zCk02O0vdFgbjuP3usmRKYNI9ya

