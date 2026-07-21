--
-- PostgreSQL database dump
--

\restrict bgcFlw1rjX8lJDnn00fmtEH2LJeKd2mhgwsyuPBehRloNzuohV3Lxi8KThSc4yD

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


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: unaccent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;


--
-- Name: EXTENSION unaccent; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION unaccent IS 'text search dictionary that removes accents';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: tbl_area; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_area (
    area_id integer NOT NULL,
    area_nombre character varying(50),
    area_descripcion character varying(300),
    CONSTRAINT chk_tbl_area_descripcion_vacia CHECK (((area_descripcion IS NULL) OR (TRIM(BOTH FROM area_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_area_nombre_vacio CHECK ((TRIM(BOTH FROM area_nombre) <> ''::text))
);


ALTER TABLE public.tbl_area OWNER TO elitsoft_admin;

--
-- Name: tbl_area_area_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_area ALTER COLUMN area_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_area_area_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_candidato (
    cand_id integer NOT NULL,
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
    cand_titulo character varying(300),
    cand_estado_usuario_id integer,
    CONSTRAINT chk_tbl_candidato_apellido_paterno_vacio CHECK ((TRIM(BOTH FROM cand_apellido_paterno) <> ''::text)),
    CONSTRAINT chk_tbl_candidato_dv CHECK ((((cand_dv >= 0) AND (cand_dv <= 9)) OR (cand_dv = 10))),
    CONSTRAINT chk_tbl_candidato_email_vacio CHECK ((TRIM(BOTH FROM cand_email) <> ''::text)),
    CONSTRAINT chk_tbl_candidato_fecha_nacimiento CHECK ((cand_fecha_nacimiento <= CURRENT_DATE)),
    CONSTRAINT chk_tbl_candidato_nombres_vacio CHECK ((TRIM(BOTH FROM cand_nombres) <> ''::text)),
    CONSTRAINT chk_tbl_candidato_rut CHECK ((cand_rut_sin_dv > 0))
);


ALTER TABLE public.tbl_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_candidato_cand_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_candidato ALTER COLUMN cand_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_candidato_cand_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_candidato_cuestionario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_candidato_cuestionario (
    cdcu_id integer NOT NULL,
    cdcu_candidato_id integer,
    cdcu_cuestionario_id integer,
    cdcu_fecha_asignacion timestamp without time zone,
    cdcu_fecha_resolucion timestamp without time zone,
    cdcu_porcentaje_obtenido numeric(5,2),
    cdcu_estado_cuestionario_candidato_id integer,
    cdcu_tiempo_utilizado integer,
    cdcu_permitir_reintento boolean,
    cdcu_aprobado boolean,
    CONSTRAINT chk_tbl_candidato_cuestionario_fechas CHECK (((cdcu_fecha_resolucion IS NULL) OR (cdcu_fecha_resolucion >= cdcu_fecha_asignacion))),
    CONSTRAINT chk_tbl_candidato_cuestionario_porcentaje CHECK (((cdcu_porcentaje_obtenido IS NULL) OR ((cdcu_porcentaje_obtenido >= (0)::numeric) AND (cdcu_porcentaje_obtenido <= (100)::numeric)))),
    CONSTRAINT chk_tbl_candidato_cuestionario_tiempo CHECK (((cdcu_tiempo_utilizado IS NULL) OR (cdcu_tiempo_utilizado >= 0)))
);


ALTER TABLE public.tbl_candidato_cuestionario OWNER TO elitsoft_admin;

--
-- Name: tbl_candidato_cuestionario_cdcu_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_candidato_cuestionario ALTER COLUMN cdcu_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_candidato_cuestionario_cdcu_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_candidato_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_candidato_habilidad (
    cdhb_id integer NOT NULL,
    cdhb_candidato_id integer,
    cdhb_habilidad_id integer,
    cdhb_nivel_habilidad_id integer,
    cdhb_anios_experiencia integer,
    CONSTRAINT chk_tbl_candidato_habilidad_anios CHECK ((cdhb_anios_experiencia >= 0))
);


ALTER TABLE public.tbl_candidato_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_candidato_habilidad_cdhb_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_candidato_habilidad ALTER COLUMN cdhb_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_candidato_habilidad_cdhb_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_cargo; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cargo (
    crgo_id integer NOT NULL,
    crgo_nombre character varying(50),
    crgo_descripcion character varying(300),
    CONSTRAINT chk_tbl_cargo_descripcion_vacia CHECK (((crgo_descripcion IS NULL) OR (TRIM(BOTH FROM crgo_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_cargo_nombre_vacio CHECK ((TRIM(BOTH FROM crgo_nombre) <> ''::text))
);


ALTER TABLE public.tbl_cargo OWNER TO elitsoft_admin;

--
-- Name: tbl_cargo_crgo_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_cargo ALTER COLUMN crgo_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_cargo_crgo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_carrera; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_carrera (
    crra_id integer NOT NULL,
    crra_nombre character varying(40),
    CONSTRAINT chk_tbl_carrera_nombre_vacio CHECK ((TRIM(BOTH FROM crra_nombre) <> ''::text))
);


ALTER TABLE public.tbl_carrera OWNER TO elitsoft_admin;

--
-- Name: tbl_carrera_crra_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_carrera ALTER COLUMN crra_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_carrera_crra_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_cita_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cita_entrevista (
    ctev_id integer NOT NULL,
    ctev_solicitud_candidato_id integer,
    ctev_tipo_entrevista_id integer,
    ctev_estado_entrevista_id integer,
    ctev_fecha_hora_inicio timestamp without time zone,
    ctev_fecha_hora_fin timestamp without time zone,
    ctev_fecha_creacion timestamp without time zone,
    ctev_enlace_reunion character varying(300),
    ctev_comentarios_convocatoria character varying(300),
    ctev_titulo_evento character varying(300),
    CONSTRAINT chk_tbl_cita_entrevista_enlace CHECK (((ctev_enlace_reunion IS NULL) OR (length(TRIM(BOTH FROM ctev_enlace_reunion)) > 0))),
    CONSTRAINT chk_tbl_cita_entrevista_fechas CHECK (((ctev_fecha_hora_fin IS NULL) OR (ctev_fecha_hora_inicio < ctev_fecha_hora_fin))),
    CONSTRAINT chk_tbl_cita_entrevista_titulo CHECK ((TRIM(BOTH FROM ctev_titulo_evento) <> ''::text))
);


ALTER TABLE public.tbl_cita_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_cita_entrevista_ctev_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_cita_entrevista ALTER COLUMN ctev_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_cita_entrevista_ctev_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_cita_tipo_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cita_tipo_entrevista (
    cten_tipo_entrevista_id integer NOT NULL,
    cten_cita_entrevista_id integer NOT NULL
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
-- Name: tbl_ciudad_ciu_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_ciudad ALTER COLUMN ciu_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_ciudad_ciu_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_cliente_cli_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_cliente ALTER COLUMN cli_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_cliente_cli_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_comuna_com_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_comuna ALTER COLUMN com_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_comuna_com_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_cuestionario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cuestionario (
    cues_id integer NOT NULL,
    cues_nombre character varying(300),
    cues_descripcion character varying(300),
    cues_porcentaje_aprobacion numeric(5,2),
    cues_solicitud_id integer,
    CONSTRAINT chk_tbl_cuestionario_nombre CHECK ((TRIM(BOTH FROM cues_nombre) <> ''::text)),
    CONSTRAINT chk_tbl_cuestionario_porcentaje_aprobacion CHECK (((cues_porcentaje_aprobacion >= (0)::numeric) AND (cues_porcentaje_aprobacion <= (100)::numeric)))
);


ALTER TABLE public.tbl_cuestionario OWNER TO elitsoft_admin;

--
-- Name: tbl_cuestionario_cues_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_cuestionario ALTER COLUMN cues_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_cuestionario_cues_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_curso; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_curso (
    curs_id integer NOT NULL,
    curs_candidato_id integer,
    curs_nombre_curso character varying(40),
    curs_institucion_id integer,
    curs_es_certificado boolean,
    curs_anio_curso integer,
    CONSTRAINT chk_tbl_curso_anio CHECK (((curs_anio_curso IS NULL) OR ((curs_anio_curso >= 1900) AND ((curs_anio_curso)::numeric <= EXTRACT(year FROM CURRENT_DATE))))),
    CONSTRAINT chk_tbl_curso_nombre_vacio CHECK ((TRIM(BOTH FROM curs_nombre_curso) <> ''::text))
);


ALTER TABLE public.tbl_curso OWNER TO elitsoft_admin;

--
-- Name: tbl_curso_curs_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_curso ALTER COLUMN curs_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_curso_curs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_direccion_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_direccion_candidato (
    drcd_id integer NOT NULL,
    drcd_candidato_id integer,
    drcd_comuna_id integer,
    drcd_calle character varying(40),
    drcd_numero integer,
    drcd_dpto_oficina character varying(10),
    CONSTRAINT chk_tbl_direccion_candidato_calle CHECK ((TRIM(BOTH FROM drcd_calle) <> ''::text)),
    CONSTRAINT chk_tbl_direccion_candidato_numero CHECK ((drcd_numero > 0))
);


ALTER TABLE public.tbl_direccion_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_direccion_candidato_drcd_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_direccion_candidato ALTER COLUMN drcd_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_direccion_candidato_drcd_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_disponibilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_disponibilidad (
    disp_id integer NOT NULL,
    disp_nombre character varying(40),
    CONSTRAINT chk_tbl_disponibilidad_nombre_vacio CHECK ((TRIM(BOTH FROM disp_nombre) <> ''::text))
);


ALTER TABLE public.tbl_disponibilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_disponibilidad_disp_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_disponibilidad ALTER COLUMN disp_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_disponibilidad_disp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_empresa_emp_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_empresa ALTER COLUMN emp_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_empresa_emp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_estado_cuestionario_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_cuestionario_candidato (
    escc_id integer NOT NULL,
    escc_nombre character varying(40),
    CONSTRAINT chk_tbl_estado_cuestionario_candidato_nombre CHECK ((TRIM(BOTH FROM escc_nombre) <> ''::text))
);


ALTER TABLE public.tbl_estado_cuestionario_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_cuestionario_candidato_escc_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estado_cuestionario_candidato ALTER COLUMN escc_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estado_cuestionario_candidato_escc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_estado_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_entrevista (
    esev_id integer NOT NULL,
    esev_nombre character varying(40),
    esev_descripcion character varying(300),
    CONSTRAINT chk_tbl_estado_entrevista_nombre CHECK ((TRIM(BOTH FROM esev_nombre) <> ''::text))
);


ALTER TABLE public.tbl_estado_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_entrevista_esev_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estado_entrevista ALTER COLUMN esev_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estado_entrevista_esev_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
    essc_id integer NOT NULL,
    essc_nombre character varying(40),
    essc_descripcion character varying(300),
    CONSTRAINT chk_tbl_estado_solicitud_candidato_nombre CHECK ((TRIM(BOTH FROM essc_nombre) <> ''::text))
);


ALTER TABLE public.tbl_estado_solicitud_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_solicitud_candidato_essc_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estado_solicitud_candidato ALTER COLUMN essc_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estado_solicitud_candidato_essc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_estado_solicitud_essl_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estado_solicitud ALTER COLUMN essl_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estado_solicitud_essl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_estado_usuario_esusr_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estado_usuario ALTER COLUMN esusr_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estado_usuario_esusr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_estudio_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estudio_candidato (
    etcd_id integer NOT NULL,
    etcd_candidato_id integer,
    etcd_nivel_educacional_id integer,
    etcd_institucion_id integer,
    etcd_carrera_id integer,
    etcd_fecha_inicio date,
    etcd_fecha_fin date,
    CONSTRAINT chk_tbl_estudio_candidato_fechas CHECK (((etcd_fecha_fin IS NULL) OR (etcd_fecha_inicio <= etcd_fecha_fin)))
);


ALTER TABLE public.tbl_estudio_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_estudio_candidato_etcd_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estudio_candidato ALTER COLUMN etcd_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estudio_candidato_etcd_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_evaluacion_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_evaluacion_entrevista (
    even_id integer NOT NULL,
    even_nombre_resultado_id integer,
    even_observacion character varying(300),
    even_cita_entrevista_id integer,
    CONSTRAINT chk_tbl_evaluacion_entrevista_observacion CHECK (((even_observacion IS NULL) OR (length(TRIM(BOTH FROM even_observacion)) > 0)))
);


ALTER TABLE public.tbl_evaluacion_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_evaluacion_entrevista_even_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_evaluacion_entrevista ALTER COLUMN even_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_evaluacion_entrevista_even_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_experiencia_laboral; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_experiencia_laboral (
    expl_id integer NOT NULL,
    expl_candidato_id integer,
    expl_empresa_id integer,
    expl_cargo_id integer,
    expl_descripcion_funciones character varying(300),
    expl_fecha_inicio date,
    expl_fecha_fin date,
    CONSTRAINT chk_tbl_experiencia_laboral_descripcion CHECK ((TRIM(BOTH FROM expl_descripcion_funciones) <> ''::text)),
    CONSTRAINT chk_tbl_experiencia_laboral_fechas CHECK (((expl_fecha_fin IS NULL) OR (expl_fecha_inicio <= expl_fecha_fin)))
);


ALTER TABLE public.tbl_experiencia_laboral OWNER TO elitsoft_admin;

--
-- Name: tbl_experiencia_laboral_expl_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_experiencia_laboral ALTER COLUMN expl_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_experiencia_laboral_expl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_experiencia_laboral_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_experiencia_laboral_habilidad (
    exph_experiencia_laboral_id integer NOT NULL,
    exph_habilidad_id integer NOT NULL
);


ALTER TABLE public.tbl_experiencia_laboral_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_habilidad (
    hab_id integer NOT NULL,
    hab_nombre character varying(20),
    hab_descripcion character varying(300),
    CONSTRAINT chk_tbl_habilidad_nombre_vacio CHECK ((TRIM(BOTH FROM hab_nombre) <> ''::text))
);


ALTER TABLE public.tbl_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_habilidad_hab_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_habilidad ALTER COLUMN hab_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_habilidad_hab_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_historial_solicitud_hsol_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_historial_solicitud ALTER COLUMN hsol_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_historial_solicitud_hsol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_institucion; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_institucion (
    inst_id integer NOT NULL,
    inst_nombre character varying(40),
    inst_tipo_institucion_id integer,
    CONSTRAINT chk_tbl_institucion_nombre_vacio CHECK ((TRIM(BOTH FROM inst_nombre) <> ''::text))
);


ALTER TABLE public.tbl_institucion OWNER TO elitsoft_admin;

--
-- Name: tbl_institucion_inst_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_institucion ALTER COLUMN inst_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_institucion_inst_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_modalidad_mdld_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_modalidad ALTER COLUMN mdld_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_modalidad_mdld_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_motivo_rechazo; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_motivo_rechazo (
    mtrc_id integer NOT NULL,
    mtrc_nombre character varying(40),
    mtrc_descripcion character varying(300),
    CONSTRAINT chk_tbl_motivo_rechazo_nombre CHECK ((TRIM(BOTH FROM mtrc_nombre) <> ''::text))
);


ALTER TABLE public.tbl_motivo_rechazo OWNER TO elitsoft_admin;

--
-- Name: tbl_motivo_rechazo_mtrc_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_motivo_rechazo ALTER COLUMN mtrc_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_motivo_rechazo_mtrc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_nivel_educacional; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nivel_educacional (
    nved_id integer NOT NULL,
    nved_nombre character varying(40),
    CONSTRAINT chk_tbl_nivel_educacional_nombre_vacio CHECK ((TRIM(BOTH FROM nved_nombre) <> ''::text))
);


ALTER TABLE public.tbl_nivel_educacional OWNER TO elitsoft_admin;

--
-- Name: tbl_nivel_educacional_nved_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_nivel_educacional ALTER COLUMN nved_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_nivel_educacional_nved_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_nivel_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nivel_habilidad (
    nvhb_id integer NOT NULL,
    nvhb_nombre character varying(20),
    nvhb_descripcion character varying(300),
    nvhb_puntaje_base integer,
    nvhb_duracion integer,
    CONSTRAINT chk_tbl_nivel_habilidad_duracion CHECK ((nvhb_duracion > 0)),
    CONSTRAINT chk_tbl_nivel_habilidad_nombre_vacio CHECK ((TRIM(BOTH FROM nvhb_nombre) <> ''::text)),
    CONSTRAINT chk_tbl_nivel_habilidad_puntaje CHECK ((nvhb_puntaje_base >= 0))
);


ALTER TABLE public.tbl_nivel_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_nivel_habilidad_nvhb_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_nivel_habilidad ALTER COLUMN nvhb_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_nivel_habilidad_nvhb_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_nombre_resultado; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nombre_resultado (
    nore_id integer NOT NULL,
    nore_nombre character varying(40),
    CONSTRAINT chk_tbl_nombre_resultado_nombre CHECK ((TRIM(BOTH FROM nore_nombre) <> ''::text))
);


ALTER TABLE public.tbl_nombre_resultado OWNER TO elitsoft_admin;

--
-- Name: tbl_nombre_resultado_nore_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_nombre_resultado ALTER COLUMN nore_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_nombre_resultado_nore_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_opcion_respuesta; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_opcion_respuesta (
    opcr_id integer NOT NULL,
    opcr_pregunta_id integer,
    opcr_texto_opcion character varying(300),
    opcr_es_correcta boolean,
    CONSTRAINT chk_tbl_opcion_respuesta_texto CHECK ((TRIM(BOTH FROM opcr_texto_opcion) <> ''::text))
);


ALTER TABLE public.tbl_opcion_respuesta OWNER TO elitsoft_admin;

--
-- Name: tbl_opcion_respuesta_opcr_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_opcion_respuesta ALTER COLUMN opcr_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_opcion_respuesta_opcr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_pais_pais_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_pais ALTER COLUMN pais_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_pais_pais_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_permiso_per_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_permiso ALTER COLUMN per_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_permiso_per_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_pregunta; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_pregunta (
    preg_id integer NOT NULL,
    preg_texto_pregunta character varying(300),
    preg_habilidad_id integer,
    preg_nivel_habilidad_id integer,
    preg_fecha_creacion timestamp without time zone,
    CONSTRAINT chk_tbl_pregunta_texto CHECK ((TRIM(BOTH FROM preg_texto_pregunta) <> ''::text))
);


ALTER TABLE public.tbl_pregunta OWNER TO elitsoft_admin;

--
-- Name: tbl_pregunta_cuestionario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_pregunta_cuestionario (
    prcu_pregunta_id integer NOT NULL,
    prcu_cuestionario_id integer NOT NULL,
    prcu_id integer NOT NULL
);


ALTER TABLE public.tbl_pregunta_cuestionario OWNER TO elitsoft_admin;

--
-- Name: tbl_pregunta_preg_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_pregunta ALTER COLUMN preg_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_pregunta_preg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_prioridad_solicitud_prsol_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_prioridad_solicitud ALTER COLUMN prsol_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_prioridad_solicitud_prsol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_region_reg_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_region ALTER COLUMN reg_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_region_reg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_respuesta_pregunta; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_respuesta_pregunta (
    rspr_id integer NOT NULL,
    rspr_candidato_cuestionario_id integer,
    rspr_es_correcta boolean,
    rspr_puntaje_obtenido integer,
    rspr_opcion_respuesta_id integer,
    rspr_pregunta_cuestionario_id integer,
    CONSTRAINT chk_tbl_respuesta_pregunta_puntaje CHECK ((rspr_puntaje_obtenido >= 0))
);


ALTER TABLE public.tbl_respuesta_pregunta OWNER TO elitsoft_admin;

--
-- Name: tbl_respuesta_pregunta_rspr_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_respuesta_pregunta ALTER COLUMN rspr_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_respuesta_pregunta_rspr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
    rlpm_permiso_id integer NOT NULL
);


ALTER TABLE public.tbl_rol_permiso OWNER TO elitsoft_admin;

--
-- Name: tbl_rol_rol_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_rol ALTER COLUMN rol_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_rol_rol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
    slcd_id integer NOT NULL,
    slcd_candidato_id integer,
    slcd_solicitud_id integer,
    slcd_pretension_renta integer,
    slcd_puntaje_compatibilidad numeric(5,2),
    slcd_estado_solicitud_id integer,
    slcd_fecha_postulacion timestamp without time zone,
    slcd_observaciones character varying(300),
    slcd_motivo_rechazo_id integer,
    CONSTRAINT chk_tbl_solicitud_candidato_observaciones CHECK (((slcd_observaciones IS NULL) OR (length(TRIM(BOTH FROM slcd_observaciones)) > 0))),
    CONSTRAINT chk_tbl_solicitud_candidato_pretension_renta CHECK (((slcd_pretension_renta IS NULL) OR (slcd_pretension_renta >= 0))),
    CONSTRAINT chk_tbl_solicitud_candidato_puntaje CHECK (((slcd_puntaje_compatibilidad IS NULL) OR ((slcd_puntaje_compatibilidad >= (0)::numeric) AND (slcd_puntaje_compatibilidad <= (100)::numeric))))
);


ALTER TABLE public.tbl_solicitud_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_candidato_slcd_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_solicitud_candidato ALTER COLUMN slcd_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_solicitud_candidato_slcd_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_solicitud_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_solicitud_habilidad (
    solhb_id integer NOT NULL,
    solhb_solicitud_id integer,
    solhb_habilidad_id integer,
    solhb_nivel_habilidad_id integer,
    solhb_anios_experiencia_req integer,
    solhb_es_excluyente boolean,
    CONSTRAINT chk_tbl_solicitud_habilidad_anios CHECK ((solhb_anios_experiencia_req >= 0))
);


ALTER TABLE public.tbl_solicitud_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_habilidad_solhb_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_solicitud_habilidad ALTER COLUMN solhb_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_solicitud_habilidad_solhb_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_solicitud_sol_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_solicitud ALTER COLUMN sol_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_solicitud_sol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
-- Name: tbl_tipo_contrato_tpct_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_tipo_contrato ALTER COLUMN tpct_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_tipo_contrato_tpct_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_tipo_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_tipo_entrevista (
    tpet_id integer NOT NULL,
    tpet_nombre character varying(40),
    tpet_descripcion character varying(300),
    CONSTRAINT chk_tbl_tipo_entrevista_nombre CHECK ((TRIM(BOTH FROM tpet_nombre) <> ''::text))
);


ALTER TABLE public.tbl_tipo_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_tipo_entrevista_tpet_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_tipo_entrevista ALTER COLUMN tpet_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_tipo_entrevista_tpet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_tipo_institucion; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_tipo_institucion (
    tint_id integer NOT NULL,
    tint_tipo_institucion character varying(40),
    CONSTRAINT chk_tbl_tipo_institucion_nombre_vacio CHECK ((TRIM(BOTH FROM tint_tipo_institucion) <> ''::text))
);


ALTER TABLE public.tbl_tipo_institucion OWNER TO elitsoft_admin;

--
-- Name: tbl_tipo_institucion_tint_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_tipo_institucion ALTER COLUMN tint_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_tipo_institucion_tint_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


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
    usrce_cita_entrevista_id integer NOT NULL,
    usrce_usuario_id integer NOT NULL
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
1	Directorio	Organo responsable de definir la estrategia, el gobierno corporativo y la direccion general de la organizacion.
2	Gerencia General	Lidera la gestion integral de la empresa y supervisa el cumplimiento de los objetivos estrategicos.
3	Asistencia de Gerencia	Brinda apoyo administrativo y operativo a la Gerencia General en la coordinacion de sus actividades.
4	Asesoria Legal	Proporciona asesoramiento juridico y vela por el cumplimiento de la normativa vigente.
5	Control Interno	Supervisa los procesos internos para asegurar el cumplimiento de politicas, normas y controles.
6	Gerencia de Adm. y Finanzas	Administra los recursos financieros, contables y administrativos de la organizacion.
7	Gerencia de Operaciones	Gestiona y optimiza los procesos operativos para garantizar la eficiencia y continuidad del negocio.
8	Gerencia Comercial	Dirige las estrategias comerciales, ventas y desarrollo de clientes para impulsar el crecimiento de la organizacion.
9	Departamento de RR.HH.	Gestiona el talento humano, incluyendo reclutamiento, seleccion, desarrollo y bienestar de los colaboradores.
\.


--
-- Data for Name: tbl_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_candidato (cand_id, cand_email, cand_password, cand_nombres, cand_apellido_paterno, cand_apellido_materno, cand_fecha_nacimiento, cand_telefono, cand_rut_sin_dv, cand_dv, cand_disponibilidad_id, cand_resumen_profesional, cand_fecha_creacion, cand_url_1, cand_titulo, cand_estado_usuario_id) FROM stdin;
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
1	Desarrollador Backend	Desarrolla la logica de negocio y los servicios del lado del servidor.
2	Desarrollador Frontend	Desarrolla la interfaz de usuario y la experiencia visual de las aplicaciones.
3	Desarrollador Full Stack	Desarrolla tanto el frontend como el backend de las aplicaciones.
4	Desarrollador Mobile	Desarrolla aplicaciones para dispositivos moviles Android e iOS.
5	Analista QA	Disena y ejecuta pruebas para asegurar la calidad del software.
6	Ingeniero QA Automation	Automatiza pruebas funcionales y de regresion.
7	Scrum Master	Facilita la metodologia Scrum y elimina impedimentos del equipo.
8	Product Owner	Gestiona el backlog del producto y prioriza los requerimientos del negocio.
9	Analista Funcional	Levanta, analiza y documenta requerimientos funcionales.
10	Analista de Sistemas	Analiza procesos y propone soluciones tecnologicas.
11	Arquitecto de Software	Define la arquitectura tecnica de las aplicaciones.
12	DevOps Engineer	Automatiza despliegues y administra la infraestructura de desarrollo.
13	Ingeniero de Datos	Disena y mantiene pipelines y plataformas de datos.
14	Cientifico de Datos	Analiza grandes volumenes de datos mediante modelos estadisticos y de inteligencia artificial.
15	Analista BI	Desarrolla indicadores, reportes y dashboards para apoyar la toma de decisiones.
16	Administrador de Base de Datos (DBA)	Administra, optimiza y asegura el correcto funcionamiento de las bases de datos.
17	Administrador de Sistemas	Gestiona servidores, sistemas operativos y plataformas tecnologicas.
18	Especialista en Ciberseguridad	Protege la infraestructura tecnologica y la informacion de la organizacion.
19	Soporte TI	Brinda soporte tecnico a usuarios y equipos tecnologicos.
20	Lider Tecnico	Coordina tecnicamente al equipo de desarrollo y promueve las buenas practicas.
21	Jefe de Proyecto TI	Planifica, coordina y controla la ejecucion de proyectos tecnologicos.
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
1	Jade Garcia	20	7	jade@bcochile.cl	jade2@bcochile.cl	998765432	998765431	1
2	Carol Urquieta	7	7	carol@bcochile.cl	carol2@bcochile.cl	987654321	987654320	1
3	Oriana Hurtado	5	7	oriana@bcochile.cl	oriana2@bcochile.cl	976543210	976543219	1
4	Sheila Valdes	21	7	sheila@latam.cl	sheila2@latam.cl	965432109	965432108	3
5	Rodrigo Riquelme	20	7	rodrigo@elitsoft.cl	rodrigo2@elitsoft.cl	954321098	954321097	4
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
1	Banco de Chile	97004000-5
2	Sparta	76074938-9
3	LATAM	89862200-2
4	Elitsoft	76876845-5
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
1	Pendiente	La solicitud fue creada por un administrador y esta pendiente de ser tomada por un reclutador.
2	En Curso	La vacante esta activa, publicada y recibiendo postulaciones. Es administrada por el reclutador asignado.
3	En Entrevistas	La recepcion de postulaciones finalizo y los candidatos seleccionados se encuentran en proceso de entrevistas y evaluacion.
4	Cancelado	El proceso de seleccion fue cancelado por decision del cliente, cambios presupuestarios u otras razones.
5	Cerrado	La vacante fue cubierta exitosamente mediante la contratacion de un candidato.
6	Pausado	El proceso de seleccion se encuentra suspendido temporalmente y podra reanudarse posteriormente.
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
1	Activo	Usuario habilitado para operar plenamente en la plataforma.
2	Inactivo	Usuario deshabilitado temporalmente; no puede iniciar sesion.
3	Bloqueado	Cuenta suspendida automaticamente por exceso de intentos fallidos de inicio de sesion.
4	Eliminado	Usuario eliminado de forma logica para conservar la informacion y la auditoria historica.
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
1	Presencial	Trabajo obligatorio en las oficinas del cliente de lunes a viernes.
2	Remoto	Trabajo completamente desde el hogar, mediante teletrabajo nacional o internacional.
3	H├¡brido	Esquema flexible de trabajo que combina d├¡as presenciales y remotos (por ejemplo, 3 d├¡as en casa y 2 d├¡as en la oficina).
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
1	USR_CREATE	Crear usuarios internos
2	USR_VIEW	Consultar usuarios
3	USR_UPDATE	Modificar usuarios
4	USR_DELETE	Desactivar usuarios
5	SOL_CREATE	Crear solicitudes de personal
6	SOL_VIEW	Consultar solicitudes
7	SOL_UPDATE	Modificar solicitudes
8	SOL_DELETE	Cerrar o eliminar solicitudes
9	CAN_VIEW	Ver candidatos
10	CAN_UPDATE	Actualizar informacion o estado del candidato
11	CAN_DELETE	Eliminar o desactivar candidato
12	CUEST_CREATE	Crear cuestionarios
13	CUEST_ASSIGN	Asignar cuestionarios
14	CUEST_VIEW	Ver resultados de cuestionarios
15	INT_CREATE	Agendar entrevistas
16	INT_VIEW	Ver entrevistas
17	INT_UPDATE	Modificar entrevistas
18	INT_EVALUATE	Registrar evaluacion de entrevista
19	CAT_ADMIN	Administrar catalogos maestros
20	REP_VIEW	Consultar reportes y metricas
\.


--
-- Data for Name: tbl_pregunta; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_pregunta (preg_id, preg_texto_pregunta, preg_habilidad_id, preg_nivel_habilidad_id, preg_fecha_creacion) FROM stdin;
\.


--
-- Data for Name: tbl_pregunta_cuestionario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_pregunta_cuestionario (prcu_pregunta_id, prcu_cuestionario_id, prcu_id) FROM stdin;
\.


--
-- Data for Name: tbl_prioridad_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_prioridad_solicitud (prsol_id, prsol_nombre, prsol_descripcion) FROM stdin;
1	Alta	Vacantes criticas que requieren cobertura en menos de 15 dias
2	Media	Procesos estandar con un tiempo estimado de cobertura de 30 dias
3	Baja	Busquedas preventivas o planes de expansion sin fecha limite estricta
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
1	Administrador	Administrador total del sistema con acceso global a todos los modulos.
2	Reclutador	Usuario que realiza el proceso de reclutamiento.
3	Candidato	Postulante externo que aplica a las ofertas laborales y responde cuestionarios.
4	Entrevistador	Colaborador tecnico o lider de area encargado de realizar entrevistas a los candidatos.
\.


--
-- Data for Name: tbl_rol_permiso; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_rol_permiso (rlpm_rol_id, rlpm_permiso_id) FROM stdin;
1	1
1	2
1	3
1	4
1	5
1	6
1	7
1	8
1	9
1	10
1	11
1	12
1	13
1	14
1	15
1	16
1	17
1	18
1	19
1	20
2	6
2	7
2	9
2	10
2	13
2	14
2	15
2	16
2	17
2	20
4	9
4	14
4	16
4	18
\.


--
-- Data for Name: tbl_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_solicitud (sol_id, sol_codigo, sol_titulo, sol_cargo_id, sol_descripcion, sol_prioridad_id, sol_cantidad_vacantes, sol_cliente_id, sol_usuario_creador_id, sol_usuario_asignado_id, sol_modalidad_id, sol_salario_min, sol_salario_max, sol_fecha_creacion, sol_fecha_inicio_busqueda, sol_fecha_cierre_busqueda, sol_fecha_inicio_cliente, sol_estado_solicitud_id, sol_hora_inicio_jornada, sol_hora_fin_jornada, sol_tipo_contrato_id, sol_observacion) FROM stdin;
1	SOL-001	Desarrollador Senior Backend Python (Presencial)	1	Buscamos un Ingeniero Full Stack o Backend con mas de 5 anos de experiencia disenando arquitecturas basadas en microservicios, APIs REST con FastAPI y optimizacion de consultas SQL nativas en PostgreSQL bajo entornos Docker.	2	2	1	1	3	2	2500000	3000000	2026-07-21 11:00:00	2026-07-21 11:00:00	2026-07-21 18:00:00	2026-07-21 11:00:00	2	09:00:00	18:00:00	2	Solicitud de prueba.
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
1	Indefinido	Contrato laboral sin fecha de termino, vigente hasta que una de las partes lo finalice conforme a la legislacion.
2	Plazo Fijo	Contrato laboral con una fecha de inicio y una fecha de termino previamente establecidas.
3	Por Proyecto	Contrato cuya duracion esta vinculada a la ejecucion de un proyecto o una tarea especifica. Finaliza una vez concluido el proyecto.
4	Practica Profesional	Acuerdo destinado a estudiantes o egresados para desarrollar experiencia practica relacionada con su formacion academica.
5	Honorarios	Prestacion de servicios independiente, sin vinculo laboral directo, regulada mediante la emision de boletas de honorarios.
\.


--
-- Data for Name: tbl_tipo_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_tipo_entrevista (tpet_id, tpet_nombre, tpet_descripcion) FROM stdin;
\.


--
-- Data for Name: tbl_tipo_institucion; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_tipo_institucion (tint_id, tint_tipo_institucion) FROM stdin;
\.


--
-- Data for Name: tbl_usuario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_usuario (usr_id, usr_rol_id, usr_estado_usuario_id, usr_area_id, usr_nombres, usr_apellido_paterno, usr_apellido_materno, usr_rut_sin_dv, usr_dv, usr_telefono, usr_email, usr_contrasena) FROM stdin;
1	1	1	1	Noelid	Chavez	Rodriguez	26380143	1	931448429	noelidch@gmail.com	$2a$06$FzwiINGdtVsSu1nZxxH7ue2UocPeuzXnxkvpikPDbZBgVyGolVNJW
3	2	1	2	Felipe	Valdes	Mella	18002594	4	978611801	f.valdesmella@gmail.com	$2a$06$zFFjx7Qv/Be32p9xq56baesQDNaqoZlYChLVg73i.bpk8Te9cxtry
2	4	1	3	Catherine	Rebolledo	Pastene	23040635	9	957034447	cathyrebopas@gmail.com	$2a$06$JGe3I81Za0WLqAD8oVREyeBdHF.ctzKb3Velnu7ti6thWD24S1RVu
\.


--
-- Data for Name: tbl_usuario_cita_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_usuario_cita_entrevista (usrce_cita_entrevista_id, usrce_usuario_id) FROM stdin;
\.


--
-- Name: tbl_area_area_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_area_area_id_seq', 9, true);


--
-- Name: tbl_candidato_cand_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_candidato_cand_id_seq', 1, false);


--
-- Name: tbl_candidato_cuestionario_cdcu_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_candidato_cuestionario_cdcu_id_seq', 1, false);


--
-- Name: tbl_candidato_habilidad_cdhb_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_candidato_habilidad_cdhb_id_seq', 1, false);


--
-- Name: tbl_cargo_crgo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_cargo_crgo_id_seq', 21, true);


--
-- Name: tbl_carrera_crra_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_carrera_crra_id_seq', 1, false);


--
-- Name: tbl_cita_entrevista_ctev_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_cita_entrevista_ctev_id_seq', 1, false);


--
-- Name: tbl_ciudad_ciu_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_ciudad_ciu_id_seq', 1, false);


--
-- Name: tbl_cliente_cli_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_cliente_cli_id_seq', 5, true);


--
-- Name: tbl_comuna_com_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_comuna_com_id_seq', 1, false);


--
-- Name: tbl_cuestionario_cues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_cuestionario_cues_id_seq', 1, false);


--
-- Name: tbl_curso_curs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_curso_curs_id_seq', 1, false);


--
-- Name: tbl_direccion_candidato_drcd_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_direccion_candidato_drcd_id_seq', 1, false);


--
-- Name: tbl_disponibilidad_disp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_disponibilidad_disp_id_seq', 1, false);


--
-- Name: tbl_empresa_emp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_empresa_emp_id_seq', 4, true);


--
-- Name: tbl_estado_cuestionario_candidato_escc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_cuestionario_candidato_escc_id_seq', 1, false);


--
-- Name: tbl_estado_entrevista_esev_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_entrevista_esev_id_seq', 1, false);


--
-- Name: tbl_estado_solicitud_candidato_essc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_solicitud_candidato_essc_id_seq', 1, false);


--
-- Name: tbl_estado_solicitud_essl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_solicitud_essl_id_seq', 6, true);


--
-- Name: tbl_estado_usuario_esusr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_usuario_esusr_id_seq', 4, true);


--
-- Name: tbl_estudio_candidato_etcd_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estudio_candidato_etcd_id_seq', 1, false);


--
-- Name: tbl_evaluacion_entrevista_even_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_evaluacion_entrevista_even_id_seq', 1, false);


--
-- Name: tbl_experiencia_laboral_expl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_experiencia_laboral_expl_id_seq', 1, false);


--
-- Name: tbl_habilidad_hab_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_habilidad_hab_id_seq', 1, false);


--
-- Name: tbl_historial_solicitud_hsol_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_historial_solicitud_hsol_id_seq', 1, false);


--
-- Name: tbl_institucion_inst_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_institucion_inst_id_seq', 1, false);


--
-- Name: tbl_modalidad_mdld_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_modalidad_mdld_id_seq', 3, true);


--
-- Name: tbl_motivo_rechazo_mtrc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_motivo_rechazo_mtrc_id_seq', 1, false);


--
-- Name: tbl_nivel_educacional_nved_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_nivel_educacional_nved_id_seq', 1, false);


--
-- Name: tbl_nivel_habilidad_nvhb_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_nivel_habilidad_nvhb_id_seq', 1, false);


--
-- Name: tbl_nombre_resultado_nore_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_nombre_resultado_nore_id_seq', 1, false);


--
-- Name: tbl_opcion_respuesta_opcr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_opcion_respuesta_opcr_id_seq', 1, false);


--
-- Name: tbl_pais_pais_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_pais_pais_id_seq', 1, false);


--
-- Name: tbl_permiso_per_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_permiso_per_id_seq', 20, true);


--
-- Name: tbl_pregunta_preg_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_pregunta_preg_id_seq', 1, false);


--
-- Name: tbl_prioridad_solicitud_prsol_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_prioridad_solicitud_prsol_id_seq', 3, true);


--
-- Name: tbl_region_reg_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_region_reg_id_seq', 1, false);


--
-- Name: tbl_respuesta_pregunta_rspr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_respuesta_pregunta_rspr_id_seq', 1, false);


--
-- Name: tbl_rol_rol_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_rol_rol_id_seq', 4, true);


--
-- Name: tbl_solicitud_candidato_slcd_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_solicitud_candidato_slcd_id_seq', 1, false);


--
-- Name: tbl_solicitud_habilidad_solhb_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_solicitud_habilidad_solhb_id_seq', 1, false);


--
-- Name: tbl_solicitud_sol_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_solicitud_sol_id_seq', 1, true);


--
-- Name: tbl_tipo_contrato_tpct_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_tipo_contrato_tpct_id_seq', 5, true);


--
-- Name: tbl_tipo_entrevista_tpet_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_tipo_entrevista_tpet_id_seq', 1, false);


--
-- Name: tbl_tipo_institucion_tint_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_tipo_institucion_tint_id_seq', 1, false);


--
-- Name: tbl_usuario_usr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_usuario_usr_id_seq', 3, true);


--
-- Name: tbl_area pk_tbl_area; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_area
    ADD CONSTRAINT pk_tbl_area PRIMARY KEY (area_id);


--
-- Name: tbl_candidato pk_tbl_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato
    ADD CONSTRAINT pk_tbl_candidato PRIMARY KEY (cand_id);


--
-- Name: tbl_candidato_cuestionario pk_tbl_candidato_cuestionario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_cuestionario
    ADD CONSTRAINT pk_tbl_candidato_cuestionario PRIMARY KEY (cdcu_id);


--
-- Name: tbl_candidato_habilidad pk_tbl_candidato_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT pk_tbl_candidato_habilidad PRIMARY KEY (cdhb_id);


--
-- Name: tbl_cargo pk_tbl_cargo; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cargo
    ADD CONSTRAINT pk_tbl_cargo PRIMARY KEY (crgo_id);


--
-- Name: tbl_carrera pk_tbl_carrera; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_carrera
    ADD CONSTRAINT pk_tbl_carrera PRIMARY KEY (crra_id);


--
-- Name: tbl_cita_entrevista pk_tbl_cita_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT pk_tbl_cita_entrevista PRIMARY KEY (ctev_id);


--
-- Name: tbl_cita_tipo_entrevista pk_tbl_cita_tipo_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_tipo_entrevista
    ADD CONSTRAINT pk_tbl_cita_tipo_entrevista PRIMARY KEY (cten_tipo_entrevista_id, cten_cita_entrevista_id);


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
-- Name: tbl_cuestionario pk_tbl_cuestionario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cuestionario
    ADD CONSTRAINT pk_tbl_cuestionario PRIMARY KEY (cues_id);


--
-- Name: tbl_curso pk_tbl_curso; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_curso
    ADD CONSTRAINT pk_tbl_curso PRIMARY KEY (curs_id);


--
-- Name: tbl_direccion_candidato pk_tbl_direccion_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_direccion_candidato
    ADD CONSTRAINT pk_tbl_direccion_candidato PRIMARY KEY (drcd_id);


--
-- Name: tbl_disponibilidad pk_tbl_disponibilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_disponibilidad
    ADD CONSTRAINT pk_tbl_disponibilidad PRIMARY KEY (disp_id);


--
-- Name: tbl_empresa pk_tbl_empresa; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_empresa
    ADD CONSTRAINT pk_tbl_empresa PRIMARY KEY (emp_id);


--
-- Name: tbl_estado_cuestionario_candidato pk_tbl_estado_cuestionario_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_cuestionario_candidato
    ADD CONSTRAINT pk_tbl_estado_cuestionario_candidato PRIMARY KEY (escc_id);


--
-- Name: tbl_estado_entrevista pk_tbl_estado_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_entrevista
    ADD CONSTRAINT pk_tbl_estado_entrevista PRIMARY KEY (esev_id);


--
-- Name: tbl_estado_solicitud pk_tbl_estado_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud
    ADD CONSTRAINT pk_tbl_estado_solicitud PRIMARY KEY (essl_id);


--
-- Name: tbl_estado_solicitud_candidato pk_tbl_estado_solicitud_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud_candidato
    ADD CONSTRAINT pk_tbl_estado_solicitud_candidato PRIMARY KEY (essc_id);


--
-- Name: tbl_estado_usuario pk_tbl_estado_usuario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_usuario
    ADD CONSTRAINT pk_tbl_estado_usuario PRIMARY KEY (esusr_id);


--
-- Name: tbl_estudio_candidato pk_tbl_estudio_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT pk_tbl_estudio_candidato PRIMARY KEY (etcd_id);


--
-- Name: tbl_evaluacion_entrevista pk_tbl_evaluacion_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_evaluacion_entrevista
    ADD CONSTRAINT pk_tbl_evaluacion_entrevista PRIMARY KEY (even_id);


--
-- Name: tbl_experiencia_laboral pk_tbl_experiencia_laboral; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral
    ADD CONSTRAINT pk_tbl_experiencia_laboral PRIMARY KEY (expl_id);


--
-- Name: tbl_experiencia_laboral_habilidad pk_tbl_experiencia_laboral_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral_habilidad
    ADD CONSTRAINT pk_tbl_experiencia_laboral_habilidad PRIMARY KEY (exph_experiencia_laboral_id, exph_habilidad_id);


--
-- Name: tbl_habilidad pk_tbl_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_habilidad
    ADD CONSTRAINT pk_tbl_habilidad PRIMARY KEY (hab_id);


--
-- Name: tbl_historial_solicitud pk_tbl_historial_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT pk_tbl_historial_solicitud PRIMARY KEY (hsol_id);


--
-- Name: tbl_institucion pk_tbl_institucion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_institucion
    ADD CONSTRAINT pk_tbl_institucion PRIMARY KEY (inst_id);


--
-- Name: tbl_modalidad pk_tbl_modalidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_modalidad
    ADD CONSTRAINT pk_tbl_modalidad PRIMARY KEY (mdld_id);


--
-- Name: tbl_motivo_rechazo pk_tbl_motivo_rechazo; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_motivo_rechazo
    ADD CONSTRAINT pk_tbl_motivo_rechazo PRIMARY KEY (mtrc_id);


--
-- Name: tbl_nivel_educacional pk_tbl_nivel_educacional; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_educacional
    ADD CONSTRAINT pk_tbl_nivel_educacional PRIMARY KEY (nved_id);


--
-- Name: tbl_nivel_habilidad pk_tbl_nivel_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_habilidad
    ADD CONSTRAINT pk_tbl_nivel_habilidad PRIMARY KEY (nvhb_id);


--
-- Name: tbl_nombre_resultado pk_tbl_nombre_resultado; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nombre_resultado
    ADD CONSTRAINT pk_tbl_nombre_resultado PRIMARY KEY (nore_id);


--
-- Name: tbl_opcion_respuesta pk_tbl_opcion_respuesta; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_opcion_respuesta
    ADD CONSTRAINT pk_tbl_opcion_respuesta PRIMARY KEY (opcr_id);


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
-- Name: tbl_pregunta pk_tbl_pregunta; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta
    ADD CONSTRAINT pk_tbl_pregunta PRIMARY KEY (preg_id);


--
-- Name: tbl_pregunta_cuestionario pk_tbl_pregunta_cuestionario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta_cuestionario
    ADD CONSTRAINT pk_tbl_pregunta_cuestionario PRIMARY KEY (prcu_id);


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
-- Name: tbl_respuesta_pregunta pk_tbl_respuesta_pregunta; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT pk_tbl_respuesta_pregunta PRIMARY KEY (rspr_id);


--
-- Name: tbl_rol pk_tbl_rol; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol
    ADD CONSTRAINT pk_tbl_rol PRIMARY KEY (rol_id);


--
-- Name: tbl_rol_permiso pk_tbl_rol_permiso; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol_permiso
    ADD CONSTRAINT pk_tbl_rol_permiso PRIMARY KEY (rlpm_rol_id, rlpm_permiso_id);


--
-- Name: tbl_solicitud pk_tbl_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT pk_tbl_solicitud PRIMARY KEY (sol_id);


--
-- Name: tbl_solicitud_candidato pk_tbl_solicitud_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT pk_tbl_solicitud_candidato PRIMARY KEY (slcd_id);


--
-- Name: tbl_solicitud_habilidad pk_tbl_solicitud_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT pk_tbl_solicitud_habilidad PRIMARY KEY (solhb_id);


--
-- Name: tbl_tipo_contrato pk_tbl_tipo_contrato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_contrato
    ADD CONSTRAINT pk_tbl_tipo_contrato PRIMARY KEY (tpct_id);


--
-- Name: tbl_tipo_entrevista pk_tbl_tipo_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_entrevista
    ADD CONSTRAINT pk_tbl_tipo_entrevista PRIMARY KEY (tpet_id);


--
-- Name: tbl_tipo_institucion pk_tbl_tipo_institucion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_institucion
    ADD CONSTRAINT pk_tbl_tipo_institucion PRIMARY KEY (tint_id);


--
-- Name: tbl_usuario pk_tbl_usuario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT pk_tbl_usuario PRIMARY KEY (usr_id);


--
-- Name: tbl_usuario_cita_entrevista pk_tbl_usuario_cita_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario_cita_entrevista
    ADD CONSTRAINT pk_tbl_usuario_cita_entrevista PRIMARY KEY (usrce_cita_entrevista_id, usrce_usuario_id);


--
-- Name: tbl_area uq_tbl_area_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_area
    ADD CONSTRAINT uq_tbl_area_nombre UNIQUE (area_nombre);


--
-- Name: tbl_candidato uq_tbl_candidato_email; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato
    ADD CONSTRAINT uq_tbl_candidato_email UNIQUE (cand_email);


--
-- Name: tbl_candidato_habilidad uq_tbl_candidato_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT uq_tbl_candidato_habilidad UNIQUE (cdhb_candidato_id, cdhb_habilidad_id);


--
-- Name: tbl_candidato uq_tbl_candidato_rut; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato
    ADD CONSTRAINT uq_tbl_candidato_rut UNIQUE (cand_rut_sin_dv, cand_dv);


--
-- Name: tbl_cargo uq_tbl_cargo_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cargo
    ADD CONSTRAINT uq_tbl_cargo_nombre UNIQUE (crgo_nombre);


--
-- Name: tbl_carrera uq_tbl_carrera_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_carrera
    ADD CONSTRAINT uq_tbl_carrera_nombre UNIQUE (crra_nombre);


--
-- Name: tbl_cita_entrevista uq_tbl_cita_entrevista_agenda; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT uq_tbl_cita_entrevista_agenda UNIQUE (ctev_solicitud_candidato_id, ctev_tipo_entrevista_id, ctev_fecha_hora_inicio);


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
-- Name: tbl_cuestionario uq_tbl_cuestionario_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cuestionario
    ADD CONSTRAINT uq_tbl_cuestionario_nombre UNIQUE (cues_nombre);


--
-- Name: tbl_curso uq_tbl_curso_candidato_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_curso
    ADD CONSTRAINT uq_tbl_curso_candidato_nombre UNIQUE (curs_candidato_id, curs_nombre_curso);


--
-- Name: tbl_direccion_candidato uq_tbl_direccion_candidato_direccion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_direccion_candidato
    ADD CONSTRAINT uq_tbl_direccion_candidato_direccion UNIQUE (drcd_candidato_id, drcd_comuna_id, drcd_calle, drcd_numero, drcd_dpto_oficina);


--
-- Name: tbl_disponibilidad uq_tbl_disponibilidad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_disponibilidad
    ADD CONSTRAINT uq_tbl_disponibilidad_nombre UNIQUE (disp_nombre);


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
-- Name: tbl_estado_cuestionario_candidato uq_tbl_estado_cuestionario_candidato_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_cuestionario_candidato
    ADD CONSTRAINT uq_tbl_estado_cuestionario_candidato_nombre UNIQUE (escc_nombre);


--
-- Name: tbl_estado_entrevista uq_tbl_estado_entrevista_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_entrevista
    ADD CONSTRAINT uq_tbl_estado_entrevista_nombre UNIQUE (esev_nombre);


--
-- Name: tbl_estado_solicitud_candidato uq_tbl_estado_solicitud_candidato_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud_candidato
    ADD CONSTRAINT uq_tbl_estado_solicitud_candidato_nombre UNIQUE (essc_nombre);


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
-- Name: tbl_estudio_candidato uq_tbl_estudio_candidato_registro; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT uq_tbl_estudio_candidato_registro UNIQUE (etcd_candidato_id, etcd_institucion_id, etcd_carrera_id, etcd_fecha_inicio);


--
-- Name: tbl_experiencia_laboral uq_tbl_experiencia_laboral_registro; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral
    ADD CONSTRAINT uq_tbl_experiencia_laboral_registro UNIQUE (expl_candidato_id, expl_empresa_id, expl_cargo_id, expl_fecha_inicio);


--
-- Name: tbl_habilidad uq_tbl_habilidad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_habilidad
    ADD CONSTRAINT uq_tbl_habilidad_nombre UNIQUE (hab_nombre);


--
-- Name: tbl_institucion uq_tbl_institucion_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_institucion
    ADD CONSTRAINT uq_tbl_institucion_nombre UNIQUE (inst_nombre);


--
-- Name: tbl_modalidad uq_tbl_modalidad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_modalidad
    ADD CONSTRAINT uq_tbl_modalidad_nombre UNIQUE (mdld_nombre);


--
-- Name: tbl_motivo_rechazo uq_tbl_motivo_rechazo_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_motivo_rechazo
    ADD CONSTRAINT uq_tbl_motivo_rechazo_nombre UNIQUE (mtrc_nombre);


--
-- Name: tbl_nivel_educacional uq_tbl_nivel_educacional_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_educacional
    ADD CONSTRAINT uq_tbl_nivel_educacional_nombre UNIQUE (nved_nombre);


--
-- Name: tbl_nivel_habilidad uq_tbl_nivel_habilidad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_habilidad
    ADD CONSTRAINT uq_tbl_nivel_habilidad_nombre UNIQUE (nvhb_nombre);


--
-- Name: tbl_nombre_resultado uq_tbl_nombre_resultado_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nombre_resultado
    ADD CONSTRAINT uq_tbl_nombre_resultado_nombre UNIQUE (nore_nombre);


--
-- Name: tbl_opcion_respuesta uq_tbl_opcion_respuesta_pregunta_opcion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_opcion_respuesta
    ADD CONSTRAINT uq_tbl_opcion_respuesta_pregunta_opcion UNIQUE (opcr_pregunta_id, opcr_texto_opcion);


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
-- Name: tbl_pregunta uq_tbl_pregunta_texto_habilidad_nivel; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta
    ADD CONSTRAINT uq_tbl_pregunta_texto_habilidad_nivel UNIQUE (preg_texto_pregunta, preg_habilidad_id, preg_nivel_habilidad_id);


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
-- Name: tbl_respuesta_pregunta uq_tbl_respuesta_pregunta_candidato_pregunta; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT uq_tbl_respuesta_pregunta_candidato_pregunta UNIQUE (rspr_candidato_cuestionario_id, rspr_pregunta_cuestionario_id);


--
-- Name: tbl_rol uq_tbl_rol_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol
    ADD CONSTRAINT uq_tbl_rol_nombre UNIQUE (rol_nombre);


--
-- Name: tbl_solicitud_candidato uq_tbl_solicitud_candidato_postulacion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT uq_tbl_solicitud_candidato_postulacion UNIQUE (slcd_candidato_id, slcd_solicitud_id);


--
-- Name: tbl_solicitud uq_tbl_solicitud_codigo; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT uq_tbl_solicitud_codigo UNIQUE (sol_codigo);


--
-- Name: tbl_solicitud_habilidad uq_tbl_solicitud_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT uq_tbl_solicitud_habilidad UNIQUE (solhb_solicitud_id, solhb_habilidad_id);


--
-- Name: tbl_tipo_contrato uq_tbl_tipo_contrato_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_contrato
    ADD CONSTRAINT uq_tbl_tipo_contrato_nombre UNIQUE (tpct_nombre);


--
-- Name: tbl_tipo_entrevista uq_tbl_tipo_entrevista_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_entrevista
    ADD CONSTRAINT uq_tbl_tipo_entrevista_nombre UNIQUE (tpet_nombre);


--
-- Name: tbl_tipo_institucion uq_tbl_tipo_institucion_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_institucion
    ADD CONSTRAINT uq_tbl_tipo_institucion_nombre UNIQUE (tint_tipo_institucion);


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
-- Name: idx_tbl_candidato_apellidos; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_apellidos ON public.tbl_candidato USING btree (cand_apellido_paterno, cand_apellido_materno);


--
-- Name: idx_tbl_candidato_cuestionario_aprobado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_cuestionario_aprobado ON public.tbl_candidato_cuestionario USING btree (cdcu_aprobado);


--
-- Name: idx_tbl_candidato_cuestionario_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_cuestionario_candidato ON public.tbl_candidato_cuestionario USING btree (cdcu_candidato_id);


--
-- Name: idx_tbl_candidato_cuestionario_cuestionario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_cuestionario_cuestionario ON public.tbl_candidato_cuestionario USING btree (cdcu_cuestionario_id);


--
-- Name: idx_tbl_candidato_cuestionario_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_cuestionario_estado ON public.tbl_candidato_cuestionario USING btree (cdcu_estado_cuestionario_candidato_id);


--
-- Name: idx_tbl_candidato_cuestionario_fecha_asignacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_cuestionario_fecha_asignacion ON public.tbl_candidato_cuestionario USING btree (cdcu_fecha_asignacion);


--
-- Name: idx_tbl_candidato_disponibilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_disponibilidad ON public.tbl_candidato USING btree (cand_disponibilidad_id);


--
-- Name: idx_tbl_candidato_email; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_email ON public.tbl_candidato USING btree (cand_email);


--
-- Name: idx_tbl_candidato_fecha_creacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_fecha_creacion ON public.tbl_candidato USING btree (cand_fecha_creacion);


--
-- Name: idx_tbl_candidato_habilidad_anios; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_habilidad_anios ON public.tbl_candidato_habilidad USING btree (cdhb_anios_experiencia);


--
-- Name: idx_tbl_candidato_habilidad_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_habilidad_candidato ON public.tbl_candidato_habilidad USING btree (cdhb_candidato_id);


--
-- Name: idx_tbl_candidato_habilidad_habilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_habilidad_habilidad ON public.tbl_candidato_habilidad USING btree (cdhb_habilidad_id);


--
-- Name: idx_tbl_candidato_habilidad_nivel; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_habilidad_nivel ON public.tbl_candidato_habilidad USING btree (cdhb_nivel_habilidad_id);


--
-- Name: idx_tbl_candidato_titulo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_titulo ON public.tbl_candidato USING btree (cand_titulo);


--
-- Name: idx_tbl_cargo_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cargo_nombre ON public.tbl_cargo USING btree (crgo_nombre);


--
-- Name: idx_tbl_carrera_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_carrera_nombre ON public.tbl_carrera USING btree (crra_nombre);


--
-- Name: idx_tbl_cita_entrevista_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_estado ON public.tbl_cita_entrevista USING btree (ctev_estado_entrevista_id);


--
-- Name: idx_tbl_cita_entrevista_fecha_creacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_fecha_creacion ON public.tbl_cita_entrevista USING btree (ctev_fecha_creacion);


--
-- Name: idx_tbl_cita_entrevista_fecha_fin; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_fecha_fin ON public.tbl_cita_entrevista USING btree (ctev_fecha_hora_fin);


--
-- Name: idx_tbl_cita_entrevista_fecha_inicio; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_fecha_inicio ON public.tbl_cita_entrevista USING btree (ctev_fecha_hora_inicio);


--
-- Name: idx_tbl_cita_entrevista_solicitud_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_solicitud_candidato ON public.tbl_cita_entrevista USING btree (ctev_solicitud_candidato_id);


--
-- Name: idx_tbl_cita_entrevista_tipo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_tipo ON public.tbl_cita_entrevista USING btree (ctev_tipo_entrevista_id);


--
-- Name: idx_tbl_cita_tipo_entrevista_cita; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_tipo_entrevista_cita ON public.tbl_cita_tipo_entrevista USING btree (cten_cita_entrevista_id);


--
-- Name: idx_tbl_cita_tipo_entrevista_tipo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_tipo_entrevista_tipo ON public.tbl_cita_tipo_entrevista USING btree (cten_tipo_entrevista_id);


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
-- Name: idx_tbl_cuestionario_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cuestionario_nombre ON public.tbl_cuestionario USING btree (cues_nombre);


--
-- Name: idx_tbl_cuestionario_porcentaje_aprobacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cuestionario_porcentaje_aprobacion ON public.tbl_cuestionario USING btree (cues_porcentaje_aprobacion);


--
-- Name: idx_tbl_cuestionario_solicitud; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cuestionario_solicitud ON public.tbl_cuestionario USING btree (cues_solicitud_id);


--
-- Name: idx_tbl_curso_anio; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_curso_anio ON public.tbl_curso USING btree (curs_anio_curso);


--
-- Name: idx_tbl_curso_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_curso_candidato ON public.tbl_curso USING btree (curs_candidato_id);


--
-- Name: idx_tbl_curso_institucion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_curso_institucion ON public.tbl_curso USING btree (curs_institucion_id);


--
-- Name: idx_tbl_curso_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_curso_nombre ON public.tbl_curso USING btree (curs_nombre_curso);


--
-- Name: idx_tbl_direccion_candidato_calle; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_direccion_candidato_calle ON public.tbl_direccion_candidato USING btree (drcd_calle);


--
-- Name: idx_tbl_direccion_candidato_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_direccion_candidato_candidato ON public.tbl_direccion_candidato USING btree (drcd_candidato_id);


--
-- Name: idx_tbl_direccion_candidato_comuna; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_direccion_candidato_comuna ON public.tbl_direccion_candidato USING btree (drcd_comuna_id);


--
-- Name: idx_tbl_disponibilidad_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_disponibilidad_nombre ON public.tbl_disponibilidad USING btree (disp_nombre);


--
-- Name: idx_tbl_empresa_identificacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_empresa_identificacion ON public.tbl_empresa USING btree (emp_identificacion);


--
-- Name: idx_tbl_empresa_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_empresa_nombre ON public.tbl_empresa USING btree (emp_nombre);


--
-- Name: idx_tbl_estado_cuestionario_candidato_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_cuestionario_candidato_nombre ON public.tbl_estado_cuestionario_candidato USING btree (escc_nombre);


--
-- Name: idx_tbl_estado_entrevista_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_entrevista_nombre ON public.tbl_estado_entrevista USING btree (esev_nombre);


--
-- Name: idx_tbl_estado_solicitud_candidato_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_solicitud_candidato_nombre ON public.tbl_estado_solicitud_candidato USING btree (essc_nombre);


--
-- Name: idx_tbl_estado_solicitud_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_solicitud_nombre ON public.tbl_estado_solicitud USING btree (essl_nombre);


--
-- Name: idx_tbl_estado_usuario_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_usuario_nombre ON public.tbl_estado_usuario USING btree (esusr_nombre);


--
-- Name: idx_tbl_estudio_candidato_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_candidato ON public.tbl_estudio_candidato USING btree (etcd_candidato_id);


--
-- Name: idx_tbl_estudio_candidato_carrera; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_carrera ON public.tbl_estudio_candidato USING btree (etcd_carrera_id);


--
-- Name: idx_tbl_estudio_candidato_fecha_fin; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_fecha_fin ON public.tbl_estudio_candidato USING btree (etcd_fecha_fin);


--
-- Name: idx_tbl_estudio_candidato_fecha_inicio; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_fecha_inicio ON public.tbl_estudio_candidato USING btree (etcd_fecha_inicio);


--
-- Name: idx_tbl_estudio_candidato_institucion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_institucion ON public.tbl_estudio_candidato USING btree (etcd_institucion_id);


--
-- Name: idx_tbl_estudio_candidato_nivel_educacional; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_nivel_educacional ON public.tbl_estudio_candidato USING btree (etcd_nivel_educacional_id);


--
-- Name: idx_tbl_evaluacion_entrevista_cita; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_evaluacion_entrevista_cita ON public.tbl_evaluacion_entrevista USING btree (even_cita_entrevista_id);


--
-- Name: idx_tbl_evaluacion_entrevista_resultado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_evaluacion_entrevista_resultado ON public.tbl_evaluacion_entrevista USING btree (even_nombre_resultado_id);


--
-- Name: idx_tbl_experiencia_laboral_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_experiencia_laboral_candidato ON public.tbl_experiencia_laboral USING btree (expl_candidato_id);


--
-- Name: idx_tbl_experiencia_laboral_cargo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_experiencia_laboral_cargo ON public.tbl_experiencia_laboral USING btree (expl_cargo_id);


--
-- Name: idx_tbl_experiencia_laboral_empresa; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_experiencia_laboral_empresa ON public.tbl_experiencia_laboral USING btree (expl_empresa_id);


--
-- Name: idx_tbl_experiencia_laboral_fecha_fin; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_experiencia_laboral_fecha_fin ON public.tbl_experiencia_laboral USING btree (expl_fecha_fin);


--
-- Name: idx_tbl_experiencia_laboral_fecha_inicio; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_experiencia_laboral_fecha_inicio ON public.tbl_experiencia_laboral USING btree (expl_fecha_inicio);


--
-- Name: idx_tbl_expl_habilidad_experiencia; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_expl_habilidad_experiencia ON public.tbl_experiencia_laboral_habilidad USING btree (exph_experiencia_laboral_id);


--
-- Name: idx_tbl_expl_habilidad_habilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_expl_habilidad_habilidad ON public.tbl_experiencia_laboral_habilidad USING btree (exph_habilidad_id);


--
-- Name: idx_tbl_habilidad_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_habilidad_nombre ON public.tbl_habilidad USING btree (hab_nombre);


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
-- Name: idx_tbl_institucion_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_institucion_nombre ON public.tbl_institucion USING btree (inst_nombre);


--
-- Name: idx_tbl_institucion_tipo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_institucion_tipo ON public.tbl_institucion USING btree (inst_tipo_institucion_id);


--
-- Name: idx_tbl_modalidad_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_modalidad_nombre ON public.tbl_modalidad USING btree (mdld_nombre);


--
-- Name: idx_tbl_motivo_rechazo_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_motivo_rechazo_nombre ON public.tbl_motivo_rechazo USING btree (mtrc_nombre);


--
-- Name: idx_tbl_nivel_educacional_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_nivel_educacional_nombre ON public.tbl_nivel_educacional USING btree (nved_nombre);


--
-- Name: idx_tbl_nivel_habilidad_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_nivel_habilidad_nombre ON public.tbl_nivel_habilidad USING btree (nvhb_nombre);


--
-- Name: idx_tbl_nivel_habilidad_puntaje; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_nivel_habilidad_puntaje ON public.tbl_nivel_habilidad USING btree (nvhb_puntaje_base);


--
-- Name: idx_tbl_nombre_resultado_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_nombre_resultado_nombre ON public.tbl_nombre_resultado USING btree (nore_nombre);


--
-- Name: idx_tbl_opcion_respuesta_correcta; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_opcion_respuesta_correcta ON public.tbl_opcion_respuesta USING btree (opcr_es_correcta);


--
-- Name: idx_tbl_opcion_respuesta_pregunta; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_opcion_respuesta_pregunta ON public.tbl_opcion_respuesta USING btree (opcr_pregunta_id);


--
-- Name: idx_tbl_pais_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pais_nombre ON public.tbl_pais USING btree (pais_nombre);


--
-- Name: idx_tbl_permiso_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_permiso_nombre ON public.tbl_permiso USING btree (per_nombre);


--
-- Name: idx_tbl_pregunta_cuestionario_cuestionario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pregunta_cuestionario_cuestionario ON public.tbl_pregunta_cuestionario USING btree (prcu_cuestionario_id);


--
-- Name: idx_tbl_pregunta_cuestionario_pregunta; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pregunta_cuestionario_pregunta ON public.tbl_pregunta_cuestionario USING btree (prcu_pregunta_id);


--
-- Name: idx_tbl_pregunta_fecha_creacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pregunta_fecha_creacion ON public.tbl_pregunta USING btree (preg_fecha_creacion);


--
-- Name: idx_tbl_pregunta_habilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pregunta_habilidad ON public.tbl_pregunta USING btree (preg_habilidad_id);


--
-- Name: idx_tbl_pregunta_nivel_habilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pregunta_nivel_habilidad ON public.tbl_pregunta USING btree (preg_nivel_habilidad_id);


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
-- Name: idx_tbl_respuesta_pregunta_candidato_cuestionario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_respuesta_pregunta_candidato_cuestionario ON public.tbl_respuesta_pregunta USING btree (rspr_candidato_cuestionario_id);


--
-- Name: idx_tbl_respuesta_pregunta_correcta; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_respuesta_pregunta_correcta ON public.tbl_respuesta_pregunta USING btree (rspr_es_correcta);


--
-- Name: idx_tbl_respuesta_pregunta_opcion_respuesta; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_respuesta_pregunta_opcion_respuesta ON public.tbl_respuesta_pregunta USING btree (rspr_opcion_respuesta_id);


--
-- Name: idx_tbl_respuesta_pregunta_pregunta_cuestionario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_respuesta_pregunta_pregunta_cuestionario ON public.tbl_respuesta_pregunta USING btree (rspr_pregunta_cuestionario_id);


--
-- Name: idx_tbl_rol_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_rol_nombre ON public.tbl_rol USING btree (rol_nombre);


--
-- Name: idx_tbl_rol_permiso_permiso; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_rol_permiso_permiso ON public.tbl_rol_permiso USING btree (rlpm_permiso_id);


--
-- Name: idx_tbl_rol_permiso_rol; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_rol_permiso_rol ON public.tbl_rol_permiso USING btree (rlpm_rol_id);


--
-- Name: idx_tbl_solicitud_candidato_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_candidato ON public.tbl_solicitud_candidato USING btree (slcd_candidato_id);


--
-- Name: idx_tbl_solicitud_candidato_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_estado ON public.tbl_solicitud_candidato USING btree (slcd_estado_solicitud_id);


--
-- Name: idx_tbl_solicitud_candidato_fecha_postulacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_fecha_postulacion ON public.tbl_solicitud_candidato USING btree (slcd_fecha_postulacion);


--
-- Name: idx_tbl_solicitud_candidato_motivo_rechazo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_motivo_rechazo ON public.tbl_solicitud_candidato USING btree (slcd_motivo_rechazo_id);


--
-- Name: idx_tbl_solicitud_candidato_puntaje; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_puntaje ON public.tbl_solicitud_candidato USING btree (slcd_puntaje_compatibilidad);


--
-- Name: idx_tbl_solicitud_candidato_solicitud; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_solicitud ON public.tbl_solicitud_candidato USING btree (slcd_solicitud_id);


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
-- Name: idx_tbl_solicitud_habilidad_excluyente; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_habilidad_excluyente ON public.tbl_solicitud_habilidad USING btree (solhb_es_excluyente);


--
-- Name: idx_tbl_solicitud_habilidad_habilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_habilidad_habilidad ON public.tbl_solicitud_habilidad USING btree (solhb_habilidad_id);


--
-- Name: idx_tbl_solicitud_habilidad_nivel; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_habilidad_nivel ON public.tbl_solicitud_habilidad USING btree (solhb_nivel_habilidad_id);


--
-- Name: idx_tbl_solicitud_habilidad_solicitud; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_habilidad_solicitud ON public.tbl_solicitud_habilidad USING btree (solhb_solicitud_id);


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
-- Name: idx_tbl_tipo_entrevista_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_tipo_entrevista_nombre ON public.tbl_tipo_entrevista USING btree (tpet_nombre);


--
-- Name: idx_tbl_tipo_institucion_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_tipo_institucion_nombre ON public.tbl_tipo_institucion USING btree (tint_tipo_institucion);


--
-- Name: idx_tbl_usuario_apellidos; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_apellidos ON public.tbl_usuario USING btree (usr_apellido_paterno, usr_apellido_materno);


--
-- Name: idx_tbl_usuario_area; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_area ON public.tbl_usuario USING btree (usr_area_id);


--
-- Name: idx_tbl_usuario_cita_entrevista_cita; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_cita_entrevista_cita ON public.tbl_usuario_cita_entrevista USING btree (usrce_cita_entrevista_id);


--
-- Name: idx_tbl_usuario_cita_entrevista_usuario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_cita_entrevista_usuario ON public.tbl_usuario_cita_entrevista USING btree (usrce_usuario_id);


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
-- Name: tbl_candidato_cuestionario fk_tbl_candidato_cuestionario_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_cuestionario
    ADD CONSTRAINT fk_tbl_candidato_cuestionario_candidato FOREIGN KEY (cdcu_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_candidato_cuestionario fk_tbl_candidato_cuestionario_cuestionario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_cuestionario
    ADD CONSTRAINT fk_tbl_candidato_cuestionario_cuestionario FOREIGN KEY (cdcu_cuestionario_id) REFERENCES public.tbl_cuestionario(cues_id);


--
-- Name: tbl_candidato_cuestionario fk_tbl_candidato_cuestionario_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_cuestionario
    ADD CONSTRAINT fk_tbl_candidato_cuestionario_estado FOREIGN KEY (cdcu_estado_cuestionario_candidato_id) REFERENCES public.tbl_estado_cuestionario_candidato(escc_id);


--
-- Name: tbl_candidato fk_tbl_candidato_disponibilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato
    ADD CONSTRAINT fk_tbl_candidato_disponibilidad FOREIGN KEY (cand_disponibilidad_id) REFERENCES public.tbl_disponibilidad(disp_id);


--
-- Name: tbl_candidato_habilidad fk_tbl_candidato_habilidad_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT fk_tbl_candidato_habilidad_candidato FOREIGN KEY (cdhb_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_candidato_habilidad fk_tbl_candidato_habilidad_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT fk_tbl_candidato_habilidad_habilidad FOREIGN KEY (cdhb_habilidad_id) REFERENCES public.tbl_habilidad(hab_id);


--
-- Name: tbl_candidato_habilidad fk_tbl_candidato_habilidad_nivel; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT fk_tbl_candidato_habilidad_nivel FOREIGN KEY (cdhb_nivel_habilidad_id) REFERENCES public.tbl_nivel_habilidad(nvhb_id);


--
-- Name: tbl_cita_entrevista fk_tbl_cita_entrevista_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT fk_tbl_cita_entrevista_estado FOREIGN KEY (ctev_estado_entrevista_id) REFERENCES public.tbl_estado_entrevista(esev_id);


--
-- Name: tbl_cita_entrevista fk_tbl_cita_entrevista_solicitud_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT fk_tbl_cita_entrevista_solicitud_candidato FOREIGN KEY (ctev_solicitud_candidato_id) REFERENCES public.tbl_solicitud_candidato(slcd_id);


--
-- Name: tbl_cita_entrevista fk_tbl_cita_entrevista_tipo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT fk_tbl_cita_entrevista_tipo FOREIGN KEY (ctev_tipo_entrevista_id) REFERENCES public.tbl_tipo_entrevista(tpet_id);


--
-- Name: tbl_cita_tipo_entrevista fk_tbl_cita_tipo_entrevista_cita; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_tipo_entrevista
    ADD CONSTRAINT fk_tbl_cita_tipo_entrevista_cita FOREIGN KEY (cten_cita_entrevista_id) REFERENCES public.tbl_cita_entrevista(ctev_id);


--
-- Name: tbl_cita_tipo_entrevista fk_tbl_cita_tipo_entrevista_tipo_entrevista; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_tipo_entrevista
    ADD CONSTRAINT fk_tbl_cita_tipo_entrevista_tipo_entrevista FOREIGN KEY (cten_tipo_entrevista_id) REFERENCES public.tbl_tipo_entrevista(tpet_id);


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
-- Name: tbl_cuestionario fk_tbl_cuestionario_solicitud; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cuestionario
    ADD CONSTRAINT fk_tbl_cuestionario_solicitud FOREIGN KEY (cues_solicitud_id) REFERENCES public.tbl_solicitud(sol_id);


--
-- Name: tbl_curso fk_tbl_curso_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_curso
    ADD CONSTRAINT fk_tbl_curso_candidato FOREIGN KEY (curs_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_curso fk_tbl_curso_institucion; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_curso
    ADD CONSTRAINT fk_tbl_curso_institucion FOREIGN KEY (curs_institucion_id) REFERENCES public.tbl_institucion(inst_id);


--
-- Name: tbl_direccion_candidato fk_tbl_direccion_candidato_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_direccion_candidato
    ADD CONSTRAINT fk_tbl_direccion_candidato_candidato FOREIGN KEY (drcd_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_direccion_candidato fk_tbl_direccion_candidato_comuna; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_direccion_candidato
    ADD CONSTRAINT fk_tbl_direccion_candidato_comuna FOREIGN KEY (drcd_comuna_id) REFERENCES public.tbl_comuna(com_id);


--
-- Name: tbl_estudio_candidato fk_tbl_estudio_candidato_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT fk_tbl_estudio_candidato_candidato FOREIGN KEY (etcd_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_estudio_candidato fk_tbl_estudio_candidato_carrera; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT fk_tbl_estudio_candidato_carrera FOREIGN KEY (etcd_carrera_id) REFERENCES public.tbl_carrera(crra_id);


--
-- Name: tbl_estudio_candidato fk_tbl_estudio_candidato_institucion; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT fk_tbl_estudio_candidato_institucion FOREIGN KEY (etcd_institucion_id) REFERENCES public.tbl_institucion(inst_id);


--
-- Name: tbl_estudio_candidato fk_tbl_estudio_candidato_nivel_educacional; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT fk_tbl_estudio_candidato_nivel_educacional FOREIGN KEY (etcd_nivel_educacional_id) REFERENCES public.tbl_nivel_educacional(nved_id);


--
-- Name: tbl_evaluacion_entrevista fk_tbl_evaluacion_entrevista_cita; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_evaluacion_entrevista
    ADD CONSTRAINT fk_tbl_evaluacion_entrevista_cita FOREIGN KEY (even_cita_entrevista_id) REFERENCES public.tbl_cita_entrevista(ctev_id);


--
-- Name: tbl_evaluacion_entrevista fk_tbl_evaluacion_entrevista_resultado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_evaluacion_entrevista
    ADD CONSTRAINT fk_tbl_evaluacion_entrevista_resultado FOREIGN KEY (even_nombre_resultado_id) REFERENCES public.tbl_nombre_resultado(nore_id);


--
-- Name: tbl_experiencia_laboral fk_tbl_experiencia_laboral_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral
    ADD CONSTRAINT fk_tbl_experiencia_laboral_candidato FOREIGN KEY (expl_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_experiencia_laboral fk_tbl_experiencia_laboral_cargo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral
    ADD CONSTRAINT fk_tbl_experiencia_laboral_cargo FOREIGN KEY (expl_cargo_id) REFERENCES public.tbl_cargo(crgo_id);


--
-- Name: tbl_experiencia_laboral fk_tbl_experiencia_laboral_empresa; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral
    ADD CONSTRAINT fk_tbl_experiencia_laboral_empresa FOREIGN KEY (expl_empresa_id) REFERENCES public.tbl_empresa(emp_id);


--
-- Name: tbl_experiencia_laboral_habilidad fk_tbl_expl_habilidad_experiencia; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral_habilidad
    ADD CONSTRAINT fk_tbl_expl_habilidad_experiencia FOREIGN KEY (exph_experiencia_laboral_id) REFERENCES public.tbl_experiencia_laboral(expl_id);


--
-- Name: tbl_experiencia_laboral_habilidad fk_tbl_expl_habilidad_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral_habilidad
    ADD CONSTRAINT fk_tbl_expl_habilidad_habilidad FOREIGN KEY (exph_habilidad_id) REFERENCES public.tbl_habilidad(hab_id);


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
-- Name: tbl_institucion fk_tbl_institucion_tipo_institucion; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_institucion
    ADD CONSTRAINT fk_tbl_institucion_tipo_institucion FOREIGN KEY (inst_tipo_institucion_id) REFERENCES public.tbl_tipo_institucion(tint_id);


--
-- Name: tbl_opcion_respuesta fk_tbl_opcion_respuesta_pregunta; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_opcion_respuesta
    ADD CONSTRAINT fk_tbl_opcion_respuesta_pregunta FOREIGN KEY (opcr_pregunta_id) REFERENCES public.tbl_pregunta(preg_id);


--
-- Name: tbl_pregunta_cuestionario fk_tbl_pregunta_cuestionario_cuestionario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta_cuestionario
    ADD CONSTRAINT fk_tbl_pregunta_cuestionario_cuestionario FOREIGN KEY (prcu_cuestionario_id) REFERENCES public.tbl_cuestionario(cues_id);


--
-- Name: tbl_pregunta_cuestionario fk_tbl_pregunta_cuestionario_pregunta; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta_cuestionario
    ADD CONSTRAINT fk_tbl_pregunta_cuestionario_pregunta FOREIGN KEY (prcu_pregunta_id) REFERENCES public.tbl_pregunta(preg_id);


--
-- Name: tbl_pregunta fk_tbl_pregunta_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta
    ADD CONSTRAINT fk_tbl_pregunta_habilidad FOREIGN KEY (preg_habilidad_id) REFERENCES public.tbl_habilidad(hab_id);


--
-- Name: tbl_pregunta fk_tbl_pregunta_nivel_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta
    ADD CONSTRAINT fk_tbl_pregunta_nivel_habilidad FOREIGN KEY (preg_nivel_habilidad_id) REFERENCES public.tbl_nivel_habilidad(nvhb_id);


--
-- Name: tbl_region fk_tbl_region_pais; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_region
    ADD CONSTRAINT fk_tbl_region_pais FOREIGN KEY (reg_pais_id) REFERENCES public.tbl_pais(pais_id);


--
-- Name: tbl_respuesta_pregunta fk_tbl_respuesta_pregunta_candidato_cuestionario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT fk_tbl_respuesta_pregunta_candidato_cuestionario FOREIGN KEY (rspr_candidato_cuestionario_id) REFERENCES public.tbl_candidato_cuestionario(cdcu_id);


--
-- Name: tbl_respuesta_pregunta fk_tbl_respuesta_pregunta_opcion_respuesta; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT fk_tbl_respuesta_pregunta_opcion_respuesta FOREIGN KEY (rspr_opcion_respuesta_id) REFERENCES public.tbl_opcion_respuesta(opcr_id);


--
-- Name: tbl_respuesta_pregunta fk_tbl_respuesta_pregunta_pregunta_cuestionario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT fk_tbl_respuesta_pregunta_pregunta_cuestionario FOREIGN KEY (rspr_pregunta_cuestionario_id) REFERENCES public.tbl_pregunta_cuestionario(prcu_id);


--
-- Name: tbl_rol_permiso fk_tbl_rol_permiso_permiso; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol_permiso
    ADD CONSTRAINT fk_tbl_rol_permiso_permiso FOREIGN KEY (rlpm_permiso_id) REFERENCES public.tbl_permiso(per_id);


--
-- Name: tbl_rol_permiso fk_tbl_rol_permiso_rol; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol_permiso
    ADD CONSTRAINT fk_tbl_rol_permiso_rol FOREIGN KEY (rlpm_rol_id) REFERENCES public.tbl_rol(rol_id);


--
-- Name: tbl_solicitud_candidato fk_tbl_solicitud_candidato_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT fk_tbl_solicitud_candidato_candidato FOREIGN KEY (slcd_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_solicitud_candidato fk_tbl_solicitud_candidato_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT fk_tbl_solicitud_candidato_estado FOREIGN KEY (slcd_estado_solicitud_id) REFERENCES public.tbl_estado_solicitud_candidato(essc_id);


--
-- Name: tbl_solicitud_candidato fk_tbl_solicitud_candidato_motivo_rechazo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT fk_tbl_solicitud_candidato_motivo_rechazo FOREIGN KEY (slcd_motivo_rechazo_id) REFERENCES public.tbl_motivo_rechazo(mtrc_id);


--
-- Name: tbl_solicitud_candidato fk_tbl_solicitud_candidato_solicitud; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT fk_tbl_solicitud_candidato_solicitud FOREIGN KEY (slcd_solicitud_id) REFERENCES public.tbl_solicitud(sol_id);


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
-- Name: tbl_solicitud_habilidad fk_tbl_solicitud_habilidad_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT fk_tbl_solicitud_habilidad_habilidad FOREIGN KEY (solhb_habilidad_id) REFERENCES public.tbl_habilidad(hab_id);


--
-- Name: tbl_solicitud_habilidad fk_tbl_solicitud_habilidad_nivel; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT fk_tbl_solicitud_habilidad_nivel FOREIGN KEY (solhb_nivel_habilidad_id) REFERENCES public.tbl_nivel_habilidad(nvhb_id);


--
-- Name: tbl_solicitud_habilidad fk_tbl_solicitud_habilidad_solicitud; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT fk_tbl_solicitud_habilidad_solicitud FOREIGN KEY (solhb_solicitud_id) REFERENCES public.tbl_solicitud(sol_id);


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
-- Name: tbl_usuario_cita_entrevista fk_tbl_usuario_cita_entrevista_cita; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario_cita_entrevista
    ADD CONSTRAINT fk_tbl_usuario_cita_entrevista_cita FOREIGN KEY (usrce_cita_entrevista_id) REFERENCES public.tbl_cita_entrevista(ctev_id);


--
-- Name: tbl_usuario_cita_entrevista fk_tbl_usuario_cita_entrevista_usuario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario_cita_entrevista
    ADD CONSTRAINT fk_tbl_usuario_cita_entrevista_usuario FOREIGN KEY (usrce_usuario_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_usuario fk_tbl_usuario_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT fk_tbl_usuario_estado FOREIGN KEY (usr_estado_usuario_id) REFERENCES public.tbl_estado_usuario(esusr_id);


--
-- Name: tbl_candidato fk_tbl_usuario_estado_usuario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato
    ADD CONSTRAINT fk_tbl_usuario_estado_usuario FOREIGN KEY (cand_estado_usuario_id) REFERENCES public.tbl_estado_usuario(esusr_id);


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

\unrestrict bgcFlw1rjX8lJDnn00fmtEH2LJeKd2mhgwsyuPBehRloNzuohV3Lxi8KThSc4yD

