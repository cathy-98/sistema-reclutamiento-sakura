--
-- PostgreSQL database dump
--

\restrict QIqinGn8oSSbMjt5JTbpPpAVjV9Db5f1pMV8FaIULydalP9wTOEAk106hSaxvEh

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: tbl_area; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_area (
    id_area integer NOT NULL,
    nombre_area character varying(100) NOT NULL
);


ALTER TABLE public.tbl_area OWNER TO elitsoft_admin;

--
-- Name: tbl_area_id_area_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.tbl_area_id_area_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_area_id_area_seq OWNER TO elitsoft_admin;

--
-- Name: tbl_area_id_area_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.tbl_area_id_area_seq OWNED BY public.tbl_area.id_area;


--
-- Name: tbl_cargo; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cargo (
    id_cargo integer NOT NULL,
    nombre_cargo character varying(100) NOT NULL
);


ALTER TABLE public.tbl_cargo OWNER TO elitsoft_admin;

--
-- Name: tbl_cargo_id_cargo_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.tbl_cargo_id_cargo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_cargo_id_cargo_seq OWNER TO elitsoft_admin;

--
-- Name: tbl_cargo_id_cargo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.tbl_cargo_id_cargo_seq OWNED BY public.tbl_cargo.id_cargo;


--
-- Name: tbl_cliente; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cliente (
    id_cliente integer NOT NULL,
    nombre_cliente character varying(150) NOT NULL
);


ALTER TABLE public.tbl_cliente OWNER TO elitsoft_admin;

--
-- Name: tbl_cliente_id_cliente_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.tbl_cliente_id_cliente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_cliente_id_cliente_seq OWNER TO elitsoft_admin;

--
-- Name: tbl_cliente_id_cliente_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.tbl_cliente_id_cliente_seq OWNED BY public.tbl_cliente.id_cliente;


--
-- Name: tbl_estado_solicitud; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_solicitud (
    id_estado_solicitud integer NOT NULL,
    nombre_estado_solicitud character varying(50) NOT NULL
);


ALTER TABLE public.tbl_estado_solicitud OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_solicitud_id_estado_solicitud_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.tbl_estado_solicitud_id_estado_solicitud_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_estado_solicitud_id_estado_solicitud_seq OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_solicitud_id_estado_solicitud_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.tbl_estado_solicitud_id_estado_solicitud_seq OWNED BY public.tbl_estado_solicitud.id_estado_solicitud;


--
-- Name: tbl_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_habilidad (
    id_habilidad integer NOT NULL,
    nombre_habilidad character varying(100) NOT NULL
);


ALTER TABLE public.tbl_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_habilidad_id_habilidad_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.tbl_habilidad_id_habilidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_habilidad_id_habilidad_seq OWNER TO elitsoft_admin;

--
-- Name: tbl_habilidad_id_habilidad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.tbl_habilidad_id_habilidad_seq OWNED BY public.tbl_habilidad.id_habilidad;


--
-- Name: tbl_modalidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_modalidad (
    id_modalidad integer NOT NULL,
    nombre_modalidad character varying(50) NOT NULL
);


ALTER TABLE public.tbl_modalidad OWNER TO elitsoft_admin;

--
-- Name: tbl_modalidad_id_modalidad_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.tbl_modalidad_id_modalidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_modalidad_id_modalidad_seq OWNER TO elitsoft_admin;

--
-- Name: tbl_modalidad_id_modalidad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.tbl_modalidad_id_modalidad_seq OWNED BY public.tbl_modalidad.id_modalidad;


--
-- Name: tbl_nivel_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nivel_habilidad (
    id_nivel_habilidad integer NOT NULL,
    nombre_nivel_habilidad character varying(50) NOT NULL
);


ALTER TABLE public.tbl_nivel_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_nivel_habilidad_id_nivel_habilidad_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.tbl_nivel_habilidad_id_nivel_habilidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_nivel_habilidad_id_nivel_habilidad_seq OWNER TO elitsoft_admin;

--
-- Name: tbl_nivel_habilidad_id_nivel_habilidad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.tbl_nivel_habilidad_id_nivel_habilidad_seq OWNED BY public.tbl_nivel_habilidad.id_nivel_habilidad;


--
-- Name: tbl_prioridad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_prioridad (
    id_prioridad integer NOT NULL,
    nombre_prioridad character varying(30) NOT NULL
);


ALTER TABLE public.tbl_prioridad OWNER TO elitsoft_admin;

--
-- Name: tbl_prioridad_id_prioridad_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.tbl_prioridad_id_prioridad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_prioridad_id_prioridad_seq OWNER TO elitsoft_admin;

--
-- Name: tbl_prioridad_id_prioridad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.tbl_prioridad_id_prioridad_seq OWNED BY public.tbl_prioridad.id_prioridad;


--
-- Name: tbl_solicitud; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_solicitud (
    id_solicitud integer NOT NULL,
    titulo character varying(200) NOT NULL,
    descripcion text,
    id_cargo integer NOT NULL,
    id_prioridad integer NOT NULL,
    cantidad_vacantes integer NOT NULL,
    id_cliente integer NOT NULL,
    id_usuario_solicitante integer NOT NULL,
    id_usuario_responsable integer,
    id_modalidad integer NOT NULL,
    salario_minimo numeric(12,2),
    salario_maximo numeric(12,2),
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_inicio_busqueda date,
    fecha_cierre_busqueda date,
    fecha_inicio_cliente date,
    id_estado_solicitud integer NOT NULL,
    id_area integer NOT NULL,
    CONSTRAINT chk_cantidad_vacantes CHECK ((cantidad_vacantes > 0)),
    CONSTRAINT chk_salarios CHECK (((salario_minimo IS NULL) OR (salario_maximo IS NULL) OR (salario_minimo <= salario_maximo)))
);


ALTER TABLE public.tbl_solicitud OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_solicitud_habilidad (
    id_solicitud_habilidad integer NOT NULL,
    id_solicitud integer NOT NULL,
    id_habilidad integer NOT NULL,
    id_nivel_habilidad integer NOT NULL,
    anios_experiencia integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.tbl_solicitud_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_habilidad_id_solicitud_habilidad_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.tbl_solicitud_habilidad_id_solicitud_habilidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_solicitud_habilidad_id_solicitud_habilidad_seq OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_habilidad_id_solicitud_habilidad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.tbl_solicitud_habilidad_id_solicitud_habilidad_seq OWNED BY public.tbl_solicitud_habilidad.id_solicitud_habilidad;


--
-- Name: tbl_solicitud_id_solicitud_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.tbl_solicitud_id_solicitud_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tbl_solicitud_id_solicitud_seq OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_id_solicitud_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.tbl_solicitud_id_solicitud_seq OWNED BY public.tbl_solicitud.id_solicitud;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    usuario character varying(50) NOT NULL,
    contrasena character varying(255) NOT NULL,
    email character varying(100) NOT NULL,
    rol character varying(30) NOT NULL
);


ALTER TABLE public.usuarios OWNER TO elitsoft_admin;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_seq OWNER TO elitsoft_admin;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: elitsoft_admin
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: tbl_area id_area; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_area ALTER COLUMN id_area SET DEFAULT nextval('public.tbl_area_id_area_seq'::regclass);


--
-- Name: tbl_cargo id_cargo; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cargo ALTER COLUMN id_cargo SET DEFAULT nextval('public.tbl_cargo_id_cargo_seq'::regclass);


--
-- Name: tbl_cliente id_cliente; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente ALTER COLUMN id_cliente SET DEFAULT nextval('public.tbl_cliente_id_cliente_seq'::regclass);


--
-- Name: tbl_estado_solicitud id_estado_solicitud; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud ALTER COLUMN id_estado_solicitud SET DEFAULT nextval('public.tbl_estado_solicitud_id_estado_solicitud_seq'::regclass);


--
-- Name: tbl_habilidad id_habilidad; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_habilidad ALTER COLUMN id_habilidad SET DEFAULT nextval('public.tbl_habilidad_id_habilidad_seq'::regclass);


--
-- Name: tbl_modalidad id_modalidad; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_modalidad ALTER COLUMN id_modalidad SET DEFAULT nextval('public.tbl_modalidad_id_modalidad_seq'::regclass);


--
-- Name: tbl_nivel_habilidad id_nivel_habilidad; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_habilidad ALTER COLUMN id_nivel_habilidad SET DEFAULT nextval('public.tbl_nivel_habilidad_id_nivel_habilidad_seq'::regclass);


--
-- Name: tbl_prioridad id_prioridad; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_prioridad ALTER COLUMN id_prioridad SET DEFAULT nextval('public.tbl_prioridad_id_prioridad_seq'::regclass);


--
-- Name: tbl_solicitud id_solicitud; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud ALTER COLUMN id_solicitud SET DEFAULT nextval('public.tbl_solicitud_id_solicitud_seq'::regclass);


--
-- Name: tbl_solicitud_habilidad id_solicitud_habilidad; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad ALTER COLUMN id_solicitud_habilidad SET DEFAULT nextval('public.tbl_solicitud_habilidad_id_solicitud_habilidad_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: tbl_area; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_area (id_area, nombre_area) FROM stdin;
1	Tecnolog├¡a
2	Operaciones
3	Recursos Humanos
\.


--
-- Data for Name: tbl_cargo; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cargo (id_cargo, nombre_cargo) FROM stdin;
1	Desarrollador Python
2	Desarrollador Angular
3	Analista QA
\.


--
-- Data for Name: tbl_cliente; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cliente (id_cliente, nombre_cliente) FROM stdin;
\.


--
-- Data for Name: tbl_estado_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_solicitud (id_estado_solicitud, nombre_estado_solicitud) FROM stdin;
1	Pendiente
2	En Curso
3	Cerrada
\.


--
-- Data for Name: tbl_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_habilidad (id_habilidad, nombre_habilidad) FROM stdin;
1	Python
2	SQL
3	Angular
4	Git
\.


--
-- Data for Name: tbl_modalidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_modalidad (id_modalidad, nombre_modalidad) FROM stdin;
1	Presencial
2	Remoto
3	H├¡brido
\.


--
-- Data for Name: tbl_nivel_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_nivel_habilidad (id_nivel_habilidad, nombre_nivel_habilidad) FROM stdin;
1	Trainee
2	Junior
3	Semi Senior
4	Senior
\.


--
-- Data for Name: tbl_prioridad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_prioridad (id_prioridad, nombre_prioridad) FROM stdin;
1	Alta
2	Media
3	Baja
\.


--
-- Data for Name: tbl_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_solicitud (id_solicitud, titulo, descripcion, id_cargo, id_prioridad, cantidad_vacantes, id_cliente, id_usuario_solicitante, id_usuario_responsable, id_modalidad, salario_minimo, salario_maximo, fecha_creacion, fecha_inicio_busqueda, fecha_cierre_busqueda, fecha_inicio_cliente, id_estado_solicitud, id_area) FROM stdin;
\.


--
-- Data for Name: tbl_solicitud_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_solicitud_habilidad (id_solicitud_habilidad, id_solicitud, id_habilidad, id_nivel_habilidad, anios_experiencia) FROM stdin;
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.usuarios (id, usuario, contrasena, email, rol) FROM stdin;
1	fvaldesm	felipe123	felipe@gmail.com	ADMIN
3	cathy98	cathy123	cathy@gmail.com	RECLUTADORA
2	nmchavezm	noe123	noelid@gmail.com	CANDIDATO
4	jperez	miClave123	juan.perez@gmail.com	CANDIDATO
\.


--
-- Name: tbl_area_id_area_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_area_id_area_seq', 3, true);


--
-- Name: tbl_cargo_id_cargo_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_cargo_id_cargo_seq', 3, true);


--
-- Name: tbl_cliente_id_cliente_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_cliente_id_cliente_seq', 1, false);


--
-- Name: tbl_estado_solicitud_id_estado_solicitud_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_solicitud_id_estado_solicitud_seq', 3, true);


--
-- Name: tbl_habilidad_id_habilidad_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_habilidad_id_habilidad_seq', 4, true);


--
-- Name: tbl_modalidad_id_modalidad_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_modalidad_id_modalidad_seq', 3, true);


--
-- Name: tbl_nivel_habilidad_id_nivel_habilidad_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_nivel_habilidad_id_nivel_habilidad_seq', 4, true);


--
-- Name: tbl_prioridad_id_prioridad_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_prioridad_id_prioridad_seq', 3, true);


--
-- Name: tbl_solicitud_habilidad_id_solicitud_habilidad_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_solicitud_habilidad_id_solicitud_habilidad_seq', 1, false);


--
-- Name: tbl_solicitud_id_solicitud_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_solicitud_id_solicitud_seq', 1, false);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 3, true);


--
-- Name: tbl_area tbl_area_nombre_area_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_area
    ADD CONSTRAINT tbl_area_nombre_area_key UNIQUE (nombre_area);


--
-- Name: tbl_area tbl_area_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_area
    ADD CONSTRAINT tbl_area_pkey PRIMARY KEY (id_area);


--
-- Name: tbl_cargo tbl_cargo_nombre_cargo_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cargo
    ADD CONSTRAINT tbl_cargo_nombre_cargo_key UNIQUE (nombre_cargo);


--
-- Name: tbl_cargo tbl_cargo_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cargo
    ADD CONSTRAINT tbl_cargo_pkey PRIMARY KEY (id_cargo);


--
-- Name: tbl_cliente tbl_cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT tbl_cliente_pkey PRIMARY KEY (id_cliente);


--
-- Name: tbl_estado_solicitud tbl_estado_solicitud_nombre_estado_solicitud_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud
    ADD CONSTRAINT tbl_estado_solicitud_nombre_estado_solicitud_key UNIQUE (nombre_estado_solicitud);


--
-- Name: tbl_estado_solicitud tbl_estado_solicitud_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud
    ADD CONSTRAINT tbl_estado_solicitud_pkey PRIMARY KEY (id_estado_solicitud);


--
-- Name: tbl_habilidad tbl_habilidad_nombre_habilidad_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_habilidad
    ADD CONSTRAINT tbl_habilidad_nombre_habilidad_key UNIQUE (nombre_habilidad);


--
-- Name: tbl_habilidad tbl_habilidad_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_habilidad
    ADD CONSTRAINT tbl_habilidad_pkey PRIMARY KEY (id_habilidad);


--
-- Name: tbl_modalidad tbl_modalidad_nombre_modalidad_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_modalidad
    ADD CONSTRAINT tbl_modalidad_nombre_modalidad_key UNIQUE (nombre_modalidad);


--
-- Name: tbl_modalidad tbl_modalidad_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_modalidad
    ADD CONSTRAINT tbl_modalidad_pkey PRIMARY KEY (id_modalidad);


--
-- Name: tbl_nivel_habilidad tbl_nivel_habilidad_nombre_nivel_habilidad_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_habilidad
    ADD CONSTRAINT tbl_nivel_habilidad_nombre_nivel_habilidad_key UNIQUE (nombre_nivel_habilidad);


--
-- Name: tbl_nivel_habilidad tbl_nivel_habilidad_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_habilidad
    ADD CONSTRAINT tbl_nivel_habilidad_pkey PRIMARY KEY (id_nivel_habilidad);


--
-- Name: tbl_prioridad tbl_prioridad_nombre_prioridad_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_prioridad
    ADD CONSTRAINT tbl_prioridad_nombre_prioridad_key UNIQUE (nombre_prioridad);


--
-- Name: tbl_prioridad tbl_prioridad_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_prioridad
    ADD CONSTRAINT tbl_prioridad_pkey PRIMARY KEY (id_prioridad);


--
-- Name: tbl_solicitud_habilidad tbl_solicitud_habilidad_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT tbl_solicitud_habilidad_pkey PRIMARY KEY (id_solicitud_habilidad);


--
-- Name: tbl_solicitud tbl_solicitud_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT tbl_solicitud_pkey PRIMARY KEY (id_solicitud);


--
-- Name: tbl_solicitud_habilidad uq_solicitud_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT uq_solicitud_habilidad UNIQUE (id_solicitud, id_habilidad);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_usuario_key; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_usuario_key UNIQUE (usuario);


--
-- Name: idx_usuarios_email; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_usuarios_email ON public.usuarios USING btree (email);


--
-- Name: tbl_solicitud_habilidad fk_sol_hab_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT fk_sol_hab_habilidad FOREIGN KEY (id_habilidad) REFERENCES public.tbl_habilidad(id_habilidad);


--
-- Name: tbl_solicitud_habilidad fk_sol_hab_nivel; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT fk_sol_hab_nivel FOREIGN KEY (id_nivel_habilidad) REFERENCES public.tbl_nivel_habilidad(id_nivel_habilidad);


--
-- Name: tbl_solicitud_habilidad fk_sol_hab_solicitud; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT fk_sol_hab_solicitud FOREIGN KEY (id_solicitud) REFERENCES public.tbl_solicitud(id_solicitud) ON DELETE CASCADE;


--
-- Name: tbl_solicitud fk_solicitud_area; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_solicitud_area FOREIGN KEY (id_area) REFERENCES public.tbl_area(id_area);


--
-- Name: tbl_solicitud fk_solicitud_cargo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_solicitud_cargo FOREIGN KEY (id_cargo) REFERENCES public.tbl_cargo(id_cargo);


--
-- Name: tbl_solicitud fk_solicitud_cliente; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_solicitud_cliente FOREIGN KEY (id_cliente) REFERENCES public.tbl_cliente(id_cliente);


--
-- Name: tbl_solicitud fk_solicitud_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_solicitud_estado FOREIGN KEY (id_estado_solicitud) REFERENCES public.tbl_estado_solicitud(id_estado_solicitud);


--
-- Name: tbl_solicitud fk_solicitud_modalidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_solicitud_modalidad FOREIGN KEY (id_modalidad) REFERENCES public.tbl_modalidad(id_modalidad);


--
-- Name: tbl_solicitud fk_solicitud_prioridad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_solicitud_prioridad FOREIGN KEY (id_prioridad) REFERENCES public.tbl_prioridad(id_prioridad);


--
-- Name: tbl_solicitud fk_solicitud_usuario_responsable; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_solicitud_usuario_responsable FOREIGN KEY (id_usuario_responsable) REFERENCES public.usuarios(id);


--
-- Name: tbl_solicitud fk_solicitud_usuario_solicitante; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_solicitud_usuario_solicitante FOREIGN KEY (id_usuario_solicitante) REFERENCES public.usuarios(id);


--
-- PostgreSQL database dump complete
--

\unrestrict yghH3j4AQRRmR70k1zb1e9JSbVwHWQVuP1AsPadpYl2BD1mHefHThWwOVM5NhAM

